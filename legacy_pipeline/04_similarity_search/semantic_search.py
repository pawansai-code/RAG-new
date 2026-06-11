import os
import argparse
import chromadb
from chromadb.utils import embedding_functions

def run_similarity_search(db_directory, schema_collection_name, subproblems_collection_name, output_dir, top_k=50):
    print(f"[*] Connecting to Vector Database at {db_directory}")
    
    # Connect to ChromaDB
    chroma_client = chromadb.PersistentClient(path=db_directory)
    
    # Initialize the same local embedding function used in Step 3
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    # Load collections
    try:
        schema_col = chroma_client.get_collection(name=schema_collection_name, embedding_function=sentence_transformer_ef)
        subprobs_col = chroma_client.get_collection(name=subproblems_collection_name, embedding_function=sentence_transformer_ef)
    except ValueError as e:
        print(f"[!] Error loading collections: {e}")
        print("Please ensure Step 3 (Vectorization) has completed successfully and populated the database.")
        return

    print("[*] Loading sub-problems from the database...")
    # Fetch all sub-problems including their mathematical embeddings
    subprobs_data = subprobs_col.get(include=["embeddings", "documents"])
    
    subprob_ids = subprobs_data.get("ids", [])
    subprob_docs = subprobs_data.get("documents", [])
    subprob_embeddings = subprobs_data.get("embeddings", [])
    
    if not subprob_ids:
        print("[!] No sub-problems found in the collection. Have you ingested them yet?")
        return
        
    print(f"[*] Found {len(subprob_ids)} sub-problems. Running Cosine Similarity search against enriched schema components...\n")
    
    # We query the schema collection using the exact mathematical embeddings of the sub-problems
    results = schema_col.query(
        query_embeddings=subprob_embeddings,
        n_results=top_k
    )
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    for i in range(len(subprob_ids)):
        subprob_id = subprob_ids[i]
        statement = subprob_docs[i]
        
        file_lines = []
        file_lines.append(f"Sub-Problem ID: {subprob_id}")
        file_lines.append(f"Statement:\n{statement}\n")
        file_lines.append("Top Matching Schema Components:")
        file_lines.append("-" * 40)
        
        # Results contain lists of lists because we passed multiple query texts
        match_ids = results['ids'][i]
        match_docs = results['documents'][i]
        match_distances = results['distances'][i] # Lower distance = higher similarity
        
        for j in range(len(match_ids)):
            raw_distance = match_distances[j]
            # ChromaDB returns Squared L2 Distance by default. 
            # For normalized embeddings, Cosine Similarity = 1 - (L2_Distance / 2)
            cosine_sim = 1 - (raw_distance / 2.0)
            
            file_lines.append(f"Match {j+1}: (ID: {match_ids[j]}) - Cosine Similarity: {cosine_sim:.4f} (Raw Distance: {raw_distance:.4f})")
            file_lines.append(match_docs[j])
            file_lines.append("-" * 40 + "\n")
            
        # Write to separate file
        filename = f"{subprob_id}.txt"
        # Sanitize filename just in case
        safe_filename = "".join([c if c.isalnum() or c in ['_', '-'] else '_' for c in filename])
        filepath = os.path.join(output_dir, safe_filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(file_lines))
            
    print(f"\n[SUCCESS] Similarity search complete! Individual text reports saved to: {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run cosine similarity search between sub-problems and schema components")
    parser.add_argument("-d", "--db-dir", required=True, help="Path to the ChromaDB directory")
    parser.add_argument("-o", "--output-dir", required=True, help="Path to save the output text reports")
    parser.add_argument("-k", "--top-k", type=int, default=50, help="Number of top schema matches to retrieve per sub-problem")
    
    args = parser.parse_args()
    
    SCHEMA_COLLECTION = "gemini_schema_collection"
    SUBPROBLEMS_COLLECTION = "gemini_subproblems_collection"
    
    run_similarity_search(args.db_dir, SCHEMA_COLLECTION, SUBPROBLEMS_COLLECTION, args.output_dir, args.top_k)
