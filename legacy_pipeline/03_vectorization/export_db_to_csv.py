import pandas as pd
import chromadb
from chromadb.utils import embedding_functions

# 1. Connect to the local database folder
db_directory = "./chroma_groq_db"
collection_name = "groq_schema_collection"

chroma_client = chromadb.PersistentClient(path=db_directory)
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

collection = chroma_client.get_collection(
    name=collection_name, 
    embedding_function=sentence_transformer_ef
)

# 2. Fetch ALL items
# We exclude the 'embeddings' list here so the CSV is actually human-readable
results = collection.get(
    include=["documents", "metadatas"] 
)

# 3. Format them into a list of dictionaries
data = []
for i in range(len(results['ids'])):
    row = {
        "id": results['ids'][i],
        "document": results['documents'][i],
    }
    # Add all metadata fields (like schema_name, component_name)
    if results['metadatas'][i]:
        row.update(results['metadatas'][i])
        
    data.append(row)

# 4. Save to CSV
df = pd.DataFrame(data)
output_file = "exported_groq_data.csv"
df.to_csv(output_file, index=False)

print(f"Successfully exported all {len(data)} rows to {output_file}!")
