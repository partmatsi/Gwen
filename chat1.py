import streamlit as st
import os
import requests
import json
import time
import random
import re
from datetime import datetime

# ========== PAGE SETUP ==========
st.set_page_config(
    page_title="CABS Banking Chat Assistant",
    page_icon="🏦",
    layout="centered"
)
st.title("🏦 CABS Banking Chat Assistant")
st.caption("Ask me about Products, Accounts, Loans, Cards, Online Banking, Branch Locations, O'mari digital wallet, Insurance or any CABS services!")

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
    st.subheader("⚙️ Model Settings")
    
    selected_model = st.selectbox(
        "Choose a model:",
        [
            "google/gemma-2-2b-it:free",  # Fastest
            "mistralai/mistral-7b-instruct:free",  # Good balance
            "qwen/qwen2.5-7b-instruct:free",  # Slightly faster than qwen3
            "qwen/qwen3-coder:free",  # Programming focused
        ],
        index=1  # Default to Mistral
    )
    
    # Chat mode selection
    st.divider()
    st.subheader("💬 Chat Mode")
    
    chat_mode = st.radio(
        "Choose response mode:",
        ["Hybrid (Recommended)", "AI Only", "Rule-Based Only"],
        index=0,
        help="Hybrid: Uses both banking knowledge and AI for best results"
    )
    
    # Performance settings
    st.divider()
    st.subheader("⚡ Performance")
    
    context_length = st.slider("Chat history (messages):", 2, 10, 4)
    max_tokens = st.slider("Max response length:", 100, 800, 300, 50)
    temperature = st.slider("Creativity:", 0.1, 1.0, 0.7, 0.1)
    
    # Clear chat button
    st.divider()
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_history = []
        st.rerun()
    
    # Debug info
    st.divider()
    if st.checkbox("Show debug info"):
        st.caption(f"Chat Mode: {chat_mode}")
        st.caption(f"Model: {selected_model}")

# ========== CABS BANKING KNOWLEDGE BASE ==========
INTENTS = {
    "greeting": {
        "patterns": [
            "hi", "hello", "hey", "good morning", "good afternoon", "good evening",
            "ndeipi", "kurisei", "madii", "hesi", "howdy", "hi there", "how are you"
        ],
        "responses": [
            "Hi! Welcome to CABS Banking Assistant. How can I help you today?", 
            "Hello! I'm here to assist with all your CABS banking needs.", 
            "Greetings! How can I assist you with your banking today?",
        ],
        "keywords": ["hi", "hello", "hey", "good", "morning", "afternoon", "evening"]
    },
    "who_are_you": {
        "patterns": [
            "who are you", "what are you", "introduce yourself", "are you an ai assistant", 
            "your name", "ndiwe ani", "what is your purpose", "tell me about yourself"
        ],
        "responses": [
            "I'm Tino an AI assistant created to help CABS customers with their banking needs", 
            "I'm Tino a virtual banking assistant designed to provide information about CABS services.", 
            "I'm Tino a CABS banking chatbot created to assist customers with their financial queries.",
        ],
        "keywords": ["who", "you", "name", "introduce", "yourself", "purpose", "identity"]
    },
    "lost_card": {
        "patterns": [
            "lost my card", "stolen card", "card stolen", "missing card", 
            "lost debit card", "lost visa card", "report lost card", "block my card"
        ],
        "responses": [
            "🚨 **URGENT: Lost/Stolen Card**\n\nPlease call us IMMEDIATELY to block your card:\n📞 **+263 242 707 771-9**\n\nWe'll block your card instantly to prevent unauthorized use and help you order a replacement.",
            "**EMERGENCY CARD BLOCKING**\n\nFor lost or stolen cards, contact us RIGHT AWAY:\n• **Phone:** +263 242 707 771-9\n• **WhatsApp:** 0777 227 227\n\nWe'll secure your account and guide you through getting a new card.",
        ],
        "keywords": ["lost", "card", "stolen", "missing", "block", "report", "emergency"]
    },
    "account_opening": {
        "patterns": [
            "how do I open an account", "i need a card", "i need a cabs card", 
            "open account", "new account", "i need a cabs account", "account opening"
        ],
        "responses": ["account_opening"],
        "keywords": ["open", "account", "new", "create", "card", "cabs"]
    },
    "loan_information": {
        "patterns": [
            "how to get a loan", "apply for loan", "need loan", "want loan", "loans",
            "Do you have civil servants loans", "do you off civil servants", 
            "tell me about civils servants loans", "i need a loan", "loan requirements"
        ],
        "responses": ["loan_information"],
        "keywords": ["loan", "borrow", "civil", "servant", "apply", "requirements"]
    },
    "online_banking": {
        "patterns": [
            "online banking", "internet banking", "mobile banking", "USSD banking", 
            "whatsapp banking", "digital banking", "reset password", "forgot password"
        ],
        "responses": ["online_banking"],
        "keywords": ["online", "internet", "mobile", "digital", "banking", "password"]
    },
    "branch_info": {
        "patterns": [
            "branch location", "working hours", "nearest branch", "where is branch", 
            "find branch", "branch near me", "branch locations"
        ],
        "responses": [
            "🏦 **CABS Branch Information**\n\nCABS has branches nationwide across Zimbabwe. Most branches operate:\n• **Weekdays**: 8:00 AM - 3:00 PM\n• **Saturdays**: 8:00 AM - 11:30 AM\n• **Closed Sundays & Public Holidays**\n\nFor specific branch locations, visit our website or call +263 242 707 771.",
        ],
        "keywords": ["branch", "location", "nearest", "hours", "working", "opening"]
    },
    "contact_info": {
        "patterns": [
            "contact", "phone number", "customer service", "emergency number", 
            "contact info", "email address", "call bank", "customer care"
        ],
        "responses": [
            "📞 **CABS Contact Information:**\n\n**Customer Service:**\n• Phone: +263 242 707 771-9\n• WhatsApp: 0777 227 227\n• USSD Banking: *227#\n\n**Other Contacts:**\n• Email: info@cabs.co.zw\n• Head Office: CABS Centre, 1st Street, Harare",
        ],
        "keywords": ["contact", "phone", "number", "email", "customer", "service"]
    },
    "account_types": {
        "patterns": [
            "varieties of accounts", "account portfolio", "accounts", 
            "banking account options", "what types of bank accounts", 
            "what accounts are available", "which accounts can I open"
        ],
        "responses": ["account_types"],
        "keywords": ["account", "type", "savings", "current", "student", "business"]
    },
    "interest_rates": {
        "patterns": [
            "interest rates", "savings interest", "loan rates", "fixed deposit", 
            "loan interest rates", "investment returns"
        ],
        "responses": ["interest_rates"],
        "keywords": ["interest", "rate", "savings", "loan", "fixed", "deposit"]
    },
    "operating_hours": {
        "patterns": [
            "public holiday hours", "are you open on sunday", "what time do you open", 
            "what time do you close", "weekend banking", "holiday hours"
        ],
        "responses": [
            "🕒 **CABS Operating Hours**\n\n**Branch Banking:**\n• **Weekdays (Mon-Fri)**: 8:00 AM - 3:00 PM\n• **Saturdays**: 8:00 AM - 11:30 AM\n• **Sundays**: Closed\n• **Public Holidays**: Closed\n\n**After Hours Services (24/7):**\n• Online Banking\n• Mobile App Banking\n• WhatsApp Banking (0777 227 227)\n• USSD Banking (*227#)\n• ATM Services",
        ],
        "keywords": ["open", "close", "hours", "time", "weekend", "saturday", "sunday", "holiday"]
    },
    "exchange_rates": {
        "patterns": [
            "exchange rates", "currency rates", "forex rates", "usd rates", "zig rates", 
            "foreign exchange", "currency exchange", "forex"
        ],
        "responses": ["exchange_rates"],
        "keywords": ["exchange", "rate", "currency", "forex", "usd", "dollar", "zig"]
    },
    "omari_info": {
        "patterns": [
            "omari", "o'mari", "digital wallet", "mobile money", "*707#", "usd wallet", 
            "zig wallet", "omari card", "visa card", "zimswitch card"
        ],
        "responses": ["omari_info"],
        "keywords": ["omari", "digital", "wallet", "mobile", "money", "*707#", "card"]
    },
    "transactional_accounts": {
        "patterns": [
            "minimum balance", "account fees", "account charges", "gold transactional", 
            "blue transactional", "account benefits", "what accounts do you have"
        ],
        "responses": ["transactional_accounts"],
        "keywords": ["minimum", "balance", "fees", "gold", "blue", "transactional", "account"]
    },
    "products_services": {
        "patterns": [
            "what financial services", "product", "banking offerings", 
            "financial products available", "available services", "cabs products", 
            "cabs services", "what do you sell"
        ],
        "responses": ["products_services"],
        "keywords": ["what", "financial", "services", "products", "available", "cabs"]
    },
    "card_types": {
        "patterns": [
            "omari visa card", "omari zimswitch card", "card benefits", "card features", 
            "gold debit card", "blue debit card", "what cards are available"
        ],
        "responses": ["card_types"],
        "keywords": ["omari", "visa", "zimswitch", "card", "benefits", "gold", "blue"]
    },
    "goodbye": {
        "patterns": [
            "bye", "goodbye", "see you", "thanks bye", "that's all", "thank you goodbye", "exit", "quit"
        ],
        "responses": [
            "Thanks for chatting! Have a great day. CABS is here whenever you need us.", 
            "Goodbye! Remember you can reach us 24/7 through WhatsApp (0777 227 227) or USSD (*227#).", 
            "Thank you for banking with CABS! Visit us again anytime. 🏦",
        ],
        "keywords": ["bye", "goodbye", "see", "you", "thanks", "exit", "quit"]
    }
}

# ========== RULE-BASED RESPONSE FUNCTIONS ==========
def account_opening_response():
    return """📋 **Account Opening at CABS**

**Requirements to Open an Account:**
1. **Valid ID:** National ID, Passport, or Driver's License
2. **Proof of Residence:** Utility bill, lease agreement, or affidavit
3. **Initial Deposit:** Varies by account type
4. **Passport-size photograph (2)**

**How to Open:**
1. **Visit any CABS branch** with your documents
2. **Apply Online:** Visit cabs.co.zw → Open Account
3. **Call us:** +263 242 707 771 for guidance

**Account Types Available:**
• Savings Account
• Current Account
• Student Account
• Corporate/Business Account
• Diaspora Account

**Need a Card?** Debit cards are issued upon account opening. Contact us for card-specific requirements!"""

def loan_information_response():
    return """💰 **Loan Services at CABS**

**Available Loan Products:**
1. **Personal Loans:** For individuals with stable income (10% - 15% p.a.)
2. **Civil Servants Loans:** Special rates for government employees (10% - 15% p.a.)
3. **Salary-Based Loans:** For salaried individuals (12% - 18% p.a.)
4. **Home Loans/Mortgages:** For property purchase/construction (8% - 12% p.a.)
5. **Vehicle Loans:** For car/motorcycle purchase (10% - 16% p.a.)
6. **Business Loans:** For entrepreneurs and companies (14% - 20% p.a.)

**General Requirements:**
• Proof of income (payslip for 3 months)
• Valid ID
• Proof of residence
• Bank statements (3-6 months)

**Apply:**
1. **Branch Visit:** With supporting documents
2. **Online:** Through CABS website
3. **Contact:** Loan department at +263 242 707 771"""

def online_banking_response():
    return """📱 **Digital Banking Services**

**Multiple Ways to Bank Digitally:**

1. **Mobile App Banking:**
   • Download "CABS Mobile" from App Store/Play Store
   • View balances, transfer funds, pay bills

2. **WhatsApp Banking:**
   • Number: 0777 227 227
   • Check balances, mini statements

3. **USSD Banking:**
   • Dial *227# from your mobile
   • No internet needed, available 24/7

4. **Internet Banking:**
   • Visit: online.cabs.co.zw
   • Full banking services, secure login

**Troubleshooting:**
• **Forgot Password:** Use "Forgot Password" link on login page
• **Can't Login:** Call +263 242 707 771
• **Account Locked:** Visit branch with ID for reset"""

def account_types_response():
    return """🏦 **CABS Account Portfolio**

**Personal Banking:**
1. **CABS Savings Account**
   • Earn competitive interest
   • Minimum balance: $10
   • Free ATM card

2. **CABS Current Account**
   • Unlimited transactions
   • Cheque book facility
   • Overdraft facility available

3. **CABS Student Account**
   • Special rates for students
   • Low minimum balance
   • Educational benefits

**Business Banking:**
4. **CABS Business Account**
   • For SMEs and corporates
   • Bulk payment facilities
   • Merchant services

5. **CABS Corporate Account**
   • Large corporations
   • Treasury services
   • Customized solutions

**Visit any branch or call +263 242 707 771 to open an account today!**"""

def interest_rates_response():
    return """📈 **Current Interest Rates**

**Deposit Accounts:**
• **Savings Account:** 2.5% - 4.5% p.a.
• **Fixed Deposit (30 days):** 7.5% p.a.
• **Fixed Deposit (90 days):** 9.0% p.a.
• **Fixed Deposit (365 days):** 15.0% p.a.

**Loan Products:**
• **Personal Loans:** 12% - 18% p.a.
• **Civil Servants Loans:** 10% - 15% p.a.
• **Home Loans:** 8% - 12% p.a.
• **Business Loans:** 14% - 20% p.a.

**For the most current rates:**
• Visit any CABS branch
• Call +263 242 707 771
• Check cabs.co.zw

*Rates are indicative and may vary.*"""

def exchange_rates_response():
    return """💱 **CABS Foreign Exchange Rates**

**Exchange Rates USD (06 January 2026):**

| Currency | Buy | Sell |
|----------|-----|------|
| BWP | 0.0691 | 0.0751 |
| EUR | 1.1382 | 1.2087 |
| GBP | 1.3148 | 1.3963 |
| ZAR | 15.8372 | 16.8232 |
| CHF | 1.2268 | 1.3031 |
| AUD | 0.6532 | 0.6938 |

**Exchange Rates ZiG:**

| Currency | Buy | Sell |
|----------|-----|------|
| USD | 0.0398 | 0.0375 |
| BWP | 1.8096 | 1.9215 |
| EUR | 29.4520 | 31.2738 |

*Rates are subject to change. Visit cabs.co.zw for live rates.*"""

def omari_info_response():
    return """📱 **O'mari Digital Wallet by CABS**

**What is O'mari?**
O'mari is CABS's digital wallet for sending, receiving, and storing money digitally in both USD and ZiG.

**How to Register:**
1. **USSD Registration:** Dial *707# from any mobile
2. **WhatsApp Registration:** Message 'hi' to 0774 707 707
3. **Mobile App:** Download 'O'mari' from app stores

**O'mari Card Options:**
• **ZimSwitch Debit Card:** For ZiG transactions
• **VISA Debit Card:** For USD transactions (works internationally)

**Card Fees:**
• Issuance fee: $5 (one-time)
• Annual maintenance: $2

**Services Available:**
• Send/receive money
• Pay bills and merchants
• Buy airtime and data
• Check balances

**Contact O'mari Support:**
• WhatsApp: 0777 227 227
• Phone: +263 242 707 771
• Email: omari@cabs.co.zw"""

def transactional_accounts_response():
    return """💳 **Transactional Accounts at CABS**

**Gold Account (Gold Class):**
• **Minimum Balance:** USD $3
• **Monthly Fees:** None (if minimum balance maintained)
• **Features:**
  - Gold Debit Card (ZimSwitch & VISA)
  - Access to Gold Class Banking Halls
  - Priority customer service
  - Higher daily withdrawal limits

**Blue Account (Blue Class):**
• **Minimum Balance:** USD $2
• **Monthly Fees:** None (if minimum balance maintained)
• **Features:**
  - Blue Debit Card (ZimSwitch)
  - Standard banking services
  - Online banking access

**Senior Citizen Benefits:**
• Special discounts on transaction fees
• Priority service in branches
• Dedicated relationship managers

**Open an Account Today:**
Visit any CABS branch or call +263 242 707 771!"""

def products_services_response():
    return """📦 **CABS Products & Services**

**Personal Banking:**
• Transactional Accounts (Gold & Blue)
• Savings Products
• Loan Products
• Card Services

**Digital Banking:**
• O'mari Digital Wallet
• Internet Banking
• Mobile App Banking
• WhatsApp Banking (0777 227 227)
• USSD Banking (*227#)

**Investment & Wealth:**
• Unit Trusts
• Money Market Funds
• Fixed Deposits

**Insurance (Bancassurance):**
• Life Insurance
• Funeral Plans
• Motor & Home Insurance

**Specialized Services:**
• International Banking
• Safe Deposit Boxes
• Business Banking

**Getting Started:**
1. **Visit any CABS branch**
2. **Call us:** +263 242 707 771
3. **WhatsApp:** 0777 227 227
4. **Online:** cabs.co.zw"""

def card_types_response():
    return """💳 **CABS Card Portfolio**

**Available Debit Cards:**

**Gold Debit Card**
• **Type:** ZimSwitch & VISA
• **Linked to:** Gold Account
• **Features:** International transactions, online shopping, priority service
• **Fees:** No monthly fee for Gold Account holders

**Blue Debit Card**
• **Type:** ZimSwitch
• **Linked to:** Blue Account
• **Features:** Local transactions, ATM withdrawals
• **Fees:** No monthly fee for Blue Account holders

**O'mari VISA Debit Card**
• **Type:** VISA
• **Linked to:** O'mari USD Wallet
• **Features:** International online shopping
• **Fees:** $5 issuance, $2 annual maintenance

**O'mari ZimSwitch Debit Card**
• **Type:** ZimSwitch
• **Linked to:** O'mari ZiG Wallet
• **Features:** Local ZiG transactions
• **Fees:** $5 issuance, $2 annual maintenance

**Contact Card Services:**
• Phone: +263 242 707 771
• WhatsApp: 0777 227 227"""

# Response function mapping
RESPONSE_FUNCTIONS = {
    "account_opening": account_opening_response,
    "loan_information": loan_information_response,
    "online_banking": online_banking_response,
    "account_types": account_types_response,
    "interest_rates": interest_rates_response,
    "exchange_rates": exchange_rates_response,
    "omari_info": omari_info_response,
    "transactional_accounts": transactional_accounts_response,
    "products_services": products_services_response,
    "card_types": card_types_response
}

# ========== INTENT MATCHING FUNCTION ==========
def match_intent(user_input):
    user_input_lower = user_input.lower().strip()
    
    # Create a dictionary to track match scores
    intent_scores = {}
    
    # Check all intents
    for intent_tag, intent_data in INTENTS.items():
        score = 0
        
        # Check for pattern matches
        for pattern in intent_data["patterns"]:
            if pattern == user_input_lower:
                score += 30  # Exact match
            elif pattern in user_input_lower:
                score += 10  # Partial match
        
        # Check for keyword matches
        if "keywords" in intent_data:
            user_words = user_input_lower.split()
            for keyword in intent_data["keywords"]:
                if keyword in user_words:
                    score += 5
        
        # Store the score
        if score > 0:
            intent_scores[intent_tag] = score
    
    # Find the intent with the highest score
    if intent_scores:
        sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)
        best_intent, best_score = sorted_intents[0]
        
        # Only return intent if score is high enough
        if best_score >= 5:
            return best_intent
    
    return None

# ========== OPTIMIZED API CALL FUNCTION ==========
@st.cache_data(show_spinner=False, max_entries=100)
def get_cached_response(api_key, messages, model, temperature, max_tokens):
    """Cached API call for repeated questions"""
    if not api_key:
        return None
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://cabschat.streamlit.app",
            "X-Title": "CABS Banking Assistant"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            return f"⚠️ API Error {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return f"Error: {str(e)[:200]}"

def get_ai_response_optimized(api_key, user_message, chat_history=None, model="mistralai/mistral-7b-instruct:free", 
                              temperature=0.7, max_tokens=300, context_length=4):
    """Get AI response with CABS context"""
    if not api_key:
        return "Please provide an API key to use AI features."
    
    try:
        # Create system prompt for banking assistant
        system_prompt = """You are Tino, a helpful AI banking assistant for CABS (Central Africa Building Society) in Zimbabwe.

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
            recent_history = chat_history[-context_length:]
            for msg in recent_history:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Get response with caching
        return get_cached_response(api_key, messages, model, temperature, max_tokens)
            
    except Exception as e:
        return f"Error: {str(e)[:200]}"

# ========== HYBRID RESPONSE FUNCTION ==========
def get_hybrid_response(user_input, api_key, chat_history, selected_model, temperature, max_tokens, context_length):
    """Get response using hybrid approach"""
    # First try to match with rule-based intents
    intent = match_intent(user_input)
    
    if intent:
        # If we have a rule-based response, use it
        if intent in RESPONSE_FUNCTIONS:
            return RESPONSE_FUNCTIONS[intent](), "rule_based"
        elif intent in INTENTS and INTENTS[intent]["responses"][0] not in RESPONSE_FUNCTIONS:
            # Use canned response
            return random.choice(INTENTS[intent]["responses"]), "rule_based"
    
    # If no rule-based match, use AI
    if api_key:
        ai_response = get_ai_response_optimized(
            api_key, user_input, chat_history, selected_model,
            temperature, max_tokens, context_length
        )
        return ai_response, "ai"
    else:
        return "I can answer specific banking questions, but for general conversation, please provide an API key in the sidebar.", "rule_based"

# ========== CHAT INTERFACE ==========
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": """Hello! I'm Tino, your CABS Banking Assistant. 

I can help you with information about:
• **Accounts** - Savings, Current, Corporate accounts
• **Loans** - Personal loans, Mortgages, Business loans
• **Cards** - Debit cards, Credit cards
• **Digital Banking** - O'mari wallet, Online banking, Mobile app
• **Insurance** - Life, Property, Vehicle insurance
• **Branch Locations & Contact Information**

How can I assist you with CABS banking today?"""
        }
    ]

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "response_times" not in st.session_state:
    st.session_state.response_times = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Display average response time in sidebar
if st.session_state.response_times:
    avg_time = sum(st.session_state.response_times) / len(st.session_state.response_times)
    st.sidebar.metric("⏱️ Avg Response Time", f"{avg_time:.1f}s")

# ========== HANDLE USER INPUT ==========
if prompt := st.chat_input("Ask about CABS banking services..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.conversation_history.append({"role": "user", "content": prompt})
    
    # Get response based on selected mode
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("💭 Thinking...")
        
        start_time = time.time()
        
        if chat_mode == "Rule-Based Only":
            # Only use rule-based responses
            intent = match_intent(prompt)
            if intent:
                if intent in RESPONSE_FUNCTIONS:
                    response = RESPONSE_FUNCTIONS[intent]()
                    response_type = "rule_based"
                elif intent in INTENTS:
                    response = random.choice(INTENTS[intent]["responses"])
                    response_type = "rule_based"
                else:
                    response = "I can help with specific banking questions. Please ask about accounts, loans, cards, or other CABS services."
                    response_type = "rule_based"
            else:
                response = "I'm trained to answer specific banking questions. Please ask about CABS accounts, loans, cards, online banking, or contact information."
                response_type = "rule_based"
                
        elif chat_mode == "AI Only":
            # Only use AI responses
            if api_key:
                response = get_ai_response_optimized(
                    api_key, prompt, st.session_state.conversation_history, 
                    selected_model, temperature, max_tokens, context_length
                )
                response_type = "ai"
            else:
                response = "Please provide an API key in the sidebar to use AI responses."
                response_type = "rule_based"
                
        else:  # Hybrid mode
            response, response_type = get_hybrid_response(
                prompt, api_key, st.session_state.conversation_history,
                selected_model, temperature, max_tokens, context_length
            )
        
        end_time = time.time()
        total_time = end_time - start_time
        st.session_state.response_times.append(total_time)
        
        # Display response
        message_placeholder.markdown(response)
        
        # Show response type indicator
        if response_type == "ai":
            st.caption(f"🤖 AI Response • ⏱️ {total_time:.1f}s")
        else:
            st.caption(f"📚 Banking Knowledge • ⏱️ {total_time:.1f}s")
    
    # Add to history
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.conversation_history.append({"role": "assistant", "content": response})

# ========== FOOTER ==========
st.divider()
st.markdown("""
<div style="text-align: center; color: gray; font-size: 0.8em;">
    <p><b>💡 CABS Banking Assistant v2.0</b></p>
    <p>Mode: <b>{}</b> | Model: <b>{}</b></p>
    <p>For official banking services, visit <a href="https://www.cabs.co.zw" target="_blank">cabs.co.zw</a></p>
    <p>Emergency lost card: +263 242 707 771-9 • WhatsApp: 0777 227 227</p>
</div>
""".format(chat_mode, selected_model.split('/')[1].split(':')[0]), unsafe_allow_html=True)

# Add custom CSS
st.markdown("""
<style>
    .stChatMessage {
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    [data-testid="stChatMessageContent"] {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 8px;
    }
    .stButton button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)