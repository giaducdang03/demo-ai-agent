import os
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.retrievers import QdrantRetriever
from langchain_google_genai import ChatGoogleGenerativeAI, HarmBlockThreshold, HarmCategory
from typing import List

load_dotenv()

class RAGService:
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        if not self.google_project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT not found in environment variables.")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            convert_system_message_to_human=True,
            handle_parsing_errors=True,
            api_key=self.google_api_key,
            temperature=0.6,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            },
        )
        self.retriever = QdrantRetriever(project_id=self.google_project_id)

    def retrieve_documents(self, query: str) -> List[Document]:
        return self.retriever.retrieve(query)

    def generate_response(self, query: str, documents: List[Document]) -> str:
        context = "\n".join([doc.page_content for doc in documents])
        messages = [
            (
                "system",
                "Bạn là một trợ lý tài chính hữu ích. Vui lòng cung cấp câu trả lời ngắn gọn và dễ hiểu bằng tiếng Việt."
            ),
            ("human", f"Context: {context}\nQuery: {query}")
        ]
        response = self.llm.invoke(messages)
        return response.content

    def handle_query(self, query: str) -> str:
        documents = self.retrieve_documents(query)
        return self.generate_response(query, documents)
