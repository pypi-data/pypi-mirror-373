import json
from typing import Dict, Any

def pretty_print_json(data: Dict[str, Any]):
    """Print JSON data in a readable format."""
    print(json.dumps(data, indent=2, default=str))
