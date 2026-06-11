import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
import json
import os
import argparse
from dotenv import load_dotenv

# ==========================================
# 1. SETUP & INITIALIZATION
# ==========================================
load_dotenv()

# ==========================================
# 2. LOCAL EMBEDDING FUNCTION
# ==========================================
# Using the same free, local sentence-transformers used in the groq_pipeline.py
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# ==========================================
# 3. AI ENRICHMENT LOGIC
# ==========================================
# (Removed duplicate generate_nl_descriptions. Now relies on RAG-schema output)

# ==========================================
# 4. MAIN PIPELINE
# ==========================================
def process_csv_to_vectordb(input_path, db_directory, collection_name):
    print(f"[*] Starting Local Pipeline for CSV(s) in: {input_path}")
    
    # Setup Vector Database with the local Sentence Transformer embedding function
    chroma_client = chromadb.PersistentClient(path=db_directory)
    
    collection = chroma_client.get_or_create_collection(
        name=collection_name, 
        embedding_function=sentence_transformer_ef
    )
    
    import glob
    if os.path.isdir(input_path):
        csv_files = glob.glob(os.path.join(input_path, "*.csv"))
    else:
        csv_files = [input_path]
        
    if not csv_files:
        print(f"    -> No CSV files found in {input_path}")
        return

    for file_path in csv_files:
        print(f"[*] Processing {file_path}...")
        df = pd.read_csv(file_path)
        total_rows = len(df)
        documents = []
        metadata_list = []
        ids = []
        
        filename = os.path.basename(file_path)
        
        print(f"[*] Enriching and formatting {total_rows} rows...")
        for index, row in df.iterrows():
            
            # Dynamically format EVERY column into the embedding text
            structured_text = "\\n".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
            documents.append(structured_text.strip())
            
            # Extract base values safely for metadata
            schema = str(row.get('schema_name', 'N/A'))
            component = str(row.get('component_name', 'N/A'))
            
            metadata_list.append({"schema_name": schema, "component_name": component, "source_file": filename})
            ids.append(f"{filename}_{index}")
            
        if documents:
            print(f"[*] Sending {len(documents)} formatted rows for local vectorization...")
            # This automatically calls the local embedding function
            collection.add(
                documents=documents,
                metadatas=metadata_list,
                ids=ids
            )
    
    print(f"[SUCCESS] High-dimensional Vector Database built at '{db_directory}'")

def process_json_dir_to_vectordb(input_dir, db_directory, collection_name):
    import glob
    print(f"[*] Starting JSON Sub-Problems Pipeline for directory: {input_dir}")
    
    # Find all JSON files
    json_files = glob.glob(os.path.join(input_dir, "*.json"))
    if not json_files:
        print(f"    -> No JSON files found in {input_dir}.")
        return

    chroma_client = chromadb.PersistentClient(path=db_directory)
    
    collection = chroma_client.get_or_create_collection(
        name=collection_name, 
        embedding_function=sentence_transformer_ef
    )
    
    documents = []
    metadata_list = []
    ids = []
    
    print(f"[*] Processing {len(json_files)} JSON files...")
    for file_path in json_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"    [!] Error decoding JSON from {file_path}")
                continue
                
        # Data is a list of sub-problem objects
        for item in data:
            doc_id = str(item.get('id', ''))
            statement = str(item.get('sub_problem_statement', ''))
            project_name = str(item.get('project_name', ''))
            
            if not doc_id or not statement:
                continue
                
            structured_text = f"""
Project Name: {project_name}
Sub-Problem: {statement}
""".strip()
            
            documents.append(structured_text)
            
            # Extract basic metadata
            meta = {
                "project_name": project_name,
                "parent_id": str(item.get('parent_id', '')),
                "source_type": "llm_problem_statement_decomposition"
            }
            metadata_list.append(meta)
            ids.append(doc_id)
            
    if documents:
        print(f"[*] Sending {len(documents)} formatted sub-problems for local vectorization...")
        collection.add(
            documents=documents,
            metadatas=metadata_list,
            ids=ids
        )
        print(f"[SUCCESS] Sub-problems embedded successfully into '{collection_name}' collection.")
    else:
        print("    -> No valid sub-problems found to embed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gemini-Powered CSV to VectorDB Pipeline")
    parser.add_argument("-i", "--input", required=False, help="Path to raw CSV file")
    parser.add_argument("-j", "--json-dir", required=False, help="Path to directory containing JSON sub-problem files")
    args = parser.parse_args()
    
    # The folder where the database will be saved
    DB_FOLDER = "./chroma_gemini_db"
    SCHEMA_COLLECTION = "gemini_schema_collection"
    SUBPROBLEMS_COLLECTION = "gemini_subproblems_collection"
    
    if not args.input and not args.json_dir:
        print("Error: Must provide either --input (CSV) or --json-dir (JSON folder) or both.")
        parser.print_help()
        exit(1)
        
    if args.input:
        if os.path.exists(args.input):
            process_csv_to_vectordb(args.input, DB_FOLDER, SCHEMA_COLLECTION)
        else:
            print(f"Error: Could not find '{args.input}'")
            
    if args.json_dir:
        if os.path.exists(args.json_dir):
            process_json_dir_to_vectordb(args.json_dir, DB_FOLDER, SUBPROBLEMS_COLLECTION)
        else:
            print(f"Error: Could not find directory '{args.json_dir}'")
