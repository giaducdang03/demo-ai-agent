import json
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    HarmBlockThreshold,
    HarmCategory,
)

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
            
        messages = [
            (
                "system",
                "Bạn là một trợ lý tài chính hữu ích. Vui lòng cung cấp câu trả lời ngắn gọn và dễ hiểu bằng tiếng Việt."
            ),
            ("human", query)
        ]
        
        # If RAG integration is required, implement the additional logic here.
        response = self.llm.invoke(messages)
        return response.content
    
  

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
