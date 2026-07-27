"""
streamlit_app.py — Streamlit UI for DriveMind RAG Assistant.
Interacts with the FastAPI backend via HTTP endpoints.
"""

import streamlit as st
import requests
import time

# Page config
st.set_page_config(
    page_title="DriveMind RAG",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Custom Styling (Dark Library Theme)
st.markdown(
    """
    <style>
    /* Dark Theme Customization */
    .stApp {
        background-color: #0F1115;
        color: #EAEAEA;
    }
    
    /* Header styling */
    h1 {
        font-family: 'Fraunces', serif;
        color: #D9A441;
        font-weight: 700;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #181B21;
        border-right: 1px solid #2A2E36;
    }
    
    /* Citation chip container */
    .citation-chip {
        display: inline-block;
        background-color: #2A2E36;
        color: #D9A441;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.85rem;
        margin-right: 6px;
        margin-top: 6px;
        text-decoration: none;
        border: 1px solid #3A3F4B;
        transition: all 0.2s ease;
    }
    .citation-chip:hover {
        background-color: #D9A441;
        color: #0F1115;
    }
    
    /* Source box */
    .source-box {
        background-color: #181B21;
        border-left: 3px solid #D9A441;
        padding: 10px 14px;
        border-radius: 4px;
        margin-top: 10px;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar Config
st.sidebar.title("⚙️ Settings")

api_url = st.sidebar.text_input(
    "API Endpoint URL",
    value="https://drivemind-rag-1.onrender.com",
    help="Target FastAPI backend URL",
).rstrip("/")

# Health Check
st.sidebar.markdown("---")
st.sidebar.subheader("System Status")

if st.sidebar.button("🔍 Check Backend Health"):
    try:
        res = requests.get(f"{api_url}/health", timeout=10)
        if res.status_code == 200:
            st.sidebar.success(f"Online ({res.json().get('status')})")
        else:
            st.sidebar.error(f"Error HTTP {res.status_code}")
    except Exception as e:
        st.sidebar.error(f"Connection Failed: {e}")

# Ingestion Trigger
st.sidebar.markdown("---")
st.sidebar.subheader("Library Ingestion")
st.sidebar.caption("Sync and index latest documents from Google Drive")

if st.sidebar.button("⚡ Sync Google Drive"):
    with st.spinner("Triggering background sync..."):
        try:
            res = requests.post(f"{api_url}/ingest", json={}, timeout=10)
            if res.status_code == 200:
                st.sidebar.success("Ingestion started! Check backend logs for progress.")
            else:
                st.sidebar.error(f"Failed to start ingestion (HTTP {res.status_code})")
        except Exception as e:
            st.sidebar.error(f"Request Error: {e}")

# Main Chat Interface
st.title("📚 DriveMind RAG")
st.caption("Ask grounded questions about your personal document library in Google Drive")

# Render Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Render source citations if available
        if msg.get("sources"):
            st.markdown("#### 📖 Sources Cited:")
            for s in msg["sources"]:
                file_name = s.get("source_file", "Document")
                drive_link = s.get("drive_link", "#")
                snippet = s.get("text_snippet", "")
                
                with st.expander(f"📄 {file_name}"):
                    st.write(f"**Snippet:** {snippet}")
                    if drive_link and drive_link != "#":
                        st.markdown(f"[🔗 Open in Google Drive]({drive_link})")

# User Input
if prompt := st.chat_input("Ask a question about your books, papers, or notes..."):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call Backend Chat Endpoint
    with st.chat_message("assistant"):
        with st.spinner("Searching document library and composing answer..."):
            try:
                response = requests.post(
                    f"{api_url}/chat",
                    json={"message": prompt},
                    timeout=120,
                )
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No answer generated.")
                    sources = data.get("sources", [])
                    
                    st.markdown(answer)
                    
                    if sources:
                        st.markdown("#### 📖 Sources Cited:")
                        for s in sources:
                            file_name = s.get("source_file", "Document")
                            drive_link = s.get("drive_link", "#")
                            snippet = s.get("text_snippet", "")
                            
                            with st.expander(f"📄 {file_name}"):
                                st.write(f"**Snippet:** {snippet}")
                                if drive_link and drive_link != "#":
                                    st.markdown(f"[🔗 Open in Google Drive]({drive_link})")
                                    
                    # Save assistant response to state
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "sources": sources,
                        }
                    )
                else:
                    error_msg = f"API Error (HTTP {response.status_code}): {response.text}"
                    st.error(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg, "sources": []}
                    )
            except Exception as e:
                error_msg = f"Connection failed: {e}"
                st.error(error_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_msg, "sources": []}
                )
