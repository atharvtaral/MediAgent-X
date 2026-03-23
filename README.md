# 🏥 MediScan AI: Agentic Medical Imaging & Voice Assistant

**MediScan AI** is an advanced AI-powered dashboard designed to analyze medical scans (X-rays, MRIs, CT scans) and provide an interactive, voice-enabled assistant for patient-friendly discussions. Built with **Python**, **Streamlit**, and **OpenAI's GPT-4o**.

## 🚀 Key Features
- **📸 Multimodal AI Analysis:** Uses GPT-4o Vision to interpret medical images with expert-level precision.
- **🎤 Voice-to-Text (Input):** Integrated **OpenAI Whisper** allows patients to ask questions using their voice instead of typing.
- **🔊 Text-to-Speech (Output):** Integrated **OpenAI TTS** enables the assistant to speak back the analysis, making it accessible for everyone.
- **📋 Structured Medical Reports:** Automatically generates findings, diagnostic assessments, and patient-friendly explanations.
- **🤖 Interactive MediBot:** A context-aware conversational agent that simplifies complex medical reports.
- **🌌 Modern Cyberpunk UI:** A sleek, professional dark-themed interface with neon gradients for a futuristic healthcare experience.

## 🛠️ Tech Stack
- **Frontend:** Streamlit (Custom CSS & Streamlit-Mic-Recorder)
- **AI Engine:** OpenAI GPT-4o (Vision), Whisper-1 (Speech-to-Text), TTS-1 (Text-to-Speech)
- **Language:** Python 3.10+
- **Security:** Secret management for API keys via Streamlit Secrets.

## 🛡️ Responsible AI & Ethical Considerations
In healthcare AI, responsibility is as important as accuracy. This project adheres to key Ethical AI principles:

- **Accuracy Awareness:** Integrated a clear **Disclaimer** in every report, stating that the AI's analysis is for educational purposes and not a final diagnosis.
- **Human-in-the-loop:** Designed as a support tool for patients to better understand their scans before consulting a qualified medical professional.
- **Transparency:** The AI explicitly structures its response to show "Diagnostic Assessment" separately from "Patient-Friendly Explanation" to avoid confusion.
- **Data Privacy:** Uses **Streamlit Secrets** and `.env` to ensure API keys are never exposed, and temporary images are deleted from the server immediately after analysis.
- **Inclusivity:** Added **Voice-to-Voice** features (Whisper & TTS) to assist users who may have difficulty typing or reading complex text.

## 📦 Installation & Local Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/atharvtaral/MediScan-AI.git](https://github.com/atharvtaral/MediScan-AI.git)
   cd MediScan-AI
