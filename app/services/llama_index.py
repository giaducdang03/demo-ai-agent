import json
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    HarmBlockThreshold,
    HarmCategory,
)
from services.qdrant import QdrantService

load_dotenv()
class SpendingCategory(BaseModel):
    """Spending category classification."""
    category: str = Field(
        description="Spending category name",
        enum=["food", "housing", "utilities", "transportation", 
                "entertainment", "healthcare", "education", "shopping", "other"]
    )
    amount: float = Field(description="Amount in VND")

class ChatBotAgent:
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_project_id = os.getenv("GOOGLE_CLOUD_PROJECT") # Get project ID from env
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        if not self.google_project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT not found in environment variables.")
        else:
            print("GOOGLE_API_KEY found in environment variables.")
        self.llm = None
        self.qdrant_service = QdrantService()

    def init_llm(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp",
            convert_system_message_to_human=True,
            handle_parsing_errors=True,
            api_key=self.google_api_key,
            temperature=0.6,
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            },
        )

    def complete(self, query, rag: bool = False):
        if not self.llm:
            self.init_llm()
            
        system_prompt = "Bạn là một trợ lý tài chính hữu ích. Vui lòng cung cấp câu trả lời ngắn gọn và dễ hiểu bằng tiếng Việt."
        
        if rag:
            # Retrieve relevant documents
            relevant_docs = self.qdrant_service.query(query, k=2)
            context = "\n".join([doc.page_content for doc in relevant_docs])
            # Combine system prompt, context and query
            full_prompt = f"{system_prompt}\nContext:\n{context}\nQuery: {query}"
        else:
            full_prompt = f"{system_prompt}\nQuery: {query}"
        
        # Use a single human message
        messages = [("human", full_prompt)]
        response = self.llm.invoke(messages)
        return response.content

    def rag_generate_response(self, query: str, context_docs: list) -> str:
        """Generate a response using RAG with specific context documents"""
        if not self.llm:
            self.init_llm()
            
        context = "\n".join([doc.page_content for doc in context_docs])
        system_prompt = (
            "Bạn là một trợ lý tài chính hữu ích. Sử dụng context được cung cấp để trả lời câu hỏi. "
            "Nếu context không đủ thông tin, hãy nói rằng bạn không có đủ thông tin để trả lời."
        )
        
        # Combine everything into a single human message
        full_prompt = f"{system_prompt}\nContext:\n{context}\nQuery: {query}"
        messages = [("human", full_prompt)]
        
        response = self.llm.invoke(messages)
        return response.content

    def rag_search(self, query: str, k: int = 2) -> list:
        """
        Perform RAG search to get relevant documents
        """
        return self.qdrant_service.query(query, k=k)

    def add_to_knowledge_base(self, documents: list) -> None:
        """
        Add documents to the knowledge base
        """
        self.qdrant_service.add_documents(documents)

    def input_to_category(self, query: str) -> SpendingCategory:
        SYSTEM_PROMPT = """
        You are a spending categorization assistant. Analyze the given text and categorize it into one of the following categories:
        - food
        - housing
        - utilities (water, electric)
        - transportation (fuel, maintenance)
        - entertainment
        - healthcare
        - education
        - shopping
        - other
        """
        
        try:
            if not self.llm:
                self.init_llm()
            
            structured_llm = self.llm.with_structured_output(SpendingCategory)
            result = structured_llm.invoke(f"{SYSTEM_PROMPT}\nText to categorize: {query}")
            return json.loads(result.model_dump_json())
                
        except Exception as e:
            return SpendingCategory(category="other", amount=0.0)

    def rag_query(self, query: str, k: int = 3, threshold: float = 0.7) -> dict:
        """
        Enhanced RAG query with relevance scoring and filtering
        """
        try:
            # Get relevant documents with scores
            relevant_docs = self.qdrant_service.search_with_scores(query, k=k)
            
            # Filter documents based on relevance threshold
            filtered_docs = [doc for doc, score in relevant_docs if score >= threshold]
            
            if not filtered_docs:
                return {
                    "response": "I don't have enough relevant information to answer your question accurately.",
                    "sources": [],
                    "has_relevant_context": False
                }
            
            # Generate response using filtered documents
            response = self.rag_generate_response(query, filtered_docs)
            
            return {
                "response": response,
                "sources": [{"content": doc.page_content, "metadata": doc.metadata} for doc in filtered_docs],
                "has_relevant_context": True
            }
            
        except Exception as e:
            print(f"Error in RAG query: {str(e)}")
            return {
                "response": "An error occurred while processing your query.",
                "sources": [],
                "has_relevant_context": False
            }
