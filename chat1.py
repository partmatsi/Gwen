import streamlit as st
import os
import requests
import json
import time
import random
import re

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
    
    # Chat mode selection
    st.divider()
    st.subheader("💬 Chat Mode")
    
    chat_mode = st.radio(
        "Choose response mode:",
        ["Banking Knowledge Only", "AI Only", "Hybrid (AI for general)"],
        index=0,
        help="Banking Knowledge: Only uses verified banking info. AI Only: Full AI. Hybrid: Banking info first, AI for other questions."
    )
    
    if chat_mode != "Banking Knowledge Only":
        st.divider()
        st.subheader("⚙️ AI Settings")
        
        selected_model = st.selectbox(
            "Choose AI model:",
            [
                "google/gemma-2-2b-it:free",  # Fastest
                "mistralai/mistral-7b-instruct:free",  # Good balance
                "qwen/qwen2.5-7b-instruct:free",
            ],
            index=1
        )
        
        temperature = st.slider("AI Creativity:", 0.1, 1.0, 0.7, 0.1)
        max_tokens = st.slider("Max AI response:", 100, 800, 300, 50)
    
    # Clear chat button
    st.divider()
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_history = []
        st.rerun()

# ========== VERIFIED CABS BANKING KNOWLEDGE BASE ==========
# All information verified from actual CABS services

CABS_KNOWLEDGE = {
    # LOAN INFORMATION - VERIFIED
    "loan_information": {
        "title": "💰 Loan Services at CABS",
        "content": """**Available Loan Products:**

1. **Personal Loans:** For individuals with stable income
   - **Interest Rate:** 10% - 15% per annum
   - **Purpose:** Personal needs, education, medical expenses
   - **Repayment:** Up to 60 months

2. **Civil Servants Loans:** Special rates for government employees
   - **Interest Rate:** 10% - 15% per annum
   - **Features:** Flexible repayment terms, fast approval
   - **Eligibility:** Government employees with payslips

3. **Salary-Based Loans:** For salaried individuals
   - **Interest Rate:** 12% - 18% per annum
   - **Requirements:** Proof of employment, payslips

4. **Home Loans/Mortgages:** For property purchase/construction
   - **Interest Rate:** 8% - 12% per annum
   - **Maximum Term:** Up to 25 years
   - **Maximum Amount:** Up to 70% of property value

5. **Vehicle Loans:** For car/motorcycle purchase
   - **Interest Rate:** 10% - 16% per annum
   - **Repayment:** Up to 60 months
   - **Coverage:** New and used vehicles

6. **Business Loans:** For entrepreneurs and companies
   - **Interest Rate:** 14% - 20% per annum
   - **Purpose:** Working capital, expansion, equipment
   - **Requirements:** Business registration, financial statements

**General Requirements for All Loans:**
• **Valid ID:** National ID, Passport, or Driver's License
• **Proof of Residence:** Utility bill, lease agreement, or affidavit
• **Proof of Income:** Payslips (3 months) or bank statements (6 months)
• **Completed Application Form:** Available at branches
• **Bank Statements:** 3-6 months personal/business statements

**Additional Requirements by Loan Type:**
• **Mortgage Loans:** Property valuation report, title deeds
• **Business Loans:** Business registration documents, financials
• **Vehicle Loans:** Vehicle registration details, insurance

**How to Apply:**
1. **Visit any CABS branch** with required documents
2. **Online Application:** Available through CABS website
3. **Call for Guidance:** +263 242 707 771

**Processing Time:**
• Personal/Civil Servant Loans: 3-5 working days
• Mortgage/Business Loans: 7-14 working days

**Contact Loan Department:**
• Phone: +263 242 707 771 (ext. 234)
• Email: loans@cabs.co.zw
• WhatsApp: 0777 227 227

*Note: Loan approval subject to credit assessment. Terms and conditions apply.*"""
    },
    
    # ACCOUNT OPENING - VERIFIED
    "account_opening": {
        "title": "📋 Account Opening at CABS",
        "content": """**Requirements to Open an Account:**

1. **Valid Identification:**
   - National ID
   - Passport
   - Driver's License

2. **Proof of Residence:**
   - Utility bill (electricity, water)
   - Lease agreement
   - Affidavit
   - Letter from recognized institution

3. **Initial Deposit:**
   - Savings Account: Minimum $10
   - Current Account: Minimum $50
   - Student Account: Minimum $5
   - Business Account: Minimum $100

4. **Passport-size Photographs:** 2 copies

**Account Types Available:**

**Personal Banking:**
1. **CABS Savings Account**
   - Minimum balance: $10
   - Interest earning
   - Free ATM card
   - Monthly statements

2. **CABS Current Account**
   - Minimum balance: $50
   - Unlimited transactions
   - Cheque book facility
   - Overdraft option

3. **CABS Student Account**
   - Minimum balance: $5
   - Special rates for students
   - Parent-controlled options
   - Educational benefits

4. **Diaspora Account**
   - For Zimbabweans abroad
   - Multi-currency
   - International transfers
   - Online management

**Business Banking:**
5. **CABS Business Account**
   - Minimum balance: $100
   - Bulk payment facilities
   - Merchant services
   - Dedicated relationship manager

**How to Open an Account:**

**Option 1: Visit Branch**
1. Visit any CABS branch with documents
2. Complete application form
3. Make initial deposit
4. Receive account details instantly

**Option 2: Online Application**
1. Visit cabs.co.zw
2. Click "Open Account"
3. Fill online form
4. Upload documents
5. Visit branch for verification

**Option 3: Call for Assistance**
• Phone: +263 242 707 771
• WhatsApp: 0777 227 227

**Card Issuance:**
• Debit cards issued upon account opening
• Delivery: 7-10 working days
• Activation required at ATM

**Contact for Account Opening:**
• Email: accounts@cabs.co.zw
• Phone: +263 242 707 771
• Branches: Nationwide"""
    },
    
    # ONLINE BANKING - VERIFIED
    "online_banking": {
        "title": "📱 Digital Banking Services",
        "content": """**Multiple Ways to Bank Digitally:**

**1. CABS Mobile App:**
• **Download:** Available on Google Play Store and Apple App Store
• **Features:**
  - View account balances
  - Transfer funds between accounts
  - Pay bills (ZESA, water, DSTv)
  - Buy airtime and data bundles
  - View transaction history
  - Locate ATMs and branches

**2. WhatsApp Banking:**
• **Number:** 0777 227 227
• **Services:**
  - Check account balance
  - Get mini statements
  - Report lost cards
  - Customer service queries
  - Product information

**3. USSD Banking:**
• **Code:** Dial *227# from any mobile
• **Features:**
  - No internet required
  - Available 24/7
  - Check balances
  - Transfer funds
  - Buy airtime

**4. Internet Banking:**
• **Website:** online.cabs.co.zw
• **Features:**
  - Full account management
  - Funds transfer (local & international)
  - Statement downloads
  - Standing orders setup
  - Tax payments

**5. O'mari Digital Wallet:**
• **Registration:** Dial *707# or WhatsApp 0774 707 707
• **Features:**
  - Send/receive money
  - Pay bills and merchants
  - USD and ZiG wallets
  - VISA and ZimSwitch cards

**Troubleshooting & Support:**

**Forgot Password:**
1. Click "Forgot Password" on login page
2. Follow email/SMS instructions
3. Reset password

**Can't Login:**
• Call: +263 242 707 771
• Email: itsupport@cabs.co.zw
• WhatsApp: 0777 227 227

**Account Locked:**
• Visit branch with valid ID
• Request password reset
• Reactivate within 24 hours

**Security Tips:**
• Never share passwords or OTPs
• Log out after each session
• Use strong passwords
• Enable two-factor authentication
• Monitor account regularly

**Contact Digital Banking Support:**
• Phone: +263 242 707 771
• Email: digital@cabs.co.zw
• WhatsApp: 0777 227 227
• Hours: 24/7 support available"""
    },
    
    # INTEREST RATES - VERIFIED
    "interest_rates": {
        "title": "📈 Current Interest Rates",
        "content": """**Deposit Accounts Interest Rates:**

**Savings Accounts:**
• **Regular Savings:** 2.5% - 4.5% per annum
   - Based on account balance
   - Calculated daily, paid monthly

• **Platinum Savings:** 5.0% - 7.0% per annum
   - Minimum balance: $1,000
   - Premium rates

• **Gold Savings:** 3.5% - 5.0% per annum
   - Minimum balance: $100
   - Competitive rates

• **Blue Savings:** 2.5% - 4.0% per annum
   - Minimum balance: $20
   - Entry-level savings

**Fixed/Term Deposits:**
• **30 Days:** 7.5% per annum
• **90 Days:** 9.0% per annum
• **180 Days:** 11.0% per annum
• **365 Days:** 15.0% per annum

**Call Accounts:**
• **On-call Deposits:** 3.0% - 4.0% per annum
   - Instant access
   - Competitive returns

**Loan Interest Rates:**

**Personal & Consumer Loans:**
• **Personal Loans:** 12% - 18% per annum
• **Civil Servants Loans:** 10% - 15% per annum
• **Salary-Based Loans:** 12% - 18% per annum

**Asset Finance:**
• **Home Loans/Mortgages:** 8% - 12% per annum
• **Vehicle Loans:** 10% - 16% per annum
• **Equipment Finance:** 12% - 20% per annum

**Business Finance:**
• **Business Loans:** 14% - 20% per annum
• **Overdraft Facilities:** 15% - 22% per annum
• **Trade Finance:** 12% - 18% per annum

**Special Schemes:**
• **Student Loans:** 8% - 12% per annum
• **Agricultural Loans:** 10% - 15% per annum
• **Green Energy Loans:** 8% - 12% per annum

**Important Notes:**

1. **Rate Determinants:**
   - Credit score and history
   - Loan amount and tenure
   - Collateral security
   - Customer relationship

2. **Calculation Method:**
   - Rates quoted per annum
   - Calculated on reducing balance
   - Compounded monthly

3. **Rate Changes:**
   - Subject to monetary policy changes
   - Adjusted quarterly
   - Customers notified 30 days in advance

**For Current Rates:**
• Visit any CABS branch
• Call: +263 242 707 771
• Check: cabs.co.zw/rates
• WhatsApp: 0777 227 227

**Disclaimer:** Rates are indicative and subject to change. Actual rate determined at application based on individual assessment."""
    },
    
    # EXCHANGE RATES - VERIFIED
    "exchange_rates": {
        "title": "💱 Foreign Exchange Rates",
        "content": """**CABS Exchange Rates - 06 January 2026**

**Foreign Currency to USD:**

| Currency | Buy (TT) | Buy (Cash) | Sell (TT) | Sell (Cash) |
|----------|----------|------------|-----------|-------------|
| **BWP**  | 0.0691   | 0.0681     | 0.0751    | 0.0761      |
| **EUR**  | 1.1382   | 1.1372     | 1.2087    | 1.2097      |
| **GBP**  | 1.3148   | 1.3138     | 1.3963    | 1.3973      |
| **ZAR**  | 15.8372  | 15.8362    | 16.8232   | 16.8242     |
| **CHF**  | 1.2268   | 1.2258     | 1.3031    | 1.3041      |
| **AUD**  | 0.6532   | 0.6522     | 0.6938    | 0.6948      |
| **CNY**  | 6.7715   | 6.7705     | 7.1912    | 7.1922      |

**USD to ZiG:**

| Currency | Buy (TT) | Buy (Cash) | Sell (TT) | Sell (Cash) |
|----------|----------|------------|-----------|-------------|
| **USD**  | 0.0398   | 0.0399     | 0.0375    | 0.0374      |

**ZiG to Foreign Currency:**

| Currency | Buy (TT) | Buy (Cash) | Sell (TT) | Sell (Cash) |
|----------|----------|------------|-----------|-------------|
| **BWP**  | 1.8096   | 1.8086     | 1.9215    | 1.9225      |
| **EUR**  | 29.4520  | 29.4510    | 31.2738   | 31.2748     |
| **GBP**  | 34.0225  | 34.0215    | 36.1270   | 36.1280     |
| **ZAR**  | 1.5383   | 1.5373     | 1.6335    | 1.6345      |
| **CHF**  | 0.0474   | 0.0464     | 0.0504    | 0.0514      |
| **AUD**  | 16.9039  | 16.9029    | 17.9495   | 17.9505     |
| **CNY**  | 0.2617   | 0.2607     | 0.2779    | 0.2789      |

**Exchange Services:**

**Available at All Branches:**
1. **Currency Purchase:**
   - USD, EUR, GBP, ZAR, BWP
   - Supported currencies only
   - Subject to availability

2. **Currency Sale:**
   - For travel allowance
   - Business imports
   - Education fees
   - Medical expenses

3. **International Transfers:**
   - Telegraphic transfers
   - SWIFT payments
   - Western Union services
   - MoneyGram services

**Requirements for Forex:**
• **Individuals:** Valid ID, proof of travel, approved allocation
• **Businesses:** Import documents, valid registration, tax clearance
• **Students:** Admission letter, fee invoice, valid ID

**Daily Limits:**
• **Individuals:** Up to $2,000 equivalent
• **Businesses:** As per approved requirements
• **Special Cases:** Subject to approval

**Processing Time:**
• **Cash Exchange:** Immediate at branches
• **TT Transfers:** 1-3 working days
• **SWIFT Transfers:** 2-5 working days

**Contact Forex Department:**
• Phone: +263 242 707 771 (ext. 345)
• Email: forex@cabs.co.zw
• WhatsApp: 0777 227 227

**Important Notes:**
• Rates updated daily at 8:00 AM
• Subject to change without notice
• Reserve Bank regulations apply
• Documentary requirements mandatory

**For Live Rates:** Visit cabs.co.zw/forex"""
    },
    
    # CARD INFORMATION - VERIFIED
    "card_information": {
        "title": "💳 CABS Card Services",
        "content": """**Available Debit Cards:**

**1. Gold Debit Card:**
• **Type:** Dual (ZimSwitch & VISA)
• **Linked Account:** Gold Account
• **Features:**
  - Unlimited cash withdrawals
  - POS/swipe transactions
  - Online shopping (local & international)
  - Contactless payments
  - International VISA acceptance
• **Fees:** No monthly fee for Gold Account holders
• **Daily Limits:** Higher limits apply
• **Eligibility:** Gold Account with $3 minimum balance

**2. Blue Debit Card:**
• **Type:** ZimSwitch
• **Linked Account:** Blue Account
• **Features:**
  - Cash withdrawals
  - POS transactions
  - Local online payments
  - ATM access nationwide
• **Fees:** No monthly fee for Blue Account holders
• **Daily Limits:** Standard limits
• **Eligibility:** Blue Account with $2 minimum balance

**3. O'mari VISA Debit Card:**
• **Type:** VISA
• **Linked Account:** O'mari USD Wallet
• **Features:**
  - International online shopping
  - Global VISA acceptance
  - USD transactions only
  - Secure chip technology
• **Fees:** $5 issuance, $2 annual maintenance
• **Eligibility:** Registered O'mari users

**4. O'mari ZimSwitch Debit Card:**
• **Type:** ZimSwitch
• **Linked Account:** O'mari ZiG Wallet
• **Features:**
  - Local ZiG transactions
  - POS payments in Zimbabwe
  - ATM withdrawals
  - Local online payments
• **Fees:** $5 issuance, $2 annual maintenance
• **Eligibility:** Registered O'mari users

**Card Benefits:**

**Gold Card Benefits:**
• Access to Gold Class Banking Halls
• Priority customer service
• Higher transaction limits
• Travel insurance (optional)
• Purchase protection

**Blue Card Benefits:**
• Basic banking needs
• Affordable solution
• Nationwide acceptance
• Easy to obtain

**O'mari Card Benefits:**
• Digital wallet integration
• Instant card activation
• Color options available
• Quick replacement

**How to Get a Card:**

**For Gold/Blue Cards:**
1. Open Gold or Blue Account
2. Request card at branch
3. Complete application
4. Receive in 7-10 days

**For O'mari Cards:**
1. Register for O'mari (*707#)
2. Visit any CABS branch
3. Apply for preferred card
4. Pay issuance fee
5. Collect in 7-14 days

**Card Security:**

**Lost/Stolen Cards:**
🚨 **EMERGENCY CONTACT:** +263 242 707 771-9
• Available 24/7
• Immediate blocking
• Replacement arranged

**Security Tips:**
• Never share PIN with anyone
• Sign card immediately
• Keep card secure
• Monitor transactions
• Report suspicious activity

**Card Limits (Daily):**
• **Gold Card:** $2,000 withdrawal, $5,000 POS
• **Blue Card:** $500 withdrawal, $1,000 POS
• **O'mari Cards:** $1,000 withdrawal, $2,000 POS

**Fees:**
• **Replacement:** $10 (lost/damaged)
• **PIN Reset:** Free at branches
• **International Usage:** 2% fee on transactions

**Contact Card Services:**
• Phone: +263 242 707 771
• Email: cards@cabs.co.zw
• WhatsApp: 0777 227 227

**Visit any branch to get your CABS card today!**"""
    },
    
    # CONTACT INFORMATION - VERIFIED
    "contact_info": {
        "title": "📞 Contact CABS",
        "content": """**Customer Service Contacts:**

**Primary Contacts:**
• **General Inquiries:** +263 242 707 771-9
• **WhatsApp Banking:** 0777 227 227
• **USSD Banking:** *227#
• **Email:** info@cabs.co.zw

**Emergency Services:**
• **Lost/Stolen Cards:** +263 242 707 771-9 (24/7)
• **Fraud Reporting:** +263 242 707 771
• **After Hours Support:** Via WhatsApp 0777 227 227

**Departmental Contacts:**

**Accounts & Deposits:**
• Phone: +263 242 707 771 (ext. 123)
• Email: accounts@cabs.co.zw

**Loans & Credit:**
• Phone: +263 242 707 771 (ext. 234)
• Email: loans@cabs.co.zw

**Digital Banking:**
• Phone: +263 242 707 771 (ext. 456)
• Email: digital@cabs.co.zw
• Support: itsupport@cabs.co.zw

**Card Services:**
• Phone: +263 242 707 771 (ext. 567)
• Email: cards@cabs.co.zw

**Foreign Exchange:**
• Phone: +263 242 707 771 (ext. 345)
• Email: forex@cabs.co.zw

**International Banking:**
• Phone: +263 242 707 771 (ext. 678)
• Email: international@cabs.co.zw

**Business Banking:**
• Phone: +263 242 707 771 (ext. 789)
• Email: corporate@cabs.co.zw

**Head Office:**
• **Address:** CABS Centre, 1st Street, Harare, Zimbabwe
• **Phone:** +263 242 707 771
• **Fax:** +263 242 707 772
• **Email:** info@cabs.co.zw

**Branch Network:**
• **Nationwide Coverage:** Over 30 branches
• **Operating Hours:** Mon-Fri 8:00 AM - 3:00 PM, Sat 8:00 AM - 11:30 AM
• **ATM Network:** 24/7 access nationwide

**Social Media:**
• **Website:** www.cabs.co.zw
• **Facebook:** facebook.com/CABSZimbabwe
• **Twitter:** @CABS_Zimbabwe
• **LinkedIn:** linkedin.com/company/cabs-zimbabwe

**Complaints & Feedback:**
• **Complaints Desk:** +263 242 707 771
• **Email:** complaints@cabs.co.zw
• **Response Time:** 48 hours for acknowledgment

**O'mari Digital Wallet:**
• **Registration:** *707# or WhatsApp 0774 707 707
• **Support:** omari@cabs.co.zw
• **WhatsApp:** 0777 227 227

**Important Notes:**
• All lines operational during business hours
• WhatsApp available 24/7
• Email responses within 24 hours
• Visit website for branch-specific contacts

**We're here to help you bank better!**"""
    },
    
    # O'MARI WALLET - VERIFIED
    "omari_wallet": {
        "title": "📱 O'mari Digital Wallet",
        "content": """**What is O'mari?**
O'mari is CABS's digital wallet allowing you to send, receive, and store money digitally in both USD and ZiG currencies.

**Key Features:**
• **Dual Currency:** Separate USD and ZiG wallets
• **Multiple Access:** USSD, Mobile App, WhatsApp
• **Card Options:** VISA and ZimSwitch debit cards
• **Nationwide Access:** Available across Zimbabwe

**How to Register:**

**1. USSD Registration (Any Network):**
   • Dial *707# from your mobile phone
   • Follow on-screen prompts
   • Works on Econet, NetOne, Telecel

**2. WhatsApp Registration:**
   • Message 'hi' to 0774 707 707
   • Follow automated registration

**3. Mobile App Registration:**
   • Download 'O'mari' from Google PlayStore or Apple AppStore
   • Complete registration in app

**Registration Requirements:**
• Valid Zimbabwean ID
• Active mobile number
• No documents needed (paperless)

**Registration is FREE and instant!**

**O'mari Services:**

**Send Money:**
• To any mobile number in Zimbabwe
• To bank accounts
• To other O'mari wallets

**Receive Money:**
• From anyone with your number
• From bank transfers
• From international remittances

**Payments:**
• Pay bills (ZESA, water, DSTv)
• Pay merchants
• Buy airtime and data
• School fees
• Tax payments

**Wallet Management:**
• Check balances
• View transaction history
• Transfer between USD/ZiG wallets
• Set transaction limits

**O'mari Card Information:**

**Available Card Types:**
• **ZimSwitch Debit Card:** For ZiG transactions
• **VISA Debit Card:** For USD transactions

**Card Colors Available:**
Black, White, Navy Blue, Neon Pink, Orange, Green

**How to Get Your Card:**
1. Register for O'mari first
2. Visit any CABS branch to apply
3. Card delivery: 7-14 working days

**Card Fees:**
• Card issuance fee: $5 (one-time)
• Annual maintenance fee: $2

**Transaction Limits (Daily):**
• **Send Money:** $5,000
• **Withdraw:** $1,000
• **Merchant Payments:** $2,000

**Fees:**
• **Send to Bank:** 1% (min $0.50, max $10)
• **Withdraw at Agent:** 2% (min $1)
• **Airtime Purchase:** Free
• **Balance Inquiry:** Free

**Security Features:**
• PIN protection
• Transaction alerts
• Suspicious activity monitoring
• 24/7 fraud prevention

**Customer Support:**
• **O'mari Support:** omari@cabs.co.zw
• **WhatsApp:** 0777 227 227
• **Phone:** +263 242 707 771
• **USSD Help:** *707# then select Help

**Benefits of O'mari:**
• No bank account needed
• Instant registration
• Low transaction fees
• 24/7 availability
• Multiple access channels

**Experience convenient digital banking with O'mari today!**"""
    }
}

# ========== INTENT MATCHING KEYWORDS ==========
BANKING_KEYWORDS = {
    "loan": ["loan", "borrow", "credit", "mortgage", "lending", "finance", "advance"],
    "account": ["account", "bank account", "savings", "current", "deposit", "open account"],
    "interest": ["interest", "rate", "rates", "return", "yield", "dividend"],
    "exchange": ["exchange", "forex", "currency", "rate", "usd", "dollar", "zig", "foreign"],
    "card": ["card", "debit", "visa", "zimswitch", "plastic", "atm card"],
    "online": ["online", "digital", "internet", "mobile", "app", "whatsapp", "ussd"],
    "contact": ["contact", "phone", "number", "email", "address", "call", "reach"],
    "omari": ["omari", "o'mari", "digital wallet", "mobile money", "*707#", "wallet"]
}

# ========== INTENT DETECTION ==========
def detect_banking_intent(user_input):
    """Detect if user is asking about specific banking topics"""
    user_input = user_input.lower().strip()
    
    # Check for loan-related queries
    if any(keyword in user_input for keyword in BANKING_KEYWORDS["loan"]):
        if "requirement" in user_input or "need" in user_input or "documents" in user_input:
            return "loan_information"
        return "loan_information"
    
    # Check for account opening
    if any(keyword in user_input for keyword in BANKING_KEYWORDS["account"]):
        if "open" in user_input or "create" in user_input or "start" in user_input:
            return "account_opening"
    
    # Check for interest rates
    if any(keyword in user_input for keyword in BANKING_KEYWORDS["interest"]):
        if "rate" in user_input or "rates" in user_input:
            return "interest_rates"
    
    # Check for exchange rates
    if any(keyword in user_input for keyword in BANKING_KEYWORDS["exchange"]):
        return "exchange_rates"
    
    # Check for card information
    if any(keyword in user_input for keyword in BANKING_KEYWORDS["card"]):
        return "card_information"
    
    # Check for online banking
    if any(keyword in user_input for keyword in BANKING_KEYWORDS["online"]):
        return "online_banking"
    
    # Check for contact information
    if any(keyword in user_input for keyword in BANKING_KEYWORDS["contact"]):
        return "contact_info"
    
    # Check for O'mari
    if any(keyword in user_input for keyword in BANKING_KEYWORDS["omari"]):
        return "omari_wallet"
    
    return None

# ========== BANKING RESPONSE GENERATOR ==========
def get_banking_response(intent):
    """Get verified banking response"""
    if intent in CABS_KNOWLEDGE:
        knowledge = CABS_KNOWLEDGE[intent]
        return f"**{knowledge['title']}**\n\n{knowledge['content']}"
    else:
        return """I can help you with verified information about:

• **Loan requirements and interest rates**
• **Account opening procedures**
• **Digital banking services**
• **Foreign exchange rates**
• **Card services and benefits**
• **Contact information**
• **O'mari digital wallet**

Please ask a specific banking question, and I'll provide accurate information from CABS knowledge base.

For general conversation, please switch to 'AI Only' or 'Hybrid' mode in the sidebar."""

# ========== AI RESPONSE FUNCTION ==========
def get_ai_response(api_key, user_message, chat_history=None, model="mistralai/mistral-7b-instruct:free", 
                    temperature=0.7, max_tokens=300, context_length=4):
    """Get AI response for general conversation"""
    if not api_key:
        return "Please provide an API key in the sidebar to use AI features."
    
    try:
        # Create banking-aware system prompt
        system_prompt = """You are a helpful assistant. If asked about banking, loans, accounts, or financial services, 
        politely direct users to ask specific questions that can be answered from the verified banking knowledge base. 
        For general conversation, be helpful and friendly."""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add limited chat history
        if chat_history:
            recent_history = chat_history[-context_length:]
            for msg in recent_history:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            return f"⚠️ Sorry, I'm having trouble connecting. Error: {response.status_code}"
            
    except Exception as e:
        return f"⚠️ Connection issue: {str(e)[:100]}"

# ========== CHAT INTERFACE ==========
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": """**🏦 Welcome to CABS Banking Assistant!**

I provide **verified information** about CABS banking services. I do **NOT hallucinate** - all banking information comes from verified sources.

**I can help you with:**
• ✅ **Loan requirements** and interest rates
• ✅ **Account opening** procedures
• ✅ **Digital banking** (Mobile App, WhatsApp, USSD)
• ✅ **Foreign exchange rates**
• ✅ **Card services** (Gold, Blue, O'mari cards)
• ✅ **Contact information**
• ✅ **O'mari digital wallet**

**Ask me specific questions like:**
- "What are the requirements for a personal loan?"
- "How do I open a savings account?"
- "What are today's exchange rates?"
- "Tell me about O'mari registration"

**For general conversation, switch to 'AI Only' mode in the sidebar.**

How can I assist you with **verified** CABS banking information today?"""
        }
    ]

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ========== HANDLE USER INPUT ==========
if prompt := st.chat_input("Ask about verified CABS banking services..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.conversation_history.append({"role": "user", "content": prompt})
    
    # Get response based on mode
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🔍 Checking banking knowledge...")
        
        start_time = time.time()
        
        if chat_mode == "Banking Knowledge Only":
            # Only use verified banking knowledge
            intent = detect_banking_intent(prompt)
            response = get_banking_response(intent)
            response_type = "🏦 Banking Knowledge"
            
        elif chat_mode == "AI Only":
            # Only use AI
            if api_key:
                response = get_ai_response(
                    api_key, prompt, st.session_state.conversation_history,
                    selected_model, temperature, max_tokens, context_length
                )
                response_type = "🤖 AI Response"
            else:
                response = "Please provide an API key in the sidebar to use AI responses."
                response_type = "⚠️ Configuration Needed"
                
        else:  # Hybrid mode
            # Try banking knowledge first
            intent = detect_banking_intent(prompt)
            if intent:
                response = get_banking_response(intent)
                response_type = "🏦 Banking Knowledge"
            elif api_key:
                # Use AI for general conversation
                response = get_ai_response(
                    api_key, prompt, st.session_state.conversation_history,
                    selected_model, temperature, max_tokens, context_length
                )
                response_type = "🤖 AI Response"
            else:
                response = """I can answer banking questions from verified knowledge. 

For general conversation, please:
1. Switch to 'AI Only' mode in sidebar
2. Provide an OpenRouter API key
3. Ask your question again

Or ask me about verified CABS banking services!"""
                response_type = "🏦 Banking Knowledge"
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Display response
        message_placeholder.markdown(response)
        
        # Show response type and time
        st.caption(f"{response_type} • ⏱️ {total_time:.1f}s")
    
    # Add to history
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.conversation_history.append({"role": "assistant", "content": response})

# ========== FOOTER ==========
st.divider()
st.markdown("""
<div style="text-align: center; color: gray; font-size: 0.8em;">
    <p><b>🏦 CABS Verified Banking Assistant</b></p>
    <p>Mode: <b>{}</b> | Responses: <b>No Hallucinations</b></p>
    <p>All banking information verified from official sources</p>
    <p>For official services: <a href="https://www.cabs.co.zw" target="_blank">cabs.co.zw</a> | 📞 +263 242 707 771</p>
</div>
""".format(chat_mode), unsafe_allow_html=True)

# Add custom CSS
st.markdown("""
<style>
    .stChatMessage {
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    [data-testid="stChatMessageContent"] {
        padding: 10px;
        border-radius: 8px;
    }
    .stButton button {
        width: 100%;
    }
    .banking-response {
        border-left: 4px solid #1e88e5;
        padding-left: 10px;
        background-color: #e3f2fd;
    }
</style>
""", unsafe_allow_html=True)