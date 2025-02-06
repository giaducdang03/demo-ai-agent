import os
import tempfile
import streamlit as st
import qdrant_client
from qdrant_client.http.exceptions import ResponseHandlingException
import time
from typing import Optional
from qdrant_client.http import models as rest

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    Settings,
)
from llama_index.core.chat_engine.simple import SimpleChatEngine
from llama_index.llms.gemini import Gemini
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.gemini import GeminiEmbedding
from dotenv import load_dotenv

load_dotenv()
print("Environment variables loaded successfully")
print(os.getenv("GOOGLE_API_KEY"))

def parse_bool(value: str):
    """Parse boolean values from environment variables"""
    return value.lower() in ("yes", "true", "t", "1")


# def check_environment_variable(variable_name):
#     """Check if environment variable is set"""
#     if variable_name not in os.environ:
#         st.error(
#             f"{variable_name} environment variable is not set. Please add it to the secrets.toml file"
#         )
#         st.stop()


def store_document(uploaded_file, storage_context):
    """Chunk the PDF & store it in Couchbase Vector Store."""
    if uploaded_file is not None:
        temp_dir = tempfile.TemporaryDirectory()
        temp_file_path = os.path.join(temp_dir.name, uploaded_file.name)

        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getvalue())

        loader = SimpleDirectoryReader(input_files=[temp_file_path])
        documents = loader.load_data()

        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
        )
        st.info(f"PDF loaded into vector store in {len(documents)} documents")
        return index
    return None


def try_connect_qdrant(max_retries: int = 3, retry_delay: int = 2) -> Optional[qdrant_client.QdrantClient]:
    """Try to connect to Qdrant with retries"""
    for attempt in range(max_retries):
        try:
            client = qdrant_client.QdrantClient(
                host="qdrant",  # Changed from localhost to qdrant service name
                port=6333
            )
            # Test connection
            client.get_collections()
            st.success("Connected to Qdrant")
            return client
        except ResponseHandlingException as e:
            if attempt == max_retries - 1:
                st.error(f"""
                {e}
                """)
                st.stop()
            else:
                time.sleep(retry_delay)
    return None

@st.cache_resource()
def get_vector_store():
    """Return the local Qdrant vector store."""
    client = try_connect_qdrant()
    if client is None:
        return None
        
    try:
        # Check if collection exists
        try:
            client.get_collection("pdf_collection")
        except Exception:
            # Create collection with proper configuration
            client.create_collection(
                collection_name="pdf_collection",
                vectors_config=rest.VectorParams(
                    size=768,  # Gemini embedding dimension
                    distance=rest.Distance.COSINE
                )
            )
            
        store = QdrantVectorStore(
            client=client, 
            collection_name="pdf_collection"
        )
        return store
    except Exception as e:
        st.error(f"Error initializing vector store: {str(e)}")
        st.stop()
        return None


if __name__ == "__main__":
    # Authorization
    if "auth" not in st.session_state:
        st.session_state.auth = False

    st.set_page_config(
        page_title="Chat with your PDF using LlamaIndex, Qdrant & OpenAI",
        page_icon="🤖",
        layout="centered",
        initial_sidebar_state="auto",
        menu_items=None,
    )

    AUTH_ENABLED = parse_bool(os.getenv("AUTH_ENABLED", "False"))

    if not AUTH_ENABLED:
        st.session_state.auth = True
    else:
        # Authorization
        if "auth" not in st.session_state:
            st.session_state.auth = False

        AUTH = os.getenv("LOGIN_PASSWORD")

        # Authentication
        user_pwd = st.text_input("Enter password", type="password")
        pwd_submit = st.button("Submit")

        if pwd_submit and user_pwd == AUTH:
            st.session_state.auth = True
        elif pwd_submit and user_pwd != AUTH:
            st.error("Incorrect password")

    if st.session_state.auth:
        # Load environment variables
        COLLECTION_NAME = os.getenv("COLLECTION_NAME", "pdf_collection")

        # Ensure that all environment variables are set

        # Connect to local Qdrant Vector Store
        vector_store = get_vector_store()

        # Build the prompt for the RAG
        template_rag = """You are a helpful bot. If you cannot answer based on the context provided, respond with a generic answer. Answer the question as truthfully as possible using the context below:
        {context}

        Question: {question}"""

        # Pure OpenAI prompt without RAG
        # template_without_rag = """You are a helpful bot. Answer the question as truthfully as possible.

        # Question: {question}"""

        # Frontend
        qdrant_logo = (
            "https://emoji.slack-edge.com/T024FJS4M/qdrant/4a361e948b15ed91.png"
        )

        st.title("Chat with PDF")
        st.markdown(
            "Answers with [Qdrant logo](https://emoji.slack-edge.com/T024FJS4M/qdrant/4a361e948b15ed91.png) are generated using *RAG* while 🤖 are generated by pure *LLM (ChatGPT)*"
        )

        # Use OpenAI as the llm & for embeddings
        llm = Gemini(temperature=0, model="models/gemini-2.0-flash-exp", api_key=os.getenv("GOOGLE_API_KEY"))
        embeddings = GeminiEmbedding()

        # Set the global settings for loading documents
        Settings.embed_model = embeddings
        Settings.chunk_size = 1500
        Settings.chunk_overlap = 150
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # Pure LLM for comparison of results
        # pure_llm = Gemini(model="models/gemini-2.0-flash-exp", api_key=os.getenv("GOOGLE_API_KEY"))
        # st.session_state.chat_llm = SimpleChatEngine.from_defaults(
        #     llm=pure_llm,
        #     system_prompt=template_without_rag,
        # )

        with st.sidebar:
            st.header("Upload your PDF")
            with st.form("upload pdf"):
                uploaded_file = st.file_uploader(
                    "Choose a PDF.",
                    help="The document will be deleted after one hour of inactivity (TTL).",
                    type="pdf",
                )
                submitted = st.form_submit_button("Upload")
                if submitted:
                    index = store_document(uploaded_file, storage_context)
                    if not index:
                        st.warning("Please upload a valid PDF")

                    # Create the chat engine with context from the uploaded data
                    st.session_state.chat_engine_rag = index.as_chat_engine(
                        chat_mode="context",
                        llm=llm,
                        system_prompt=template_rag,
                    )

            st.subheader("How does it work?")
            st.markdown(
                """
                For each question, you will get two answers:
                * one using RAG ([Qdrant logo](https://emoji.slack-edge.com/T024FJS4M/qdrant/4a361e948b15ed91.png))
                * one using pure LLM - OpenAI (🤖).
                """
            )

            st.markdown(
                "For RAG, we are using [LlamaIndex](https://www.llamaindex.ai/), [Qdrant Vector Search](https://qdrant.tech/) & [OpenAI](https://openai.com/). We fetch parts of the PDF relevant to the question using Vector search & add it as the context to the LLM. The LLM is instructed to answer based on the context from the Vector Store."
            )

            # View Code
            if st.checkbox("View Code"):
                st.write(
                    "View the code here: [Github](https://github.com/couchbase-examples/rag-demo-llama-index/blob/main/chat_with_pdf.py)"
                )

        if "messages" not in st.session_state:
            st.session_state.messages = []
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "Hi, I'm a chatbot who can chat with the PDF. How can I help you?",
                    "avatar": "🤖",
                }
            )
            st.session_state.chat_llm = None
            st.session_state.chat_engine_rag = None

        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"], avatar=message["avatar"]):
                st.markdown(message["content"])

        # React to user input
        if question := st.chat_input("Ask a question based on the PDF"):
            # Display user message in chat message container
            st.chat_message("user").markdown(question)

            # Add user message to chat history
            st.session_state.messages.append(
                {"role": "user", "content": question, "avatar": "👤"}
            )

            if st.session_state.chat_engine_rag is None:
                st.warning("Please upload and process a PDF file first.")
                st.stop()

            # Add placeholder for streaming the response
            with st.chat_message("assistant", avatar=qdrant_logo):
                message_placeholder = st.empty()

            # stream the response from the RAG
            rag_response = ""
            rag_stream_response = st.session_state.chat_engine_rag.stream_chat(question)
            for chunk in rag_stream_response.response_gen:
                rag_response += chunk
                message_placeholder.markdown(rag_response + "▌")

            message_placeholder.markdown(rag_response)
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": rag_response,
                    "avatar": qdrant_logo,
                }
            )

            # stream the response from the pure LLM

            # Add placeholder for streaming the response
            # with st.chat_message("ai", avatar="🤖"):
            #     message_placeholder_pure_llm = st.empty()

            # pure_llm_response = ""
            # pure_llm_stream_response = st.session_state.chat_llm.stream_chat(question)

            # for chunk in pure_llm_stream_response.response_gen:
                # pure_llm_response += chunk
                # message_placeholder_pure_llm.markdown(pure_llm_response + "▌")

            # message_placeholder_pure_llm.markdown(pure_llm_response)
            # st.session_state.messages.append(
            #     {
            #         "role": "assistant",
            #         "content": pure_llm_response,
            #         "avatar": "🤖",
            #     }
            # )
