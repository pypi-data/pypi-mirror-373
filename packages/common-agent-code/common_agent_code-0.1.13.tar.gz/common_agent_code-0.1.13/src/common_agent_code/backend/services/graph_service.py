import json
import networkx as nx
from common_agent_code.backend.services.llm_service import llm_select_entities
from common_agent_code.backend.utils import load_file_by_type

def load_knowledge_graph():
    """Load and parse the knowledge graph data."""
    try:
        with open('/Users/TejasSai/Desktop/ML_Projects/BioMedical_Graph_Knowledge_Graphs/cumulative_entities1.json', 'r') as f:
            kg_data = json.load(f)
            return kg_data
    except Exception as e:
        print(f"Error loading knowledge graph: {e}")
        return None
def create_graph(entities, relationships):
    """Creates a networkx graph from the entities and relationships."""
    graph = nx.DiGraph()
    for entity_name, entity_id in entities.items():
        print(f" Entity Name and Enitity ID : {entity_name}, {entity_id}")
        graph.add_node(entity_id, name=entity_name)

    for rel in relationships:
        print(f"Relationship : {rel}")
        graph.add_edge(rel['source'], rel['target'], type=rel['type'], description=rel['description'])
    return graph

def find_all_paths(graph, start_node, end_node):
    """Finds all paths between two nodes in the graph."""
    try:
        all_paths = list(nx.all_simple_paths(graph, source=start_node, target=end_node))
        return all_paths
    except nx.NetworkXNoPath:
        return None
    except nx.NetworkXError as e:
        return f"Error: {str(e)}"

def get_all_paths(query, kg_data):
    """
    Finds all paths between two entities in the knowledge graph,
    using the LLM to select the entities based on a query.
    """
    entities = kg_data['entities']
    relationships = kg_data['relationships']

    if not query:
        return {"error": "A query is required to select entities using the LLM."}

    # Use LLM to select the start and end
    selected_entities = llm_select_entities(query, entities)
    print(f"Selected Entities are  : {selected_entities}")
    if not selected_entities:
        return {"error": "Could not determine start and end entities from LLM."}

    # Find all paths between FIRST and LAST elements
    start_node, end_node = selected_entities[0], selected_entities[1]

    graph = create_graph(entities, relationships)
    all_paths = find_all_paths(graph, start_node, end_node)

    if all_paths:
        # Convert node IDs to names for better readability
        paths_with_details = []
        for path in all_paths:
            detailed_path = []
            for i in range(len(path) - 1):
                source = graph.nodes[path[i]]['name']
                target = graph.nodes[path[i + 1]]['name']
                edge_data = graph.get_edge_data(path[i], path[i + 1])
                relationship = edge_data.get('type', 'relationship')
                description = edge_data.get('description', 'No description')
                detailed_path.append(f"{source} --[{relationship}]--> {target}: {description}")
            paths_with_details.append(detailed_path)
        return {"all_paths": paths_with_details}
    else:
        return {"message": f"No paths found between {start_node} and {end_node}"}

def execute_knowledge_graph(tool_payload):
    """Execute the knowledge graph query and return structured results."""
    try:
        # Load knowledge graph data
        KG_DATA = load_knowledge_graph()
        if not KG_DATA:
            return "Error: Could not load knowledge graph data."
        query = tool_payload['query_string']
        result = get_all_paths(query, KG_DATA)
        
        # Format results
        print(f"Query: {query}")
        if "all_paths" in result:
            print("All Paths:")
            for path in result["all_paths"]:
                print(" -> ".join(path))
        else:
            print(f"Result: {result}")

        formatted_results = {
        'query': query,
        'type': 'paths' if 'all_paths' in result else 'result',
        'data': {}
    }
    
        if 'all_paths' in result:
            # Format each path as a joined string
            formatted_paths = []
            for path in result['all_paths']:
                formatted_path = " -> ".join(path)
                formatted_paths.append(formatted_path)
            
            formatted_results['data'] = {
                'paths': formatted_paths,
                'path_count': len(formatted_paths)
            }
        else:
            formatted_results['data'] = result
        
        return json.dumps(formatted_results)  # Serialize to JSON string
        
    except Exception as e:
        return f"Error executing knowledge graph query: {str(e)}"
