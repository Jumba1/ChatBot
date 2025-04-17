import streamlit as st
import openai
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import speech_recognition  as sr
import numpy as np
import av

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
if "voice_input" not in st.session_state:
    st.session_state.voice_input = ""

class AudioProcessor(AudioProcessorBase):
    def recv(self, frame):
        audio = frame.to_ndarray()
        st.session_state.audio_data = audio
        return av.AudioFrame.from_ndarray(audio, layout="mono")

audio_ctx = webrtc_streamer(
    key="speech-to-text",
    mode="SENDRECV",
    audio_receiver_size=1024,
    client_settings={"media_stream_constraints": {"audio": True, "video": False}},
    async_processing=True,
)

voice_text = ""
if audio_ctx and audio_ctx.audio_receiver:
    audio_frames = audio_ctx.audio_receiver.get_frames(timeout=1)
    if audio_frames:
        audio = b"".join([f.to_ndarray().tobytes() for f in audio_frames])
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(sr.io.BytesIO(audio)) as source:
                audio_data = recognizer.record(source)
                voice_text = recognizer.recognize_google(audio_data)
                st.session_state.voice_input = voice_text
                st.success(f"Transcribed: {voice_text}")
        except Exception as e:
            st.warning(f"Voice input error: {e}")

# Chat input
user_input = st.session_state.voice_input or st.chat_input("Type your message...")
st.session_state.voice_input = ""  # Reset after use

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