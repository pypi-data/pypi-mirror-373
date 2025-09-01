import pytest
from yamale.yamale_error import YamaleError

from worker_configuration.validator import validate

from .conftest import assert_yamale_error


def test_group_without_children():
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": "group_opt",
                        "display_name": "Some Group",
                        "type": "group",
                    },
                ],
            }
        )

    assert_yamale_error(
        e, ["configuration.group_opt: Missing 'children' for group type option"]
    )


def test_group_empty_children():
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": "group_opt",
                        "display_name": "Some Group",
                        "type": "group",
                        "children": [],
                    },
                ],
            }
        )

    assert_yamale_error(
        e,
        ["configuration.group_opt: Set at least one 'children' for group type option"],
    )


def test_group_invalid_child():
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": "group_opt",
                        "display_name": "Some Group",
                        "type": "group",
                        "children": [
                            {"some": "test"},
                        ],
                    },
                ],
            }
        )

    assert_yamale_error(
        e,
        [
            "configuration.0.children.0.some: Unexpected element",
            "configuration.0.children.0.key: Required field missing",
            "configuration.0.children.0.display_name: Required field missing",
            "configuration.0.children.0.type: Required field missing",
        ],
    )


def test_group_in_group():
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": "top_group",
                        "display_name": "Top level group",
                        "type": "group",
                        "children": [
                            {
                                "key": "sub_group",
                                "display_name": "Sub level group",
                                "type": "group",
                                "children": [
                                    {
                                        "key": "int_opt",
                                        "display_name": "Some integer",
                                        "type": "int",
                                        "default": 12,
                                    }
                                ],
                            }
                        ],
                    },
                ],
            }
        )

    assert_yamale_error(
        e,
        [
            "configuration.top_group: A group cannot have a child group",
        ],
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
                        "key": "group",
                        "display_name": "Some option group",
                        "type": "group",
                        "children": [
                            {
                                "key": "opt_a",
                                "display_name": "Option A",
                                "type": "int",
                            }
                        ],
                    },
                    {
                        "key": "group.opt_a",
                        "display_name": "Some conflicting option",
                        "type": "string",
                    },
                ],
            }
        )

    assert_yamale_error(
        e,
        [
            "configuration.group.opt_a: Duplicate key",
        ],
    )


def test_group_non_editable():
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": "group_opt",
                        "display_name": "Some Group",
                        "type": "group",
                        "editable": False,
                        "children": [
                            {
                                "key": "opt_a",
                                "display_name": "Option A",
                                "type": "int",
                            }
                        ],
                    },
                ],
            }
        )

    assert_yamale_error(e, ["configuration.group_opt: A group must be editable"])


def test_group_non_required():
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "configuration": [
                    {
                        "key": "group_opt",
                        "display_name": "Some Group",
                        "type": "group",
                        "required": True,
                        "children": [
                            {
                                "key": "opt_a",
                                "display_name": "Option A",
                                "type": "int",
                            }
                        ],
                    },
                ],
            }
        )

    assert_yamale_error(e, ["configuration.group_opt: A group cannot be required"])
