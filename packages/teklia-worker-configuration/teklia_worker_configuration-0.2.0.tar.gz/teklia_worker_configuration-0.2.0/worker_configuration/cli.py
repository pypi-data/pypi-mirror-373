import argparse
import logging
from pathlib import Path

from worker_configuration.convert import convert
from worker_configuration.validator import validate_files


def main():
    logging.basicConfig(
        format="[%(levelname)s] %(message)s",
        level=logging.INFO,
    )

    parser = argparse.ArgumentParser(
        prog="worker-configuration",
        description="Scripts for Arkindex worker configuration management and validation",
    )
    commands = parser.add_subparsers()

    validate = commands.add_parser(
        "validate",
        help="Validate one or more Arkindex worker configuration files in YAML format",
    )
    validate.set_defaults(func=validate_files)
    validate.add_argument(
        "paths",
        type=Path,
        nargs="+",
        metavar="PATH",
        help="Path to a file to validate.",
    )

    convert_command = commands.add_parser(
        "convert",
        help="Convert a .arkindex.yml configuration to the new format",
    )
    convert_command.set_defaults(func=convert)
    convert_command.add_argument(
        "path",
        type=Path,
        help="Path to a .arkindex.yml configuration to convert.",
        nargs="?",
        default=Path(".arkindex.yml"),
    )

    args = vars(parser.parse_args())
    if "func" in args:
        parser.exit(status=args.pop("func")(**args))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
