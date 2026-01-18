from fastapi import APIRouter
from app.models.chat import ChatRequest, ChatResponse
from app.services.agent.rag import rag_service

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = await rag_service.answer_question(request.message)
        return ChatResponse(
            answer=response["answer"],
            sources=list(set(response["sources"])) # Deduplicate sources
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Return a polite error message to the AI instead of crashing
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))
