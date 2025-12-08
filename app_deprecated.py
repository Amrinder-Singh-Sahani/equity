import streamlit as st
from utils.text_extractors import extract_text_from_pdf, extract_text_from_csv, extract_text_from_txt, extract_text_from_url
from utils.gemini_api import ask_question_with_gemini
from utils.theme_css import get_custom_css

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="EquityTool: Research Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SESSION STATE ---
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "content_loaded" not in st.session_state:
    st.session_state.content_loaded = False
if "total_content" not in st.session_state:
    st.session_state.total_content = ""
if "question" not in st.session_state:
    st.session_state.question = ""

# --- APPLY CSS ---
st.markdown(get_custom_css(st.session_state.theme), unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div class="custom-header">
    <h1>📊 EquityTool: Research Assistant</h1>
    <p>Upload documents • Analyze web content • Get insights</p>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🎨 Theme")
    selected_theme = st.radio(
        "Choose theme",
        ["Light", "Dark"],
        index=["Light", "Dark"].index(st.session_state.theme),
        key="theme_selector",
        horizontal=True,
        label_visibility="collapsed"
    )
    if selected_theme != st.session_state.theme:
        st.session_state.theme = selected_theme
        st.rerun()

    st.markdown("---")
    st.markdown("### 📁 Content Sources")

    resource_type = st.selectbox(
        "Choose resource type:",
        ["📄 Upload Document", "🌐 Add Web Article", "📝 Enter Text Directly"],
        label_visibility="collapsed"
    )

    content_text = ""
    if resource_type == "📄 Upload Document":
        uploaded_file = st.file_uploader("Upload PDF/CSV/TXT", type=["pdf", "csv", "txt"])
        if uploaded_file and st.button("📊 Process Document", type="primary"):
            if uploaded_file.type == "application/pdf":
                content_text = extract_text_from_pdf(uploaded_file)
                st.session_state.content_source = f"📄 PDF: {uploaded_file.name}"
            elif uploaded_file.type == "text/csv":
                content_text = extract_text_from_csv(uploaded_file)
                st.session_state.content_source = f"📊 CSV: {uploaded_file.name}"
            elif uploaded_file.type == "text/plain":
                content_text = extract_text_from_txt(uploaded_file)
                st.session_state.content_source = f"📝 TXT: {uploaded_file.name}"

    elif resource_type == "🌐 Add Web Article":
        urls = [st.text_input(f"URL {i+1}", key=f"url_{i}") for i in range(3)]
        if any(urls) and st.button("🌐 Fetch All Articles", type="primary"):
            content_text = ""
            progress = st.progress(0, text="Fetching...")
            for i, url in enumerate(urls):
                if url.strip():
                    content_text += f"\n\n--- Article {i+1} from {url} ---\n\n" + extract_text_from_url(url)
                    progress.progress((i + 1) / len(urls))
            st.session_state.content_source = f"🌐 {len(urls)} Web Articles"

    elif resource_type == "📝 Enter Text Directly":
        direct_text = st.text_area("Enter your text", height=200)
        if direct_text and st.button("📝 Use Text", type="primary"):
            content_text = direct_text
            st.session_state.content_source = f"📝 Direct input ({len(direct_text)} chars)"

    if content_text.strip():
        st.session_state.total_content = content_text
        st.session_state.content_loaded = True
        st.success("Content loaded successfully!")
        st.session_state.messages.append({
            "role": "system",
            "content": f"✅ Content loaded from: {st.session_state.content_source}"
        })
        st.rerun()

# --- MAIN CHAT UI ---
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        st.markdown(f'<div class="chat-message assistant-message"><strong>EquityTool:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-message system-message">ℹ️ {msg["content"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- ASK QUESTION ---
question = st.text_input("Ask a question:", key="question")
if st.button("Ask"):
    if not st.session_state.content_loaded:
        st.warning("⚠️ Please load some content first!")
    else:
        st.session_state.messages.append({"role": "user", "content": question})
        answer = ask_question_with_gemini(st.session_state.total_content, question)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()
