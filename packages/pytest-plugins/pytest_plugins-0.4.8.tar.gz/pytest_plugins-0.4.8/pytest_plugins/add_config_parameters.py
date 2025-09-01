import logging
from pathlib import Path

import pytest
from _pytest.config import Parser, Config
from _pytest.python import Function

from pytest_plugins.utils.helper import open_json

logger = logging.getLogger('pytest_plugins.add_parameters')


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--config-path",
        action="store_true",
        default=None,
        help="Load configuration from a JSON file. If a file path is provided, it will be opened and parsed as JSON.",
    )


def pytest_configure(config: Config) -> None:
    if not config.getoption("--config-path"):
        return

    config.config_path = config.getoption("--config-path")


@pytest.fixture(scope="class", autouse=True)
def add_param_to_class(request: Function) -> None:
    if getattr(request.config, '_config', None) and getattr(request, 'cls', None):
        request.cls.config = open_json(Path(request.config.config_path))
