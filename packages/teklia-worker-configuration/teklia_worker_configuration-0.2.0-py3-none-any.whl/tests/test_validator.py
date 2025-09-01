from pathlib import Path

import pytest
from yamale.yamale_error import YamaleError

from worker_configuration.validator import validate

from .conftest import assert_yamale_error


def test_empty():
    with pytest.raises(YamaleError) as e:
        validate({})

    # All required fields are mentioned
    assert_yamale_error(
        e,
        [
            "slug: Required field missing",
            "display_name: Required field missing",
            "type: Required field missing",
            "description: Required field missing",
        ],
    )


def test_just_slug():
    with pytest.raises(YamaleError) as e:
        validate({"slug": "test"})

    # slug is not mentioned in the error list
    assert_yamale_error(
        e,
        [
            "display_name: Required field missing",
            "type: Required field missing",
            "description: Required field missing",
        ],
    )


def test_minimal_worker():
    # A minimal worker just needs slug, display_name and type set
    assert validate(
        {
            "slug": "test_Valid",
            "display_name": "A test worker",
            "type": "Transcription",
            "description": "Details about worker",
        }
    )


def test_invalid_slug():
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "Hello World !",
                "display_name": "A test worker",
                "description": "Details about worker",
                "type": "Transcription",
            }
        )

    assert_yamale_error(
        e,
        [
            "slug: 'Hello World !' is not a slug (only alphanumeric and underscores are allowed).",
        ],
    )


def test_empty_strings():
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": " ",
                "display_name": "",
                "type": "  ",
                "description": "        ",
            }
        )

    assert_yamale_error(
        e,
        [
            "slug: ' ' is not a slug (only alphanumeric and underscores are allowed).",
            "display_name: '' is not a non-empty string.",
            "type: '  ' is not a non-empty string.",
            "description: '        ' is not a non-empty string.",
        ],
    )


def test_invalid_type():
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "A test worker",
                "type": 12,
                "description": "Worker 12",
            }
        )

    # The type should be a string
    assert_yamale_error(
        e,
        ["type: '12' is not a non-empty string."],
    )


def test_extra_values():
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "A test worker",
                "description": "Details about worker",
                "type": "Transcription",
                "extra_value": "Something",
            }
        )

    # The type should be a string
    assert_yamale_error(
        e,
        ["extra_value: Unexpected element"],
    )


def test_invalid_gpu_usage():
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "A test worker",
                "description": "Details about worker",
                "type": "Transcription",
                "gpu_usage": "no",
            }
        )

    # The gpu_usage is an enum, unknown values are rejected
    assert_yamale_error(
        e,
        [
            "gpu_usage: 'no' not in ('supported', 'required', 'disabled')",
        ],
    )


def test_many_errors():
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": None,
                "type": "Transcription",
                "gpu_usage": "supported",
                "model_usage": "ChatGPT please",
                "description": Path("external.md"),
                "configuration": [1, 2, {"key": "test"}],
            }
        )

    # The validator display all errors at once, not one by one
    assert_yamale_error(
        e,
        [
            "display_name: 'None' is not a non-empty string.",
            "description: 'external.md' is not a non-empty string.",
            "model_usage: 'ChatGPT please' not in ('supported', 'required', 'disabled')",
            "configuration.0 : '1' is not a map",
            "configuration.1 : '2' is not a map",
            "configuration.2.display_name: Required field missing",
            "configuration.2.type: Required field missing",
        ],
    )


def test_not_editable_without_default():
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": "test",
                        "display_name": "Test option",
                        "type": "int",
                        "editable": False,
                    }
                ],
            }
        )

    # The validator display all errors at once, not one by one
    assert_yamale_error(
        e, ["configuration.test: Missing default value on editable option"]
    )


def test_enum_without_choices():
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": "test_enum",
                        "display_name": "Enum option",
                        "type": "enum",
                        # "choices" is missing
                    }
                ],
            }
        )

    assert_yamale_error(
        e, ["configuration.test_enum: Missing 'choices' for enum type option"]
    )


def test_duplicate_keys():
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": "a",
                        "display_name": "option A",
                        "type": "int",
                    },
                    {
                        "key": "b",
                        "display_name": "option B",
                        "type": "text",
                    },
                    {
                        "key": "a",
                        "display_name": "option A again",
                        "type": "float",
                    },
                ],
            }
        )

    assert_yamale_error(e, ["configuration.a: Duplicate key"])


def test_duplicate_keys_whitespaces():
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": "word",
                        "display_name": "option A",
                        "type": "int",
                    },
                    {
                        "key": " word ",
                        "display_name": "option A again",
                        "type": "float",
                    },
                ],
            }
        )

    assert_yamale_error(e, ["configuration. word : Duplicate key"])


def test_non_enpty_configuration():
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": " ",
                        "display_name": "option A",
                        "type": "int",
                    },
                    {
                        "key": "x",
                        "display_name": "",
                        "type": "text",
                    },
                    {
                        "key": " ",
                        "display_name": "   ",
                        "type": "float",
                    },
                ],
            }
        )

    assert_yamale_error(
        e,
        [
            "configuration.0.key: ' ' is not a non-empty string.",
            "configuration.1.display_name: '' is not a non-empty string.",
            "configuration.2.key: ' ' is not a non-empty string.",
            "configuration.2.display_name: '   ' is not a non-empty string.",
            "configuration. : Duplicate key",
        ],
    )


@pytest.mark.parametrize(
    "invalid_type",
    [
        "bool",
        "dict",
        "model",
        "secret",
        "text",
    ],
)
def test_invalid_type_on_many(invalid_type):
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": "some_list",
                        "display_name": "Some List",
                        "type": invalid_type,
                        "many": True,
                    },
                ],
            }
        )

    assert_yamale_error(
        e,
        [
            f"configuration.some_list: Type {invalid_type} is not supported when using 'many'. Only int|float|string|worker_version|element_type are supported."
        ],
    )


def test_invalid_enum_on_many():
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": "some_list",
                        "display_name": "Some List",
                        "type": "enum",
                        "many": True,
                        "choices": ["a", "b", "c"],
                    },
                ],
            }
        )

    assert_yamale_error(
        e,
        [
            "configuration.some_list: Type enum is not supported when using 'many'. Only int|float|string|worker_version|element_type are supported."
        ],
    )


def test_invalid_group_on_many():
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": "some_list",
                        "display_name": "Some List",
                        "type": "group",
                        "many": True,
                        "children": [
                            {
                                "key": "some_int",
                                "type": "int",
                                "display_name": "Integer",
                            }
                        ],
                    },
                ],
            }
        )

    assert_yamale_error(
        e,
        [
            "configuration.some_list: Type group is not supported when using 'many'. Only int|float|string|worker_version|element_type are supported."
        ],
    )


@pytest.mark.parametrize(
    "valid_type", ["int", "float", "string", "worker_version", "element_type"]
)
def test_valid_type_on_many(valid_type):
    assert validate(
        {
            "slug": "test",
            "display_name": "Test",
            "description": "Details about worker",
            "type": "Transcription",
            "configuration": [
                {
                    "key": "some_list",
                    "display_name": "Some List",
                    "type": valid_type,
                    "many": True,
                },
            ],
        }
    )


def test_help_text():
    assert validate(
        {
            "slug": "test",
            "display_name": "Test",
            "description": "Details about worker",
            "type": "Transcription",
            "configuration": [
                {
                    "key": "color",
                    "display_name": "A color",
                    "help_text": "Pick a nice color for your element",
                    "type": "enum",
                    "default": "red",
                    "choices": ["red", "green", "blue"],
                }
            ],
        }
    )


def test_unique_enum_choices():
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": "some_enum",
                        "display_name": "Some Enum",
                        "type": "enum",
                        "choices": ["a", "b", "c", "a"],
                    },
                ],
            }
        )

    assert_yamale_error(
        e,
        ["configuration.some_enum: Duplicate values in 'choices' is not allowed"],
    )
