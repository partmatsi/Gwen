import streamlit as st
import os
import requests
import json

# ========== PAGE SETUP ==========
st.set_page_config(page_title="OpenRouters Chatbot", page_icon="🤖", layout="centered")
st.title("🤖 Free AI Chatbot")
st.caption("Powered by OpenRouter")

# ========== SIDEBAR CONFIGURATION ==========
with st.sidebar:
    st.header("🔑 Configuration")
    
    # Get API key from environment variable FIRST
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    
    if api_key:
        st.success("✅ Using API key from environment")
        api_key_input = st.text_input("Or enter a different key:", type="password", value=api_key)
        if api_key_input and api_key_input != api_key:
            api_key = api_key_input
            st.info("⚠️ Using manually entered key")
    else:
        api_key_input = st.text_input("Enter your OpenRouter API Key:", type="password", placeholder="sk-or-v1-...")
        api_key = api_key_input if api_key_input else ""
        if api_key:
            st.success("✅ Using provided API key")
        else:
            st.warning("⚠️ No API key provided")
    
    # Model selection
    st.divider()
    selected_model = st.selectbox(
        "Choose a model:",
        ["qwen/qwen3-coder:free", "mistralai/mistral-7b-instruct:free"]
    )
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# ========== SIMPLE API CALL FUNCTION ==========
def get_ai_response_simple(api_key, user_message, chat_history=None, model="qwen/qwen3-coder:free"):
    """Simple API call using requests"""
    if not api_key:
        return "Please provide an API key"
    
    try:
        messages = [{"role": "system", "content": "You are a helpful AI assistant."}]
        
        if chat_history:
            for msg in chat_history[-6:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({"role": "user", "content": user_message})
        
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 500
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Error: {str(e)}"

# ========== CHAT INTERFACE ==========
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! 👋 How can I help you today?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ========== HANDLE USER INPUT ==========
if prompt := st.chat_input("Type your message here..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    if not api_key:
        with st.chat_message("assistant"):
            st.error("Please provide an API key in the sidebar")
    else:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_ai_response_simple(api_key, prompt, st.session_state.messages, selected_model)
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})