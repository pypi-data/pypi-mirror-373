from common_agent_code.backend.utils import CustomJSONEncoder
import pandas as pd
import os
import pickle
from common_agent_code.backend.models import ChatHistory
from common_agent_code.backend import db
import json
from common_agent_code.backend.utils.run_agent import run_agent
from flask import jsonify
import matplotlib.pyplot as plt

def handle_data_analysis(conversation_id, message, file_path=None):
    """Handle messages for the data analysis agent"""
    try:
        # Check conversation state to see if we have a DataFrame already
        conversation_state = db.session.query(ChatHistory).filter_by(
            conversation_id=conversation_id,
            agent_type='data_analysis'
        ).all()
        
        is_new_conversation = len(conversation_state) <= 1
        
        # Only require file path for new conversations
        if is_new_conversation and not file_path:
            error_message = ChatHistory(
                conversation_id=conversation_id,
                agent_type='data_analysis',
                model_type = 'gpt-4o',
                role="system",
                content="Please provide a CSV file to analyze."
            )
            db.session.add(error_message)
            db.session.commit()
            return json.dumps({
                "response": "Please provide a CSV file to analyze."
            })
            
        # Save user message to database
        user_message = ChatHistory(
            conversation_id=conversation_id,
            agent_type='data_analysis',
            model_type = 'gpt-4o',
            role="user",
            content=message
        )
        db.session.add(user_message)
        db.session.commit()
        
        # Handle file loading if file_path is provided (initial or subsequent file loads)
        if file_path:
            try:
                # Check if multiple CSV files are provided (comma-separated paths)
                if "," in file_path:
                    file_paths = [path.strip() for path in file_path.split(",")]
                    dataframes = []
                    
                    for path in file_paths:
                        try:
                            df_new = pd.read_csv(path)
                            # Add source file information as a column
                            filename = os.path.basename(path)
                            df_new['source_file'] = filename
                            dataframes.append(df_new)
                        except Exception as e:
                            return jsonify({
                                "error": f"Error reading CSV file {path}: {str(e)}"
                            }), 500
                    
                    # Initialize df as the first DataFrame to ensure it exists
                    df = dataframes[0]
                    
                    # Run the agent with the message and all dataframes (will be handled in the agent's first step)
                    result = run_agent(message, dataframes,conversation_id)
                else:
                    # Single CSV file
                    df = pd.read_csv(file_path)
                    result = run_agent(message, df,conversation_id)
            except FileNotFoundError:
                error_message = ChatHistory(
                    conversation_id=conversation_id,
                    agent_type='data_analysis',
                    model_type = 'gpt-4o',
                    role="system",
                    content=f"File not found at {file_path}"
                )
                db.session.add(error_message)
                db.session.commit()
                
                return jsonify({
                    "error": f"File not found at {file_path}"
                }), 400
            except Exception as e:
                error_message = ChatHistory(
                    conversation_id=conversation_id,
                    agent_type='data_analysis',
                    model_type = 'gpt-4o',
                    role="system",
                    content=f"Error reading CSV file: {str(e)}"
                )
                db.session.add(error_message)
                db.session.commit()
                
                return jsonify({
                    "error": f"Error reading CSV file: {str(e)}"
                }), 500
        else:
            # No file path provided but we have existing dataframes from previous interactions
            # We'll continue the conversation by running the agent with the message only
            result = run_agent(message, None,conversation_id)  # df will be retrieved from the state

        # Process the execution history to extract reasoning steps for frontend
        reasoning_steps = []
        plot_paths = []
        final_reasoning = ""
        final_code = ""
        
        if isinstance(result, dict) and 'execution_history' in result:
            for i, execution in enumerate(result['execution_history']):
                # Create a standardized step that the frontend expects
                reasoning = execution.get('reasoning', '')
                next_step = execution.get('next_step', '')
                code = execution.get('code_to_execute', '')
                
                step = {
                    "step_number": i + 1,
                    "reasoning": reasoning,
                    "next_step": next_step,
                    "code": code,
                }
                
                # Keep track of the last code executed
                if code:
                    final_code = code
                objects_to_pickle = {}
                # Add execution results if available
                if 'result' in execution:
                    step["output"] = execution['result'].get('output', '')
                    step["error"] = execution['result'].get('error', '')
                    
                    # Extract any plot paths
                    if 'returned_objects' in execution['result']:
                        returned_objects = execution['result']['returned_objects']
                        for key, value in returned_objects.items():
                            # Skip certain types that shouldn't be pickled
                            if not isinstance(value, (plt.Figure, str)) and key != 'plot_path':
                                # Add to objects that should be pickled
                                try:
                                    # Test if object is picklable
                                    pickle.dumps(value)
                                    objects_to_pickle[key] = value
                                except (pickle.PickleError, TypeError):
                                    # Skip objects that can't be pickled
                                    pass
                        if 'plot_path' in returned_objects:
                            plot_path = returned_objects['plot_path']
                            step["plot_path"] = plot_path
                            plot_paths.append(plot_path)
                
                reasoning_steps.append(step)
                
                # Store each step as a separate message in the database
                step_message = ChatHistory(
                    conversation_id=conversation_id,
                    agent_type='data_analysis',
                    model_type='gpt-4o',
                    role="assistant",
                    content=reasoning,
                    code=code,
                    output=step.get("output", ""),
                    error=step.get("error", ""),
                    plot_path=step.get("plot_path", ""),
                    plot_paths=json.dumps(plot_paths),
                    execution_history=json.dumps({"execution": execution}, cls=CustomJSONEncoder)
                )
                if objects_to_pickle:
                    step_message.save_objects(objects_to_pickle)
                db.session.add(step_message)
                
                # Track final reasoning (from steps marked as complete)
                if execution.get('is_complete') and reasoning:
                    final_reasoning = reasoning
        
        # If no step was explicitly marked complete, use the last reasoning
        if not final_reasoning and reasoning_steps:
            final_reasoning = reasoning_steps[-1]["reasoning"]
        
        # Commit all changes to database
        db.session.commit()
        
        # Format the response to match what the frontend expects for data_analysis
        response_data = {
            "response": final_reasoning or str(result),
            "reasoning_steps": reasoning_steps,
            "plot_paths": plot_paths,
            "final_output": {
                "reasoning": "",
                "status": result.get("status", ""),
                "iterations": result.get("iterations", 0)
            }
        }

        return json.dumps(response_data, cls=CustomJSONEncoder)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
