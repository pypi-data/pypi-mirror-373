from sentence_transformers import SentenceTransformer
import faiss
from common_agent_code.backend.services.visualization_service import gathered_context_visualization
from common_agent_code.backend.services.pdf_service import process_all_pdfs

def run_faiss_knn(tool_payload):
    """Enhanced FAISS KNN search with automatic visualization."""
    query_string = tool_payload['query_string']
    k = tool_payload['k']

    try:
        query_embedding = get_embeddings(query_string)
        if query_embedding is None:
            return {"error": "Failed to generate embeddings for the query."}

        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        distances, indices = index.search(query_embedding, k)

        # Gather contexts
        contexts = []
        total_context = ""
        for i in range(k):
            relationship_text = all_chunks[indices[0][i]]
            contexts.append(relationship_text)
            total_context += f"{i + 1}. {relationship_text}\n"
            # print(f"Relationship: {relationship_text}")
            # print(f"Distance: {distances[0][i]}")

        # Create visualization automatically
        viz_result = gathered_context_visualization(
            query_string,
            contexts,
            distances[0].tolist()
        )

        return {
            "cached_result": False,
            "answer": total_context,
            "context": contexts,
            "distances": distances[0].tolist(),
            "visualization": viz_result
        }

    except Exception as e:
        print(f"Error in run_faiss_knn: {e}")
        return {"error": str(e)}

DIRECTORY_PATH = '/Users/TejasSai/Desktop/Projects_with_Sriram/ML Projects/BioMedical_Graph_Knowledge_Graphs/Directory_of_Files'  # Replace with your directory path
try:
    all_chunks, embeddings, file_mapping = process_all_pdfs(DIRECTORY_PATH)

    print(f"Total number of chunks across all PDFs: {len(all_chunks)}")
    print(f"Shape of all embeddings: {embeddings.shape}")
    print(f"Number of processed files: {len(file_mapping)}")

    # Initialize FAISS index
    EMBEDDING_DIM = embeddings.shape[1]
    index = faiss.IndexFlatL2(EMBEDDING_DIM)
    index.add(embeddings)

    print(f"Number of embeddings in index: {index.ntotal}")

except Exception as e:
    print(f"Error initializing FAISS index: {e}")
    all_chunks, embeddings, file_mapping, index = [], [], {}, None
    
def get_embeddings(chunks, model_name='all-MiniLM-L6-v2'):
    """
    Generate embeddings for text chunks using SentenceTransformer.
    """
    try:
        model = SentenceTransformer(model_name)
        return model.encode(chunks, show_progress_bar=False)
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None