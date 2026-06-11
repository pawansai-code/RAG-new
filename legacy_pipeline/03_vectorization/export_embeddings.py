import json
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

# 2. Fetch ALL items, but ONLY the embeddings
results = collection.get(
    include=["embeddings"] 
)

# 3. Format them into a clean dictionary
data = {}
for i in range(len(results['ids'])):
    embedding = results['embeddings'][i]
    if hasattr(embedding, 'tolist'):
        embedding = embedding.tolist()
    data[results['ids'][i]] = embedding

# 4. Save to JSON
output_file = "exported_embeddings.json"
with open(output_file, 'w') as f:
    json.dump(data, f, indent=4)

print(f"Successfully exported {len(data)} raw embeddings to {output_file}!")
