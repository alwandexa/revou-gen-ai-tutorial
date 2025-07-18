import streamlit as st
import requests
import json
from typing import List, Dict
import uuid
from datetime import datetime

# API configuration
API_BASE_URL = "http://localhost:8000"

def upload_document(file_content: bytes, filename: str) -> Dict:
    """Upload document via API"""
    files = {"file": (filename, file_content, "application/pdf")}
    response = requests.post(f"{API_BASE_URL}/documents/upload", files=files)
    return response.json()

def chat_with_documents(query: str, session_id: str | None = None) -> Dict:
    """Chat with document system via API"""
    url = f"{API_BASE_URL}/chat"
    data = {"query": query}
    if session_id:
        data["session_id"] = session_id
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

# Initialize session state for conversations
if "conversations" not in st.session_state:
    st.session_state.conversations = {}
if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None
if "conversation_counter" not in st.session_state:
    st.session_state.conversation_counter = 0

def create_new_conversation():
    """Create a new conversation"""
    conversation_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.session_state.conversation_counter += 1
    
    st.session_state.conversations[conversation_id] = {
        "id": conversation_id,
        "title": f"New Chat {st.session_state.conversation_counter}",
        "messages": [],
        "created_at": timestamp,
        "updated_at": timestamp
    }
    st.session_state.current_conversation_id = conversation_id
    return conversation_id

def get_current_conversation():
    """Get the current conversation"""
    if st.session_state.current_conversation_id is None:
        create_new_conversation()
    return st.session_state.conversations[st.session_state.current_conversation_id]

def update_conversation_title(conversation_id: str, title: str):
    """Update conversation title"""
    if conversation_id in st.session_state.conversations:
        st.session_state.conversations[conversation_id]["title"] = title
        st.session_state.conversations[conversation_id]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    if conversation_id in st.session_state.conversations:
        del st.session_state.conversations[conversation_id]
        if st.session_state.current_conversation_id == conversation_id:
            if st.session_state.conversations:
                st.session_state.current_conversation_id = list(st.session_state.conversations.keys())[0]
            else:
                st.session_state.current_conversation_id = None

# Sidebar for conversations
with st.sidebar:
    st.title("💬 Conversations")
    
    # New conversation button
    if st.button("➕ New Chat", use_container_width=True):
        create_new_conversation()
        st.rerun()
    
    st.divider()
    
    # Conversation list
    if st.session_state.conversations:
        for conv_id, conversation in st.session_state.conversations.items():
            # Create a unique key for each conversation
            col1, col2 = st.columns([4, 1])
            
            with col1:
                # Highlight current conversation
                if conv_id == st.session_state.current_conversation_id:
                    st.markdown(f"**{conversation['title']}**")
                else:
                    if st.button(conversation['title'], key=f"conv_{conv_id}", use_container_width=True):
                        st.session_state.current_conversation_id = conv_id
                        st.rerun()
            
            with col2:
                if st.button("🗑️", key=f"del_{conv_id}", help="Delete conversation"):
                    delete_conversation(conv_id)
                    st.rerun()
        
        st.divider()
    
    # Document upload section in sidebar
    st.subheader("📚 Upload Documents")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file", 
        type=['pdf'],
        help="Only PDF files are supported",
        key="sidebar_file_uploader"
    )
    
    if uploaded_file is not None:
        st.write(f"**File:** {uploaded_file.name}")
        st.write(f"**Size:** {uploaded_file.size} bytes")
        
        if st.button("Upload Document", key="sidebar_upload_btn"):
            try:
                with st.spinner("Processing document..."):
                    result = upload_document(uploaded_file.read(), uploaded_file.name)
                
                st.success(f"✅ Document uploaded successfully!")
                
                # Handle the response safely
                if isinstance(result, dict):
                    doc_id = result.get('id', 'Unknown')
                    chunk_count = result.get('chunk_count', 0)
                    uploaded_at = result.get('uploaded_at', 'Unknown')
                    
                    st.write(f"**Document ID:** {doc_id}")
                    st.write(f"**Chunks created:** {chunk_count}")
                    st.write(f"**Uploaded at:** {uploaded_at}")
                else:
                    st.write(f"**Response:** {result}")
                
                st.rerun()
                
            except requests.exceptions.RequestException as e:
                st.error(f"Error uploading document: {e}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")
                st.write(f"**Response type:** {type(result)}")
                st.write(f"**Response:** {result}")

# Main chat interface
st.title("📚 Document-Based Chatbot")
st.write("Upload PDF documents and chat with them using LangGraph and vector search")

# Get current conversation
current_conversation = get_current_conversation()

# Display conversation title
if current_conversation:
    col1, col2 = st.columns([3, 1])
    with col1:
        new_title = st.text_input(
            "Conversation Title:",
            value=current_conversation["title"],
            key=f"title_{current_conversation['id']}"
        )
        if new_title != current_conversation["title"]:
            update_conversation_title(current_conversation["id"], new_title or "Untitled")
    
    with col2:
        st.write(f"**Created:** {current_conversation['created_at']}")

# Display chat messages
if current_conversation and current_conversation["messages"]:
    for message in current_conversation["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message and message["sources"]:
                with st.expander("📚 Sources used"):
                    for i, source in enumerate(message["sources"], 1):
                        st.write(f"**{i}. {source}**")

# Chat input
if prompt := st.chat_input("Ask a question about your documents..."):
    # Add user message to conversation
    current_conversation["messages"].append({
        "role": "user",
        "content": prompt,
        "timestamp": datetime.now().isoformat()
    })
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Searching documents and generating response..."):
            try:
                # Use conversation ID as session ID for LangGraph
                session_id = current_conversation["id"]
                response = chat_with_documents(prompt, session_id)
                answer = response.get("answer", "Sorry, I couldn't generate a response.")
                
                # Display AI response
                st.markdown(answer)
                
                # Show search info
                search_count = response.get("search_count", 0)
                if search_count > 1:
                    st.info(f"🔍 Searched {search_count} times to find the best answer")
                
                # Add assistant message to conversation
                current_conversation["messages"].append({
                    "role": "assistant",
                    "content": answer,
                    "sources": response.get("sources", []),
                    "search_count": search_count,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Update conversation timestamp
                current_conversation["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                
            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to backend: {e}")
                current_conversation["messages"].append({
                    "role": "assistant",
                    "content": "Sorry, I'm having trouble connecting to the backend.",
                    "timestamp": datetime.now().isoformat()
                })

# Health check
try:
    health_response = requests.get(f"{API_BASE_URL}/health")
    if health_response.status_code == 200:
        st.sidebar.success("Backend: Connected")
    else:
        st.sidebar.error("Backend: Error")
except requests.exceptions.RequestException:
    st.sidebar.error("Backend: Disconnected") 