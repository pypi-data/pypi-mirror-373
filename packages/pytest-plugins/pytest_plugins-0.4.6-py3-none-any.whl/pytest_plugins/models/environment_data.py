from dataclasses import dataclass
from typing import Optional


@dataclass
class EnvironmentData:
    python_version: Optional[str]
    platform: Optional[str]
