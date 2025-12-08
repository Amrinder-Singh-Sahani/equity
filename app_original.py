import streamlit as st
import pymysql
import bcrypt

import fitz  # PyMuPDF
import pandas as pd
import google.generativeai as genai
from langdetect import detect
import requests
from bs4 import BeautifulSoup
import time




def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",         # default in XAMPP
        password="",           # keep empty unless you’ve set one
        database="equitytool_db",
        cursorclass=pymysql.cursors.DictCursor
    )

def create_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')

    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_pw))
        conn.commit()
        return True
    except pymysql.err.IntegrityError:
        st.error("Username already exists. Please choose another.")
        return False
    except Exception as e:
        st.error(f"Error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
    record = cursor.fetchone()
    cursor.close()
    conn.close()

    if record and bcrypt.checkpw(password.encode(), record["password"].encode()):
        return True
    return False

if "page" not in st.session_state:
    st.session_state.page = "login"

if "username" not in st.session_state:
    st.session_state.username = ""


def signup_page():
    st.title("📝 Create Account")

    username = st.text_input("Choose Username")
    password = st.text_input("Choose Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Sign Up ✅"):
        if password != confirm_password:
            st.error("❌ Passwords do not match")
        elif create_user(username, password):
            st.success("✅ Account created! Please login")
            st.session_state.page = "login"
            st.rerun()

    st.write("Already have an account?")
    if st.button("Go to Login 🔙"):
        st.session_state.page = "login"
        st.rerun()


def login_page():
    st.title("🔐 Login to EquityTool")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login ✅"):
        if login_user(username, password):
            st.session_state.username = username
            st.session_state.page = "home"
            st.rerun()
        else:
            st.error("❌ Incorrect username or password")

    st.write("Don't have an account?")
    if st.button("Create Account 📝"):
        st.session_state.page = "signup"
        st.rerun()




st.set_page_config(
    page_title="EquityTool: Research Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# STOP loading main UI unless logged in
if st.session_state.page == "login":
    login_page()
    st.stop()
elif st.session_state.page == "signup":
    signup_page()
    st.stop()




# ------------------ CONFIG ------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
# Use the model you prefer
model = genai.GenerativeModel("gemini-2.5-flash")

# Initialize theme in session state
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

# ------------------ THEME-BASED CSS ------------------
def get_custom_css(theme="Light"):
    # Define your new color palette
    color1 = "#9CF6FB" # Lightest Blue
    color2 = "#E1FCFD" # Very Light Blue (almost white)
    color3 = "#394F8A" # Darker Blue
    color4 = "#4A5FC1" # Mid Blue
    color5 = "#E5B9A8" # Light Peach
    color6 = "#EAD6CD" # Light Tan

    if theme == "Light":
        main_bg = color2 # Very Light Blue
        content_bg = "#ffffff"
        card_bg = color6 # Light Tan
        text_color = color3 # Darker Blue
        border_color = color1 # Lightest Blue
        input_bg = "#ffffff"
        input_text = color3 # Darker Blue
        sidebar_bg = f"linear-gradient(180deg, {color2} 0%, {color1} 100%)"
        user_msg_bg = color1 # Lightest Blue
        assistant_msg_bg = color4 # Mid Blue
        assistant_msg_text = "#ffffff"
        system_msg_bg = f"rgba({int(color4[1:3], 16)}, {int(color4[3:5], 16)}, {int(color4[5:7], 16)}, 0.08)" # Mid Blue w/ opacity
        system_msg_text = color3 # Darker Blue
        placeholder_color = "#6b7280" # Default grey, or could use a desaturated palette color
        header_grad_start = color3 # Darker Blue
        header_grad_end = color4 # Mid Blue
        button_grad_start = color3
        button_grad_end = color4
        button_hover_start = color4
        button_hover_end = color3
        shadow_color = f"rgba({int(color3[1:3], 16)}, {int(color3[3:5], 16)}, {int(color3[5:7], 16)}, 0.25)"
        dashed_border = color4 # Mid Blue
        uploader_bg = f"rgba({int(color4[1:3], 16)}, {int(color4[3:5], 16)}, {int(color4[5:7], 16)}, 0.05)"
        uploader_hover_bg = f"rgba({int(color4[1:3], 16)}, {int(color4[3:5], 16)}, {int(color4[5:7], 16)}, 0.1)"
    else: # Dark theme
        main_bg = "#111827" # A darker base, keeping with the original dark mode feel
        content_bg = "#1f293b" # Dark grey
        card_bg = color3 # Darker Blue
        text_color = "#e2e8f0" # Light grey for readability
        border_color = color4 # Mid Blue
        input_bg = "#1f293b"
        input_text = "#e2e8f0"
        sidebar_bg = "linear-gradient(180deg, #1f293b 0%, #111827 100%)"
        user_msg_bg = color4 # Mid Blue
        assistant_msg_bg = "#1f293b" # Dark grey
        assistant_msg_text = "#e2e8f0"
        system_msg_bg = f"rgba({int(color1[1:3], 16)}, {int(color1[3:5], 16)}, {int(color1[5:7], 16)}, 0.2)" # Lightest Blue w/ opacity
        system_msg_text = color1 # Lightest Blue
        placeholder_color = "#94a3b8" # Lighter grey
        header_grad_start = color3 # Darker Blue
        header_grad_end = color4 # Mid Blue
        button_grad_start = color3
        button_grad_end = color4
        button_hover_start = color4
        button_hover_end = color3
        shadow_color = f"rgba({int(color3[1:3], 16)}, {int(color3[3:5], 16)}, {int(color3[5:7], 16)}, 0.25)"
        dashed_border = color1 # Lightest Blue
        uploader_bg = f"rgba({int(color1[1:3], 16)}, {int(color1[3:5], 16)}, {int(color1[5:7], 16)}, 0.05)"
        uploader_hover_bg = f"rgba({int(color1[1:3], 16)}, {int(color1[3:5], 16)}, {int(color1[5:7], 16)}, 0.1)"

    # Add a keyframe animation for messages popping in
    return f"""
    <style>
    @keyframes popIn {{
        0% {{
            opacity: 0;
            transform: translateY(10px);
        }}
        100% {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}

    /* --- Base Theme --- */
    body {{
        background-color: {main_bg};
        color: {text_color};
    }}
    .stApp {{
        background-color: {main_bg};
    }}
    /* Main content area */
    .st-emotion-cache-1y4p8pa {{ 
        background-color: {content_bg};
    }}
    /* Sidebar */
    .st-emotion-cache-uf99v8 {{ 
        background: {sidebar_bg};
        border-right: 1px solid {border_color};
    }}
    .stTextInput input, .stTextArea textarea {{
        background-color: {input_bg};
        color: {input_text};
        border: 1px solid {border_color};
    }}
    ::placeholder {{
        color: {placeholder_color} !important;
    }}
    .stRadio label span {{
        color: {text_color} !important;
    }}
    .stSelectbox > div {{
        border: 1px solid {border_color};
        background-color: {input_bg};
    }}
    
    /* --- Custom Header & Buttons --- */
    .custom-header {{
        background: linear-gradient(135deg, {header_grad_start} 0%, {header_grad_end} 100%);
        padding: 1.5rem 0;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 12px {shadow_color};
        transition: all 0.3s ease;
    }}
    .custom-header:hover {{
        transform: scale(1.01);
        box-shadow: 0 6px 16px {shadow_color};
    }}

    .stButton > button {{
        width: 100%;
        border-radius: 10px;
        border: none;
        background: linear-gradient(135deg, {button_grad_start} 0%, {button_grad_end} 100%);
        color: white;
        padding: 0.8rem 1.2rem;
        font-size: 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 6px {shadow_color};
    }}
    .stButton > button:hover {{
        transform: translateY(-2px);
        background: linear-gradient(135deg, {button_hover_start} 0%, {button_hover_end} 100%);
        box-shadow: 0 4px 12px {shadow_color};
    }}

    .stFileUploader {{
        border: 2px dashed {dashed_border};
        border-radius: 12px;
        padding: 2rem;
        background: {uploader_bg};
        transition: background 0.3s ease;
    }}
    .stFileUploader:hover {{
        background: {uploader_hover_bg};
    }}

    .stats-card {{
        background: {card_bg};
        border: 1px solid {border_color};
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }}
    .stats-card:hover {{
         transform: translateY(-3px);
         box-shadow: 0 4px 12px {shadow_color};
    }}
    .stats-card h3 {{
        color: {system_msg_text}; /* Using a primary blue from the palette */
        font-size: 2rem;
        margin: 0;
    }}
     .stats-card p {{
        color: {text_color};
        font-size: 0.9rem;
        margin: 0;
    }}
    
    /* --- Chat Message Styling --- */
    .chat-container {{
        background-color: {content_bg};
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid {border_color};
        margin-bottom: 1rem;
    }}

    .chat-message {{
        display: flex;
        margin: 0.5rem 0;
        padding: 1rem 1.25rem;
        border-radius: 15px;
        max-width: 75%;
        word-wrap: break-word;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        animation: popIn 0.3s ease forwards;
        transition: all 0.3s ease;
    }}

    .user-message {{
        background: {user_msg_bg};
        color: {text_color};
        margin-left: auto;
        border-bottom-right-radius: 0;
    }}

    .assistant-message {{
        background: {assistant_msg_bg};
        color: {assistant_msg_text};
        margin-right: auto;
        border-bottom-left-radius: 0;
    }}
    .assistant-message:hover {{
        transform: scale(1.02);
        box-shadow: 0 4px 12px {shadow_color};
    }}

    .system-message {{
        background: {system_msg_bg};
        color: {system_msg_text};
        margin: 1rem auto;
        max-width: 80%;
        text-align: center;
        font-weight: 500;
        border-radius: 10px;
    }}

    /* --- Footer --- */
    .footer {{
        text-align: center;
        color: {placeholder_color};
        font-size: 0.9rem;
        padding: 1rem 0;
    }}
    </style>
    """


# Apply the CSS
st.markdown(get_custom_css(st.session_state.theme), unsafe_allow_html=True)




def main_app():
    st.title("📊 Equity Research Tool")
    with st.sidebar:
        st.write(f"👋 Logged in as: {st.session_state.username}")

        if st.button("Logout 🚪"):
            st.session_state.page = "login"
            st.session_state.username = ""
            st.rerun()


# ------------------ TEXT EXTRACTORS ------------------

def extract_text_from_pdf(uploaded_file):
    text = ""
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_csv(uploaded_file):
    df = pd.read_csv(uploaded_file)
    return df.to_string(index=False)

def extract_text_from_txt(uploaded_file):
    return uploaded_file.read().decode("utf-8")

def extract_text_from_url(url):
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Get visible text only
        paragraphs = [p.get_text() for p in soup.find_all('p')]
        return "\n".join(paragraphs[:50])  # Limit to 50 paragraphs
    except Exception as e:
        st.error(f"Error fetching {url}: {e}")
        return f"Error fetching {url}: {e}"


    # st.sidebar.title("Menu")

    # Sidebar buttons, filters, and visualization logic here
    # ⬇️ THIS IS WHERE WE’LL PUT THE LOGOUT BUTTON
    # if st.sidebar.button("🚪 Logout", use_container_width=True):
    #     st.session_state.authenticated = False
    #     st.success("You’ve been logged out.")
    #     st.rerun()



# ------------------ GEMINI Q&A ------------------

def detect_language(text):
    try:
        return detect(text)
    except:
        return "en"

def ask_question_with_gemini(content_text, question):
    prompt = f"""
You are a helpful research assistant called EquityTool.
Use the following content to answer the question in English only, clearly and concisely.

Content:
\"\"\" 
{content_text}
\"\"\"

Question: {question}
Answer in English:
"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"An error occurred with the Gemini API: {e}")
        return f"Error: {e}"


# ------------------ STREAMLIT UI ------------------

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
if "content_loaded" not in st.session_state:
    st.session_state.content_loaded = False
if "total_content" not in st.session_state:
    st.session_state.total_content = ""
if "question" not in st.session_state:
    st.session_state.question = ""

# Add initial welcome message if the chat is empty
if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": "👋 Hello! I'm EquityTool, your research assistant. Upload some content or add URLs in the sidebar, and I'll help you analyze and answer questions about it."
    })

# Custom header
st.markdown(f"""
<div class="custom-header">
    <h1>📊 EquityTool: Research Assistant</h1>
    <p>Upload documents • Analyze web content • Get insights</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for content management
with st.sidebar:
    # Theme toggle at the top of sidebar
    st.markdown("### 🎨 Theme")
    theme_options = ["Light", "Dark"]
    selected_theme = st.radio(
        "Choose theme",
        theme_options,
        index=theme_options.index(st.session_state.theme),
        key="theme_selector",
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # Add logout button if user is authenticated
    # if "authenticated" in st.session_state and st.session_state["authenticated"]:
    #     if st.button("Logout"):
    #         logout()
    
    # Update theme if changed
    if selected_theme != st.session_state.theme:
        st.session_state.theme = selected_theme
        st.rerun()
    
    st.markdown("---")
    
    st.markdown("### 📁 Content Sources")
    
    # Resource type selection
    resource_type = st.selectbox(
        "Choose resource type:",
        ["📄 Upload Document", "🌐 Add Web Article", "📝 Enter Text Directly"],
        index=0,
        label_visibility="collapsed"
    )
    
    content_text = ""
    
    if resource_type == "📄 Upload Document":
        st.markdown("#### Upload Documents")
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["pdf", "csv", "txt"],
            help="Supported formats: PDF, CSV, TXT",
            label_visibility="collapsed"
        )
        
        if uploaded_file and st.button("📊 Process Document", type="primary"):
            with st.spinner("Processing document..."):
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
        st.markdown("#### Add Web Articles (up to 3)")
        urls = []
        
        # Three URL inputs
        for i in range(1, 4):
            url = st.text_input(f"URL {i}:", placeholder=f"https://example{i}.com/article", key=f"url_{i}")
            if url.strip():
                urls.append(url.strip())
        
        if urls and st.button("🌐 Fetch All Articles", type="primary"):
            content_text = ""
            progress_bar = st.progress(0, text="Fetching articles...")
            
            for i, url in enumerate(urls):
                with st.spinner(f"Fetching article {i+1} of {len(urls)}..."):
                    article_content = extract_text_from_url(url)
                    content_text += f"\n\n--- Article {i+1} from {url} ---\n\n" + article_content
                    progress_bar.progress((i + 1) / len(urls), text=f"Fetched article {i+1}...")
            
            progress_bar.empty()
            st.session_state.content_source = f"🌐 Web Articles: {len(urls)} articles loaded"
    
    elif resource_type == "📝 Enter Text Directly":
        st.markdown("#### Direct Text Input")
        direct_text = st.text_area(
            "Paste your text here:",
            height=200,
            placeholder="Enter or paste your text content here...",
            label_visibility="collapsed"
        )
        
        if direct_text and st.button("📝 Use Text", type="primary"):
            content_text = direct_text
            st.session_state.content_source = f"📝 Direct input ({len(direct_text)} chars)"
    
    # Process the content if any
    if content_text.strip():
        st.session_state.total_content = content_text
        st.session_state.content_loaded = True
        st.success(f"Content loaded successfully!")
        
        # Add system message to chat
        source_info = getattr(st.session_state, 'content_source', 'Unknown source')
        st.session_state.messages.append({
            "role": "system",
            "content": f"✅ Content loaded from: {source_info}. You can now ask questions about it."
        })
        st.rerun()
    
    # Show current content source
    if st.session_state.content_loaded and hasattr(st.session_state, 'content_source'):
        st.markdown("### 📌 Current Source")
        st.info(st.session_state.content_source)
        
        if st.button("🗑️ Clear Content"):
            st.session_state.content_loaded = False
            st.session_state.total_content = ""
            if hasattr(st.session_state, 'content_source'):
                delattr(st.session_state, 'content_source')
            st.session_state.messages.append({
                "role": "system",
                "content": "Content cleared. Please load new content to continue."
            })
            st.rerun()
    
    # Content stats
    if st.session_state.content_loaded:
        st.markdown("### 📊 Content Statistics")
        content_length = len(st.session_state.total_content)
        word_count = len(st.session_state.total_content.split())
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="stats-card">
                <h3>{content_length:,}</h3>
                <p>Characters</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stats-card">
                <h3>{word_count:,}</h3>
                <p>Words</p>
            </div>
            """, unsafe_allow_html=True)



# ------------------ CHAT INTERFACE ------------------

# Main chat container
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>You:</strong> {message['content']}
        </div>
        """, unsafe_allow_html=True)
    elif message["role"] == "assistant":
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <strong>EquityTool:</strong> {message['content']}
        </div>
        """, unsafe_allow_html=True)
    elif message["role"] == "system":
        st.markdown(f"""
        <div class="chat-message system-message">
            ℹ️ {message['content']}
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# Function to handle the message submission
def handle_submit():
    if st.session_state.question.strip():
        question = st.session_state.question
        st.session_state.question = ""  # Clear input BEFORE running the rest of the code
        
        if not st.session_state.content_loaded:
            st.session_state.messages.append({
                "role": "system",
                "content": "⚠️ Please load some content first using the sidebar!"
            })
            st.rerun()
            return
        
        # Add user message to chat
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })
        
        # Generate response
        with st.spinner("EquityTool is thinking..."):
            answer = ask_question_with_gemini(st.session_state.total_content, question)
        
        # Add assistant response to chat
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })
        
        st.rerun()

# Chat input - Using on_change callback
col1, col2 = st.columns([4, 1])

with col1:
    st.text_input(
        "Ask your question...",
        key="question",
        placeholder="Ask a question about your content...",
        label_visibility="collapsed",
        on_change=handle_submit
    )

with col2:
    st.button("Send", type="primary", use_container_width=True, on_click=handle_submit)


# if "authenticated" not in st.session_state:
#     st.session_state.authenticated = False
# if "show_signup" not in st.session_state:
#     st.session_state.show_signup = False






# if st.session_state.authenticated:
#     # call your main EquityTool app here
#     main_app()
# elif st.session_state.show_signup:
#     signup_page()
# else:
#     login_page()

    # ---------------- PAGE ROUTER ----------------
# if "page" not in st.session_state:
#     st.session_state.page = "login"

# if st.session_state.page == "login":
#     login_page()
# elif st.session_state.page == "signup":
#     signup_page()
# elif st.session_state.page == "home":
#     main_app()



# Footer
st.markdown("---")
theme_emoji = "🌞" if st.session_state.theme == "Light" else "🌙"
st.markdown(f"""
<div class="footer">
    Made by BotBuddies | {theme_emoji} {st.session_state.theme} Theme
</div>
""", unsafe_allow_html=True)