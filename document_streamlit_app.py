import streamlit as st
import requests
import json
from typing import List, Dict
import uuid

# API configuration
API_BASE_URL = "http://localhost:8000"

def upload_document(file_content: bytes, filename: str) -> Dict:
    """Upload document via API"""
    files = {"file": (filename, file_content, "application/pdf")}
    response = requests.post(f"{API_BASE_URL}/documents/upload", files=files)
    return response.json()

def chat_with_documents(query: str, session_id: str = None) -> Dict:
    """Chat with document system via API"""
    url = f"{API_BASE_URL}/chat"
    data = {"query": query, "session_id": session_id}
    response = requests.post(url, json=data)
    return response.json()

def list_documents() -> List[Dict]:
    """List all documents via API"""
    url = f"{API_BASE_URL}/documents"
    response = requests.get(url)
    return response.json()

def delete_document(document_id: str) -> Dict:
    """Delete document via API"""
    url = f"{API_BASE_URL}/documents/{document_id}"
    response = requests.delete(url)
    return response.json()

# Streamlit UI
st.title("📚 Document-Based Chatbot")
st.write("Upload PDF documents and chat with them using LangGraph and vector search")

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar for navigation
page = st.sidebar.selectbox(
    "Choose a page",
    ["Chat with Documents", "Upload Documents", "Manage Documents"]
)

if page == "Chat with Documents":
    st.header("💬 Chat with Your Documents")
    st.write("Ask questions about your uploaded documents")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message and message["sources"]:
                with st.expander("📚 Sources used"):
                    for i, source in enumerate(message["sources"], 1):
                        st.write(f"**{i}. {source}**")
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Searching documents and generating response..."):
                try:
                    response = chat_with_documents(prompt, st.session_state.session_id)
                    answer = response.get("answer", "Sorry, I couldn't generate a response.")
                    
                    # Display AI response
                    st.markdown(answer)
                    
                    # Show search info
                    search_count = response.get("search_count", 0)
                    if search_count > 1:
                        st.info(f"🔍 Searched {search_count} times to find the best answer")
                    
                    # Add assistant message to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": answer,
                        "sources": response.get("sources", [])
                    })
                    
                except requests.exceptions.RequestException as e:
                    st.error(f"Error connecting to backend: {e}")
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": "Sorry, I'm having trouble connecting to the backend."
                    })

elif page == "Upload Documents":
    st.header("📤 Upload Documents")
    st.write("Upload PDF documents to add to your knowledge base")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file", 
        type=['pdf'],
        help="Only PDF files are supported"
    )
    
    if uploaded_file is not None:
        st.write(f"**File:** {uploaded_file.name}")
        st.write(f"**Size:** {uploaded_file.size} bytes")
        
        if st.button("Upload Document"):
            try:
                with st.spinner("Processing document..."):
                    result = upload_document(uploaded_file.read(), uploaded_file.name)
                
                st.success(f"✅ Document uploaded successfully!")
                st.write(f"**Document ID:** {result['id']}")
                st.write(f"**Chunks created:** {result['chunk_count']}")
                st.write(f"**Uploaded at:** {result['uploaded_at']}")
                
            except requests.exceptions.RequestException as e:
                st.error(f"Error uploading document: {e}")

elif page == "Manage Documents":
    st.header("📋 Manage Documents")
    st.write("View and manage your uploaded documents")
    
    try:
        documents = list_documents()
        if documents:
            st.subheader(f"Total Documents: {len(documents)}")
            for doc in documents:
                with st.expander(f"📄 {doc['filename']}"):
                    st.write(f"**ID:** {doc['id']}")
                    st.write(f"**Chunks:** {doc['chunk_count']}")
                    st.write(f"**Uploaded:** {doc['uploaded_at']}")
                    
                    if st.button(f"Delete {doc['filename']}", key=doc['id']):
                        try:
                            delete_document(doc['id'])
                            st.success("Document deleted successfully!")
                            st.rerun()
                        except requests.exceptions.RequestException as e:
                            st.error(f"Error deleting document: {e}")
        else:
            st.info("No documents uploaded yet.")
    except requests.exceptions.RequestException as e:
        st.error(f"Error loading documents: {e}")

# Health check
try:
    health_response = requests.get(f"{API_BASE_URL}/health")
    if health_response.status_code == 200:
        st.sidebar.success("Backend: Connected")
    else:
        st.sidebar.error("Backend: Error")
except requests.exceptions.RequestException:
    st.sidebar.error("Backend: Disconnected")

# Session info
st.sidebar.write("---")
st.sidebar.write(f"**Session ID:** {st.session_state.session_id[:8]}...")
if st.sidebar.button("New Session"):
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.chat_history = []
    st.rerun() 