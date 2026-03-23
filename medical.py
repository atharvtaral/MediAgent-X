import streamlit as st
import openai
import base64
import os
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    st.error("❌ OpenAI API Key not found! Please add it to Streamlit Secrets or your .env file.")
    st.stop()

# Initializing OpenAI client directly
client = openai.OpenAI(api_key=API_KEY)

# --- AI LOGIC ---

def analyze_medical_image(image_path):
    """Analyze image using GPT-4o Vision directly"""
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    prompt_query = """
    You are a highly skilled medical imaging expert with extensive knowledge in radiology. 
    Analyze the medical image and structure your response as follows:

    ### 1. Image Type & Region
    - Identify imaging modality (X-ray/MRI/CT/Ultrasound/etc.)
    - Specify anatomical region and positioning

    ### 2. Key Findings
    - Highlight primary observations and abnormalities systematically.

    ### 3. Diagnostic Assessment
    - Provide primary diagnosis and differential diagnoses ranked by likelihood.

    ### 4. Patient-Friendly Explanation
    - Simplify findings in clear, non-technical language.

    ⚠️ Disclaimer: This is AI-assisted analysis only. Always consult a qualified doctor for final diagnosis.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}},
                    {"type": "text", "text": prompt_query}
                ]
            }
        ],
        max_tokens=2000
    )
    return response.choices[0].message.content

def get_chat_response(user_message, analysis_report):
    """MediBot Chatbot logic"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"You are MediBot, a friendly medical assistant. Context: {analysis_report}. Explain simply and always end with: Please consult a qualified doctor. 🏥"
            },
            {"role": "user", "content": user_message}
        ],
        max_tokens=1000
    )
    return response.choices[0].message.content

# --- UI SETUP ---

st.set_page_config(page_title="MediScan AI", page_icon="🏥", layout="wide")

# Apply Custom CSS to fix button color and text visibility
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: white; }
    
    /* Fix for st.info() and st.warning() boxes */
    .stAlert {
        background-color: rgba(0, 212, 255, 0.1) !important;
        border: 1px solid #00d4ff !important;
        color: white !important;
    }
    .stAlert p { color: white !important; }

    /* Titles & Headers */
    h1 { background: linear-gradient(90deg, #00d4ff, #7b2ff7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.8rem !important; font-weight: 800 !important; text-align: center; }
    h2, h3 { color: #00d4ff !important; }

    /* Sidebar Fix */
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #1a1a2e, #16213e); border-right: 2px solid #00d4ff; }
    [data-testid="stSidebar"] * { color: white !important; }

    /* Report Card & Chat Messages */
    .report-card, [data-testid="stChatMessage"] {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid #7b2ff744 !important;
        border-radius: 12px !important;
        color: white !important;
    }
    [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] div { color: white !important; }

    /* All Buttons Gradient */
    .stButton > button, [data-testid="stFileUploader"] button {
        background: linear-gradient(90deg, #00d4ff, #7b2ff7) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
    }

    /* Labels & Captions Fix */
    [data-testid="stWidgetLabel"] p, .stMarkdown p, label { color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- HEADER WITH ICONS & TAGS ---
st.markdown("""
<div style='text-align:center; padding: 10px 0 0 0;'>
    <span style='font-size:3.5rem;'>🏥</span>
    <h1>MediScan AI</h1>
    <p style='color:#a0a0c0; font-size:1.1rem; margin-top:-10px;'>AI-Powered Medical Image Analysis & Patient Assistant</p>
    <div style='display:flex; justify-content:center; gap:20px; margin:10px 0; flex-wrap:wrap;'>
        <span style='background:rgba(0,212,255,0.15); border:1px solid #00d4ff; border-radius:20px; padding:4px 16px; font-size:0.85rem;'>🔬 X-Ray</span>
        <span style='background:rgba(0,212,255,0.15); border:1px solid #00d4ff; border-radius:20px; padding:4px 16px; font-size:0.85rem;'>🧠 MRI</span>
        <span style='background:rgba(0,212,255,0.15); border:1px solid #00d4ff; border-radius:20px; padding:4px 16px; font-size:0.85rem;'>🩻 CT Scan</span>
        <span style='background:rgba(0,212,255,0.15); border:1px solid #00d4ff; border-radius:20px; padding:4px 16px; font-size:0.85rem;'>🔊 Ultrasound</span>
    </div>
    <hr>
</div>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "analysis_report" not in st.session_state: st.session_state.analysis_report = None
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- SIDEBAR ---
st.sidebar.markdown("<div style='text-align:center;'><span style='font-size:2.5rem;'>🩺</span><h2 style='color:#00d4ff; margin:5px 0;'>Upload Image</h2></div>", unsafe_allow_html=True)
uploaded_file = st.sidebar.file_uploader("Choose file...", type=["jpg", "jpeg", "png", "bmp", "gif"], label_visibility="collapsed")

if uploaded_file:
    st.sidebar.markdown("---")
    st.sidebar.button("🔍 Analyze Image", key="analyze_btn")

# --- MAIN DASHBOARD ---
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    if uploaded_file:
        st.markdown("### 🖼️ Uploaded Image")
        st.image(uploaded_file, use_container_width=True)

        if st.session_state.get("analyze_btn"):
            with st.spinner("🔬 Analyzing image with AI..."):
                temp_path = f"temp_image.{uploaded_file.type.split('/')[1]}"
                with open(temp_path, "wb") as f: f.write(uploaded_file.getbuffer())
                st.session_state.analysis_report = analyze_medical_image(temp_path)
                st.session_state.chat_history = []
                os.remove(temp_path)

        if st.session_state.analysis_report:
            st.markdown("### 📋 Analysis Report")
            st.markdown(f"<div class='report-card'>{st.session_state.analysis_report}</div>", unsafe_allow_html=True)
    else:
        st.info("Please upload a medical image from the sidebar.")

with col2:
    st.markdown("<div style='text-align:center;'><h3>🤖 MediBot Assistant</h3></div>", unsafe_allow_html=True)
    if st.session_state.analysis_report:
        for chat in st.session_state.chat_history:
            with st.chat_message("user", avatar="👤"): st.write(chat["user"])
            with st.chat_message("assistant", avatar="🩺"): st.write(chat["bot"])

        user_input = st.chat_input("💬 Ask MediBot...")
        if user_input:
            bot_res = get_chat_response(user_input, st.session_state.analysis_report)
            st.session_state.chat_history.append({"user": user_input, "bot": bot_res})
            st.rerun()
    else:
        st.markdown("<p style='text-align:center; color:#a0a0c0;'>MediBot will activate after analysis.</p>", unsafe_allow_html=True)

# Footer
st.markdown("<hr><div style='text-align:center;'><p style='color:#a0a0c0; font-size:0.85rem;'>🏥 MediScan AI | For Educational Purposes Only</p></div>", unsafe_allow_html=True)
