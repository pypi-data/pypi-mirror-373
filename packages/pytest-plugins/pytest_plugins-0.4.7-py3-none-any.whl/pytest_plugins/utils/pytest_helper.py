import json
import logging

from _pytest.python import Function

from pytest_plugins.utils.helper import serialize_data

logger = logging.getLogger()


def get_test_path_without_parameters(item: Function) -> str:
    """Get the test name without parameters."""
    return item.nodeid.split('[')[0]


def get_test_name_without_parameters(item: Function) -> str:
    """Get the test name without parameters."""
    return item.nodeid.split('.py::')[-1].split('[')[0]


def get_pytest_test_name(item: Function) -> str:
    """Get the test name without parameters."""
    return item.nodeid.split('.py::')[-1]


def get_test_full_name(item: Function) -> str:
    """Get the full name of the test, including parameters if available."""
    test_name = get_test_name_without_parameters(item=item)
    return f"{test_name}[{item.callspec.params}]" if getattr(item, 'callspec', None) else test_name


def get_test_full_path(item: Function) -> str:
    """Get the full name of the test, including parameters if available."""
    test_name = get_test_path_without_parameters(item=item)
    return f"{test_name}[{item.callspec.params}]" if getattr(item, 'callspec', None) else test_name


def log_test_results(item: Function, test_results: dict) -> None:
    if not getattr(item.config, '_better_report_enabled', None):
        return

    test_full_name = get_test_full_name(item=item)
    if test_full_name in test_results:
        logger.debug(f'Test Results: \n{json.dumps(test_results[test_full_name], indent=4, default=serialize_data)}')
    else:
        logger.warning(f"Test {test_full_name} missing in test_results during report")
