from common_agent_code.backend.services.graph_service import execute_knowledge_graph
from common_agent_code.backend.services.web_service import web_search
from common_agent_code.backend.services.nlp_service import extract_key_terms
from common_agent_code.backend.utils.current_date import current_date

def handle_other_tools(tool_id, tool_payload):
    """Helper function to handle other tools."""
    if tool_id == 'current_date':
        return current_date()
    elif tool_id == 'web_search':
        return web_search(tool_payload['query_string'], tool_payload['num_results'])
    elif tool_id == 'extract_key_terms':
        return extract_key_terms(tool_payload['query_string'])
    elif tool_id == 'knowledge_graph':
        return execute_knowledge_graph(tool_payload)
    return None
