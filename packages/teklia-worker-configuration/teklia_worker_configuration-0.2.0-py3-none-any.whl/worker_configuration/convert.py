import errno
import logging
from collections.abc import Generator
from pathlib import Path

import yaml

from worker_configuration.validator import validate

logger = logging.getLogger(__name__)


def get_worker_definitions(value, base_dir: Path) -> Generator[dict]:
    """
    From any value within a `workers` key, return the worker's definition
    """
    if isinstance(value, dict):
        yield value
    elif isinstance(value, str):
        # When a worker is a string, it is a glob pattern for any YAML file within the directory.
        for file in base_dir.rglob(value):
            logger.info(f"Using external YAML file at {file}")
            with file.open() as f:
                yield yaml.safe_load(f)
    else:
        raise ValueError(f"Type {type(value)} is not supported within `workers`")


def get_description(worker: dict, base_dir: Path) -> str:
    """
    Retrieve a worker's description from an external file
    """
    # Descriptions were optional
    if not isinstance(worker.get("description"), str):
        raise KeyError("Description was not set to a string")

    # Descriptions were always only parsed by `arkindex worker publish` as paths
    description_file = base_dir / worker["description"]
    if not description_file.is_file():
        raise FileNotFoundError(
            f"Description file at {description_file} does not exist"
        )

    # Empty descriptions will not be allowed in the new config
    if not (description := description_file.read_text().strip()):
        raise ValueError(f"Description file at {description_file} is empty")

    return description


def get_configuration_type(value) -> str | None:
    """
    Guess the `type` for a worker configuration field based on its default value.
    Returns None when there is no compatible type.
    """
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        # Use multiline string type when there are line breaks
        return "text" if "\n" in value else "string"
    # Dicts only support string keys and string values
    if isinstance(value, dict) and all(
        isinstance(k, str) and isinstance(v, str) for k, v in value.items()
    ):
        return "dict"


def convert_static_configuration(key: str, default) -> dict:
    many = isinstance(default, list)
    # Auto-detect the field type, and skip the field if we cannot use it
    # When this is a list, we will only accept lists that only have one type
    if many:
        types = set(get_configuration_type(item) for item in default)
        if len(types) > 1:
            raise ValueError("Only lists with values of the same type are supported.")

        # Use a fallback type when the list is empty
        type = types[0] if types else "string"
    else:
        type = get_configuration_type(default)

    if type is None:
        raise ValueError("No compatible type found.")

    return {
        "key": key,
        "display_name": key.replace("_", " ").capitalize(),
        "type": type,
        "editable": False,
        "default": default,
        "many": many,
    }


def convert_user_configuration(key: str, option: dict) -> dict:
    """
    Convert a user configuration option into a worker configuration field.
    """
    field = {
        "key": key,
        "display_name": option["title"],
        "type": option["type"],
    }

    for param in ("required", "default", "choices"):
        if param in option:
            field[param] = option[param]

    if option["type"] == "list":
        field["many"] = True
        field["type"] = option["subtype"]

    if field["type"] == "string" and option.get("multiline"):
        field["type"] = "text"

    return field


def convert_worker(worker: dict, base_dir: Path) -> bool:
    """
    Convert a single worker parsed from a `.arkindex.yml` into a new `arkindex/{slug}.yml` file.

    Returns True when warnings have occurred during the conversion, requiring manual review.
    """
    has_warnings = False

    for key in ("slug", "type", "name"):
        if not isinstance(worker.get(key), str):
            raise KeyError(f"Key {key!r} is required and must be a string")

    # Basic worker attributes
    new_worker = {
        "slug": worker["slug"],
        "display_name": worker["name"],
        "type": worker["type"],
    }
    if "gpu_usage" in worker:
        new_worker["gpu_usage"] = worker["gpu_usage"]
    if "model_usage" in worker:
        new_worker["model_usage"] = worker["model_usage"]

    try:
        new_worker["description"] = get_description(worker, base_dir)
    except Exception as e:
        logger.warning(
            f"Could not get description for worker {worker['slug']}: {e}. A placeholder will be used instead."
        )
        has_warnings = True
        new_worker["description"] = new_worker["display_name"]

    # Docker section
    if worker.get("docker"):
        new_worker["docker"] = {}
        if "command" in worker["docker"]:
            new_worker["docker"]["command"] = worker["docker"]["command"]
        if "shm_size" in worker["docker"]:
            new_worker["docker"]["shm_size"] = worker["docker"]["shm_size"]

    if worker.get("configuration") or worker.get("user_configuration"):
        new_worker["configuration"] = []

    # Turn `configuration` into non-editable configuration fields
    for key, default in worker.get("configuration", {}).items():
        try:
            new_worker["configuration"].append(
                convert_static_configuration(key, default)
            )
        except Exception as e:
            logger.warning(f"Could not convert static configuration {key!r}: {e}")
            has_warnings = True

    # Turn `user_configuration` into editable configuration fields
    for key, option in worker.get("user_configuration", {}).items():
        try:
            new_worker["configuration"].append(convert_user_configuration(key, option))
        except Exception as e:
            logger.warning(f"Could not convert user configuration {key!r}: {e}")
            has_warnings = True

    if worker.get("secrets"):
        logger.warning(
            f"Some secrets have been defined for worker {worker['slug']}, but they cannot be converted. Use `secret` fields instead."
        )
        has_warnings = True

    # Ensure the generated config conforms to the new spec
    validate(new_worker, name=f"arkindex/{worker['slug']}.yml")

    worker_path = base_dir / "arkindex" / f"{worker['slug']}.yml"
    if worker_path.exists():
        raise FileExistsError(
            f"{worker_path} already exists. The new configuration cannot be saved."
        )

    worker_path.parent.mkdir(exist_ok=True)
    with worker_path.open("w") as f:
        yaml.safe_dump(
            new_worker,
            f,
            # Preserve our key order as it is more human-readable
            sort_keys=False,
        )

    return has_warnings


def convert(path: Path) -> int:
    """
    Convert a .arkindex.yml configuration to the new configuration format.
    The new files will be stored in `arkindex/*.yml`, in the same parent directory as the original file.

    <https://doc.teklia.com/base-worker/contents/implem/configure/yaml/>
    """
    if not path.is_file():
        logger.critical(f"{path} is not a valid file.")
        return errno.ENOENT

    with path.open() as f:
        workers = yaml.safe_load(f).get("workers")

    if not workers:
        logger.critical(f"No workers found in {path}.")
        return errno.EINVAL

    warnings, failures = 0, 0
    base_dir = path.parent
    for worker in workers:
        for worker_definition in get_worker_definitions(worker, base_dir):
            try:
                warnings += convert_worker(worker_definition, base_dir)
            except Exception as e:
                logger.error(f"Could not convert worker: {e}")
                failures += 1

    logger.info(f"Conversion finished: {warnings} with warnings, {failures} failed")

    if not warnings and not failures:
        logger.info(f"Deleting {path}")
        path.unlink()

    return failures > 0
