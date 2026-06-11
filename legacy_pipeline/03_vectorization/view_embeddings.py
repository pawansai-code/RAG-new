import chromadb
from chromadb.utils import embedding_functions

# 1. Connect to the local database folder
db_directory = "./chroma_groq_db"
collection_name = "groq_schema_collection"

chroma_client = chromadb.PersistentClient(path=db_directory)

# We need to provide the same embedding function we used to create it
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# 2. Get the collection
collection = chroma_client.get_collection(
    name=collection_name, 
    embedding_function=sentence_transformer_ef
)

# 3. Fetch the first 2 items to see what they look like
results = collection.get(
    limit=2,
    include=["embeddings", "documents", "metadatas"]
)

print(f"\nTotal items in database: {collection.count()}\n")
print("="*50)

for i in range(len(results['ids'])):
    print(f"ID: {results['ids'][i]}")
    print(f"Metadata: {results['metadatas'][i]}")
    print(f"Document Text:\n{results['documents'][i][:200]}... [truncated]")
    
    # The actual embedding is a massive list of math numbers (floats)
    embedding_vector = results['embeddings'][i]
    print(f"\nEmbedding Vector (first 5 numbers out of {len(embedding_vector)}):")
    print(f"{embedding_vector[:5]} ...")
    print("="*50)
