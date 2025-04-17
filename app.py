import streamlit as st
import openai
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import speech_recognition  as sr
import numpy as np
import av

import streamlit.components.v1 as components

st.set_page_config(page_title="Jim's AI Chatbot", page_icon="🤖", layout="centered")

st.title("🤖 Jim's AI Chatbot")
st.markdown(
    "Powered by OpenAI's gpt-4o-mini. "
    "Enter your OpenAI API key to get started."
)

# Sidebar for API key input
with st.sidebar:
    st.header("OpenAI API Key")
    api_key = st.text_input(
        "Paste your OpenAI API key here",
        type="password",
        placeholder="sk-...",
        help="Your key is only stored in this session and never sent anywhere else."
    )

if not api_key:
    st.info("Please enter your OpenAI API key in the sidebar to start chatting.")
    st.stop()

openai.api_key = api_key

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful AI assistant."}
    ]

# Display chat history
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Voice Input Section ---
st.subheader("🎤 Voice Input (Optional)")

if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""

def speech_to_text_component():
    result = components.html(
        """
        <script>
        let recognition;
        function startRecognition() {
            if (!('webkitSpeechRecognition' in window)) {
                document.getElementById('stt-result').innerText = "Speech recognition not supported in this browser.";
                return;
            }
            recognition = new webkitSpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
            recognition.start();
            recognition.onresult = function(event) {
                let transcript = event.results[0][0].transcript;
                window.parent.postMessage({isStreamlitMessage: true, type: 'streamlit:setComponentValue', value: transcript}, '*');
            };
            recognition.onerror = function(event) {
                document.getElementById('stt-result').innerText = "Error: " + event.error;
            };
        }
        </script>
        <button onclick="startRecognition()">🎤 Record</button>
        <div id="stt-result"></div>
        """,
        height=80,
    )
    return result

voice_text = speech_to_text_component()
if voice_text and isinstance(voice_text, str) and voice_text.strip():
    st.session_state.voice_text = voice_text
    st.success(f"Transcribed: {voice_text}")

# Chat input
user_input = st.session_state.voice_text or st.chat_input("Type your message...")
st.session_state.voice_text = ""  # Reset after use

if user_input:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call OpenAI API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=st.session_state.messages,
                    stream=True,
                )
                full_response = ""
                placeholder = st.empty()
                for chunk in response:
                    delta = getattr(chunk.choices[0].delta, "content", "")
                    if delta:
                        full_response += delta
                        placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"Error: {e}")