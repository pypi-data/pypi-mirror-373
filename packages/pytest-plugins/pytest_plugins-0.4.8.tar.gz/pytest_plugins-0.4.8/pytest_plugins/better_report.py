import json
import logging
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator

import pytest
from _pytest.config import Config, Parser
from _pytest.fixtures import FixtureRequest
from _pytest.main import Session
from _pytest.python import Function

from pytest_plugins.models.environment_data import EnvironmentData
from pytest_plugins.utils.helper import save_as_json, serialize_data, save_as_markdown, get_project_root
from pytest_plugins.models import ExecutionData, ExecutionStatus, TestData
from pytest_plugins.utils.pytest_helper import (
    get_test_full_name,
    get_test_name_without_parameters,
    get_test_full_path,
    get_pytest_test_name, log_test_results
)
from pytest_plugins.utils.create_report import generate_md_report

execution_results = {}
test_results = {}

logger = logging.getLogger('pytest_plugins.better_report')


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--better-report",
        action="store_true",
        default=False,
        help="Enable the pytest-better-report plugin",
    )
    parser.addoption(
        "--output-dir",
        type=Path,
        action="store",
        default=None,
        help="Directory to save the results and reports",
    )
    parser.addoption(
        "--traceback",
        action="store_true",
        default=False,
        help="Enable detailed traceback in the report"
    )
    parser.addoption(
        "--md-report",
        action="store_true",
        default=False,
        help="Generate a markdown report of the test results"
    )
    parser.addoption(
        "--repo-name",
        action="store",
        default=None,
        help="Git Repository Name"
    )
    parser.addoption(
        "--pr-number",
        action="store",
        default=None,
        help="Pull Request Number"
    )
    parser.addoption(
        "--mr-number",
        action="store",
        default=None,
        help="Merge Request Number"
    )
    parser.addoption(
        "--pipeline-number",
        action="store",
        default=None,
        help="CI Pipeline Number"
    )
    parser.addoption(
        "--commit",
        action="store",
        default=None,
        help="Commit Hash (SHA-1) of the repository at the time of test execution"
    )
    parser.addoption(
        "--add-parameters",
        action="store_true",
        default=None,
        help='Add the test parameters as fields to the "test_results.json" file'
    )
    parser.addoption(
        "--pytest-command",
        action="store_true",
        default=None,
        help='Add the detailed information about the pytest command-line to the "execution_results.json" file'
    )


def pytest_configure(config: Config) -> None:
    if not config.getoption("--better-report"):
        return

    config._better_report_enabled = config.getoption("--better-report")

    output_dir = Path('results_output')
    if _output_dir := config.getoption("--output-dir"):
        config.option.output_dir = get_project_root() / _output_dir / output_dir if get_project_root() else output_dir
    else:
        config.option.output_dir = get_project_root() / Path('results_output') if get_project_root() else output_dir


def pytest_sessionstart(session: Session) -> None:
    if not getattr(session.config, '_better_report_enabled', None):
        logger.debug("Better report plugin is not enabled, skipping session start processing")
        return

    execution_results["environment_info"] = EnvironmentData(
        python_version=platform.python_version(),
        platform=platform.platform(),
    )

    execution_results["execution_info"] = ExecutionData(
        execution_status=ExecutionStatus.STARTED,
        revision=datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f"),
        execution_start_time=datetime.now(timezone.utc).isoformat(),
        repo_name=session.config.getoption("--repo-name", None),
        pull_request_number=session.config.getoption("--pr-number", None),
        merge_request_number=session.config.getoption("--mr-number", None),
        pipeline_number=session.config.getoption("--pipeline-number", None),
        commit=session.config.getoption("--commit", None),
    )

    if session.config.getoption("--pytest-command"):
        execution_results["pytest_command"] = {
            "real_cli": sys.argv,
            "ini_addopts": session.config.getini("addopts"),
            "raw_args": session.config.invocation_params.args,
        }

    logger.debug("Better report: Test session started")


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config: Config, items: list[Function]) -> None:
    if not getattr(config, '_better_report_enabled', None):
        return

    for item in items:
        test_name = get_test_name_without_parameters(item=item)
        test_full_name = get_test_full_name(item=item)
        test_results[test_full_name] = TestData(
            class_test_name=item.cls.__name__ if item.cls else None,
            test_name=test_name,
            pytest_test_name=get_pytest_test_name(item=item),
            test_full_name=test_full_name,
            test_full_path=get_test_full_path(item=item),
            test_file_name=item.fspath.basename,
            test_parameters=item.callspec.params if getattr(item, 'callspec', None) else None,
            test_markers=[marker.name for marker in item.iter_markers() if not marker.args],
            test_status=ExecutionStatus.COLLECTED,
            test_start_time=None,
            run_index=len(test_results) + 1
        )
        if getattr(item, 'callspec', None) and config.getoption('--add-parameters'):
            test_results[test_full_name].__dict__.update(**item.callspec.params)
    logger.debug(f'Tests to be executed: \n{json.dumps(list(test_results.keys()), indent=4, default=serialize_data)}')
    time.sleep(0.3)  # Sleep to ensure the debug log is printed before the tests start


@pytest.fixture(scope="session", autouse=True)
def session_setup_teardown(request: FixtureRequest) -> Generator[None, Any, None]:
    yield

    if not getattr(request.config, '_better_report_enabled', None):
        return

    exec_info = execution_results.get("execution_info")
    if not exec_info:
        logger.error("Execution info missing at session teardown")
        return

    # update execution end time
    exec_info.execution_end_time = datetime.now(timezone.utc).isoformat()

    # update execution duration time
    try:
        start_obj = datetime.fromisoformat(exec_info.execution_start_time)
        end_obj = datetime.fromisoformat(exec_info.execution_end_time)
        exec_info.execution_duration_sec = (end_obj - start_obj).total_seconds()
    except Exception as e:
        logger.error(f"Error computing execution duration: {e}")
        exec_info.execution_duration_sec = None

    # update execution status
    exec_info.execution_status = (
        ExecutionStatus.PASSED if all(
            t.test_status in [ExecutionStatus.PASSED, ExecutionStatus.SKIPPED] for t in test_results.values()
        ) else ExecutionStatus.FAILED
    )

    exec_info.test_list = list(test_results.keys())

    output_dir = request.config.option.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    save_as_json(path=output_dir / 'execution_results.json', data=execution_results, default=serialize_data)
    save_as_json(path=output_dir / 'test_results.json', data=test_results, default=serialize_data)
    logger.info("Better report: Execution results saved")


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item: Function, call: Any) -> Generator[None, Any, None]:
    if not getattr(item.config, '_better_report_enabled', None):
        logger.debug("Better report plugin is not enabled, skipping session start processing")
        yield
        return

    test_full_name = get_test_full_name(item=item)
    test_item = test_results.get(test_full_name)

    if call.when == "setup":
        test_full_name = get_test_full_name(item=item)
        test_results[test_full_name].test_start_time = datetime.now(timezone.utc).isoformat()

    if call.excinfo and call.excinfo.typename == ExecutionStatus.SKIPPED.value.title():
        test_item.test_status = ExecutionStatus.SKIPPED

    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not getattr(item.config, '_better_report_enabled', None):
        return

    if not test_item:
        logger.warning(f"Test {test_full_name} missing in test_results during makereport")
        return

    test_item.test_status = ExecutionStatus.PASSED if call.excinfo is None else ExecutionStatus.FAILED

    if call.excinfo:
        exception_message = str(call.excinfo.value).split('\nassert')[0]
        try:
            test_item.exception_message = json.loads(exception_message)
        except json.JSONDecodeError:
            test_item.exception_message = {
                'exception_type': call.excinfo.typename if call.excinfo else None,
                'message': exception_message if call.excinfo else None,
            }

        if item.config.getoption("--traceback"):
            test_item.exception_message.update(
                {
                    'traceback': {
                        'repr_crash': call.excinfo.getrepr().reprcrash if call.excinfo else None,
                        'traceback': [str(frame.path) for frame in call.excinfo.traceback] if call.excinfo else None,
                    }
                }
            )

    else:
        test_item.exception_message = None


def pytest_runtest_teardown(item: Function) -> None:
    if not getattr(item.config, '_better_report_enabled', None):
        return

    test_full_name = get_test_full_name(item=item)
    test_item = test_results[test_full_name]
    if not test_item:
        logger.warning(f"Test {test_full_name} missing in test_results during teardown")
        return

    test_item.test_end_time = datetime.now(timezone.utc).isoformat()
    if test_item.test_start_time:  # Add test duration only if start time is set
        try:
            start_obj = datetime.fromisoformat(test_item.test_start_time)
            end_obj = datetime.fromisoformat(test_item.test_end_time)
            test_item.test_duration_sec = (end_obj - start_obj).total_seconds()
        except Exception as e:
            logger.error(f"Error computing test duration for {test_full_name}: {e}")

    log_test_results(item=item, test_results=test_results)


def pytest_sessionfinish(session: Session) -> None:
    if session.config.getoption("--collect-only") or not getattr(session.config, '_better_report_enabled', None):
        return

    exit_status_code = session.session.exitstatus
    logger.info(f'Test session finished with exit status: {exit_status_code}')
    if exit_status_code != 0:
        failed_tests = [v for v in test_results.values() if v.test_status == ExecutionStatus.FAILED]
        logger.debug(f'Failed tests: {json.dumps(failed_tests, indent=4, default=serialize_data)}')

    if session.config.getoption("--md-report"):
        output_dir = session.config.option.output_dir
        res_md = generate_md_report(report=json.loads(json.dumps(test_results, default=serialize_data)))
        save_as_markdown(path=Path(output_dir / 'test_report.md'), data=res_md)
