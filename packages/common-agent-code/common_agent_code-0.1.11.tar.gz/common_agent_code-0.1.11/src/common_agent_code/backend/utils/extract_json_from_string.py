import re
import json

def extract_json_from_string(llm_output: str):
    # First try to find JSON in markdown code blocks
    pattern = r'``````'
    match = re.search(pattern, llm_output)

    
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass  # Continue if JSON decoding fails
    
    # If no markdown blocks found, try to find raw JSON
    try:
        json_pattern = r'\{[\s\S]*\}'
        match = re.search(json_pattern, llm_output)
        if match:
            return json.loads(match.group(0))
    except json.JSONDecodeError:
        pass
    
    print("Could not extract valid JSON from response")
    return None
