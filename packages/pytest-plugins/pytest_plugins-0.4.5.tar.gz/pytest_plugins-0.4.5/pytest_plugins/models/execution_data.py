from dataclasses import dataclass
from typing import Optional

from pytest_plugins.models.status import ExecutionStatus


@dataclass
class ExecutionData:
    execution_status: ExecutionStatus
    revision: Optional[str]
    execution_start_time: Optional[str] = None
    execution_end_time: Optional[str] = None
    execution_duration_sec: Optional[str] = None

    repo_name: Optional[str] = None
    pull_request_number: Optional[str] = None
    merge_request_number: Optional[str] = None
    pipeline_number: Optional[str] = None
    commit: Optional[str] = None

    test_list: Optional[list] = None
