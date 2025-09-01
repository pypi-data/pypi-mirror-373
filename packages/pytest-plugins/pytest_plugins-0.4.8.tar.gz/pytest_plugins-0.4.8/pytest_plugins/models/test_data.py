from dataclasses import dataclass
from typing import Optional

from pytest_plugins.models.status import ExecutionStatus


@dataclass
class TestData:
    test_file_name: str
    class_test_name: str
    test_name: str
    pytest_test_name: str
    test_full_name: str
    test_full_path: str
    test_status: ExecutionStatus = ExecutionStatus.COLLECTED
    test_parameters: Optional[dict[str, str]] = None
    test_markers: Optional[list] = None
    test_start_time: Optional[str] = None
    test_end_time: Optional[str] = None
    test_duration_sec: Optional[float] = None  # only for the tst itself, not including fixtures
    exception_message: Optional[str] = None
    run_index: Optional[int] = None
