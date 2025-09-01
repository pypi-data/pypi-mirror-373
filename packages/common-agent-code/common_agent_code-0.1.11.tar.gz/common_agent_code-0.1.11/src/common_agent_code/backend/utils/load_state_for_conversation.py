from common_agent_code.backend.utils import AgentState
import pickle
def load_state_for_conversation(conversation_id):
    if not conversation_id:
        return AgentState({})
    try:
        with open(f"memory/{conversation_id}.pkl", "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AgentState({})
