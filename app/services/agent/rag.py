from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
from app.services.retrieval.vector_db import vector_db

class RAGService:
    def __init__(self):
        # Initialize Gemini Chat Model
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest",
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.3
        )

    async def answer_question(self, query: str, history: List[Dict[str, str]] = []) -> Dict[str, Any]:
        """
        Retrieve context and answer using Gemini, considering conversation history.
        """
        # 1. Retrieve
        chunks = await vector_db.search(query, k=15)
        
        if not chunks:
            return {
                "answer": "I couldn't find any information in the uploaded documents to answer your question.",
                "sources": []
            }

        # 2. Format Context
        context_text = "\n\n".join([
            f"Source: {c['metadata']['source']} (Page {c['metadata'].get('page', 'N/A')})\nContent: {c['text']}" 
            for c in chunks
        ])

        # Format History
        history_text = ""
        for msg in history[-5:]: # Keep last 5 messages for context window efficiency
            role = "User" if msg['role'] == 'user' else "Assistant"
            history_text += f"{role}: {msg['content']}\n"

        # 3. Construct Prompt
        full_prompt = f"""You are a helpful AI assistant. Answer the question based ONLY on the following context.
If you cannot answer from the context, state that you don't have enough information.

Context:
{context_text}

Conversation History:
{history_text}

Current Question: {query}
"""

        # 4. Call LLM
        response = await self.llm.ainvoke(full_prompt)
        
        answer_text = response.content
        
        # Handle case where Gemini returns a list of content parts
        if isinstance(answer_text, list):
            final_text = ""
            for part in answer_text:
                if isinstance(part, dict) and "text" in part:
                    final_text += part["text"]
                elif isinstance(part, str):
                    final_text += part
                else:
                    final_text += str(part)
            answer_text = final_text
            
        return {
            "answer": str(answer_text),
            "sources": [c['metadata']['source'] for c in chunks]
        }

rag_service = RAGService()
