import math


def rule_not_editable_with_default(data: dict):
    """
    Editable fields must have a default
    Except groups, which must be editable
    """
    if data.get("editable", True) is True:
        return

    if data.get("type") == "group":
        raise ValueError("A group must be editable")

    if data.get("default") is None:
        raise ValueError("Missing default value on editable option")


def rule_enum_requires_choices(data: dict):
    """
    Enum type fields must have choices set
    """
    if data.get("type") != "enum":
        return

    choices = data.get("choices")
    if not choices:
        raise ValueError("Missing 'choices' for enum type option")

    if len(set(choices)) != len(choices):
        raise ValueError("Duplicate values in 'choices' is not allowed")


def rule_group_requires_children(data: dict):
    """
    Group type fields must have at least one child
    """
    if data.get("type") != "group":
        return

    children = data.get("children")
    if children is None:
        raise ValueError("Missing 'children' for group type option")
    if len(children) < 1:
        raise ValueError("Set at least one 'children' for group type option")


def rule_group_not_required(data: dict):
    """
    Group type fields cannot be required
    """
    if data.get("type") == "group" and data.get("required", False) is True:
        raise ValueError("A group cannot be required")


def rule_no_subgroups(data: dict):
    """
    Group type fields cannot have a sub group
    """
    if data.get("type") != "group":
        return

    subgroups = [child.get("type") == "group" for child in data.get("children", [])]
    if any(subgroups):
        raise ValueError("A group cannot have a child group")


def rule_limit_types_on_many(data: dict):
    """
    Limit supported types when many is set (list mode)
    """
    _supported_types = ("int", "float", "string", "worker_version", "element_type")
    _type = data.get("type")
    if data.get("many") is True and _type not in _supported_types:
        raise ValueError(
            f"Type {_type} is not supported when using 'many'. Only {'|'.join(_supported_types)} are supported."
        )


def _check_default_value(data: dict, value=None, use_plurals=False):
    """
    Helper to check the type of the default values matches the expected type
    """
    _type = data.get("type")
    _supported_types = ("bool", "dict", "enum", "float", "int", "string", "text")
    error_prefix = "All default values" if use_plurals else "Default value"

    if _type == "bool":
        if not isinstance(value, bool):
            raise ValueError(f"{error_prefix} must be a boolean")

    elif _type == "dict":
        if not isinstance(value, dict):
            raise ValueError(f"{error_prefix} must be a mapping")

        # Check all items are strings
        if not all(map(lambda x: isinstance(x, str), value.keys())):
            raise ValueError("Keys of the default mapping must all be strings")
        if not all(map(lambda x: isinstance(x, str), value.values())):
            raise ValueError("Values of the default mapping must all be strings")

    elif _type == "enum":
        if not isinstance(value, str):
            raise ValueError(f"{error_prefix} must be a string")

        # Check the default is amongst choices
        choices = data.get("choices")
        if value not in choices:
            raise ValueError(
                f"{error_prefix} must be one of the choices: {'|'.join(choices)}"
            )

    elif _type == "float":
        if not isinstance(value, int | float):
            raise ValueError(f"{error_prefix} must be a float")

        # Infinity and NaN are not allowed
        if math.isnan(value):
            raise ValueError(f"{error_prefix} cannot be NaN")
        if math.isinf(value):
            raise ValueError(f"{error_prefix} cannot be Infinite")

    elif _type == "int":
        if not isinstance(value, int):
            raise ValueError(f"{error_prefix} must be an integer")

    elif _type in ("string", "text"):
        if not isinstance(value, str):
            raise ValueError(f"{error_prefix} must be a string")

    else:
        # Unsupported type
        raise ValueError(
            f"Type {_type} cannot have a default value. Only {'|'.join(_supported_types)} can."
        )


def rule_default_type_match(data: dict):
    """
    Check the default value type matches the type
    Also check that there is no default set on unsupported types
    When "many" is set, this checks all the values in the default list
    """
    default = data.get("default")
    if default is None:
        return

    if data.get("many") is True:
        # Check default values from list
        if not isinstance(default, list):
            raise ValueError("Default value must be a list")

        for value in default:
            _check_default_value(data, value, use_plurals=True)

    else:
        # Check unique default values
        _check_default_value(data, default)
