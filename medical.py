import streamlit as st
import openai
import base64
import os
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURATION ---
# Load environment variables for local development
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    st.error("❌ OpenAI API Key not found! Please add it to Streamlit Secrets or your .env file.")
    st.stop()

# Initializing OpenAI client directly for API calls
client = openai.OpenAI(api_key=API_KEY)

# --- AI LOGIC FUNCTIONS ---

def analyze_medical_image(image_path):
    """
    Analyzes the uploaded medical image using GPT-4o Vision model.
    Converts image to base64 and sends it with a structured prompt.
    """
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
    """
    Generates a text response from the assistant based on the analysis report context.
    """
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

def text_to_speech(text):
    """
    Converts the assistant's text response into high-quality audio using OpenAI TTS.
    Returns the path to the generated audio file.
    """
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy", # Professional medical tone
            input=text
        )
        audio_path = "bot_speech.mp3"
        response.stream_to_file(audio_path)
        return audio_path
    except Exception as e:
        st.error(f"TTS Error: {e}")
        return None

def speech_to_text(audio_bytes):
    """
    Converts user's recorded audio into text using OpenAI Whisper model.
    """
    if audio_bytes:
        with open("user_audio.wav", "wb") as f:
            f.write(audio_bytes)
        
        # Using Whisper API for transcription
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=open("user_audio.wav", "rb")
        )
        return transcript.text
    return None

# --- UI SETUP ---

st.set_page_config(page_title="MediScan AI", page_icon="🏥", layout="wide")

# Custom CSS for the Cyberpunk UI & Styling
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: white; }
    
    .stAlert {
        background-color: rgba(0, 212, 255, 0.1) !important;
        border: 1px solid #00d4ff !important;
        color: white !important;
    }
    .stAlert p { color: white !important; }

    h1 { background: linear-gradient(90deg, #00d4ff, #7b2ff7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.8rem !important; font-weight: 800 !important; text-align: center; }
    h2, h3 { color: #00d4ff !important; }

    [data-testid="stSidebar"] { background: linear-gradient(180deg, #1a1a2e, #16213e); border-right: 2px solid #00d4ff; }
    [data-testid="stSidebar"] * { color: white !important; }

    .report-card, [data-testid="stChatMessage"] {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid #7b2ff744 !important;
        border-radius: 12px !important;
        color: white !important;
    }
    [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] div { color: white !important; }

    .stButton > button, [data-testid="stFileUploader"] button {
        background: linear-gradient(90deg, #00d4ff, #7b2ff7) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
    }
    [data-testid="stWidgetLabel"] p, .stMarkdown p, label { color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- APPLICATION HEADER ---
st.markdown("""
<div style='text-align:center; padding: 10px 0 0 0;'>
    <span style='font-size:3.5rem;'>🏥</span>
    <h1>MediScan AI</h1>
    <p style='color:#a0a0c0; font-size:1.1rem; margin-top:-10px;'>AI-Powered Medical Image Analysis & Voice Assistant</p>
    <div style='display:flex; justify-content:center; gap:20px; margin:10px 0; flex-wrap:wrap;'>
        <span style='background:rgba(0,212,255,0.15); border:1px solid #00d4ff; border-radius:20px; padding:4px 16px; font-size:0.85rem;'>🔬 X-Ray</span>
        <span style='background:rgba(0,212,255,0.15); border:1px solid #00d4ff; border-radius:20px; padding:4px 16px; font-size:0.85rem;'>🧠 MRI</span>
        <span style='background:rgba(0,212,255,0.15); border:1px solid #00d4ff; border-radius:20px; padding:4px 16px; font-size:0.85rem;'>🩻 CT Scan</span>
        <span style='background:rgba(0,212,255,0.15); border:1px solid #00d4ff; border-radius:20px; padding:4px 16px; font-size:0.85rem;'>🔊 Ultrasound</span>
    </div>
    <hr>
</div>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "analysis_report" not in st.session_state: st.session_state.analysis_report = None
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- SIDEBAR FOR INPUTS ---
st.sidebar.markdown("<div style='text-align:center;'><span style='font-size:2.5rem;'>🩺</span><h2 style='color:#00d4ff; margin:5px 0;'>Upload Image</h2></div>", unsafe_allow_html=True)
uploaded_file = st.sidebar.file_uploader("Choose file...", type=["jpg", "jpeg", "png", "bmp", "gif"], label_visibility="collapsed")

if uploaded_file:
    st.sidebar.markdown("---")
    st.sidebar.button("🔍 Analyze Image", key="analyze_btn")

# --- MAIN DASHBOARD LAYOUT ---
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    if uploaded_file:
        st.markdown("### 🖼️ Uploaded Medical Scan")
        st.image(uploaded_file, use_container_width=True)

        if st.session_state.get("analyze_btn"):
            with st.spinner("🔬 AI is interpreting the scan..."):
                temp_path = f"temp_image.{uploaded_file.type.split('/')[1]}"
                with open(temp_path, "wb") as f: f.write(uploaded_file.getbuffer())
                st.session_state.analysis_report = analyze_medical_image(temp_path)
                st.session_state.chat_history = []
                os.remove(temp_path)

        if st.session_state.analysis_report:
            st.markdown("### 📋 Expert Analysis Report")
            st.markdown(f"<div class='report-card'>{st.session_state.analysis_report}</div>", unsafe_allow_html=True)
    else:
        st.info("Please upload a medical image from the sidebar to get started.")

with col2:
    st.markdown("<div style='text-align:center;'><h3>🤖 MediBot Voice Assistant</h3></div>", unsafe_allow_html=True)
    
    if st.session_state.analysis_report:
        # Voice Input Feature (Mic Recorder)
        st.write("🎤 **Talk to MediBot:**")
        voice_data = mic_recorder(start_prompt="Record Question", stop_prompt="Stop Recording", key='mic')

        # Display Chat History with Audio Support
        for chat in st.session_state.chat_history:
            with st.chat_message("user", avatar="👤"): st.write(chat["user"])
            with st.chat_message("assistant", avatar="🩺"): 
                st.write(chat["bot"])
                if "audio" in chat:
                    st.audio(chat["audio"], format="audio/mp3")

        # Capture Input (Text or Voice)
        user_msg = None
        if voice_data:
            with st.spinner("Transcribing your voice..."):
                user_msg = speech_to_text(voice_data['bytes'])
        
        # Standard Chat Input
        chat_input = st.chat_input("💬 Ask about your report...")
        final_input = chat_input if chat_input else user_msg

        if final_input:
            with st.spinner("MediBot is thinking & preparing audio..."):
                bot_res = get_chat_response(final_input, st.session_state.analysis_report)
                audio_file = text_to_speech(bot_res)
                
                st.session_state.chat_history.append({
                    "user": final_input, 
                    "bot": bot_res,
                    "audio": audio_file
                })
                st.rerun()
    else:
        st.markdown("<p style='text-align:center; color:#a0a0c0;'>Analyze an image first to activate MediBot Voice features.</p>", unsafe_allow_html=True)

# Footer Disclaimer
st.markdown("<hr><div style='text-align:center;'><p style='color:#a0a0c0; font-size:0.85rem;'>🏥 MediScan AI | Empowering Patients with Voice & Vision AI</p></div>", unsafe_allow_html=True)
