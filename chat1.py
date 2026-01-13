import streamlit as st
import os
import requests
import json
import time
from datetime import datetime

# ========== PAGE SETUP ==========
st.set_page_config(page_title="CABSChat", layout="centered")
st.title("💬 CABS Banking Chat Assistant")
st.markdown("Ask me about Products, Accounts, Loans, Cards, Online Banking, Branch Locations, O'mari digital wallet, Insurance or any CABS services!")

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
    
    # Model selection - using faster models
    st.divider()
    st.subheader("⚙️ Model Settings")
    
    # Group models by speed/capability
    selected_model = st.selectbox(
        "Choose a model (faster models first):",
        [
            "google/gemma-2-2b-it:free",  # Fastest
            "mistralai/mistral-7b-instruct:free",  # Good balance
            "qwen/qwen2.5-7b-instruct:free",  # Slightly faster than qwen3
            "qwen/qwen3-coder:free",  # Programming focused
        ],
        index=1  # Default to Mistral for better speed
    )
    
    # Performance settings
    st.divider()
    st.subheader("⚡ Performance")
    
    # Reduce context length for faster responses
    context_length = st.slider("Chat history (messages to remember):", 2, 10, 4)
    
    max_tokens = st.slider("Max response length:", 100, 1000, 300, 50)
    
    temperature = st.slider("Creativity (0=precise, 1=creative):", 0.1, 1.0, 0.7, 0.1)
    
    # Show performance tip
    st.info(f"💡 **Tip:** {selected_model.split('/')[1].split(':')[0]} is selected")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ========== OPTIMIZED API CALL FUNCTION ==========
@st.cache_data(show_spinner=False, max_entries=100)
def get_cached_response(api_key, messages, model, temperature, max_tokens):
    """Cached API call for repeated questions"""
    if not api_key:
        return None
    
    # Create a unique key for caching
    cache_key = f"{api_key[:10]}_{model}_{hash(str(messages[-1]))}"
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://cabschat.streamlit.app",  # Add your app URL
            "X-Title": "CABS Banking Assistant"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False  # Non-streaming for better compatibility
        }
        
        # Add timeout and retry logic
        start_time = time.time()
        
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60  # Increased timeout
        )
        
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            return {
                "response": data["choices"][0]["message"]["content"],
                "time": elapsed_time,
                "cached": False
            }
        elif response.status_code == 429:  # Rate limit
            return {
                "response": f"⚠️ Rate limit exceeded. Please wait a moment and try again. (Took {elapsed_time:.1f}s)",
                "time": elapsed_time,
                "cached": False
            }
        else:
            return {
                "response": f"Error {response.status_code}: {response.text[:200]} (Took {elapsed_time:.1f}s)",
                "time": elapsed_time,
                "cached": False
            }
            
    except requests.exceptions.Timeout:
        return {
            "response": "⚠️ Request timed out. The model might be busy. Please try again.",
            "time": 60,
            "cached": False
        }
    except Exception as e:
        return {
            "response": f"Error: {str(e)[:200]}",
            "time": 0,
            "cached": False
        }

def get_ai_response_optimized(api_key, user_message, chat_history=None, model="mistralai/mistral-7b-instruct:free", 
                              temperature=0.7, max_tokens=300, context_length=4):
    """Optimized AI response with caching and performance improvements"""
    if not api_key:
        return "Please provide an API key", 0
    
    try:
        # Create system prompt for banking assistant
        system_prompt = """You are CABS Assistant, a helpful AI banking assistant for CABS (Central Africa Building Society) in Zimbabwe.
        
        About CABS:
        - CABS is one of Zimbabwe's largest building societies
        - Offers banking, loans, savings accounts, mortgages, and insurance
        - Has the O'mari digital wallet for mobile money
        - Provides corporate banking, treasury services, and investment products
        
        Your role:
        1. Answer questions about CABS products and services helpfully
        2. Provide general banking information (don't give specific account advice)
        3. If asked about specific account details, recommend contacting CABS directly
        4. Keep responses concise and focused (2-3 paragraphs maximum)
        5. For complex inquiries, suggest visiting a branch or calling customer service
        
        Important: Never ask for personal or account information. Always maintain professionalism."""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add limited chat history for context
        if chat_history:
            # Only keep last N messages to avoid long contexts
            recent_history = chat_history[-context_length:]
            for msg in recent_history:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Get response with caching
        result = get_cached_response(api_key, messages, model, temperature, max_tokens)
        
        if result:
            return result["response"], result["time"]
        else:
            return "No response received", 0
            
    except Exception as e:
        return f"Error: {str(e)[:200]}", 0

# ========== CHAT INTERFACE ==========
# Initialize empty chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "response_times" not in st.session_state:
    st.session_state.response_times = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Display average response time in sidebar
if st.session_state.response_times:
    avg_time = sum(st.session_state.response_times) / len(st.session_state.response_times)
    st.sidebar.metric("⏱️ Average Response Time", f"{avg_time:.1f}s")

# ========== HANDLE USER INPUT ==========
if prompt := st.chat_input("Ask about CABS banking services..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    if not api_key:
        with st.chat_message("assistant"):
            st.error("Please provide an API key in the sidebar")
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "I need an API key to respond. Please enter your OpenRouter API key in the sidebar."
            })
    else:
        # Display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("💭 Thinking...")
            
            # Get sidebar settings
            context_len = context_length if 'context_length' in locals() else 4
            max_tokens_val = max_tokens if 'max_tokens' in locals() else 300
            temp_val = temperature if 'temperature' in locals() else 0.7
            
            # Get response
            start_time = time.time()
            response, api_time = get_ai_response_optimized(
                api_key, 
                prompt, 
                st.session_state.messages, 
                selected_model,
                temp_val,
                max_tokens_val,
                context_len
            )
            end_time = time.time()
            
            # Calculate total time
            total_time = end_time - start_time
            
            # Store response time
            st.session_state.response_times.append(total_time)
            
            # Display response
            message_placeholder.markdown(response)
            
            # Show timing info (optional, can be removed)
            st.caption(f"⏱️ Response time: {total_time:.1f}s")
        
        # Add to history
        st.session_state.messages.append({"role": "assistant", "content": response})

# ========== FOOTER ==========                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        

# Add CSS for better loading experience
st.markdown("""
<style>
    .stSpinner > div {
        text-align: center;
    }
    [data-testid="stChatMessage"] {
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    [data-testid="stChatMessage"]:has(> [data-testid="stChatMessageContent"] > div > div > p) {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)