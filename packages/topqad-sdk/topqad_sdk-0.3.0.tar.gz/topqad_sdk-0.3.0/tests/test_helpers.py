from typing import Callable, Any


def generate_test_name(testcase_func: Callable, param_num: int, param: Any) -> str:
    """Generate custom test names for parameterized tests.

    Args:
        testcase_func (Callable): The test case function.
        param_num (int): The parameter number.
        param (Any): The parameter object.

    Returns:
        str: A descriptive test name.
    """
    param_name = param.args[0] if hasattr(param, "args") and param.args else ""
    return f"{testcase_func.__name__}_{param_name}"
