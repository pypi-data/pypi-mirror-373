import logging
from typing import Any, Callable, Union

from pyparsing import ParseResults
from pypika import analytics as an
from pypika import functions as fn
from pypika.enums import Arithmetic, Boolean
from pypika.queries import Selectable
from pypika.terms import (
    AggregateFunction,
    ArithmeticExpression,
    Case,
    ComplexCriterion,
    Criterion,
    Field,
    NullValue,
    Term,
    ValueWrapper,
)

from tesseract_olap.common import shorthash
from tesseract_olap.query import (
    Comparison,
    Condition,
    ConditionType,
    LogicOperator,
    Membership,
    NullityOperator,
    is_single_condition,
)
from tesseract_olap.schema import Measure

from .dialect import ArrayElement, Power, Quantile, TopK

logger = logging.getLogger(__name__)


def _get_aggregate(
    table: Selectable,
    measure: Measure,
) -> Union[fn.Function, ArithmeticExpression]:
    """Return the AggregateFunction instance needed to calculate a measure."""
    aggregator_type = str(measure.aggregator)
    column_hash = shorthash(measure.key_column)
    field = table.field(f"ms_{column_hash}")

    if aggregator_type == "Sum":
        return fn.Sum(field)

    if aggregator_type == "Count":
        return fn.Count(field)

    if aggregator_type == "Average":
        return fn.Avg(field)

    if aggregator_type == "Max":
        return fn.Max(field)

    if aggregator_type == "Min":
        return fn.Min(field)

    if aggregator_type == "Mode":
        return ArrayElement(TopK(1, field), 1)

    # elif aggregator_type == "BasicGroupedMedian":
    #     return fn.Abs()

    if aggregator_type == "WeightedSum":
        params = measure.aggregator.get_params()
        weight_field = table.field(f"msp_{column_hash}_weight")
        return fn.Sum(field * weight_field)

    if aggregator_type == "WeightedAverage":
        params = measure.aggregator.get_params()
        weight_field = table.field(f"msp_{column_hash}_weight")
        return AggregateFunction("avgWeighted", field, weight_field)

    # elif aggregator_type == "ReplicateWeightMoe":
    #     return fn.Abs()

    if aggregator_type == "CalculatedMoe":
        params = measure.aggregator.get_params()
        critical_value = ValueWrapper(params["critical_value"])
        term = fn.Sqrt(fn.Sum(Power(field / critical_value, 2)))
        return ArithmeticExpression(Arithmetic.mul, term, critical_value)

    if aggregator_type == "Median":
        return AggregateFunction("median", field)

    if aggregator_type == "Quantile":
        params = measure.aggregator.get_params()
        quantile_level = float(params["quantile_level"])
        return Quantile(quantile_level, field)

    if aggregator_type == "DistinctCount":
        # Count().distinct() might use a different function, configured in Clickhouse
        return AggregateFunction("uniqExact", field)

    # elif aggregator_type == "WeightedAverageMoe":
    #     return fn.Abs()

    msg = f"Aggregation type {aggregator_type!r} not implemented in Clickhouse module."
    raise NameError(msg)


def _filter_criterion(
    column: Field,
    constraint: Condition[Any],
    get_field: Callable[[str], Field],
) -> Criterion:
    """Apply comparison filters to query."""
    if not is_single_condition(constraint):
        # create criterion for first constraint
        left = _filter_criterion(column, constraint[0], get_field)
        right = _filter_criterion(column, constraint[2], get_field)

        if constraint[1] == LogicOperator.AND:
            return left & right
        if constraint[1] == LogicOperator.OR:
            return left | right
        if constraint[1] == LogicOperator.XOR:
            return left ^ right

    if constraint[0] == ConditionType.NULLITY:
        if constraint[1] == NullityOperator.ISNULL:
            return column.isnull()
        if constraint[1] == NullityOperator.ISNOTNULL:
            return column.isnotnull()

    if constraint[0] == ConditionType.MEMBERSHIP:
        if constraint[1] == Membership.IN:
            return column.isin(constraint[2])
        if constraint[1] == Membership.NIN:
            return column.notin(constraint[2])

    if constraint[0] == ConditionType.AGAINST_COLUMN:
        return _filter_comparison(column, (constraint[1], get_field(constraint[2])))

    if constraint[0] == ConditionType.AGAINST_SCALAR:
        return _filter_comparison(column, constraint[1:])

    msg = f"Invalid constraint: {constraint!r}"
    raise ValueError(msg)


def _filter_comparison(field: Field, constr: tuple[Comparison, Union[float, Field]]) -> Criterion:
    """Retrieve the comparison operator for the provided field."""
    comparison, reference = constr

    # Note we must use == to also compare Enums values to strings
    if comparison == Comparison.GT:
        return field.gt(reference)
    if comparison == Comparison.GTE:
        return field.gte(reference)
    if comparison == Comparison.LT:
        return field.lt(reference)
    if comparison == Comparison.LTE:
        return field.lte(reference)
    if comparison == Comparison.EQ:
        return field.eq(reference)
    if comparison == Comparison.NEQ:
        return field.ne(reference)

    msg = f"Invalid criterion type: {comparison}"
    raise ValueError(msg)


def _transf_formula(tokens: Any, field_builder: Callable[[str], Field]) -> Term:
    """Transform a :class:`pyparsing.ParseResults` formula into a :class:`pypika.Term` object."""
    if isinstance(tokens, (int, float)):
        return ValueWrapper(tokens)

    if isinstance(tokens, str):
        if (tokens.startswith("'") and tokens.endswith("'")) or (
            tokens.startswith('"') and tokens.endswith('"')
        ):
            return ValueWrapper(tokens[1:-1])
        if tokens == "NULL":
            return NullValue()
        return field_builder(tokens)

    if isinstance(tokens, ParseResults):
        if len(tokens) == 1:
            return _transf_formula(tokens[0], field_builder)

        if tokens[0] == "CASE":
            case = Case()

            for item in tokens[1:]:
                if item[0] == "WHEN":
                    clauses = _transf_formula(item[1], field_builder)
                    expr = _transf_formula(item[3], field_builder)
                    case = case.when(clauses, expr)
                elif item[0] == "ELSE":
                    expr = _transf_formula(item[1], field_builder)
                    case = case.else_(expr)
                    break

            return case

        if tokens[0] == "NOT":
            # 2 tokens: ["NOT", A]
            return _transf_formula(tokens[1], field_builder).negate()

        if tokens[1] in ("AND", "OR", "XOR"):
            # 2n + 1 tokens: [A, "AND", B, "OR", C]
            left = _transf_formula(tokens[0], field_builder)
            for index in range(len(tokens) // 2):
                comparator = Boolean(tokens[index * 2 + 1])
                right = _transf_formula(tokens[index * 2 + 2], field_builder)
                left = ComplexCriterion(comparator, left, right)
            return left

        column = tokens[1]
        if not isinstance(column, str):
            msg = f"Malformed formula: {tokens}"
            raise TypeError(msg)

        if tokens[0] == "ISNULL":
            return field_builder(column).isnull()

        if tokens[0] == "ISNOTNULL":
            return field_builder(column).isnotnull()

        if tokens[0] == "TOTAL":
            return an.Sum(field_builder(column)).over()

        if tokens[0] == "SQRT":
            return fn.Sqrt(field_builder(column))

        if tokens[0] == "POW":
            return field_builder(column) ** tokens[2]

        # At this point expected formula is binary op, ensure odd number of params
        if len(tokens) % 2 == 0:
            msg = f"Malformed formula, binary operation expected: {tokens}"
            raise ValueError(msg)

        # Parse binary expressions left to right in order
        branch_left = _transf_formula(tokens[0], field_builder)

        for index in range(1, len(tokens), 2):
            operator = tokens[index]

            if not isinstance(operator, str):
                msg = f"Malformed formula, binary operator expected: {operator!r}"
                raise TypeError(msg)

            branch_right = _transf_formula(tokens[index + 1], field_builder)

            if operator == ">":
                branch_left = branch_left > branch_right
            elif operator == "<":
                branch_left = branch_left < branch_right
            elif operator == ">=":
                branch_left = branch_left >= branch_right
            elif operator == "<=":
                branch_left = branch_left <= branch_right
            elif operator == "==":
                branch_left = branch_left == branch_right
            elif operator in ("!=", "<>"):
                branch_left = branch_left != branch_right

            elif operator == "+":
                branch_left = branch_left + branch_right
            elif operator == "-":
                branch_left = branch_left - branch_right
            elif operator == "*":
                branch_left = branch_left * branch_right
            elif operator == "/":
                branch_left = branch_left / branch_right
            elif operator == "%":
                branch_left = branch_left % branch_right

            else:
                msg = f"Malformed formula, operator {operator!r} is not supported"
                raise ValueError(msg)

        return branch_left

    logger.error("Couldn't parse formula: <%s %r>", type(tokens).__name__, tokens)
    msg = f"Expression '{tokens!r}' can't be parsed"
    raise ValueError(msg)
