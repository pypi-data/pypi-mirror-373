from pyparsing import (
    Forward,
    Group,
    Keyword,
    OneOrMore,
    OpAssoc,
    Opt,
    ParserElement,
    ParseResults,
    QuotedString,
    Suppress,
    Word,
    identchars,
    infixNotation,
    oneOf,
)
from pyparsing import pyparsing_common as ppc


def arith_check_types(tokens: ParseResults):
    if len(tokens) == 3:
        if tokens[1] != "+" and "numbers" in tokens and "strings" in tokens:
            msg = f"Arithmetic expression '{tokens}' mixes numbers and strings"
            raise TypeError(msg)
    return tokens


# Memoize latest n parsed formulas
ParserElement.enablePackrat(48)

# Define basic elements
number = ppc.number().set_results_name("numbers", True)
string = (
    QuotedString(r"'", esc_char=r"\\", esc_quote=r"\\", unquote_results=False)
).set_results_name("strings", True)
column = (
    Suppress("[") + Word(identchars, identchars + " ") + Suppress("]")
).set_results_name("columns", True)
null_value = Keyword("NULL").set_results_name("null", True)

ISNULL, ISNOTNULL, TOTAL, SQRT, POW = (
    Keyword(token) for token in ["ISNULL", "ISNOTNULL", "TOTAL", "SQRT", "POW"]
)
unary_func = Group(
    (ISNULL | ISNOTNULL | TOTAL | SQRT) + Suppress("(") + column + Suppress(")"),
).setName("unary function")

parameterized_func = Group(
    POW + Suppress("(") + column + Suppress(",") + number + Suppress(")"),
).setName("unary function")

operand = column | number | string | null_value | unary_func | parameterized_func

# Define a recursive expression
expr = Forward()

# Define arithmetic expressions
arith_expr = infixNotation(
    operand,
    [
        (oneOf("* / %"), 2, OpAssoc.LEFT, arith_check_types),
        (oneOf("+ -"), 2, OpAssoc.LEFT, arith_check_types),
    ],
)

# Define individual condition clauses
binop = oneOf("< > <= >= == != <>").setName("binary operation")
clause = infixNotation(expr, [(binop, 2, OpAssoc.LEFT)])

# Define conditions as composable clauses
NOT, AND, OR, XOR = Keyword("NOT"), Keyword("AND"), Keyword("OR"), Keyword("XOR")
condition = infixNotation(
    clause,
    [(NOT, 1, OpAssoc.RIGHT), (AND | OR | XOR, 2, OpAssoc.LEFT)],
)

# A conditional expression is a series of alternatives and maybe a default
WHEN, THEN, ELSE = (Keyword(token) for token in ["WHEN", "THEN", "ELSE"])
cond_expr = (
    Keyword("CASE")
    + OneOrMore(Group(WHEN + condition + THEN + expr))
    + Opt(Group(ELSE + arith_expr))
    + Keyword("END").suppress()
)

# An expression can be an arithmetic expression or a conditional expression
expr <<= arith_expr | cond_expr | unary_func

# expr.set_debug(flag=True)
