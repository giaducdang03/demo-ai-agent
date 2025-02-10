import json
import os
from dotenv import load_dotenv #type: ignore
from llama_index.llms.gemini import Gemini #type: ignore
from utils.helper import parse_json_from_response, logger

load_dotenv()

class ChatBotAgent:
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        else:
            print("GOOGLE_API_KEY found in environment variables.")
        self.llm = None

    def init_llm(self):
        self.llm = Gemini(
            google_api_key=self.google_api_key,
            model="models/gemini-2.0-flash-exp",
            temperature=1,
        )

    def complete(self, query, rag: bool = False):
        SYSTEM_PROMPT = """Bạn là một trợ lý hữu ích. 
        Vui lòng cung cấp câu trả lời ngắn gọn và dễ hiểu bằng tiếng Việt."""
        if not self.llm:
            self.init_llm()
        # If RAG integration is required, implement the additional logic here.
        full_prompt = f"{SYSTEM_PROMPT}\nUser query: {query}"
        response = self.llm.complete(full_prompt)
        return response.text
    
    def input_to_category(self, query: str) -> dict:
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
        
    
        
        Return your response in JSON format with exactly this structure:
        {
            "category": "category_name",
            "ammount": ammount_in_vnd
        }

        Example:
        {
            "category": "food",
            "ammount": 100000
        }

        """
        
        try:
            if not self.llm:
                self.init_llm()
            
            full_prompt = f"{SYSTEM_PROMPT}\nText to categorize: {query}"
            response = self.llm.complete(full_prompt)
            logger.debug(f"Response from model: {response.text}")
            # Parse the response to get JSON
            category_data = parse_json_from_response(response.text)
            
            return json.loads(category_data)
            # if category_data and "category" in category_data:
            #     logger.debug(f"Successfully categorized: {category_data}")
            #     return category_data["category"]
            # else:
            #     logger.error("Failed to get valid category from model response")
            #     return "other"
                
        except Exception as e:
            logger.error(f"Error in categorization: {str(e)}")
            return "other"