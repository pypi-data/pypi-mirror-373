from openai import AzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv()
def my_completion(messages):
    """Interact with Azure OpenAI to generate a completion."""
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-02-15-preview",
        azure_endpoint="https://radiusofself.openai.azure.com",
        azure_deployment="gpt-4o"
    )
    chat_completion = client.chat.completions.create(
        model='gpt-4o',
        messages=messages,
        temperature=0.1,
        response_format={"type": "json_object"} 
    )
    return chat_completion.choices[0].message.content


def llm_select_entities(query, entities):
    """
    Uses the LLM to select entities from the knowledge graph based on a query.
    """
    entity_names = list(entities.keys())
    entity_list_string = "\n".join(entity_names)

    prompt = f"""
    Given the following query: {query}, and the following list of entities from a knowledge graph:
    {entity_list_string}

    Which entities from the list are in the query? Remember to return entities in order of position w.r.t the query.  Return their names, separated by a comma.
    For example:  Entity A, Entity B, Entity C
    """

    messages = [{"role": "user", "content": prompt}]
    llm_output = my_completion(messages)
    print(f"LLM OUTPUT : {llm_output}")
    # Parse the LLM output to get the entity names
    try:
        entity_names = [name.strip() for name in llm_output.split(",")]
        print(f"Entity names : {entity_names}")
        #Look up the entity IDs
        entity_ids = [entities[name] for name in entity_names if name in entities]
        if len(entity_ids) >= 2:  # Require at least two entities for a path
            return entity_ids
        else:
            return None #Didn't get enough valid entities
    except:
        return None #Error parsing
