import streamlit as st
import openai

st.set_page_config(page_title="ChatGPT-Style AI Chatbot", page_icon="🤖", layout="centered")

st.title("🤖 ChatGPT-Style AI Chatbot")
st.markdown(
    "A conversational AI chatbot powered by OpenAI's gpt-4o-mini. "
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

# Chat input
user_input = st.chat_input("Type your message...")

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