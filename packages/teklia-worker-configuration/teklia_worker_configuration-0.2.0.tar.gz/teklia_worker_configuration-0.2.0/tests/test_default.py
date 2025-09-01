import pytest
from yamale.yamale_error import YamaleError

from worker_configuration.validator import validate

from .conftest import assert_yamale_error


@pytest.mark.parametrize(
    "invalid_type",
    [
        "element_type",
        "model",
        "worker_version",
        "secret",
    ],
)
def test_default_invalid_type(invalid_type):
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": "some_default",
                        "display_name": "A test with default",
                        "type": invalid_type,
                        "default": "whatever",
                    }
                ],
            }
        )

    assert_yamale_error(
        e,
        [
            f"configuration.some_default: Type {invalid_type} cannot have a default value. Only bool|dict|enum|float|int|string|text can."
        ],
    )


def test_default_group():
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": "some_default",
                        "display_name": "A test with default",
                        "type": "group",
                        "default": "whatever",
                        "children": [
                            {
                                "key": "some_int",
                                "type": "int",
                                "display_name": "Integer",
                            }
                        ],
                    }
                ],
            }
        )

    assert_yamale_error(
        e,
        [
            "configuration.some_default: Type group cannot have a default value. Only bool|dict|enum|float|int|string|text can."
        ],
    )


def test_default_boolean():
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": "some_default",
                        "display_name": "A test with default",
                        "type": "bool",
                        "default": "some text",
                    }
                ],
            }
        )

    assert_yamale_error(
        e,
        [
            "configuration.some_default: Default value must be a boolean",
        ],
    )

    assert validate(
        {
            "slug": "test",
            "display_name": "Test",
            "description": "Details about worker",
            "type": "Transcription",
            "configuration": [
                {
                    "key": "some_default",
                    "display_name": "A test with default",
                    "type": "bool",
                    "default": True,
                }
            ],
        }
    )

    assert validate(
        {
            "slug": "test",
            "display_name": "Test",
            "description": "Details about worker",
            "type": "Transcription",
            "configuration": [
                {
                    "key": "some_default",
                    "display_name": "A test with default",
                    "type": "bool",
                    "default": False,
                }
            ],
        }
    )


def test_default_dict():
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": "some_default",
                        "display_name": "A test with default",
                        "type": "dict",
                        "default": "some text",
                    }
                ],
            }
        )

    assert_yamale_error(
        e,
        [
            "configuration.some_default: Default value must be a mapping",
        ],
    )

    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": "some_default",
                        "display_name": "A test with default",
                        "type": "dict",
                        "default": {"1": "a", "2": 12},
                    }
                ],
            }
        )

    assert_yamale_error(
        e,
        [
            "configuration.some_default: Values of the default mapping must all be strings",
        ],
    )

    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": "some_default",
                        "display_name": "A test with default",
                        "type": "dict",
                        "default": {1: 1, 2: "AAA"},
                    }
                ],
            }
        )

    assert_yamale_error(
        e,
        [
            "configuration.some_default: Keys of the default mapping must all be strings",
        ],
    )

    assert validate(
        {
            "slug": "test",
            "display_name": "Test",
            "description": "Details about worker",
            "type": "Transcription",
            "configuration": [
                {
                    "key": "some_default",
                    "display_name": "A test with default",
                    "type": "dict",
                    "default": {"key A": "a", "Key B": "b"},
                }
            ],
        }
    )


def test_default_enum():
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": "some_default",
                        "display_name": "A test with default",
                        "type": "enum",
                        "choices": ["a", "b", "c"],
                        "default": 123,
                    }
                ],
            }
        )

    assert_yamale_error(
        e,
        [
            "configuration.some_default: Default value must be a string",
        ],
    )

    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": "some_default",
                        "display_name": "A test with default",
                        "type": "enum",
                        "choices": ["a", "b", "c"],
                        "default": "x",
                    }
                ],
            }
        )

    assert_yamale_error(
        e,
        [
            "configuration.some_default: Default value must be one of the choices: a|b|c",
        ],
    )

    assert validate(
        {
            "slug": "test",
            "display_name": "Test",
            "description": "Details about worker",
            "type": "Transcription",
            "configuration": [
                {
                    "key": "some_default",
                    "display_name": "A test with default",
                    "type": "enum",
                    "choices": ["a", "b", "c"],
                    "default": "c",
                }
            ],
        }
    )


def test_default_float():
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": "some_default",
                        "display_name": "A test with default",
                        "type": "float",
                        "default": "Whatever string",
                    }
                ],
            }
        )

    assert_yamale_error(
        e,
        [
            "configuration.some_default: Default value must be a float",
        ],
    )

    assert validate(
        {
            "slug": "test",
            "display_name": "Test",
            "description": "Details about worker",
            "type": "Transcription",
            "configuration": [
                {
                    "key": "some_default",
                    "display_name": "A test with default",
                    "type": "float",
                    "default": 12.3,
                }
            ],
        }
    )


def test_default_int():
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": "some_default",
                        "display_name": "A test with default",
                        "type": "int",
                        "default": 45.6,
                    }
                ],
            }
        )

    assert_yamale_error(
        e,
        [
            "configuration.some_default: Default value must be an integer",
        ],
    )

    assert validate(
        {
            "slug": "test",
            "display_name": "Test",
            "description": "Details about worker",
            "type": "Transcription",
            "configuration": [
                {
                    "key": "some_default",
                    "display_name": "A test with default",
                    "type": "int",
                    "default": 123,
                }
            ],
        }
    )


def test_default_string():
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": "some_default",
                        "display_name": "A test with default",
                        "type": "string",
                        "default": 45.6,
                    }
                ],
            }
        )

    assert_yamale_error(
        e,
        [
            "configuration.some_default: Default value must be a string",
        ],
    )

    assert validate(
        {
            "slug": "test",
            "display_name": "Test",
            "description": "Details about worker",
            "type": "Transcription",
            "configuration": [
                {
                    "key": "some_default",
                    "display_name": "A test with default",
                    "type": "string",
                    "default": "This is short string",
                }
            ],
        }
    )


def test_default_text():
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": "some_default",
                        "display_name": "A test with default",
                        "type": "text",
                        "default": 45.6,
                    }
                ],
            }
        )

    assert_yamale_error(
        e,
        [
            "configuration.some_default: Default value must be a string",
        ],
    )

    assert validate(
        {
            "slug": "test",
            "display_name": "Test",
            "description": "Details about worker",
            "type": "Transcription",
            "configuration": [
                {
                    "key": "some_default",
                    "display_name": "A test with default",
                    "type": "text",
                    "default": "This is short string",
                }
            ],
        }
    )


def test_default_with_many():
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": "some_default",
                        "display_name": "A test with default",
                        "type": "string",
                        "many": True,
                        "default": 45.6,
                    }
                ],
            }
        )

    assert_yamale_error(
        e,
        [
            "configuration.some_default: Default value must be a list",
        ],
    )

    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": "some_default",
                        "display_name": "A test with default",
                        "type": "string",
                        "many": True,
                        "default": [1, 2, "A"],
                    }
                ],
            }
        )

    assert_yamale_error(
        e,
        [
            "configuration.some_default: All default values must be a string",
        ],
    )

    assert validate(
        {
            "slug": "test",
            "display_name": "Test",
            "description": "Details about worker",
            "type": "Transcription",
            "configuration": [
                {
                    "key": "some_default",
                    "display_name": "A test with default",
                    "type": "int",
                    "many": True,
                    "default": [1, 2, 789],
                }
            ],
        }
    )


def test_default_float_nan():
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": "some_default",
                        "display_name": "A test with default",
                        "type": "float",
                        "default": float("nan"),
                    }
                ],
            }
        )

    assert_yamale_error(
        e,
        [
            "configuration.some_default: Default value cannot be NaN",
        ],
    )


@pytest.mark.parametrize(
    "invalid_default", [float("inf"), float("+inf"), float("-inf")]
)
def test_default_float_infinite(invalid_default):
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": "some_default",
                        "display_name": "A test with default",
                        "type": "float",
                        "default": invalid_default,
                    }
                ],
            }
        )

    assert_yamale_error(
        e,
        [
            "configuration.some_default: Default value cannot be Infinite",
        ],
    )
