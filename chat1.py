import streamlit as st
import os

# ========== PAGE SETUP ==========
st.set_page_config(page_title="OpenRouter Chatbot", page_icon="🤖", layout="centered")
st.title("🤖 Free AI Chatbot")
st.caption("Powered by OpenRouter and the Qwen3 Model")

# ========== SIDEBAR CONFIGURATION ==========
with st.sidebar:
    st.header("🔑 Configuration")
    
    # Get API key from environment variable FIRST (for Render deployment)
    api_key_from_env = os.environ.get("OPENROUTER_API_KEY")
    
    if api_key_from_env:
        # If deployed on Render with env var, use it automatically
        api_key = api_key_from_env
        st.success("✅ Using API key from environment (Render)")
        # Optionally still show an input for local override
        api_key_input_override = st.text_input("Or enter a different key:", type="password", placeholder="sk-or-v1-...")
        if api_key_input_override:
            api_key = api_key_input_override
            st.info("⚠️ Using manually entered key instead of environment key")
    else:
        # For local development without env var
        api_key_input = st.text_input("Enter your OpenRouter API Key:", type="password", placeholder="sk-or-v1-...")
        api_key = api_key_input if api_key_input else None
        if api_key:
            st.success("✅ Using provided API key")
        else:
            st.warning("⚠️ No API key provided")
    
    st.divider()
    st.markdown("**How to get started:**")
    st.markdown("1. Sign up at [OpenRouter.ai](https://openrouter.ai)")
    st.markdown("2. Go to **Keys** page and **Create API Key**")
    st.markdown("3. Copy your key (starts with `sk-or-v1`)")
    st.markdown("4. Paste it above or set as `OPENROUTER_API_KEY` env variable")
    
    # Model selection
    st.divider()
    st.markdown("**⚙️ Model Settings**")
    selected_model = st.selectbox(
        "Choose a model:",
        ["qwen/qwen3-coder:free", "mistralai/mistral-7b-instruct:free"],
        help="Qwen3-Coder is for programming. Mistral-7B is for general conversation."
    )
    st.caption(f"Using: `{selected_model}`")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# ========== COMPATIBLE CLIENT INITIALIZATION ==========
def initialize_openrouter_client(api_key):
    """Initialize OpenRouter client - COMPATIBLE with ALL OpenAI versions"""
    if not api_key:
        return None, "No API key provided"
    
    try:
        import openai
        
        # Detect OpenAI version
        openai_version = getattr(openai, '__version__', '0.0.0')
        
        if openai_version.startswith('1.'):
            # NEW STYLE: OpenAI ≥1.0.0
            from openai import OpenAI
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key
            )
            return {"type": "new", "client": client}, "✅ Connected to OpenRouter API"
        else:
            # OLD STYLE: OpenAI <1.0.0
            openai.api_base = "https://openrouter.ai/api/v1"
            openai.api_key = api_key
            return {"type": "old", "client": openai, "api_key": api_key}, "✅ Connected to OpenRouter API (legacy)"
            
    except Exception as e:
        return None, f"❌ Connection failed: {str(e)}"

# ========== COMPATIBLE AI RESPONSE FUNCTION ==========
def get_ai_response(client_info, user_message, chat_history=None, model="qwen/qwen3-coder:free"):
    """Get response from OpenRouter - COMPATIBLE with both OpenAI versions"""
    try:
        messages = []
        
        # System prompt
        messages.append({
            "role": "system", 
            "content": "You are a helpful, friendly, and concise AI assistant. Answer the user's questions helpfully."
        })
        
        # Add chat history
        if chat_history:
            for msg in chat_history[-6:]:
                role = "user" if msg["role"] == "user" else "assistant"
                messages.append({"role": role, "content": msg["content"]})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Make API call based on client type
        if client_info["type"] == "new":
            # NEW STYLE: OpenAI ≥1.0.0
            response = client_info["client"].chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        else:
            # OLD STYLE: OpenAI <1.0.0
            response = client_info["client"].ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
            
    except Exception as e:
        return f"⚠️ Sorry, I encountered an error: {str(e)}"

# ========== CHAT INTERFACE ==========
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! 👋 I'm your AI assistant powered by OpenRouter. How can I help you today?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ========== HANDLE USER INPUT ==========
if prompt := st.chat_input("Type your message here..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Always use the api_key variable from the sidebar logic
    if not api_key:
        with st.chat_message("assistant"):
            st.error("Please provide an OpenRouter API key in the sidebar to use the chatbot.")
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "I need an API key to respond. Please enter your OpenRouter API key in the sidebar."
            })
    else:
        client_info, status = initialize_openrouter_client(api_key)
        
        if client_info:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = get_ai_response(client_info, prompt, st.session_state.messages, selected_model)
                    st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            with st.chat_message("assistant"):
                st.error(status)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"Connection issue: {status}"
                })