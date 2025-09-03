from flask import jsonify
from common_agent_code.backend.models import ChatHistory
from common_agent_code.backend import db
import json
from common_agent_code.backend.services.faiss_service import run_faiss_knn
from common_agent_code.backend.utils.handle_other_tools import handle_other_tools
from common_agent_code.backend.services.nlp_service import strip_markdown
from common_agent_code.backend.utils import CustomJSONEncoder

def handle_knowledge_extraction(conversation_id, message):
    """Handle messages for the knowledge extraction agent"""
    try:
        # Initialize messages list
        messages = []

        # Fetch conversation history for context
        conversation_history = ChatHistory.query.filter_by(
            conversation_id=conversation_id,
            agent_type='knowledge_extraction'
        ).order_by(ChatHistory.timestamp).all()

        # Append previous messages to the messages list (for LLM context)
        for msg in conversation_history:
            messages.append({"role": msg.role, "content": msg.content})

        # Get your existing system prompt
        system_prompt = """
        You are a helpful agent that solves problems.
        You have access to the following tools :
        -   tool_id : current_date()
                - this function has no input parameters and returns a string as its output
                - Example tool_payload : None
        -   tool_id : run_faiss_knn(query_string : str, k : int)
                - this function has 2 input parameters query_string and k
                - Example tool_payload : {"query_string" : "What is my Name", "k" : 5}
        -   tool_id : web_search(query_string: str, num_results: int)
                - this function has 2 input parameters query_string 
                - Example tool_payload : {"query_string" : "What is my Name", "num_results" : 5}
        -   tool_id : gathered_context_visualization(query_string : str, contexts : list, distances : list)
                - this function has 3 input parameters query_string, contexts and distances
                - Example tool_payload : {"query_string" : "What is my Name", "contexts" : ["My name is this", "I have h in my name"], "distances" : [1.4,2.3]}
        -   tool_id : extract_key_terms(query_string : str)
                - this function has 1 input parameter query_string
                -- Example tool_payload : {"query_string" : "What is my Name"}
        -   tool_id: knowledge_graph(query_string: str)
                - this function has 1 input parameter query_string
                - Example tool_payload: {"query_string": "What is related to COVID-19?"}
        If there is any code, add it in the reasoning itself.
        All responses must be in the following JSON Format : 
        {
            "reasoning" : " ", # the reasoning should include all of the assitants thoughts and answer the user's questions - this is the only thing the user sees, make it conversational.
            "tool_id" : " ",
            "tool_payload" : " ",
            "is_complete" : true / false
        }
        """

        # Prepare initial context for the AI
        messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})

        # Loop for processing tools (use your existing loop logic)
        not_complete = True
        final_answer = None
        reasoning_steps = []
        count = 0
        max_iterations = 10
        
        while not_complete and count < max_iterations:
            try:
                count += 1
                raw_output = my_completion(messages)
                
                try:
                    output = json.loads(raw_output)
                    if isinstance(output.get('reasoning'), str):
                        output['reasoning'] = strip_markdown(output['reasoning'])
                except json.JSONDecodeError as json_err:
                    # [error handling code remains the same]
                    continue
                
                # Handle the tool output
                tool_id = output['tool_id']
                tool_payload = output['tool_payload']
                
                if tool_id == 'run_faiss_knn':
                    tool_output = run_faiss_knn(output['tool_payload'])
                else:
                    tool_output = handle_other_tools(tool_id, output['tool_payload'])
                
                # Add AI's reasoning to the database
                ai_message = ChatHistory(
                    conversation_id=conversation_id,
                    agent_type='knowledge_extraction',
                    model_type='gpt-4o',
                    role="system",
                    tool_used=tool_id,
                    tool_payload=json.dumps(tool_payload),
                    tool_output=json.dumps(tool_output),
                    step_number=count,
                    content=output['reasoning']
                )
                
                db.session.add(ai_message)
                
                # Add spacing for better formatting in the reasoning
                formatted_reasoning = output["reasoning"].replace("\n", "\n\n")
                
                reasoning_steps.append({
                    "role": "assistant",
                    "tool_used": f"Tool being used: {output['tool_id']}",
                    "tool_payload": f"What is being searched for: {output['tool_payload']}",
                    "tool_output": tool_output,
                    "reasoning": formatted_reasoning
                })
                
                db.session.commit()
                
                if output['is_complete']:
                    # For the final answer, don't duplicate the reasoning
                    # Instead, add a clear "FINAL ANSWER:" prefix
                    final_answer = {
                        "reasoning": "FINAL ANSWER:\n\n" + formatted_reasoning,
                        "tool_used": tool_id,
                        "final_output": None  # Don't include the tool output again
                    }
                    
                    # Return only the final reasoning in the final_output
                    return json.dumps({
                        "reasoning_steps": reasoning_steps,
                        "final_output": final_answer
                    }, cls = CustomJSONEncoder)
                
                messages.append({"role": "assistant", "content": raw_output})
                if tool_output:
                    messages.append({"role": "user", "content": str(tool_output)})
                    
            except Exception as e:
                print(f"Error during processing: {e}")
                return jsonify({"error": f"An error occurred: {str(e)}"}), 500
                
        return jsonify({"error": "Processing did not complete in time."}), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
