import pytest
from _pytest.config import Config, Parser
from _pytest.python import Function

from pytest_plugins.utils.pytest_helper import get_test_full_name


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--verbose-param-ids",
        action="store_true",
        default=None,
        help="Include parameter names in pytest test IDs (e.g., test_name[param1=value1,param2=value2] instead of test_name[param1,value1,param2,value2])"
    )


def pytest_configure(config: Config) -> None:
    if not config.getoption("--verbose-param-ids"):
        return

    config._verbose_param_ids = config.getoption("--verbose-param-ids")


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(config: Config, items: list[Function]) -> None:
    if not getattr(config, '_verbose_param_ids', None):
        return

    for item in items:
        test_full_name = get_test_full_name(item=item)
        test_full_name = test_full_name.replace('{', '').replace('}', '')
        item._nodeid = f"{item.fspath.basename}::{test_full_name}"
