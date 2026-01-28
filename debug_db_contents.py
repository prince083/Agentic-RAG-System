import chromadb
from app.services.retrieval.vector_db import vector_db

client = chromadb.PersistentClient(path="data/vector_store")
collection = client.get_collection("rag_documents")

count = collection.count()
print(f"Total chunks in DB: {count}")

peek = collection.peek()
metadatas = peek['metadatas']
sources = set()

# Since peek might not show everything, let's query all metadata
all_data = collection.get()
for m in all_data['metadatas']:
    if m: 
        sources.add(m.get('source'))

print(f"Found sources: {sources}")
