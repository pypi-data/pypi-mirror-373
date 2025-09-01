from worker_configuration.schema import SCHEMA_PATH


def assert_yamale_error(error, expected_failures: list):
    """
    Method to check content of a Yamale validation error
    """
    assert len(expected_failures) > 0, "You need to set some failures in your test case"

    # The exception message prefixes every failure by a tab
    # We add it here instead of having to manage that in test cases
    expected_failures_str = "\n".join([f"\t{fail}" for fail in expected_failures])

    # The exception message has a first line detailing what is validated against which schema
    error_str = f"Error validating data 'in-memory' with schema '{SCHEMA_PATH}'\n{expected_failures_str}"

    assert str(error.value) == error_str
