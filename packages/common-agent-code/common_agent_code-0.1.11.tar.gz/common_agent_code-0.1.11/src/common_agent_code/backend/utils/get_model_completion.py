from common_agent_code.backend.services.llm_service import my_completion

def get_model_completion(messages, model_type="gpt-4o"):
    """
    Get completion from different AI models based on model_type.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        model_type: String indicating which model to use (e.g., 'gpt-4o', 'claude-sonnet')
        
    Returns:
        String containing the model's response
    """
    if model_type == "gpt-4o" or model_type.startswith("gpt-"):
        # Use your existing OpenAI function
        return my_completion(messages)
    elif model_type.startswith("claude-"):
        # Implement Claude API call here if needed
        # For now, fallback to GPT-4o
        print(f"Claude model {model_type} not implemented, falling back to GPT-4o")
        return my_completion(messages)
    else:
        # Default to GPT-4o for unknown models
        print(f"Unknown model type {model_type}, falling back to GPT-4o")
        return my_completion(messages)


