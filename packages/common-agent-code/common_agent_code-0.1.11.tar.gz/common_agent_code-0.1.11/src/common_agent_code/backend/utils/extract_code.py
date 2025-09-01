import re
from typing import Optional

def extract_code(response: str) -> Optional[str]:
    match = re.search(r'``````', response, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None