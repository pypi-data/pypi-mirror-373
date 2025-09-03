from typing import Any, Dict
from dataclasses import dataclass

@dataclass
class AgentState:
    data: dict
    def __init__(self, initial_data: Dict[str, Any]):
        self.data = initial_data
        self.execution_history = []

    def update(self, new_data: Dict[str, Any]):
        self.data.update(new_data)

    def get(self, key: str) -> Any:
        return self.data.get(key)

    def add_execution(self, execution_data):
        self.execution_history.append(execution_data)
