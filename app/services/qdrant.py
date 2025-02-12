import os
from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain_qdrant import RetrievalMode
from typing import List
from uuid import uuid4

class QdrantService:
    # def __init__(self, collection_name: str, remote_url: str, api_key: str, google_api_key: str):
    #     self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=google_api_key)
    #     self.collection_name = collection_name
    #     self.vector_store = QdrantVectorStore.from_documents(
    #         documents=[],
    #         embedding=self.embeddings,
    #         url=remote_url,
    #         api_key=api_key,
    #         collection_name=collection_name,
    #         retrieval_mode=RetrievalMode.DENSE)

    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=self.google_api_key)
        self.collection_name = ""
        self.vector_store = QdrantVectorStore.from_documents(
            documents=[],
            embedding=self.embeddings,
            url="https://b61261e7-9348-4df5-8bde-237e2b24061d.europe-west3-0.gcp.cloud.qdrant.io:6333",
            api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwiZXhwIjoxNzQ3MDcwMjU3fQ.I8sj9MVlKF5oWEgev6fyfSwXXfDARRin_o9drRc0mmI",
            collection_name="my_documents",
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

    def hybrid_search(self, query: str, k: int = 2) -> List[Document]:
        """
        Perform hybrid search combining semantic and keyword search
        """
        semantic_results = self.similarity_search(query, k=k)
        # You can add keyword search here if needed
        return semantic_results

    def search_with_scores(self, query: str, k: int = 3) -> List[tuple[Document, float]]:
        """
        Perform similarity search and return documents with their relevance scores
        """
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            return results
        except Exception as e:
            print(f"Error in search_with_scores: {str(e)}")
            return []

    def batch_search(self, queries: List[str], k: int = 3) -> List[List[Document]]:
        """
        Perform batch similarity search for multiple queries
        """
        try:
            results = []
            for query in queries:
                docs = self.similarity_search(query, k=k)
                results.append(docs)
            return results
        except Exception as e:
            print(f"Error in batch_search: {str(e)}")
            return [[] for _ in queries]
