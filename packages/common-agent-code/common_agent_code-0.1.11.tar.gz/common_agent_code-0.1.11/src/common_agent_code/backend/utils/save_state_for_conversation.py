import pickle

def save_state_for_conversation(conversation_id, state):
    with open(f"memory/{conversation_id}.pkl", "wb") as f:
        pickle.dump(state, f)
