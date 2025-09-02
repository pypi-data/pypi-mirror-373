"Tesseract OLAP command line tools."

import argparse
from pathlib import Path

from .schema import validate_schema


def command_validate(args: argparse.Namespace):
    for path in args.path:
        if not path.exists():
            raise FileNotFoundError(f"Schema target '{path}' does not exist")
        validate_schema(path.resolve())


def main():
    parser = argparse.ArgumentParser(prog="tesseract_olap", description=__doc__)
    subpar = parser.add_subparsers(title="subcommands", required=True)

    # Validator command
    parser_validate = subpar.add_parser(
        "validate",
        help="Validates a single schema file, or multiple schema files in a folder.",
    )
    parser_validate.add_argument(
        "path",
        metavar="P",
        type=Path,
        nargs=1,
        help="The path to the schema file or folder",
    )
    parser_validate.set_defaults(func=command_validate)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
