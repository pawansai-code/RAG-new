import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
from groq import Groq
import json
import time
import os
import argparse
from dotenv import load_dotenv

# ==========================================
# 1. SETUP & INITIALIZATION
# ==========================================
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    # In case the key is still named GEMINI_API_KEY in the .env file
    API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file!")

# Initialize the Groq client
client = Groq(api_key=API_KEY)

# ==========================================
# 2. LOCAL EMBEDDING FUNCTION
# ==========================================
# We use sentence-transformers to run embeddings completely locally and for free
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# ==========================================
# 3. AI ENRICHMENT LOGIC (GROQ)
# ==========================================
def generate_nl_descriptions(row_data, column_names):
    """Calls Groq (Llama-3) to understand the raw CSV row."""
    prompt = f"""
    You are a database expert. Analyze this schema row.
    Columns: {', '.join(column_names)}
    Row Values: {row_data}
    
    Generate two descriptions:
    1. "purpose": A short business explanation of what this row does.
    2. "technical_logic": A brief technical explanation of its backend operation.
    
    Respond STRICTLY in valid JSON format only, with no other text, like this: {{"purpose": "...", "technical_logic": "..."}}
    """
    
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You output only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant", # Extremely fast Llama 3.1 model
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        response_text = response.choices[0].message.content.strip()
        
        result = json.loads(response_text)
        return result.get("purpose", ""), result.get("technical_logic", "")
    except Exception as e:
        print(f"  [!] AI Text Generation Error: {e}")
        return "Unknown purpose", "Unknown logic"

# ==========================================
# 4. MAIN PIPELINE
# ==========================================
def process_csv_to_vectordb(input_csv, db_directory, collection_name):
    print(f"[*] Starting Groq + Local Embeddings Pipeline for: {input_csv}")
    
    df = pd.read_csv(input_csv)
    column_names = df.columns.tolist()
    total_rows = len(df)
    
    # Setup Vector Database with Local Sentence Transformers
    chroma_client = chromadb.PersistentClient(path=db_directory)
    
    collection = chroma_client.get_or_create_collection(
        name=collection_name, 
        embedding_function=sentence_transformer_ef
    )
    
    documents = []
    metadata_list = []
    ids = []
    
    print(f"[*] Enriching and formatting {total_rows} rows...")
    for index, row in df.iterrows():
        print(f"    -> Asking Groq AI to analyze Row {index + 1}/{total_rows}...")
        
        # Step A: Get AI Enrichment
        row_dict = row.to_dict()
        purpose, tech_logic = generate_nl_descriptions(row_dict, column_names)
        
        # Step B: Extract base values safely
        schema = str(row.get('schema_name', 'N/A'))
        component = str(row.get('component_name', 'N/A'))
        comp_type = str(row.get('component_type', 'N/A'))
        
        # Step C: Format for Embeddings
        structured_text = f"""
        Schema Name: {schema}
        Component Name: {component}
        Component Type: {comp_type}
        Business Purpose: {purpose}
        Technical Logic: {tech_logic}
        """.strip()
        
        documents.append(structured_text)
        metadata_list.append({"schema_name": schema, "component_name": component})
        ids.append(f"{schema}_{component}_{index}")
        
        # Very small pause for Groq limits (usually they allow many requests per second)
        time.sleep(0.3) 
        
    print(f"[*] Sending {len(documents)} formatted texts to local Sentence-Transformers for vectorization...")
    collection.add(
        documents=documents,
        metadatas=metadata_list,
        ids=ids
    )
    
    print(f"[SUCCESS] High-dimensional Vector Database built at '{db_directory}'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Groq-Powered CSV to VectorDB Pipeline")
    parser.add_argument("-i", "--input", required=True, help="Path to raw CSV file")
    args = parser.parse_args()
    
    # The folder where the database will be saved
    DB_FOLDER = "./chroma_groq_db"
    COLLECTION = "groq_schema_collection"
    
    if os.path.exists(args.input):
        process_csv_to_vectordb(args.input, DB_FOLDER, COLLECTION)
    else:
        print(f"Error: Could not find '{args.input}'")
