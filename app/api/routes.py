from fastapi import APIRouter  #type: ignore
from pydantic import BaseModel #type: ignore
from services.llama_index import ChatBotAgent

router = APIRouter()
chat_agent = ChatBotAgent()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
async def chat(request: ChatRequest):
    response = chat_agent.complete(request.message)
    return {"status_code": 200, "response": str(response)}

@router.post("/categorize")
async def categorize(request: ChatRequest):
    response = chat_agent.input_to_category(request.message)
    return {"status_code": 200, "response": response}
