import json
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class ExecutionResult:
    output: str
    error: Optional[str] = None
    traceback: Optional[str] = None
    returned_objects: Dict[str, Any] = None
