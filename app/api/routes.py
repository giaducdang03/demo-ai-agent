from fastapi import APIRouter, HTTPException  #type: ignore
from pydantic import BaseModel, Field #type: ignore
from services.qdrant import QdrantService
from services.llama_index import ChatBotAgent
from typing import Dict, Any, List
from langchain_core.documents import Document

router = APIRouter()
chat_agent = ChatBotAgent()
qdrant_service = QdrantService()

class ChatRequest(BaseModel):
    message: str

class DocumentDetail(BaseModel):
    page_content: str
    metadata: Dict[str, Any] = {}

class DocumentRequest(BaseModel):
    documents: List[DocumentDetail] = Field(..., description="List of documents")

@router.post("/chat")
async def chat(request: ChatRequest):
    response = chat_agent.complete(request.message)
    return {"status_code": 200, "response": str(response)}

@router.post("/categorize")
async def categorize(request: ChatRequest):
    response = chat_agent.input_to_category(request.message)
    return {"status_code": 200, "response": response}

@router.post("/documents")
async def handle_documents(request: DocumentRequest):
    try:
        documents = request.documents
        langchain_documents = []

        for doc in documents:
            page_content = doc.page_content
            metadata = doc.metadata
            langchain_document = Document(page_content=page_content, metadata=metadata)
            langchain_documents.append(langchain_document)

        # Add the documents to Qdrant
        qdrant_service.add_documents(langchain_documents)

        print(f"Received and processed {len(langchain_documents)} documents")

        return {"status_code": 200, "message": "Documents processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
