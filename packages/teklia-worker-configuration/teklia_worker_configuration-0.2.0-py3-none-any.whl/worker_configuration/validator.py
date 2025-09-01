import sys
from pathlib import Path

import yamale
from yaml.error import YAMLError

from worker_configuration.schema import build_schema


def validate(payload: dict, name="in-memory"):
    """
    Validate the structure and content of an Arkindex worker as Python dict
    """
    # Yamale needs a list of tuples to build explicit errors
    schema = build_schema()
    yamale.validate(schema, [(payload, name)])

    return True


def validate_file(path: Path) -> None:
    """
    Validate the structure and content of an Arkindex worker as YAML file
    """
    assert path.exists(), f"Missing file {path}"

    # We only support one file at a time
    # whereas yamale can process multiple payloads
    data = yamale.make_data(path)
    assert len(data) == 1, "Only one YAML payload at a time"

    # Validate file structure and content at once
    yamale.validate(build_schema(), data)

    return data[0][0]


def validate_files(paths: list[Path]) -> int:
    """
    Validate the structure and content of one or more Arkindex workers as YAML files.

    Prints any validation errors to stderr.
    Returns 1 when any error occurred in any file and 0 otherwise.
    """
    assert paths, "At least one path is required"

    failed = False
    for path in paths:
        try:
            validate_file(path)
        except (AssertionError, YAMLError) as e:
            failed = True
            print(f"{path}: {e}", file=sys.stderr)
        except yamale.YamaleError as e:
            failed = True
            for error in e.results[0].errors:
                print(f"{path}: {error}", file=sys.stderr)

    return failed
