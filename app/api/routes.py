from fastapi import APIRouter, HTTPException  #type: ignore
from pydantic import BaseModel, Field, confloat #type: ignore
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

class RAGQueryRequest(BaseModel):
    query: str
    k: int = Field(default=3, ge=1, le=10, description="Number of documents to retrieve")
    threshold: confloat(ge=0.0, le=1.0) = Field(
        default=0.7, 
        description="Relevance score threshold"
    )

@router.post("/chat")
async def chat(request: ChatRequest):
    response = chat_agent.complete(request.message, rag=True)
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

@router.post("/rag/query")
async def rag_query(request: RAGQueryRequest):
    """
    Enhanced RAG query with relevance scoring and source tracking
    """
    try:
        result = chat_agent.rag_query(
            query=request.query,
            k=request.k,
            threshold=request.threshold
        )
        return {
            "status_code": 200,
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rag/search")
async def rag_search(request: ChatRequest):
    """
    Search for relevant documents without generating a response
    """
    try:
        documents = chat_agent.rag_search(request.message)
        return {
            "status_code": 200,
            "documents": [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in documents
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rag/generate")
async def rag_generate(request: RAGQueryRequest):
    """
    Generate a response using specific context documents
    """
    try:
        # First retrieve relevant documents
        context_docs = chat_agent.rag_search(request.query, k=request.k)
        
        # Generate response using these documents
        response = chat_agent.rag_generate_response(request.query, context_docs)
        
        return {
            "status_code": 200,
            "response": response,
            "context_used": [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in context_docs
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
