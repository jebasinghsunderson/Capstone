import os
import shutil
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from agent import ask_agent
from rag import create_vector_database

# Page Configuration
st.set_page_config(
    page_title="AI Research Workstation",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Dual-Pane Glassmorphism Layout & Modern Aesthetics
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Main background with deep dark gradient */
    .stApp {
        background: radial-gradient(circle at 10% 20%, #151928 0%, #0F172A 45%, #080B11 100%);
        color: #F8FAFC;
    }

    /* Top Navigation Header */
    .app-header {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 16px 28px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    }

    .app-logo {
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366F1 0%, #A855F7 50%, #EC4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.1);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.25);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        background-color: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 10px #10B981;
    }

    /* Dashboard Cards */
    .dashboard-card {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }

    .card-title {
        font-size: 0.95rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #818CF8;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Custom Input Fields */
    div[data-baseweb="input"] {
        border-radius: 10px !important;
        background-color: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    /* Styling Primary & Secondary Buttons */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        color: #FFFFFF;
        border: none;
        border-radius: 10px;
        padding: 10px 18px;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.25s ease;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.3);
    }

    div.stButton > button:hover {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5);
        transform: translateY(-1px);
    }

    /* Quick Prompt Chips */
    .prompt-chip-btn button {
        background: rgba(30, 41, 59, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #CBD5E1 !important;
        box-shadow: none !important;
        text-align: left !important;
        padding: 8px 14px !important;
        border-radius: 8px !important;
        font-size: 0.85rem !important;
    }
    
    .prompt-chip-btn button:hover {
        background: rgba(99, 102, 241, 0.2) !important;
        border-color: rgba(99, 102, 241, 0.4) !important;
        color: #FFFFFF !important;
    }

    /* Chat Area Styling */
    .chat-container {
        background: rgba(15, 23, 42, 0.6);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 24px;
        min-height: 520px;
    }

    div[data-testid="stChatMessage"] {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 14px;
    }

    div[data-testid="stChatMessage"][data-testimonial="user"] {
        background: rgba(49, 46, 129, 0.35);
        border: 1px solid rgba(99, 102, 241, 0.25);
    }

    /* Integration Badges */
    .integration-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 6px 12px;
        font-size: 0.8rem;
        color: #E2E8F0;
        margin-right: 6px;
        margin-bottom: 8px;
    }
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# Initialize Session Messages & Active Prompt Trigger
if "messages" not in st.session_state:
    st.session_state.messages = []

if "quick_prompt" not in st.session_state:
    st.session_state.quick_prompt = None

# Top App Navigation Header
st.markdown("""
    <div class="app-header">
        <div class="app-logo">
            <span>⚡</span> AI Research Workstation
        </div>
        <div style="display: flex; align-items: center; gap: 16px;">
            <div style="font-size: 0.85rem; color: #94A3B8;">Multi-Tool RAG & Agent Console</div>
            <div class="status-badge">
                <div class="status-dot"></div>
                Agent Connected
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Dual-Pane Workstation Layout (1 : 2.2 ratio)
col_control, col_chat = st.columns([1, 2.2], gap="large")

# ==================== LEFT PANE: CONTROL CENTER ====================
with col_control:
    # 1. Session Manager Card
    st.markdown("""
        <div class="dashboard-card">
            <div class="card-title">⚙️ Session & Memory</div>
    """, unsafe_allow_html=True)
    
    user_name = st.text_input(
        "Thread Session ID",
        value="jebasingh",
        help="Unique identifier for maintaining agent conversation memory"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # 2. Knowledge Base Manager Card
    st.markdown("""
        <div class="dashboard-card">
            <div class="card-title">📚 Knowledge Base Builder</div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Upload Reference PDF",
        type=["pdf"],
        help="Upload PDF to index into Chroma Vector DB for RAG retrieval"
    )
    
    build_button = st.button("⚡ Index PDF to Vector DB")
    
    if build_button:
        if uploaded_file is not None:
            os.makedirs("uploads", exist_ok=True)
            file_path = os.path.join("uploads", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())
            
            with st.spinner("Processing & indexing PDF chunks..."):
                create_vector_database(file_path)
            st.success("✅ Knowledge Base Created!")
        else:
            st.warning("⚠️ Please select a PDF file first.")
            
    st.markdown("</div>", unsafe_allow_html=True)

    # 3. Quick Action Recommendations Card
    st.markdown("""
        <div class="dashboard-card">
            <div class="card-title">💡 Quick Action Prompts</div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='prompt-chip-btn'>", unsafe_allow_html=True)
    if st.button("🔍 Summarize indexed PDF document"):
        st.session_state.quick_prompt = "Summarize the key findings from the uploaded PDF document."
    if st.button("📧 Check recent unread emails"):
        st.session_state.quick_prompt = "Check my recent unread Gmail messages."
    if st.button("📁 Search files in Google Drive"):
        st.session_state.quick_prompt = "List recent files available in my Google Drive."
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

    # 4. Engine & Integrations Status Card
    st.markdown("""
        <div class="dashboard-card">
            <div class="card-title">🔌 Active Integrations</div>
            <div>
                <span class="integration-badge">🤖 LangChain Agent</span>
                <span class="integration-badge">⚡ Groq LLM</span>
                <span class="integration-badge">🔍 ChromaDB RAG</span>
                <span class="integration-badge">✉️ Gmail API</span>
                <span class="integration-badge">📂 Google Drive API</span>
            </div>
        </div>
    """, unsafe_allow_html=True)


# ==================== RIGHT PANE: AGENT CHAT CONSOLE ====================
with col_chat:
    # Chat Console Header Bar with Clear Action
    header_col1, header_col2 = st.columns([3, 1])
    with header_col1:
        st.markdown("<h3 style='margin:0; color:#F8FAFC; font-weight:700;'>💬 Research Chat Console</h3>", unsafe_allow_html=True)
    with header_col2:
        if st.button("🗑️ Clear History"):
            st.session_state.messages = []
            st.rerun()

    st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

    # Empty State Graphic when chat is empty
    if not st.session_state.messages:
        st.markdown("""
            <div style='background: rgba(30, 41, 59, 0.3); border: 1px dashed rgba(255, 255, 255, 0.1); border-radius: 16px; padding: 40px 24px; text-align: center; margin-bottom: 24px;'>
                <div style='font-size: 3rem; margin-bottom: 12px;'>⚡</div>
                <h3 style='color: #E2E8F0; margin-bottom: 8px;'>AI Research Assistant Ready</h3>
                <p style='color: #94A3B8; font-size: 0.9rem; max-width: 540px; margin: 0 auto 20px auto;'>
                    Type a message below, select a Quick Action prompt from the left panel, or upload a PDF document to query vector knowledge embeddings.
                </p>
            </div>
        """, unsafe_allow_html=True)

    # Render Messages
    for message in st.session_state.messages:
        avatar = "👤" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # Determine input prompt (either from quick prompt click or chat input box)
    user_input = st.chat_input("Ask Anything...")
    
    prompt_to_process = None
    if user_input:
        prompt_to_process = user_input
    elif st.session_state.quick_prompt:
        prompt_to_process = st.session_state.quick_prompt
        st.session_state.quick_prompt = None

    # Handle Processing
    if prompt_to_process:
        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt_to_process
            }
        )
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt_to_process)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                response = ask_agent(prompt_to_process, user_name)
                st.markdown(response)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response
            }
        )
        st.rerun()