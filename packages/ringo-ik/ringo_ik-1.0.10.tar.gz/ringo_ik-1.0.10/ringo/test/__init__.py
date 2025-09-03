from .tests import RINGO_TESTS, base
from typing import Union


class FailedTestError(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def run_tests(print_result=True) -> Union[None, str]:
    resA = run_ringo_tests(print_result=print_result)
    resB = run_pyxyz_tests(print_result=print_result)
    if not print_result:
        return resA + '\n' + resB


def run_pyxyz_tests(print_result=True) -> Union[None, str]:
    if base.use_pyxyz:
        import ringo.pyxyz.test
        return ringo.pyxyz.test.run_tests(print_result=print_result)
    else:
        print("Skipping PyXYZ tests because it won't be used")


def run_ringo_tests(print_result=True) -> Union[None, str]:
    print("Running tests...")
    failed_tests = {}
    successfull_tests = {}
    for test_name, test_call in RINGO_TESTS.items():
        success, message = test_call()
        if not success:
            failed_tests[test_name] = message
        else:
            successfull_tests[test_name] = message

    if len(failed_tests) == 0:
        message_lines = ['All tests completed successfully:']
        for i, test_name in enumerate(RINGO_TESTS.keys(), start=1):
            if successfull_tests[test_name] == '':
                sign = '✔'
                text = 'OK'
            elif successfull_tests[test_name] == 'Skipped':
                sign = '✖'
                text = 'Skipped'
            else:
                raise Exception(
                    f"Unknown message: {successfull_tests[test_name]}")
            message_lines.append(f"{sign} {i}) {test_name} ({text})")
        message = '\n'.join(message_lines)
        if print_result:
            print(message)
            return None
        else:
            return message

    num_failed_tests = len(failed_tests)
    num_tests_total = len(RINGO_TESTS)
    error_lines = [
        f"{num_failed_tests} test(s) out of {num_tests_total} had failed:"
    ]
    for i, (test_name, message) in enumerate(failed_tests.items(), start=1):
        error_lines.append(f"{i}) {test_name}: {message}")
    raise FailedTestError('\n'.join(error_lines))
