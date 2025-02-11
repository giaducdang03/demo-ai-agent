from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain_qdrant import RetrievalMode
from typing import List
from uuid import uuid4

class QdrantService:
    def __init__(self, collection_name: str, remote_url: str, api_key: str, google_api_key: str):
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=google_api_key)
        self.collection_name = collection_name
        self.vector_store = QdrantVectorStore.from_documents(
            documents=[],
            embedding=self.embeddings,
            url=remote_url,
            api_key=api_key,
            collection_name=collection_name,
            retrieval_mode=RetrievalMode.DENSE)

    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the vector store"""
        uuids = [str(uuid4()) for _ in range(len(documents))]
        self.vector_store.add_documents(documents=documents, ids=uuids)

    def similarity_search(self, query: str, k: int = 2) -> List[Document]:
        """Perform similarity search"""
        return self.vector_store.similarity_search(query, k=k)
    
    def delete_documents(self, document_ids: List[str]) -> None:
        """Delete documents from the vector store"""
        self.vector_store.delete(ids=document_ids)

    @staticmethod
    def create_document(page_content: str, source: str) -> Document:
        """Create a document with metadata"""
        return Document(
            page_content=page_content,
            metadata={"source": source}
        )
    
    def query(self, query: str, k: int = 2) -> List[Document]:
        """Query the vector store"""
        retriever = self.vector_store.as_retriever(search_type="mmr", search_kwargs={"k": k})
        return retriever.invoke(query)