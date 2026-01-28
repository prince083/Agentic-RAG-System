from typing import List, Dict, Any, Optional
import chromadb
import asyncio
from chromadb.utils import embedding_functions
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.core.config import settings
from app.models.document import ProcessedChunk

class VectorDBService:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="data/vector_store")
        
        # Use Google Gemini Embeddings (via LangChain wrapper for manual handling or direct API if simpler)
        # Note: ChromaDB doesn't have a native simple Google impl in older versions, 
        # so we will use a custom embedding function adapter or just generate them before insertion.
        # For simplicity and robustness, let's use the LangChain wrapper to generate embeddings 
        # and pass them as lists to Chroma.
        
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001", 
            google_api_key=settings.GOOGLE_API_KEY
        )
        
        # We create collection without a built-in function because we will embed manually
        self.collection = self.client.get_or_create_collection(name="rag_documents")

    async def add_chunks(self, chunks: List[ProcessedChunk]):
        if not chunks:
            return

        import time
        
        # Batch processing to avoid hitting Rate Limits (especially for free tier)
        BATCH_SIZE = 5
        total_chunks = len(chunks)
        
        for i in range(0, total_chunks, BATCH_SIZE):
            batch = chunks[i : i + BATCH_SIZE]
            
            texts = [chunk.text for chunk in batch]
            metadatas = [chunk.metadata for chunk in batch]
            ids = [f"{chunk.source_document}_{chunk.chunk_index}" for chunk in batch]

            try:
                # Generate embeddings
                embeddings = self.embeddings.embed_documents(texts)

                # Delete existing chunks with same IDs to prevent "Duplicate ID" error
                try:
                    self.collection.delete(ids=ids)
                except:
                    pass # Ignore if IDs don't exist yet

                self.collection.add(
                    documents=texts,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    ids=ids
                )
                print(f"Added batch {i//BATCH_SIZE + 1} ({len(batch)} chunks)")
                
                # Sleep to be nice to the API (configurable for Production)
                await asyncio.sleep(2) 
                
            except Exception as e:
                print(f"Error adding batch {i}: {e}")
                # Simple retry once after long delay
                await asyncio.sleep(10)
                try:
                    embeddings = self.embeddings.embed_documents(texts)
                    self.collection.add(
                        documents=texts,
                        embeddings=embeddings,
                        metadatas=metadatas,
                        ids=ids
                    )
                except Exception as e2:
                    print(f"Failed retry for batch {i}: {e2}")
                    raise e2

    async def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        # Embed query
        query_embedding = self.embeddings.embed_query(query)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        
        formatted_results = []
        if results['documents']:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if results['distances'] else None
                })
                
        return formatted_results

    async def delete_collection(self):
        self.client.delete_collection("rag_documents")

vector_db = VectorDBService()
