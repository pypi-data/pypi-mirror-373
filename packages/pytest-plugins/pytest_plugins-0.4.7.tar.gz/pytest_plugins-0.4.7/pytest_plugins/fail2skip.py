import logging
from typing import Any, Generator

import pytest
from _pytest.config import Config, Parser
from _pytest.python import Function

from pytest_plugins.better_report import test_results
from pytest_plugins.models import ExecutionStatus
from pytest_plugins.utils.pytest_helper import get_test_full_name

logger = logging.getLogger("pytest_plugins.fail2skip")


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--fail2skip",
        action="store_true",
        default=False,
        help="Enable converting failed tests marked with @pytest.mark.fail2skip into skipped.",
    )


def pytest_configure(config: Config) -> None:
    if not config.getoption("--fail2skip"):
        return

    config._fail2skip_enabled = config.getoption("--fail2skip")
    config.addinivalue_line(
        name="markers",
        line="fail2skip: convert failed test to skip instead of fail"
    )


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item: Function, call: Any) -> Generator[None, Any, None]:
    outcome = yield
    report = outcome.get_result()

    if (
        getattr(item.config, '_fail2skip_enabled', None)
        and item.get_closest_marker("fail2skip")
        and call.when == "call"
        and report.outcome == "failed"
    ):
        report.outcome = "skipped"
        report.longrepr = "fail2skip: forcibly skipped after failure"
        report.wasxfail = "fail2skip"

        if get_test_full_name(item=item) in test_results:
            test_results[get_test_full_name(item=item)].test_status = ExecutionStatus.FAILED_SKIPPED
            test_results[get_test_full_name(item=item)].exception_message.update(
                {
                    'fail2skip_reason': [
                        marker.kwargs.get('reason', None) for marker in item.iter_markers(name='fail2skip')
                    ][0]
                }
            )
