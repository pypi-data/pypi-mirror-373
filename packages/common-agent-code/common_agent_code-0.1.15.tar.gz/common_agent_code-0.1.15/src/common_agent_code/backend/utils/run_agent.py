import json
import pandas as pd
import matplotlib.pyplot as plt
from common_agent_code.backend.utils.AgentState import AgentState
from common_agent_code.backend.utils.execute_code import execute_code
from common_agent_code.backend.utils.pretty_print_json import pretty_print_json
from common_agent_code.backend.utils.extract_json_from_string import extract_json_from_string
from common_agent_code.backend.utils.get_model_completion import my_completion
from common_agent_code.backend.utils.print_separator import print_separator
from common_agent_code.backend.utils.inspect_dataframe import inspect_dataframe
from common_agent_code.backend.models import ChatHistory
from common_agent_code.backend.utils.CustomJSONEncoder import CustomJSONEncoder

def run_agent(input_question: str, data=None, conversation_id = None):
    # Initialize agent state based on what's provided
    initial_state = AgentState({
        'pd': pd,
        'plt': plt,
        'inspect_dataframe': inspect_dataframe
    })
    previous_messages = []
    if conversation_id:
        # Try to find the most recent message with pickled objects
        latest_message = ChatHistory.query.filter_by(
            conversation_id=conversation_id,
            agent_type='data_analysis'
        ).filter(ChatHistory.pickled_objects != None).order_by(
            ChatHistory.timestamp.desc()
        ).first()
        
        if latest_message:
            # Load the objects and add them to the state
            objects = latest_message.load_objects()
            if objects:
                for key, value in objects.items():
                    initial_state.data[key] = value
                print(f"✅ Restored objects for conversation {conversation_id}: {list(objects.keys())}")
                
        history = ChatHistory.query.filter_by(
            conversation_id=conversation_id,
            agent_type='data_analysis'
        ).order_by(ChatHistory.timestamp.asc()).all()
        
        # Convert to message format expected by LLM
        for msg in history:
            if msg.role in ["user", "assistant"]:
                content = msg.content
                # For assistant messages that contained code, include the code and output
                if msg.role == "assistant" and msg.code:
                    content += f"\nCode executed:\n```python\n{msg.code}\n```"
                    if msg.output:
                        content += f"\nOutput:\n{msg.output}"
                
                previous_messages.append({
                    "role": msg.role,
                    "content": content
                })
    
    # Handle multiple dataframes or existing dataframe case
    if data is not None:
        if isinstance(data, list):
            # Multiple dataframes case - store all dataframes and set df to the first one initially
            initial_state.data['dataframes'] = data
            initial_state.data['df'] = data[0]
            # Flag to indicate multiple dataframes are available
            initial_state.data['multiple_dfs'] = True
        else:
            # Single dataframe case
            initial_state.data['df'] = data
            initial_state.data['multiple_dfs'] = False
    else:
        # No dataframe provided - this is a follow-up question
        # We'll add instructions for the LLM to continue with existing dataframes
        initial_state.data['continue_analysis'] = True

    # Add specific system prompt based on the state
    if initial_state.data.get('multiple_dfs', False):
        system_prompt = f'''
        You are an expert data scientist analyzing data through code execution.
        You have been provided with MULTIPLE CSV files which are available as a list called 'dataframes'.
        The first dataframe is already set as 'df' for convenience. Each dataframe has a 'source_file' column 
        indicating which file it came from.
        
        Available objects and functions:
        - dataframes: A list containing all loaded DataFrames
        - df: The first DataFrame (for convenience)
        - inspect_dataframe(df): Returns key DataFrame information
        - pd: pandas library
        - plt: matplotlib.pyplot
        
        IMPORTANT GUIDELINES:
        1. ALWAYS start by inspecting all dataframes using inspect_dataframe()
        2. Depending on the user's question, you might need to:
           - Merge/concatenate/join multiple dataframes
           - Analyze them separately and compare results
           - Focus on just one of the dataframes
        3. Break down complex tasks into steps
        4. Handle errors and missing data appropriately
        5. Return any created objects that need to be preserved
        
        Your output at each iteration must be a JSON with these fields:
        {{
            "reasoning": "Explain your thought process and what you learned",
            "next_step": "Clearly state what you will do next",
            "code_to_execute": "Your code here",
            "is_complete": false,
            "objects_to_preserve": ["list", "of", "variable", "names"]
        }}
        Do NOT return plain text responses, only JSON.
        '''
    elif initial_state.data.get('continue_analysis', False):
        system_prompt = f'''
        You are an expert data scientist analyzing data through code execution.
        This is a FOLLOW-UP question in an ongoing analysis. All previous objects and dataframes from 
        the prior conversation are still available in your execution context.
        
        Available objects and functions:
        - All variables from the previous conversation
        - Dataframes, plots, and results from previous analysis
        - inspect_dataframe(df): Returns key DataFrame information
        - pd: pandas library
        - plt: matplotlib.pyplot
        
        IMPORTANT GUIDELINES:
        1. First, check the existing objects to understand what's available
        2. You can reference and use all variables created in previous steps
        3. Break down complex tasks into steps
        4. Handle errors and missing data appropriately
        5. Return any created objects that need to be preserved
        
        Your output at each iteration must be a JSON with these fields:
        {{
            "reasoning": "Explain your thought process and what you learned",
            "next_step": "Clearly state what you will do next",
            "code_to_execute": "Your code here",
            "is_complete": false,
            "objects_to_preserve": ["list", "of", "variable", "names"]
        }}
        Do NOT return plain text responses, only JSON.
        '''
    else:
        system_prompt = f'''
        You are an expert data scientist analyzing data through code execution.
        The DataFrame and utilities are available in your execution context.
        You are an AI assistant that provides structured JSON responses. 

        Available objects and functions:
        - df: The input DataFrame
        - inspect_dataframe(df): Returns key DataFrame information
        - pd: pandas library
        - plt: matplotlib.pyplot

        IMPORTANT GUIDELINES:
        1. ALWAYS start by inspecting the dataframe using inspect_dataframe() and add it to "code_to_execute"
        2. After inspection, analyze the data structure before proceeding
        3. Break down complex tasks into steps
        4. Handle errors and missing data appropriately
        5. Return any created objects that need to be preserved

        Your output at each iteration must be a JSON with these fields:
        {{
            "reasoning": "Explain your thought process and what you learned",
            "next_step": "Clearly state what you will do next",
            "code_to_execute": "Your code here",
            "is_complete": false,
            "objects_to_preserve": ["list", "of", "variable", "names"]
        }}
        Do NOT return plain text responses, only JSON.
        '''

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": input_question}
    ]

    print_separator("Initial Question")
    print(f"User Question: {input_question}\n")

    is_complete = False
    max_iterations = 20
    iteration_count = 0
    last_code = None

    while not is_complete and iteration_count < max_iterations:
        iteration_count += 1
        print_separator(f"Iteration {iteration_count}")

        # Get next action from LLM
        print("\n[LLM Response]")
        response = my_completion(messages)
        print("Raw LLM Output:")
        print(response)

        # Parse the response
        try:
            action = json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from string if the response isn't pure JSON
            action = extract_json_from_string(response)
            if not action:
                print("\n❌ Failed to parse JSON from LLM output")
                messages.append({
                    "role": "user", 
                    "content": "Your last response was not valid JSON. Please provide a valid JSON response."
                })
                continue

        print("\nParsed Action:")
        pretty_print_json(action)

        if not action or "code_to_execute" not in action:
            print("\n❌ Failed to get valid action from LLM")
            messages.append({
                "role": "user",
                "content": "Your response is missing the 'code_to_execute' field. Please provide valid JSON with all required fields."
            })
            continue

        if action.get("is_complete") and not action["code_to_execute"].strip():
            print("\n✅ Task completed without additional code execution")
            break
            
        # Check for loops
        if action["code_to_execute"] == last_code:
            print("\n⚠️ Detected code repetition - requesting new approach")
            messages.append({
                "role": "user",
                "content": "Warning: Detected repeated code execution. Please try a different approach."
            })
            continue

        last_code = action["code_to_execute"]

        # Execute code and capture results
        print("\n[Code Execution]")
        print("Executing code:")
        print(action["code_to_execute"])
        
        result = execute_code(action["code_to_execute"], initial_state)

        serializable_objects = {}
        if result.returned_objects:
            for key, value in result.returned_objects.items():
                if isinstance(value, pd.DataFrame):
                    # Convert DataFrame to a dict representation
                    serializable_objects[key] = {
                        "type": "DataFrame",
                        "shape": value.shape,
                        "head": value.head(5).to_dict('records'),
                        "columns": list(value.columns)
                    }
                elif isinstance(value, np.ndarray):
                    # Convert numpy arrays to lists
                    serializable_objects[key] = {
                        "type": "ndarray",
                        "shape": value.shape,
                        "data": value.tolist() if value.size < 1000 else "Array too large to display"
                    }
                elif isinstance(value, plt.Figure):
                    # Just store the type for matplotlib figures
                    serializable_objects[key] = {"type": "matplotlib.Figure"}
                else:
                    # For other types, try to convert to string
                    try:
                        json.dumps(value, cls=CustomJSONEncoder)  # Test if it's JSON serializable
                        serializable_objects[key] = value
                    except (TypeError, OverflowError):
                        serializable_objects[key] = str(value)
        
        # Now add the execution with serializable objects
        initial_state.add_execution({
            "reasoning": action.get("reasoning", ""),
            "next_step": action.get("next_step", ""),
            "code_to_execute": action["code_to_execute"],
            "is_complete": action.get("is_complete", False),
            "result": {
                "output": result.output,
                "error": result.error,
                "returned_objects": serializable_objects
            }
        })

        print("\nExecution Result:")
        if result.error:
            print(f"❌ Error occurred: {result.error}")
            print("Traceback:")
            print(result.traceback)
        else:
            print("✅ Execution successful")

        if result.output:
            print("\nOutput:")
            print(result.output)

        if result.returned_objects:
            print("\nReturned Objects:")
            for key, value in result.returned_objects.items():
                print(f"{key}: {str(value)[:100]}...")

        # Prepare detailed feedback for LLM
        feedback = {
            "stdout": result.output,
            "error": result.error,
            "traceback": result.traceback,
            "returned_objects": {
                k: str(v) for k, v in (result.returned_objects or {}).items()
            }
        }

        # Update state with preserved objects
        if result.returned_objects:
            objects_to_preserve = action.get("objects_to_preserve", [])
            if not objects_to_preserve and result.returned_objects.get('df') is not None:
                # Always preserve df by default if not specified
                objects_to_preserve = ['df']
                
            preserved = {
                k: v for k, v in result.returned_objects.items()
                if k in objects_to_preserve
            }
            initial_state.update(preserved)
            print("\nPreserved Objects:")
            for key in preserved:
                print(f"- {key}")

        # Update conversation
        messages.extend([
            {"role": "assistant", "content": response},
            {"role": "user", "content": f"Execution result: {json.dumps(feedback)}"}
        ])

        # Check completion
        is_complete = action.get("is_complete", False)
        if is_complete:
            print("\n✅ Task completed")

        if iteration_count >= max_iterations:
            print("\n⚠️ Maximum iterations reached")
            return "Agent reached maximum iterations without completing task."

    print_separator("Final Results")
    final_result = {
        "status": "completed" if is_complete else "terminated",
        "iterations": iteration_count,
        "execution_history": initial_state.execution_history
    }
    pretty_print_json(final_result)
    return final_result
