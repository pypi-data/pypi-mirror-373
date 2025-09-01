import pytest
from yamale.yamale_error import YamaleError

from worker_configuration.validator import validate

from .conftest import assert_yamale_error


@pytest.mark.parametrize(
    "invalid_case",
    [
        "test",
        "",
        "123G",
        "64M",
        "64aM",
        "12.3m",
        "0",
        "0g",
        "42a",
        "-12m",
    ],
)
def test_invalid_shm_size(invalid_case):
    with pytest.raises(YamaleError) as e:
        validate(
            {
                "slug": "test",
                "display_name": "Test",
                "description": "Details about worker",
                "type": "Transcription",
                "docker": {"shm_size": invalid_case},
            }
        )

    assert_yamale_error(
        e,
        [
            f"docker.shm_size: '{invalid_case}' is not a Docker shared memory size (format is <number><unit>)."
        ],
    )


@pytest.mark.parametrize(
    "valid_case",
    [
        "123g",
        "64m",
        "123456789b",
        "1",
    ],
)
def test_valid_shm_size(valid_case):
    assert validate(
        {
            "slug": "test",
            "display_name": "Test",
            "description": "Details about worker",
            "type": "Transcription",
            "docker": {"shm_size": valid_case},
        }
    )
