import streamlit as st
import openai
import base64
import os
from dotenv import load_dotenv

# --- CONFIGURATION & SETUP ---
# Load environment variables from .env file (used for local development)
load_dotenv()

# Retrieve the OpenAI API Key from environment or Streamlit Secrets
# This key is essential for the AI Agent to function
API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    st.error("❌ OpenAI API Key not found! Please add it to Streamlit Secrets or your .env file.")
    st.stop()

# Initialize the OpenAI client to interact with GPT-4o
client = openai.OpenAI(api_key=API_KEY)

# --- CORE AI AGENT LOGIC ---

def analyze_medical_image(image_path):
    """
    This function acts as a 'Medical Imaging Agent'.
    It converts the image to base64 and sends it to GPT-4o Vision 
    with a specific expert persona and structured instructions.
    """
    # Encoding the image to base64 so it can be transmitted via the API
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    # The System Prompt defines the Agent's expertise and output format
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
    - Simplify findings in clear, non-technical language for the patient.

    ⚠️ Disclaimer: This is AI-assisted analysis only. Always consult a qualified doctor for final diagnosis.
    """

    try:
        # Calling the multimodal GPT-4o model
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
    except Exception as e:
        return f"Error during analysis: {str(e)}"

def get_chat_response(user_message, analysis_report):
    """
    This function powers 'MediBot', an interactive conversational agent.
    It uses the analysis report as context to answer patient questions.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"You are MediBot, a friendly medical assistant. Context: {analysis_report}. Explain findings simply and always remind the user to consult a doctor. 🏥"
                },
                {"role": "user", "content": user_message}
            ],
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error in chat: {str(e)}"

# --- STREAMLIT UI SETUP ---

# Configure page settings
st.set_page_config(page_title="MediScan AI", page_icon="🏥", layout="wide")

# Applying Custom CSS for a professional 'Cyberpunk/Medical' theme
st.markdown("""
<style>
    /* Dark gradient background for the app */
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: white; }
    
    /* Styling the analysis report box */
    .report-card { background: rgba(255,255,255,0.05); border: 1px solid #00d4ff44; border-radius: 16px; padding: 20px; color: white !important; }
    
    /* Neon gradient title effect */
    h1 { background: linear-gradient(90deg, #00d4ff, #7b2ff7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.8rem; font-weight: 800; text-align: center; }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] { background: #1a1a2e; border-right: 2px solid #00d4ff; }
    
    /* Custom button styling */
    .stButton > button { background: linear-gradient(90deg, #00d4ff, #7b2ff7) !important; color: white !important; border-radius: 10px; font-weight: 700; width: 100%; transition: 0.3s; }
    .stButton > button:hover { transform: scale(1.02); box-shadow: 0 0 15px #00d4ff88; }
</style>
""", unsafe_allow_html=True)

# Application Header
st.markdown("<h1>🏥 MediScan AI</h1><p style='text-align:center; color:#a0a0c0;'>Agentic AI for Medical Imaging & Patient Assistance</p><hr>", unsafe_allow_html=True)

# --- SESSION STATE MANAGEMENT ---
# Storing analysis results and chat history so they don't disappear on refresh
if "analysis_report" not in st.session_state:
    st.session_state.analysis_report = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- SIDEBAR: USER INPUT ---
st.sidebar.markdown("### 🩺 Diagnostic Center")
uploaded_file = st.sidebar.file_uploader("Upload Medical Scan (X-ray, MRI, etc.)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Button to trigger the AI Agent's analysis
    st.sidebar.button("🔍 Run AI Analysis", key="analyze_btn")

# --- MAIN DASHBOARD LAYOUT ---
col1, col2 = st.columns([1, 1], gap="large")

# LEFT COLUMN: Image display and Analysis Report
with col1:
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Scan", use_container_width=True)
        
        if st.session_state.get("analyze_btn"):
            with st.spinner("🔬 Agent is interpreting the scan..."):
                # Save uploaded file temporarily for the processing agent
                temp_filename = f"temp_file.{uploaded_file.name.split('.')[-1]}"
                with open(temp_filename, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Execute analysis logic
                report = analyze_medical_image(temp_filename)
                st.session_state.analysis_report = report
                st.session_state.chat_history = [] # Reset chat for a new scan
                os.remove(temp_filename) # Clean up temp file

        if st.session_state.analysis_report:
            st.markdown("### 📋 AI Analysis Report")
            st.markdown(f"<div class='report-card'>{st.session_state.analysis_report}</div>", unsafe_allow_html=True)
    else:
        st.info("👋 Welcome! Please upload a medical scan in the sidebar to begin the AI analysis.")

# RIGHT COLUMN: Interactive Chatbot (MediBot)
with col2:
    st.markdown("### 🤖 MediBot Assistant")
    if st.session_state.analysis_report:
        # Render the conversation history
        for chat in st.session_state.chat_history:
            with st.chat_message("user"): st.write(chat["user"])
            with st.chat_message("assistant"): st.write(chat["bot"])

        # Capture user questions about the report
        user_input = st.chat_input("Ask MediBot about these findings...")
        if user_input:
            with st.spinner("MediBot is typing..."):
                bot_res = get_chat_response(user_input, st.session_state.analysis_report)
                st.session_state.chat_history.append({"user": user_input, "bot": bot_res})
                st.rerun() # Refresh UI to show new message
    else:
        st.markdown("<p style='color:#a0a0c0;'>MediBot will activate once an image is successfully analyzed.</p>", unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("<hr><p style='text-align:center; font-size:0.8rem; color:#a0a0c0;'>Disclaimer: For educational purposes only. This AI agent is not a replacement for professional medical diagnosis.</p>", unsafe_allow_html=True)
