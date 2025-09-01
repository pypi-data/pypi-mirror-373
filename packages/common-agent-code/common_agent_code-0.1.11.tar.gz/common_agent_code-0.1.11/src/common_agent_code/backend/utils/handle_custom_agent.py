from flask import jsonify
from common_agent_code.backend.models import ChatHistory
from common_agent_code.backend import db
import json
import traceback
from common_agent_code.backend.utils.execute_code import execute_code
from common_agent_code.backend.utils.AgentState import AgentState
from common_agent_code.backend.utils.get_model_completion import get_model_completion

def handle_custom_agent(conversation_id, message, definition, file_path=None, preserved_objects={}):
    try:
        print(f"Starting custom agent handler for conversation {conversation_id}")

        plot_paths_accumulated = []
        system_prompt = definition.system_prompt
        
        system_prompt += (
            "\n\nIMPORTANT: Your response MUST be a JSON object. "
            "Your main goal is to solve the user's request step-by-step. "
            "If you need to write and execute code, provide it in the 'code' field. "
            "After execution, I will provide you with the output and errors. "
            "Based on that feedback, you will plan your next step."
            "🔒 SYSTEM REQUIREMENT 🔒 : FIRST UNDERSTAND WHAT IS IN THE OBJECT for e.g if DF then do df.columns(), df.head(), df.describe() etc."
            "🔒 SYSTEM REQUIREMENT 🔒 : You MUST re-use the returned_objects dictionary already present in memory if it exists, instead of reinitializing it. Do not use returned_objects = {} if one is already available."
            "🔒 SYSTEM REQUIREMENT 🔒 : When saving plots, you MUST save them to the 'static' folder using os.makedirs('static', exist_ok=True') AND record the file path into returned_objects['plot_paths']"
            "🔒 SYSTEM REQUIREMENT 🔒 : Make sure no spaces are there in the file path"
            "🔒 SYSTEM REQUIREMENT 🔒 : Make sure the plot paths are added to returned_objects using returned_objects.setdefault('plot_paths', []).append(path)"
            "🔒 SYSTEM REQUIREMENT 🔒 : VERY IMPORTANTTTTTT: If you want to print, you can't think it acts like a notebook. YOU HAVE TO PRINT IT by calling print and other relevant functions!"
            "🔒 SYSTEM REQUIREMENT 🔒 : This is NOT a notebook — previous code cells do NOT persist. All functions and variables must be redefined or explicitly carried forward using `'persist_state': true`"
            "\n\nJSON Structure:"
            "{\n"
            "  \"reasoning\": \"Your thought process and explanation for EACH step. ***DO NOT use 'updated_answer' or any other key. This is the only supported explanation key***\",\n"
            "  \"code\": \"The Python code to execute for this step. (can be an empty string)\",\n"
            "  \"persist_state\": boolean (Set to true ONLY when you want to save the current variables for future turns),\n"
            "  \"is_complete\": boolean (Set to true ONLY when the final answer is ready and all tasks are done.)\n"
            "}\n"
        ) 
    
        messages = [{"role": "system", "content": system_prompt}]

        if preserved_objects:
            available_vars = ", ".join(preserved_objects.keys())
            initial_state_message = (
                f"The following variables have been restored/loaded and are available for use: {available_vars}. "
                "These are already loaded in memory - DO NOT reload them from files. "
                "**IMPORTANT AND REQUIRED** - Start by inspecting them (e.g., with `.head()`, `.columns`, `.info()`) to understand their structure before proceeding."
            )
            messages.append({"role": "system", "content": initial_state_message})
            
        conversation_history = ChatHistory.query.filter(
            ChatHistory.conversation_id == conversation_id,
            ChatHistory.role.in_(["user", "assistant"])
        ).order_by(ChatHistory.timestamp).all()

        for msg in conversation_history:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": message})

        not_complete = True
        final_answer = None
        reasoning_steps = []
        count = 0
        max_iterations = 15

        state = AgentState(initial_data=preserved_objects)
        
        while not_complete and count < max_iterations:
            count += 1
            raw_output = get_model_completion(messages, definition.model_type)

            try:
                output_json = json.loads(raw_output)
            except json.JSONDecodeError:
                # Handle JSON parsing error
                messages.append({"role": "assistant", "content": raw_output})
                messages.append({"role": "user", "content": "Error: Your last response was not valid JSON. Please correct it and adhere to the specified JSON format."})
                continue
            print(f"🔍 Model output JSON: {output_json}")
            is_complete = output_json.get('is_complete', False)
            reasoning = output_json.get("reasoning") or output_json.get("updated_answer", "")
            code_to_execute = output_json.get('code', '')
            should_persist_state = output_json.get('persist_state', False)
            
            # Initialize execution result variables
            execution_output, execution_error = "", ""
            execution_result = None
            plot_paths = []
            
            # Add assistant message to conversation
            messages.append({"role": "assistant", "content": raw_output})
            
            if code_to_execute:
                print("⚙️ Executing code...")
                print(f"Code to execute:\n{code_to_execute}")
                execution_result = execute_code(code_to_execute, state)
                print(f'Execution result is : {execution_result}')
                execution_output = execution_result.output
                execution_error = execution_result.error
                # Collect all plot paths over multiple iterations
                persisted_returned = preserved_objects.get("returned_objects", {})
                persisted_paths = persisted_returned.get("plot_paths", [])
                new_paths = execution_result.returned_objects.get("plot_paths", [])
                merged_paths = list(dict.fromkeys(persisted_paths + new_paths))
                persisted_returned["plot_paths"] = merged_paths
                preserved_objects["returned_objects"] = persisted_returned
                plot_paths_accumulated = merged_paths
                print(plot_paths_accumulated)
                # Update the main state with any new or modified variables from the execution
                preserved_objects.update(state.data) 
                print(f"State updated. Current variables: {list(preserved_objects.keys())}")
                
                # Provide feedback to the model
                feedback = (
                    f"Your code has been executed.\n"
                    f"Output (stdout):\n---\n{execution_output or 'No output'}\n---\n"
                    f"Error:\n---\n{execution_error or 'None'}\n---\n"
                )
                if execution_error:
                    feedback += "The code failed. Please analyze the error and provide the corrected code. Do NOT repeat the failed code."
                else:
                    feedback += "The code executed successfully. Please proceed to the next step or conclude the task."
                messages.append({"role": "user", "content": feedback})
                
                if should_persist_state and definition.memory_enabled:
                    print(f"💾 Persisting state for conversation {conversation_id} as requested by the agent.")
                    memory_message = ChatHistory(
                        conversation_id=conversation_id,
                        agent_type="custom",
                        model_type=definition.model_type,
                        agent_definition_id=definition.id,
                        role="system",
                        content=f"State persisted. Variables saved: {list(preserved_objects.keys())}"
                    )
                    memory_message.save_objects(preserved_objects)
                    db.session.add(memory_message)
                    db.session.commit()
                    print("✅ State saved successfully.")

            # Prepare response content with safe defaults
            response_content = {
                "updated_answer": reasoning,
                "code": code_to_execute,
                "is_complete": is_complete,
                "output": execution_output,
                "error": execution_error,
                "plot_paths": plot_paths_accumulated
            }
            ai_message = ChatHistory(
                conversation_id=conversation_id,
                agent_type="custom",
                model_type=definition.model_type,
                agent_definition_id=definition.id,
                role="assistant",
                content=json.dumps(response_content),
                code=code_to_execute,
                step_number=count
            )

            db.session.add(ai_message)
            db.session.commit()

            reasoning_steps.append({
                "step_number": count,
                "reasoning": reasoning,
                "next_step": output_json.get('next_step', ''),
                "code": code_to_execute,
                "output": execution_output,
                "error": execution_error,
                "plot_paths": plot_paths_accumulated
            })
            print(reasoning)
            if is_complete:
                if not plot_paths_accumulated:
                    final_returned = preserved_objects.get("returned_objects", {})
                    if "plot_paths" in final_returned:
                        plot_paths_accumulated.extend(final_returned["plot_paths"])
                final_answer = {
                    "reasoning": "FINAL ANSWER:\n\n" + reasoning,
                    "code_to_execute": code_to_execute,
                    "final_output": execution_output,
                    "plot_paths": plot_paths_accumulated
                }
                not_complete = False

        # Final state persistence (only if memory is enabled and we have objects to save)
        if definition.memory_enabled and preserved_objects and not should_persist_state:
            memory_message = ChatHistory(
                conversation_id=conversation_id,
                agent_type="custom",
                model_type=definition.model_type,
                agent_definition_id=definition.id,
                role="system",
                content="Memory state updated at end of conversation"
            )
            memory_message.save_objects(preserved_objects)
            db.session.add(memory_message)
            db.session.commit()

        print(f"Custom agent handler completed. Is complete: {not not_complete}")
        
        result = {
            "reasoning_steps": reasoning_steps,
            "final_output": final_answer,
            "preserved_objects": list(preserved_objects.keys()) if preserved_objects else [],
            "plot_paths": plot_paths_accumulated
        }
        print('Plot Paths:', plot_paths_accumulated)
        return jsonify(result)

    except Exception as e:
        traceback.print_exc()
        print(f"Error in handle_custom_agent: {e}")
        return jsonify({"error": f"Error in custom agent: {str(e)}"}), 500
    