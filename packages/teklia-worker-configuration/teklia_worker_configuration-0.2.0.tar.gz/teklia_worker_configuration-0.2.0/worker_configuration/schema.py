from inspect import getmembers, isfunction
from pathlib import Path

import yamale
from yamale.schema.schema import Schema
from yamale.validators import DefaultValidators, Regex

from worker_configuration import rules

# Build base schema from included YAML file
SCHEMA_PATH = Path(__file__).parent / "schema.yml"


# List all method from rules module prefixed by rule_
CONFIGURATION_RULES = [
    method
    for (name, method) in getmembers(rules, isfunction)
    if name.startswith("rule_")
]


SCHEMA_SOURCE = {
    "key": r"non_empty_string()",
    "display_name": r"non_empty_string()",
    "help_text": "str(required=False)",
    "type": "enum('bool', 'dict', 'element_type', 'enum', 'float', 'group', 'int', 'model', 'secret', 'string', 'text', 'worker_version')",
    "default": "any(required=False)",
    "many": "bool(required=False)",
    "editable": "bool(required=False)",
    "required": "bool(required=False)",
    "choices": "list(str(), min=2, required=False)",
    "children": "list(include('configuration_field'), required=False)",
}


class DuplicateKey(Exception):
    """
    Error raised when a duplicate key is found
    """

    def __init__(self, key):
        self.key = key


class NonEmptyString(Regex):
    """
    Helper to validate strings that are not empty (prevent whitespaces-only)
    """

    tag = "non_empty_string"

    def __init__(self, **kwargs):
        super().__init__(
            r"^(?!\s*$).+",
            name="non-empty string",
            **kwargs,
        )


class MemorySize(Regex):
    """
    Docker shared memory size validator
    The format is <number><unit>. number must be greater than 0.
    Unit is optional and can be b (bytes), k (kilobytes), m (megabytes), or g (gigabytes).
    """

    tag = "memory_size"

    def __init__(self, **kwargs):
        # Setup regex to validate <number><unit> format
        super().__init__(
            "^([0-9]+)([bkmg]?)$",
            name="Docker shared memory size (format is <number><unit>)",
            **kwargs,
        )

    def _is_valid(self, value):
        # Apply regex validation
        if not super()._is_valid(value):
            return False

        # Remove unit suffix
        value = value[:-1] if value[-1] in ("b", "k", "m", "g") else value

        # Check value is positive
        return int(value) > 0


class ConfigurationSchema(Schema):
    """
    Custom schema to validate the structure and rules of configuration options
    """

    def __init__(self, **kwargs):
        super().__init__(
            name="configuration_field", schema_dict=SCHEMA_SOURCE.copy(), **kwargs
        )

        # The schema includes itself to support group children
        self.includes["configuration_field"] = self

        # List all known keys to avoid duplicates
        self._keys = set()

    def _validate(self, validator, data, path, *args, **kwargs):
        errors = super()._validate(validator, data, path, *args, **kwargs)

        # Only process configuration options
        if (
            not isinstance(validator, dict)
            or not isinstance(data, dict)
            or "key" not in data
        ):
            return errors

        # Structure validation ensure we have a key at this stage
        key = data["key"]

        # Check duplicate keys from top level configuration
        # ignoring the one from children
        if "children" not in path._path:
            try:
                self.check_key(key)
            except DuplicateKey:
                errors.append(f"configuration.{key}: Duplicate key")

        # Check duplicate keys from children in groups, using the parent key
        for child in data.get("children", []):
            try:
                self.check_key(child.get("key"), parent=key)
            except DuplicateKey:
                errors.append(f"configuration.{key}: Duplicate key")

        # Apply every rule for configuration options and report each error
        for rule in CONFIGURATION_RULES:
            try:
                rule(data)
            except ValueError as e:
                errors.append(f"configuration.{key}: {e}")

        return errors

    def check_key(self, key, parent=None):
        """
        Check that a configuration key is unique across all options and groups
        """
        if parent is not None:
            key = f"{parent}.{key}"

        # Remove leading & trailing white spaces to check duplicates on non whitespaces
        key = key.strip()

        if key in self._keys:
            raise DuplicateKey(key)
        else:
            self._keys.add(key)


def build_schema():
    # Add custom validators for top-level parameters
    validators = DefaultValidators.copy()  # This is a dictionary
    validators[MemorySize.tag] = MemorySize
    validators[NonEmptyString.tag] = NonEmptyString

    # Start from the YAML schema describing overall structure
    schema = yamale.make_schema(SCHEMA_PATH, validators=validators)

    # Directly add the custom field into the schema to validate configuration options
    schema.includes["configuration_field"] = ConfigurationSchema(validators=validators)

    return schema
