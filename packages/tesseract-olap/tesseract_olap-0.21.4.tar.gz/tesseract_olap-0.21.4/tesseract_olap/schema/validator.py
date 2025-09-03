from pathlib import Path
from typing import Optional

import xmlschema

schema_file = Path(__file__, "../schema.xsd").resolve()
schema = xmlschema.XMLSchema11(schema_file)


def _custom_validation(element, schema_element):
    # TODO: this is a raw validation inside the cube, and does not take into
    # account shared entities; we also need to check unique names for those
    if schema_element.name == "Cube":
        nameset = set()
        for item in element.iterfind("Level,Property"):
            name = item["name"]
            if name in nameset:
                yield xmlschema.XMLSchemaValidationError(
                    validator=_custom_validation,
                    obj=item,
                    reason=f"The name '{name}' is not unique in cube '{element['name']}'",
                )
            nameset.add(name)


def validate_schema(target: Path):
    if target.is_dir():
        for file in target.glob("**/*.xml"):
            _validate_xmlfile(file, target)

    elif target.is_file():
        _validate_xmlfile(target)


def _validate_xmlfile(file: Path, folder: Optional[Path] = None):
    for error in schema.iter_errors(
        file, extra_validator=_custom_validation, use_location_hints=True
    ):
        path = file.resolve() if folder is None else file.relative_to(folder)
        print("%s: %s" % (path, error.reason))
        # print(error.get_elem_as_string("    "))
        print("")
