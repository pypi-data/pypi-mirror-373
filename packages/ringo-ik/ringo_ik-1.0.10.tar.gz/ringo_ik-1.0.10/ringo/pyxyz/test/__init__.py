from .tests import PYXYZ_TESTS
from typing import Union


class FailedTestError(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def run_tests(print_result=True) -> Union[None, str]:
    """Run built-in installation tests

    Args:
        print_result (bool, optional): Whether to print results, otherwise, to return results as str. Defaults to True.

    Raises:
        FailedTestError: If some tests had failed

    Returns:
        Union[None, str]: Returns results as string if ``print_result=False``
    """
    if print_result:
        print("Running tests...")
    failed_tests = {}
    for test_name, test_call in PYXYZ_TESTS.items():
        success, message = test_call()
        if not success:
            failed_tests[test_name] = message

    if len(failed_tests) == 0:
        message_lines = ['All tests completed successfully:']
        for i, test_name in enumerate(PYXYZ_TESTS.keys(), start=1):
            message_lines.append(f"✔ {i}) {test_name}")
        message = '\n'.join(message_lines)
        if print_result:
            print(message)
            return None
        else:
            return message

    num_failed_tests = len(failed_tests)
    num_tests_total = len(PYXYZ_TESTS)
    error_lines = [
        f"{num_failed_tests} test(s) out of {num_tests_total} had failed:"
    ]
    for i, (test_name, message) in enumerate(failed_tests.items(), start=1):
        error_lines.append(f"{i}) {test_name}: {message}")
    raise FailedTestError('\n'.join(error_lines))
