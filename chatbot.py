import streamlit as st
import os
import time
import openai
from openai import OpenAI

# Initialize client with API key from Streamlit secrets
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("💬 Basic Chatbot with Rate Limit Handling")

# Keep chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

# Display past messages
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message("assistant").write(msg["content"])

# User input
if prompt := st.chat_input("Type your message..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Try sending request with retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # or "gpt-4"
                messages=st.session_state["messages"]
            )
            reply = response.choices[0].message.content
            st.session_state["messages"].append({"role": "assistant", "content": reply})
            st.chat_message("assistant").write(reply)
            break  # success, exit retry loop

        except openai.RateLimitError:
            if attempt < max_retries - 1:
                st.warning("Rate limit reached. Retrying in 5 seconds...")
                time.sleep(5)  # wait before retry
            else:
                st.error("Rate limit reached. Please wait or check your usage quota.")
        except Exception as e:
            st.error(f"Unexpected error: {e}")
            break
