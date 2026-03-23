from agno.agent import Agent
import streamlit as st
from agno.models.openai import OpenAIChat
import openai
import base64
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=API_KEY)

medical_agent = Agent(
    model=OpenAIChat(id="gpt-4o", api_key=API_KEY),
    markdown=True
)

chat_agent = Agent(
    model=OpenAIChat(id="gpt-4o", api_key=API_KEY),
    markdown=True
)

query = """
You are a highly skilled medical imaging expert with extensive knowledge in radiology and diagnostic imaging. Analyze the medical image and structure your response as follows:

### 1. Image Type & Region
- Identify imaging modality (X-ray/MRI/CT/Ultrasound/etc.)
- Specify anatomical region and positioning
- Evaluate image quality and technical adequacy

### 2. Key Findings
- Highlight primary observations systematically
- Identify potential abnormalities with detailed descriptions
- Include measurements and densities where relevant

### 3. Diagnostic Assessment
- Provide primary diagnosis with confidence level
- List differential diagnoses ranked by likelihood
- Support each diagnosis with observed evidence
- Highlight critical/urgent findings

### 4. Patient-Friendly Explanation
- Simplify findings in clear, non-technical language
- Avoid medical jargon or provide easy definitions
- Include relatable visual analogies

### 5. Research Context
- Use DuckDuckGo search to find recent medical literature
- Search for standard treatment protocols
- Provide 2-3 key references supporting the analysis

---
Ensure a structured and medically accurate response using clear markdown formatting.
⚠️ Disclaimer: This is AI-assisted analysis only. Always consult a qualified doctor for final diagnosis.
"""


def analyze_medical_image(image_path):
   
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_data}"
                        }
                    },
                    {
                        "type": "text",
                        "text": query
                    }
                ]
            }
        ],
        max_tokens=2000
    )
    return response.choices[0].message.content

def get_chat_response(user_message, analysis_report):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"""You are MediBot, a friendly medical assistant chatbot.
Analysis report: {analysis_report}
Explain findings simply like a doctor would to a patient.
Always end with: Please consult a qualified doctor. 🏥"""
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        max_tokens=1000
    )
    return response.choices[0].message.content

# =====================
# Custom CSS
# =====================
st.set_page_config(page_title="MediScan AI", page_icon="🏥", layout="wide")

st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: white;
    }
    
        /* Report card text */
    .report-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid #00d4ff44;
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(10px);
        margin-top: 10px;
        color: white !important;
    }
    .report-card * {
        color: white !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e, #16213e);
        border-right: 2px solid #00d4ff;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Title */
    h1 {
        background: linear-gradient(90deg, #00d4ff, #7b2ff7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        text-align: center;
    }

    h2, h3 {
        color: #00d4ff !important;
    }

    /* Cards */
    .report-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid #00d4ff44;
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(10px);
        margin-top: 10px;
    }

    /* Chat messages */
    [data-testid="stChatMessage"] {
        background: rgba(255,255,255,0.05) !important;
        border-radius: 12px !important;
        border: 1px solid #7b2ff744 !important;
        margin-bottom: 8px !important;
    }
    [data-testid="stChatMessage"] p {
        color: white !important;
    }
    [data-testid="stChatMessage"] * {
        color: white !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #00d4ff, #7b2ff7) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 10px 24px !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        transform: scale(1.03);
        box-shadow: 0 0 20px #00d4ff88 !important;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background: rgba(0, 10, 40, 0.8) !important;
        border: 2px dashed #00d4ff !important;
        border-radius: 12px !important;
        padding: 10px !important;
    }
    [data-testid="stFileUploader"] > div {
        background: rgba(0, 10, 40, 0.9) !important;
        border-radius: 10px !important;
    }
    [data-testid="stFileDropzone"] {
        background: rgba(0, 10, 40, 0.9) !important;
        border: none !important;
    }
    [data-testid="stFileDropzone"] * {
        color: white !important;
    }
    [data-testid="stFileUploader"] button {
        background: linear-gradient(90deg, #00d4ff, #7b2ff7) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
    }

    /* Chat input */
    [data-testid="stChatInput"] {
        background: rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        border: 1px solid #00d4ff !important;
    }

    /* Spinner */
    .stSpinner > div {
        border-top-color: #00d4ff !important;
    }

    /* Warning/Info */
    .stWarning, .stInfo {
        background: rgba(0, 212, 255, 0.1) !important;
        border: 1px solid #00d4ff !important;
        border-radius: 10px !important;
        color: white !important;
    }

    /* Divider */
    hr {
        border-color: #00d4ff44 !important;
    }

    /* Image border */
    [data-testid="stImage"] img {
        border-radius: 16px !important;
        border: 2px solid #00d4ff !important;
        box-shadow: 0 0 30px #00d4ff44 !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #1a1a2e; }
    ::-webkit-scrollbar-thumb { background: #00d4ff; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# =====================
# Header
# =====================
st.markdown("""
<div style='text-align:center; padding: 10px 0 0 0;'>
    <span style='font-size:3.5rem;'>🏥</span>
    <h1>MediScan AI</h1>
    <p style='color:#a0a0c0; font-size:1.1rem; margin-top:-10px;'>
        AI-Powered Medical Image Analysis & Patient Assistant
    </p>
    <div style='display:flex; justify-content:center; gap:20px; margin:10px 0; flex-wrap:wrap;'>
        <span style='background:rgba(0,212,255,0.15); border:1px solid #00d4ff; border-radius:20px; padding:4px 16px; font-size:0.85rem;'>🔬 X-Ray</span>
        <span style='background:rgba(0,212,255,0.15); border:1px solid #00d4ff; border-radius:20px; padding:4px 16px; font-size:0.85rem;'>🧠 MRI</span>
        <span style='background:rgba(0,212,255,0.15); border:1px solid #00d4ff; border-radius:20px; padding:4px 16px; font-size:0.85rem;'>🫁 CT Scan</span>
        <span style='background:rgba(0,212,255,0.15); border:1px solid #00d4ff; border-radius:20px; padding:4px 16px; font-size:0.85rem;'>🔊 Ultrasound</span>
    </div>
    <hr>
</div>
""", unsafe_allow_html=True)

# =====================
# Session State
# =====================
if "analysis_report" not in st.session_state:
    st.session_state.analysis_report = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# =====================
# Sidebar
# =====================
st.sidebar.markdown("""
<div style='text-align:center; padding:10px 0;'>
    <span style='font-size:2.5rem;'>🩺</span>
    <h2 style='color:#00d4ff; margin:5px 0;'>Upload Image</h2>
    <p style='color:#a0a0c0; font-size:0.85rem;'>Supported: JPG, PNG, BMP, GIF</p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.sidebar.file_uploader(
    "Choose a medical image file...",
    type=["jpg", "jpeg", "png", "bmp", "gif"],
    label_visibility="collapsed"
)

if uploaded_file:
    st.sidebar.markdown("---")
    st.sidebar.button("🔍 Analyze Image", key="analyze_btn")
    st.sidebar.markdown("""
    <div style='background:rgba(255,165,0,0.1); border:1px solid orange; border-radius:10px; padding:10px; margin-top:10px;'>
        <p style='color:orange; font-size:0.8rem; margin:0;'>
        ⚠️ <b>Disclaimer:</b> This tool is for educational purposes only. Always consult a qualified doctor for medical advice.
        </p>
    </div>
    """, unsafe_allow_html=True)

# =====================
# Main Layout
# =====================
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    if uploaded_file is not None:
        st.markdown("### 🖼️ Uploaded Image")
        st.image(uploaded_file, caption="Medical Image", use_container_width=True)

        if st.session_state.get("analyze_btn"):
            with st.spinner("🔬 Analyzing image with AI... Please wait..."):
                image_path = f"temp_image.{uploaded_file.type.split('/')[1]}"
                with open(image_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                report = analyze_medical_image(image_path)
                st.session_state.analysis_report = report
                st.session_state.chat_history = []
                os.remove(image_path)

        if st.session_state.analysis_report:
            st.markdown("### 📋 Analysis Report")
            st.markdown(f"""
            <div class='report-card'>
            {st.session_state.analysis_report}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='text-align:center; padding:60px 20px; background:rgba(255,255,255,0.03); border-radius:16px; border:2px dashed #00d4ff44;'>
            <span style='font-size:4rem;'>🩻</span>
            <h3 style='color:#00d4ff;'>No Image Uploaded</h3>
            <p style='color:#a0a0c0;'>Upload a medical image from the sidebar to get started</p>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='text-align:center; margin-bottom:10px;'>
        <span style='font-size:2rem;'>🤖</span>
        <h3 style='color:#7b2ff7; display:inline; margin-left:8px;'>MediBot Assistant</h3>
        <p style='color:#a0a0c0; font-size:0.9rem;'>Ask anything about your report in simple language</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.analysis_report:
        # Chat history
        chat_container = st.container()
        with chat_container:
            for chat in st.session_state.chat_history:
                with st.chat_message("user", avatar="👤"):
                    st.write(chat["user"])
                with st.chat_message("assistant", avatar="🩺"):
                    st.write(chat["bot"])

        # Chat input
        user_input = st.chat_input("💬 Ask MediBot your question...")
        if user_input:
            with st.spinner("🔎 MediBot is thinking..."):
                bot_response = get_chat_response(user_input, st.session_state.analysis_report)
                st.session_state.chat_history.append({
                    "user": user_input,
                    "bot": bot_response
                })
                st.rerun()
    else:
        st.markdown("""
        <div style='text-align:center; padding:60px 20px; background:rgba(123,47,247,0.05); border-radius:16px; border:2px dashed #7b2ff744;'>
            <span style='font-size:4rem;'>🤖</span>
            <h3 style='color:#7b2ff7;'>MediBot is Ready!</h3>
            <p style='color:#a0a0c0;'>Analyze an image first to start chatting with MediBot</p>
            <br>
            <span style='font-size:1.5rem;'>🩺 🔬 💊 🧬 🏥</span>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("""
<hr>
<div style='text-align:center; padding:10px 0;'>
    <p style='color:#a0a0c0; font-size:0.85rem;'>
        🏥 MediScan AI | Powered by Groq & Llama 4 | 
        <span style='color:#00d4ff;'>For Educational Purposes Only</span>
    </p>
</div>
""", unsafe_allow_html=True)
