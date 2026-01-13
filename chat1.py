import streamlit as st
import os
import requests
import json
import time
from datetime import datetime
import re
import random

# ========== INTENTS AND DATABASES ==========
INTENTS = {
    "greeting": {
        "patterns": [
            "hi", "hello", "hey", "good morning", "good afternoon", "ndeipi", "kurisei", "madii", 
            "hesi", "good evening", "howdy", "hi there", "how are you", "how is it",
        ],
        "responses": [
            "Hi! Welcome to CABS Banking Assistant. How can I help you today?", 
            "Hello! I'm here to assist with all your CABS banking needs.", 
            "Greetings! How can I assist you with your banking today?",
        ],
        "keywords": ["hi", "hello", "hey", "good", "morning", "afternoon", "evening", "ndeipi", "kurisei", "madii", "hesi", "howdy"]
    },
    "who_are_you": {
        "patterns": [
            "who are you", "what are you", "introduce yourself", "are you an ai assistant", 
            "your name", "ndiwe ani", "what is your purpose", "tell me about yourself", 
            "are you human", "are you a robot", "are you a bot", "what is your identity",
        ],
        "responses": [
            "I'm Tino an AI assistant created to help CABS customers with their banking needs", 
            "I'm Tino a virtual banking assistant designed to provide information about CABS services.", 
            "I'm Tino a CABS banking chatbot created to assist customers with their financial queries.",
        ],
        "keywords": ["who", "you", "name", "introduce", "yourself", "purpose", "identity", "robot", "bot", "ai", "assistant", "ndiwe", "ani"]
    },
    "creator_info": {
        "patterns": [
            "who is ishmael", "who created you", "who made you", "who built you", 
            "who developed you", "who programmed you", "who designed you", "tell me about ishmael", 
            "who is your creator", "who is your developer", "who is your maker", 
            "who is your programmer", "who is your maker", "who built this chatbot", 
            "who created this bot", "who made this assistant", "Do you know ishmael", "who made you",
        ],
        "responses": [
            "Ishmael is the AI Engineer who created me! He designed and developed this banking assistant to help CABS customers with their financial needs.", 
            "I was created by Ishmael, an AI Engineer who built me specifically for CABS banking services.", 
            "My creator is Ishmael - he's the AI Engineer who designed and programmed me to assist with CABS banking queries!", 
            "Ishmael is my creator! He's the AI Engineer who developed this banking assistant to provide excellent service to CABS customers.",
        ],
        "keywords": ["ishmael", "creator", "created", "made", "built", "developed", "programmed", "designed", "maker", "developer", "engineer"]
    },
    "lost_card": {
        "patterns": [
            "lost my card", "stolen card", "card stolen", "missing card", "I can't see my card", 
            "lost debit card", "lost visa card", "card is lost", "I have lost my card", 
            "someone took my card", "can't find my card", "reporting missing card", 
            "My card is stolen", "report lost card", "block my card", "card missing", 
            "suspicious transaction alerts", "my card is gone", "card disappeared", 
            "where is my card", "cannot locate my card", "my card is not with me", 
            "card has been taken", "my card was stolen", "i think i lost my card", 
            "possibly lost my card", "might have lost my card", "card not in wallet", 
        ],
        "responses": [
            "🚨 **URGENT: Lost/Stolen Card**\n\nPlease call us IMMEDIATELY to block your card:\n📞 **+263 242 707 771-9**\n\nWe'll block your card instantly to prevent unauthorized use and help you order a replacement. Would you like our WhatsApp number for faster assistance?", 
            "**EMERGENCY CARD BLOCKING**\n\nFor lost or stolen cards, contact us RIGHT AWAY:\n• **Phone:** +263 242 707 771-9\n• **WhatsApp:** 0777 227 227\n\nWe'll secure your account and guide you through getting a new card.", 
            "🔴 **IMMEDIATE ACTION REQUIRED: Lost Card**\n\n🚨 **Emergency Contact:** +263 242 707 771-9\n\nWe need to block your card immediately to prevent fraud. Please call us NOW or use WhatsApp: 0777 227 227 for instant assistance.", 
            "⚠️ **CRITICAL: Card Security Alert**\n\nYour card appears to be missing! Contact us URGENTLY:\n📞 **24/7 Emergency Line:** +263 242 707 771-9\n💬 **WhatsApp:** 0777 227 227\n\nWe'll secure your account and arrange a replacement card."
        ],
        "keywords": ["lost", "card", "stolen", "missing", "block", "report", "emergency", "debit", "visa", "stolen", "disappeared", "cannot", "find"]
    },
    "account_opening": {
        "patterns": [
            "how do I open an account", "i need a card ", "i need a cabs card", 
            "open account", "new account", "i need a cabs account", "account opening", 
            "start banking", "become customer", "open savings account", 
            "open current account", "i need account", "need account", "want account", 
            "create account", "get account", "apply for account", "account application", 
            "i need cabs account", "need cabs account", "want cabs account", "open cabs account"
        ],
        "responses": ["account_opening"],
        "keywords": ["open", "account", "new", "create", "start", "apply", "application", "banking", "customer", "savings", "current", "need", "want", "card", "cabs"]
    },
    "loan_information": {
        "patterns": [
            "how to get a loan", "apply for loan", "need loan", "want loan", "loans",
            "Do you have civil servants loans", "do you off civil servants", 
            "tell me about civils servants loans", "i need a loan", "loan requirements", 
            "personal loan", "home loan", "mortgage", "which loans do you offer", 
            "tell me about loans", "business loan", "car loan", "vehicle loan", 
            "loan application", "loan interest rates", "loan rates", "loan calculator", 
            "loan eligibility", "loan for civil servants", "loan for teachers", 
            "loan for nurses", "loan for government workers", "loan for employees", 
            "salary loan", "payroll loan", "get loan", "i need a loan", "loan options", 
            "types of loans", "what loans do you offer", "loan amount", "maximum loan", 
            "minimum loan", "loan tenure", "loan repayment", "loan period", 
            "loan duration", "how much can i borrow", "loan criteria", 
            "loan qualifications", "loan documents needed", "loan processing time", 
            "loan approval", "how long for loan approval", "loan disbursement", 
            "secured loan", "unsecured loan", "collateral for loan", "guarantor for loan",
            "cabs loans", "tell me about cabs loans", "information about cabs loans", "what is cabs loans",
            "cabs loan", "tell me about cabs loan", "information about cabs loan", "what is cabs loan"
        ],
        "responses": ["loan_information"],
        "keywords": ["loan", "borrow", "credit", "mortgage", "personal", "home", "business", "car", "vehicle", "apply", "application", "civil", "servant", "government", "teacher", "nurse", "salary", "requirements", "eligibility", "rate", "interest", "cabs"]
    },
    "online_banking": {
        "patterns": [
            "online banking", "internet banking", "mobile banking", "USSD banking", 
            "whatsapp banking", "digital banking", "reset password", "forgot password", 
            "can't login"
        ],
        "responses": ["online_banking"],
        "keywords": ["online", "internet", "mobile", "digital", "banking", "USSD", "whatsapp", "reset", "password", "forgot", "login", "app"]
    },
    "branch_info": {
        "patterns": [
            "branch location", "working hours", "nearest branch", "where is branch", 
            "find branch", "branch near me", "branch locations", "find branch", 
            "branch hours", "opening hours", 
        ],
        "responses": [
            "🏦 **CABS Branch Information**\n\nCABS has branches nationwide across Zimbabwe. Most branches operate:\n• **Weekdays**: 8:00 AM - 3:00 PM\n• **Saturdays**: 8:00 AM - 11:30 AM\n• **Closed Sundays & Public Holidays**\n\nFor specific branch locations, visit our website or call +263 242 707 771.", 
            "📍 **Branch Network**\n\nYou can find CABS branches in all major cities and towns. Operating hours are typically:\n• Mon-Fri: 8:00 AM - 3:00 PM\n• Saturday: 8:00 AM - 11:30 AM\n• ATMs are available 24/7 at most locations.\n\nVisit cabs.co.zw for a full branch directory."
        ],
        "keywords": ["branch", "location", "nearest", "find", "where", "hours", "working", "opening", "close", "address", "atm", "branches", "locate", "cabs"]
    },
    "contact_info": {
        "patterns": [
            "contact", "phone number", "customer service", "give me your emergency number", 
            "give me your contact info", "whats your email address", "call bank", 
            "email", "head office", "get in touch", "how can i reach you", 
            "Give me your contact details", "what you customer care number", 
            "whats your supports contact", "customer care", "support", 
            "whats your after hours support contact",
        ],
        "responses": [
            "📞 **CABS Contact Information:**\n\n**Customer Service:**\n• Phone: +263 242 707 771-9\n• WhatsApp: 0777 227 227\n• USSD Banking: *227#\n\n**Other Contacts:**\n• Email: info@cabs.co.zw\n• Head Office: CABS Centre, 1st Street, Harare\n\nWe're here to help 24/7 through digital channels!", 
            "**How to Reach Us:**\n\n**Primary Contacts:**\n• Customer Service: +263 242 707 771\n• WhatsApp Banking: 0777 227 227\n• Emergency Lost Card: +263 242 707 771-9\n\n**Digital Banking:**\n• USSD: *227#\n• Email: info@cabs.co.zw\n\nVisit us at CABS Centre, 1st Street, Harare"
        ],
        "keywords": ["contact", "phone", "number", "email", "address", "customer", "service", "support", "emergency", "whatsapp", "call", "reach", "head", "office"]
    },
    "account_types": {
        "patterns": [
            "varieties of accounts", "range of accounts", "account portfolio", "accounts", 
            "banking account options", "which account types do you offer", 
            "what types of bank accounts", "kinds of accounts", "what accounts are available", 
            "which accounts can I open", "account classification", "account varieties", 
            "account offerings", "account products", "bank account types", 
            "different accounts", "various accounts", "all accounts", "complete account list", 
            "which account do you have", "give me account types", "provide account information", 
            "show account types", "list all accounts", "what are your accounts", 
            "account categories", "account types", "savings account", "current account", 
            "student account", "business account", "corporate account", "types of accounts", 
            "what accounts", "which accounts do you have", "tell me about accounts", 
            "list accounts", "show me accounts", "what kind of accounts", "which account types", 
            "available accounts", "account options", "bank accounts", "what banking accounts",
        ],
        "responses": ["account_types"],
        "keywords": ["account", "type", "kinds", "varieties", "different", "savings", "current", "student", "business", "corporate", "diaspora", "list", "show", "offer", "available"]
    },
    "interest_rates": {
        "patterns": [
            "interest rates", "savings interest", "loan rates", "fixed deposit", "loan interest rates"
            "investment returns", "what interest", "rate of interest"
        ],
        "responses": ["interest_rates"],
        "keywords": ["interest", "rate", "savings", "loan", "fixed", "deposit", "investment", "return", "percentage", "apy", "apr"]
    },
    "operating_hours": {
        "patterns": [
            "public holiday hours", "christmas hours", "new year hours", 
            "are you open on sunday", "sunday banking", "what time do you open", 
            "what time do you close", "weekend banking", "holiday hours", 
            "after hours services", "when do you close", "when do you open", 
            "saturday hours", "working hours", "business hours", "opening times", 
            "do you open on holidays", "which services do you offer after hours", 
            "do you open on weekends", "what time do close on weekdays", 
            "do you work on weekends", "what time do you open on saturday", 
            "what time do you close on saturday",
        ],
        "responses": [
            "🕒 **CABS Operating Hours**\n\n**Branch Banking:**\n• **Weekdays (Mon-Fri)**: 8:00 AM - 3:00 PM\n• **Saturdays**: 8:00 AM - 11:30 AM\n• **Sundays**: Closed\n• **Public Holidays**: Closed\n\n**After Hours Services (24/7):**\n• Online Banking\n• Mobile App Banking\n• WhatsApp Banking (0777 227 227)\n• USSD Banking (*227#)\n• ATM Services\n\n**Emergency Services:**\n• Lost card reporting: +263 242 707 771",  
            "**Banking Hours Overview:**\n\n**Regular Branch Hours:**\n• Monday to Friday: 8:00 AM - 3:00 PM\n• Saturday: 8:00 AM - 11:30 AM\n• Sunday: Closed\n• Public Holidays: Closed\n\n**24/7 Digital Banking:**\nYou can bank anytime using our digital platforms: Online Banking, Mobile App, WhatsApp Banking, and USSD (*227#)."
        ],
        "keywords": ["open", "close", "hours", "time", "working", "business", "weekend", "saturday", "sunday", "holiday", "christmas", "operating", "after", "hours", "service"]
    },
    "exchange_rates": {
        "patterns": [
            "buying rates", "selling rates", "current rates", "exchange rates", 
            "currency rates", "forex rates", "usd rates", "zig rates", 
            "foreign exchange", "currency exchange", "forex",
            "exchange rate", "cabs exchange rate", "cabs exchange rates", "cabs exchange",
            "what is the exchange rate", "what are the exchange rates", "tell me exchange rates",
            "show me exchange rates", "exchange rates today", "today's exchange rates",
            "current exchange rates", "latest exchange rates", "foreign currency rates",
        ],
        "responses": ["exchange_rates"],
        "keywords": ["exchange", "rate", "currency", "forex", "foreign", "usd", "dollar", "euro", "pound", "rand", "buying", "selling", "zig", "rates"]
    },
    "website_info": {
        "patterns": [
            "website", "cabs website", "online services", "internet banking", 
            "digital services", "web portal", "online platform", "cabs.co.zw", 
            "website features", "what's on your website", "website services",
        ],
        "responses": ["website_info"],
        "keywords": ["website", "online", "internet", "digital", "web", "portal", "platform", "cabs.co.zw", "features", "services"]
    },
    "about_cabs": {
        "patterns": [
            "cabs overview", "cabs company", "deposit protection scheme", 
            "company profile", "about the company", "who are we", "what we do", 
            "cabs background", "about cabs", "who is cabs", "what is cabs", 
            "tell me about cabs", "cabs information", "cabs history", "our vision", 
            "mission statement", "board of directors", "management team", "directors",
        ],
        "responses": ["about_cabs"],
        "keywords": ["about", "cabs", "company", "profile", "history", "background", "vision", "mission", "directors", "management", "deposit", "protection", "scheme"]
    },
    "about_old_mutual": {
        "patterns": [
            "old mutual group", "omz", "tell me about oldmutual", "who is oldmutual", 
            "old mutual history", "old mutual services", "about old mutual", 
            "old mutual", "our parent company", "old mutual zimbabwe", 
            "tell me about old mutual", "what is old mutual", "old mutual information",
        ],
        "responses": ["about_old_mutual"],
        "keywords": ["old", "mutual", "omz", "parent", "company", "group", "zimbabwe", "history", "services", "about", "information"]
    },
    "omari_info": {
        "patterns": [
            "omari", "o'mari", "digital wallet", "mobile money", "*707#", "usd wallet", "zig wallet", "omari card", "visa card", "zimswitch card", "omari registration", "how to register omari", "omari wallet", "omari services", "omari app", "omari ussd",
        ],
        "responses": ["omari_info"],
        "keywords": ["omari", "o'mari", "digital", "wallet", "mobile", "money", "*707#", "usd", "zig", "card", "visa", "zimswitch", "registration", "app", "ussd"]
    },
    "management_info": {
        "patterns": [
            "who is washington matsaira", "who is mehluli mpofu", "who is cecil ndoro", "who is valerie muyambo",
            "board of directors", "senior management", "directors", "executives", "leadership team",
            "management team", "board members", "corporate directors", "company directors",
            "who are the directors", "who are the board members", "directors list", "board list",
            "company leadership", "executive team", "management structure"
        ],
        "responses": ["management_info"],
        "keywords": ["board", "directors", "management", "team", "senior", "executives", "leadership", "members", "corporate", "company", "structure"]
    },
    "transactional_accounts": {
        "patterns": [
            "minimum balance", "account fees", "account charges", "gold transactional", "blue transactional", "account benefits", "what accounts do you have", "account options", "bank accounts", "current account", "cheque account", "checking account", "daily account", "transactional accounts", "gold account", "blue account", "senior citizen discounts", "gold class", "gold class account", "gold banking", "gold card", "blue class", "blue card", "blue class account", "blue banking", "cabs account", "cabs accounts", "tell me about cabs account", "information about cabs account", "what is cabs account"
        ],
        "responses": ["transactional_accounts"],
        "keywords": ["minimum", "balance", "fees", "charges", "gold", "blue", "transactional", "account", "benefits", "options", "current", "cheque", "checking", "daily", "senior", "citizen", "discounts", "class", "banking", "card", "cabs"]
    },
    "savings_plan": {
        "patterns": [
            "platinum savings", "blue savings", "gold savings", "savings account", "savings plan", "save money", "investment savings", "cabs savings", "savings interest", "save for future", "how to save", "savings products", "monthly savings",
        ],
        "responses": ["savings_plan"],
        "keywords": ["platinum", "blue", "gold", "savings", "account", "plan", "save", "money", "investment", "interest", "future", "monthly"]
    },
    "investment_products": {
        "patterns": [
            "cabs investments", "financial investments", "investment", "invest money", "term deposit", "unit trust", "money market", "investment services", "grow money", "investment options", "fixed deposit", "investment rates", "where to invest",
        ],
        "responses": ["investment_products"],
        "keywords": ["cabs", "investments", "financial", "investment", "invest", "money", "term", "deposit", "unit", "trust", "money", "market", "services", "grow", "options", "fixed", "rates", "where"]
    },
    "equity_release": {
        "patterns": [
            "equity release", "release equity", "property loan", "mortgage against property", "home equity", "property value loan", "unlock property value", "paid up property", "property mortgage", "home value loan", "tell me about equity release", "information about equity release", "what is equity release", "explain equity release", "how does equity release work"
        ],
        "responses": ["equity_release"],
        "keywords": ["equity", "release", "property", "loan", "mortgage", "against", "home", "value", "unlock", "paid", "up"]
    },
    "other_loans": {
        "patterns": [
            "short term loans", "other loans", "investor loans", "quick loans", "small loans", "emergency loans", "fast loans", "small loans", "emergency loans", "fast loans", "loan against investment", "investment loans", "tell me about short term loans", "information about quick loans", "what are emergency loans"
        ],
        "responses": ["other_loans"],
        "keywords": ["short", "term", "loans", "other", "investor", "quick", "small", "emergency", "fast", "against", "investment"]
    },
    "bancassurance": {
        "patterns": [
            "short term insurance", "long term insurance", "bancassurance", "insurance", "life insurance", "funeral plan", "easyinsure", "diamond plan", "life plan", "insurance products", "financial protection", "assurance", "tell me about bancassurance", "information about insurance", "what is easyinsure",
            "cabs insurance", "tell me about cabs insurance", "insurance at cabs", "cabs insurance products", "what insurance do you offer", "insurance services", "insurance coverage", "insurance plans", "insurance policies", "insurance options"
        ],
        "responses": ["bancassurance"],
        "keywords": ["short", "term", "insurance", "long", "bancassurance", "life", "funeral", "plan", "easyinsure", "diamond", "products", "financial", "protection", "assurance", "coverage", "policies", "cabs"]
    },
    "safe_deposit": {
        "patterns": [
            "safe deposit box", "safety deposit", "secure storage", "vault", "store valuables", "document storage", "secure vault", "northridge park vault", "secure storage facility", "tell me about safe deposit", "information about vault", "what is northridge park vault"
        ],
        "responses": ["safe_deposit"],
        "keywords": ["safe", "deposit", "box", "safety", "secure", "storage", "vault", "store", "valuables", "document", "northridge", "park", "facility"]
    },
    "custodial_services": {
        "patterns": [
            "custodial services", "share custody", "stock exchange", "zse", "securities", "trustee services", "safe custody", "investment custody", "share registration", "tell me about custodial services", "information about share custody", "what are trustee services"
        ],
        "responses": ["custodial_services"],
        "keywords": ["custodial", "services", "share", "custody", "stock", "exchange", "zse", "securities", "trustee", "safe", "investment", "registration"]
    },
    "international_payments": {
        "patterns": [
            "foreign currency", "cross border payments", "international payments", "telegraphic transfer", "swift transfer", "foreign payments", "international transfer", "send money abroad", "receive money from abroad", "diaspora remittances", "tell me about international payments", "information about swift transfer", "how to send money abroad"
        ],
        "responses": ["international_payments"],
        "keywords": ["foreign", "currency", "cross", "border", "payments", "international", "telegraphic", "transfer", "swift", "send", "money", "abroad", "receive", "diaspora", "remittances"]
    },
    "products_services": {
        "patterns": [
            "what financial services", "product", "banking offerings", "financial products available", "available services", "cabs products", "cabs services", "what do you sell", "what kind of products", "what type of services", "available products", "tell me about cabs product", "which banking products", "what are your offerings", "tell me about services", "im looking for products", "i need to know your services", "what financial products", "list your products", "show me your services", "what banking services", "what do you offer", "what can I get from cabs", "what are your products", "tell me about your products", "what banking products", "which services do you have", "what products do you have", "which products do you offer", "what services do you provide", "what product do you offer",
            "tell me about cabs products", "tell me about cabs services", "tell me about your products and services", "what are cabs products", "what are cabs services", "cabs financial products", "cabs banking services", "products offered by cabs", "services offered by cabs", "all cabs products", "all cabs services", "complete product list", "complete service list", "product portfolio", "service portfolio", "cabs offerings", "banking products and services", "financial products and services",
        ],
        "responses": ["products_services"],
        "keywords": ["what", "financial", "services", "banking", "offerings", "products", "available", "cabs", "sell", "kind", "type", "list", "show", "offer", "provide", "get", "portfolio", "complete", "all", "financial", "products", "services"]
    },
    "card_types": {
        "patterns": [
            "omari visa card", "omari zimswitch card", "card benefits", "card features", "gold debit card", "blue debit card", "visa debit", "zimswitch debit", "what cards are available", "which cards can I get", "card classification", "all cards", "complete card list", "card offerings", "card portfolio", "card products", "card varieties", "different cards", "various cards", "tell me about your cards", "show me your cards", "list all cards", "payment cards", "banking cards", "what card can I get", "which card should I get", "available cards", "bank cards", "cabs cards", "plastic cards", "omari card", "what debit cards", "which debit cards", "card options", "debit cards", "visa cards", "zimswitch cards", "gold card", "blue card", "card types", "types of cards", "what cards do you have", "which cards do you offer",
            "cabs cards", "tell me about cabs cards", "information about cabs cards", "what is cabs cards", "cabs card", "tell me about cabs card", "information about cabs card", "what is cabs card"
        ],
        "responses": ["card_types"],
        "keywords": ["omari", "visa", "zimswitch", "card", "benefits", "features", "gold", "blue", "debit", "what", "cards", "available", "which", "classification", "all", "complete", "list", "offerings", "portfolio", "products", "varieties", "different", "various", "tell", "show", "payment", "banking", "plastic", "options", "types", "cabs"]
    },
    "branch_lookup": {
        "patterns": [
            "do you have a branch in", "is there a branch in", "branches in", "branch at", "branch in", "branch",
            "cabs branch in", "cabs branches in", "cabs at", "cabs near", "find branch in",
            "locate branch in", "where is cabs in", "where is branch in",
            "are there branches in", "do you have branches in", "is there cabs in","do you have a branch in", "is there a branch in",
            "branches in", "branch at", "branch near", "locate branch", "branch address",
            "where can i find cabs branch", "find cabs branch", "locate cabs branch",
            "cabs branch in", "cabs branches in", "cabs at", "cabs near", "cabs location"
        ],
        "responses": ["branch_lookup"],
        "keywords": ["branch", "branches", "cabs", "in", "at", "near", "find", "locate", "where", "is", "there", "have", "do", "you"]
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
        "keywords": ["bye", "goodbye", "see", "you", "thanks", "that's", "all", "thank", "exit", "quit"]
    }
}

# Management team database - ONLY BOARD OF DIRECTORS REMAIN
MANAGEMENT_TEAM = {
    "board_of_directors": [
        {"name": "Washington Matsaira", "position": "Chairman"},
        {"name": "Mehluli Mpofu", "position": "Managing Director"}, 
        {"name": "Cecil Ndoro", "position": "Deputy Managing Director"}, 
        {"name": "Valerie Muyambo", "position": "Chief Finance Officer"}, 
        {"name": "Munyaradzi Dube", "position": "Independent Non-Executive Director"}, 
        {"name": "Warren Gillwald", "position": "Independent Non-Executive Director"}, 
        {"name": "Samuel Matsekete", "position": "Non-Executive Director"}, 
        {"name": "Joshua Tapambgwa", "position": "Independent Non-Executive Director"}, 
        {"name": "Tracey Mutaviri", "position": "Independent Non-Executive Director"}, 
        {"name": "Duduzile Shinya", "position": "Independent Non-Executive Director"}
    ]
}

# Card types database
CARD_TYPES = {
    "gold_debit_card": {
        "name": "Gold Debit Card",
        "type": "ZimSwitch & VISA",
        "account_link": "Gold Account (Gold Class)",
        "features": [
            "Unlimited cash withdrawals (subject to daily limits)",
            "Access to Gold Class Banking Halls",
            "POS/Swipe machine transactions",
            "Online shopping and payments",
            "International transactions (VISA)",
            "ATM withdrawals nationwide",
            "Contactless payments"
        ],
        "fees": "No monthly card fee for Gold Account holders",
        "eligibility": "Gold Account holders with minimum balance of USD$3"
    },
    "blue_debit_card": {
        "name": "Blue Debit Card", 
        "type": "ZimSwitch",
        "account_link": "Blue Account (Blue Class)",
        "features": [
            "Cash withdrawals (subject to daily limits)",
            "POS/Swipe machine transactions", 
            "Local online payments",
            "ATM withdrawals nationwide",
            "Basic banking transactions"
        ],
        "fees": "No monthly card fee for Blue Account holders",
        "eligibility": "Blue Account holders with minimum balance of USD$2"
    },
    "omari_visa_card": {
        "name": "O'mari VISA Debit Card",
        "type": "VISA",
        "account_link": "O'mari Digital Wallet (USD)",
        "features": [
            "International online shopping",
            "Global VISA acceptance",
            "USD transactions",
            "Online and in-store payments worldwide",
            "Secure chip technology"
        ],
        "fees": "Card issuance: $5 (one-time), Annual maintenance: $2",
        "eligibility": "Registered O'mari users"
    },
    "omari_zimswitch_card": {
        "name": "O'mari ZimSwitch Debit Card", 
        "type": "ZimSwitch",
        "account_link": "O'mari Digital Wallet (ZiG)",
        "features": [
            "Local ZiG transactions",
            "POS payments in Zimbabwe",
            "ATM withdrawals",
            "Local online payments",
            "ZimSwitch network acceptance"
        ],
        "fees": "Card issuance: $5 (one-time), Annual maintenance: $2", 
        "eligibility": "Registered O'mari users"
    }
}

# Updated comprehensive CABS branch database from actual data
BRANCHES = {
    "harare": [
        {
            "name": "CABS Central Avenue",
            "address": "Corner Fourth Street/Central Avenue, Harare",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "(024) 2 252 861-7",
            "services": ["Deposit-Taking", "ATM", "Full Banking"]
        },
        {
            "name": "CABS First Street",
            "address": "17 First Street / George Silundika Ave, Harare",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "(024) 2 700 611-22",
            "services": ["Deposit-Taking", "ATM", "Full Banking"]
        },
        {
            "name": "CABS Northridge Park",
            "address": "Northridge Park, Northend Close, Borrowdale, Harare",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "(024) 2 883 823-59",
            "services": ["Deposit-Taking", "ATM", "Full Banking"]
        },
        {
            "name": "CABS Park Street",
            "address": "No. 1 Park St /Cnr Jason Moyo Ave, Harare",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "(024) 2 781 171/756 538/756 656",
            "services": ["Deposit-Taking", "ATM", "Full Banking"]
        },
        {
            "name": "CABS Arundel",
            "address": "Cottage Shop Arundel Village, Quorn Ave, Mt Pleasant, Harare",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "(024) 2 883823-59",
            "services": ["Deposit-Taking", "ATM", "Full Banking"]
        },
        {
            "name": "CABS Southerton",
            "address": "12 Highfield Rd Southerton, Harare",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "(024) 2 700 0611-22",
            "services": ["Deposit-Taking", "ATM", "Full Banking"]
        },
        {
            "name": "CABS Avondale",
            "address": "Shop 9 Stand 12A, Avondale Shopping Centre, Harare",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "(024) 2 883823-59",
            "services": ["Deposit-Taking", "ATM", "Full Banking"]
        },
        {
            "name": "CABS Borrowdale",
            "address": "Borrowdale Village Walk, Harare",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "(024) 2 850 027",
            "services": ["Deposit-Taking", "ATM", "Full Banking"]
        },
        {
            "name": "Digital Service Centre",
            "address": "Stand No 19555 Robert Mugabe Street, Eastgate Market, Harare",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "08677 008 059",
            "services": ["Deposit-Taking", "ATM", "Digital Services"]
        },
        {
            "name": "CABS Kelvin Corner",
            "address": "Shop 1 and 2 Corner Crips and kelvin Road, Graniteside, Harare",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "(024) 2 700 0611-22",
            "services": ["Full Banking", "Business Banking"]
        },
        {
            "name": "Mutual Gardens",
            "address": "Old Mutual Head Office 100 The Chase Harare",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "(024) 2 308 400-40",
            "services": ["Corporate Banking", "Head Office Services"]
        },
        {
            "name": "OM Green Zone",
            "address": "CABS Center Cnr Sam Njoma & Jason Moyo Harare",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "(024) 2 707 731-34",
            "services": ["Full Banking", "ATM"]
        }
    ],
    "bulawayo": [
        {
            "name": "CABS Centre Bulawayo",
            "address": "98 Jason Moyo St Bulawayo",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "(029) 2 759 02-6/75991-6",
            "services": ["Deposit-Taking", "ATM", "Full Banking"]
        },
        {
            "name": "Bulawayo Fife St",
            "address": "Fife St Between 9th and 10th Ave Bulawayo",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "(029) 2 75991-6",
            "services": ["Full Banking", "Business Banking"]
        },
        {
            "name": "CA House",
            "address": "CA House 78 Jason Moyo, Cnr Jason Moyo St/Leopold Takawira St, Bulawayo",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "(029) 2 75991-6",
            "services": ["Full Banking", "Corporate Services"]
        },
        {
            "name": "Platinum Ascot",
            "address": "Shop 1 & 2 Ascot Shopping Centre, Bulawayo",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "(029) 2 881480/2",
            "services": ["Full Banking", "ATM"]
        }
    ],
    "chiredzi": [
        {
            "name": "CABS Chiredzi",
            "address": "CABS Building Chiredzi",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "(031) 231 3379/3597/2694",
            "services": ["Deposit-Taking", "ATM", "Full Banking"]
        }
    ],
    "masvingo": [
        {
            "name": "CABS Masvingo",
            "address": "402 R Mugabe Way, Masvingo",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "(039) 2 262391/2/264176",
            "services": ["Deposit-Taking", "ATM", "Full Banking"]
        }
    ],
    "mutare": [
        {
            "name": "CABS Mutare",
            "address": "81 Herbert Chitepo Street, Mutare",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "(020) 2 063529/63540/64311/63546",
            "services": ["Deposit-Taking", "ATM", "Full Banking"]
        }
    ],
    "gweru": [
        {
            "name": "CABS Gweru Branch",
            "address": "Cnr 5th St & R Mugabe Way Gweru",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "(054) 2 222051-8",
            "services": ["Deposit-Taking", "ATM", "Full Banking"]
        }
    ],
    "kadoma": [
        {
            "name": "CABS Kadoma",
            "address": "68 Newton Street Kadoma",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "(068) 21 23538/24314",
            "services": ["Full Banking", "ATM"]
        }
    ],
    "chinhoyi": [
        {
            "name": "CABS Chinhoyi",
            "address": "11 Magamba Way/Cnr Independence way Chinhoyi",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "(067) 2 122112/26262/24296/08677008837",
            "services": ["Full Banking", "ATM"]
        }
    ],
    "marondera": [
        {
            "name": "CABS Marondera",
            "address": "Stand 68 The Green Marondera",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "(065) 23 27258/25425",
            "services": ["Full Banking", "ATM"]
        }
    ],
    "bindura": [
        {
            "name": "CABS Bindura",
            "address": "29 R.G. Mugabe Street Bindura",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "(066) 2 107 883-4/106 543",
            "services": ["Full Banking", "ATM"]
        }
    ],
    "kariba": [
        {
            "name": "CABS Kariba",
            "address": "133 Makuti Road Kariba",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "(026) 1 214 6202/6274",
            "services": ["Full Banking", "ATM"]
        }
   ],
    "victoria falls": [
        {
            "name": "CABS Victoria Falls",
            "address": "306 Parkway Drive Victoria Falls",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "(083) 2 844 642",
            "services": ["Full Banking", "ATM", "Tourism Banking"]
        }
    ],
    "chitungwiza": [
        {
            "name": "CABS Chitungwiza Shopping Centre",
            "address": "Shop No.10A Chitungwiza Town Centre, Chitungwiza",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "(024) 2 883823-59",
            "services": ["Deposit-Taking", "ATM"]
        }
    ],
    "beitbridge": [
        {
            "name": "CABS Beitbridge",
            "address": "349 Jsticis Road Beitbridge",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "0780 656 640 (Cellphone)",
            "services": ["Full Banking", "ATM", "Border Services"]
        }
    ],
    "chipinge": [
        {
            "name": "CABS Chipinge",
            "address": "Main St, Chipinge Zimbabwe",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "(027) 2 04 2282",
            "services": ["Full Banking", "ATM"]
        }
    ],
    "rusape": [
        {
            "name": "CABS Rusape",
            "address": "Stand 796 18 Robert Mugabe Street Rusape",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "(025) 205 2664",
            "services": ["Full Banking", "ATM"]
        }
    ],
    "gokwe": [
        {
            "name": "CABS Gokwe",
            "address": "Stand No. 3816 Gokwe",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "(059) 2 295",
            "services": ["Full Banking", "ATM"]
        }
    ],
    "murewa": [
        {
            "name": "CABS Murewa",
            "address": "Stand 247 Murewa Growth Point Murewa",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "(065) 2 122 119/224 25",
            "services": ["Full Banking", "ATM"]
        }
    ],
    "hauna": [
        {
            "name": "CABS Hauna",
            "address": "Hauna Growth Point Manicaland",
            "hours": "Mon-Fri: 8:00 AM - 3:00 PM, Sat: 8:00 AM - 11:30 AM",
            "phone": "0785 432 552 (Cellphone)",
            "services": ["Full Banking", "ATM"]
        }
    ]
}

# ========== CUSTOM RESPONSE FUNCTIONS ==========
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
1. **Personal Loans:** For individuals with stable income : interest rate is 10% - 15% p.a. 
2. **Civil Servants Loans:** Special rates for government employees : : interest rate is 10% - 15% p.a.
3. **Salary-Based Loans:** For salaried individuals : interest rate is 12% - 18% p.a.
4. **Home Loans/Mortgages:** For property purchase/construction : interest rate is 8% - 12% p.a.
5. **Vehicle Loans:** For car/motorcycle purchase : interest rate is 10% - 16% p.a.
6. **Business Loans:** For entrepreneurs and companies : interest rate is 14% - 20% p.a.

**Civil Servants Loan Features:**
• Competitive interest rates
• Flexible repayment terms (up to 60 months)
• Loan amounts based on salary scale
• Fast approval process

**General Requirements:**
• Proof of income (payslip for 3 months)
• Valid ID
• Proof of residence
• Bank statements (3-6 months)
• Completed application form

**Apply:**
1. **Branch Visit:** With supporting documents
2. **Online:** Through CABS website
3. **Contact:** Loan department at +263 242 707 771

**Interest Rates:** Vary based on loan type and amount. Contact us for current rates!"""

def online_banking_response():
    return """📱 **Digital Banking Services**

**Multiple Ways to Bank Digitally:**

1. **Mobile App Banking:**
   • Download "CABS Mobile" from App Store/Play Store
   • View balances and transactions
   • Transfer funds
   • Pay bills

2. **WhatsApp Banking:**
   • Number: 0777 227 227
   • Check balances
   • Mini statements
   • Customer service

3. **USSD Banking:**
   • Dial *227# from your mobile
   • No internet needed
   • Available 24/7

4. **Internet Banking:**
   • Visit: online.cabs.co.zw
   • Full banking services
   • Secure login

**Troubleshooting:**
• **Forgot Password:** Use "Forgot Password" link on login page
• **Can't Login:** Call +263 242 707 771
• **Account Locked:** Visit branch with ID for reset

**Security Tips:**
• Never share OTPs or passwords
• Log out after each session
• Use strong passwords"""

def account_types_response():
    return """🏦 **CABS Account Portfolio**

**Personal Banking:**
1. **CABS Savings Account**
   • Earn competitive interest
   • Minimum balance: $10
   • Free ATM card
   • Monthly statements

2. **CABS Current Account**
   • Unlimited transactions
   • Cheque book facility
   • Overdraft facility available
   • Business transactions

3. **CABS Student Account**
   • Special rates for students
   • Low minimum balance
   • Educational benefits
   • Parent-controlled options

4. **CABS Diaspora Account**
   • For Zimbabweans abroad
   • Multi-currency
   • International transfers
   • Online management

**Business Banking:**
5. **CABS Business Account**
   • For SMEs and corporates
   • Bulk payment facilities
   • Merchant services
   • Dedicated relationship manager

6. **CABS Corporate Account**
   • Large corporations
   • Treasury services
   • Customized solutions
   • International banking

**Special Accounts:**
• **Fixed Deposit Accounts:** Higher interest rates
• **Call Accounts:** Flexible access to funds
• **Premium Accounts:** For high-net-worth individuals

**Visit any branch or call +263 242 707 771 to open an account today!**"""

def interest_rates_response():
    return """📈 **Current Interest Rates**

**Deposit Accounts:**
• **Savings Account:** 2.5% - 4.5% p.a. (based on balance)
• **Fixed Deposit (30 days):** 7.5% p.a.
• **Fixed Deposit (90 days):** 9.0% p.a.
• **Fixed Deposit (180 days):** 11.0% p.a.
• **Fixed Deposit (365 days):** 15.0% p.a.

**Loan Products:**
• **Personal Loans:** 12% - 18% p.a.
• **Civil Servants Loans:** 10% - 15% p.a.
• **Home Loans:** 8% - 12% p.a.
• **Vehicle Loans:** 10% - 16% p.a.
• **Business Loans:** 14% - 20% p.a.

**Important Notes:**
1. Rates are subject to change based on monetary policy
2. Actual rate depends on credit assessment
3. Terms and conditions apply
4. Rates effective as of current month

**For the most current rates:**
• Visit any CABS branch
• Call +263 242 707 771
• Check cabs.co.zw

*Rates are indicative and may vary. Contact us for personalized quotes.*"""

def exchange_rates_response():
    """Updated exchange rates response with actual figures for 31/12/2025"""
    response = """💱 **CABS Foreign Exchange Rates **
**Date: 06 January 2026**

**Exchange Rates USD**

| Currency | Buy | Buy Cash | Sell | Sell Cash |
|----------|-----|----------|------|-----------|
| BWP | 0.0691 | 0.0681 | 0.0751 | 0.0761 |
| EUR | 1.1382 | 1.1372 | 1.2087 | 1.2097 |
| GBP | 1.3148 | 1.3138 | 1.3963 | 1.3973 |
| ZAR | 15.8372 | 15.8362 | 16.8232 | 16.8242 |
| CHF | 1.226843332 | 1.225843332 | 1.303101381 | 1.304101381 |
| AUD | 0.6532 | 0.6522 | 0.6938 | 0.6948 |
| CNY | 6.7715 | 6.7705 | 7.1912 | 7.1922 |

**Exchange Rates ZiG**

| Currency | Buy | Buy Cash | Sell | Sell Cash |
|----------|-----|----------|------|-----------|
| USD | 0.039842776 | 0.039942776 | 0.037521837 | 0.037421837 |
| BWP | 1.809612881 | 1.808612881 | 1.921547699 | 1.922547699 |
| EUR | 29.45201436 | 29.45101436 | 31.27378845 | 31.27478845 |
| GBP | 34.02247907 | 34.02147907 | 36.12696232 | 36.12796232 |
| ZAR | 1.538331566 | 1.537331566 | 1.633486096 | 1.634486096 |
| CHF | 0.047420963 | 0.046420963 | 0.050354219 | 0.051354219 |
| AUD | 16.9039428 | 16.9029428 | 17.9495475 | 17.9505475 |
| CNY | 0.261717321 | 0.260717321 | 0.277906021 | 0.278906021 |


"""
    
    return response

def website_info_response():
    return """🌐 **CABS Digital Platform**

**Official Website:** https://www.cabs.co.zw

**Website Features:**

1. **Online Banking Portal:**
   • Secure login for existing customers
   • Account management
   • Fund transfers
   • Statement downloads

2. **Products & Services:**
   • Complete product catalog
   • Loan calculators
   • Rate information
   • Application forms

3. **Customer Services:**
   • Branch locator with maps
   • Contact information
   • FAQ section
   • Downloadable forms

4. **Digital Banking:**
   • Mobile app download links
   • USSD banking guide
   • WhatsApp banking setup
   • Security tips

5. **Information Hub:**
   • Latest news and updates
   • Financial tips
   • Exchange rates
   • Economic insights

**Mobile App:**
• Available on Google Play Store and Apple App Store
• Search: "CABS Mobile Banking"

**Need Help with Website?**
• Technical support: itsupport@cabs.co.zw
• General queries: info@cabs.co.zw
• Phone: +263 242 707 771

**Security Reminder:** Always ensure you're on the official website before entering login credentials!"""

def about_cabs_response():
    return """🏛️ **About CABS**

**Company Overview:**
CABS (Central Africa Building Society) is a leading financial institution in Zimbabwe, operating as a building society and commercial bank. We're part of the Old Mutual Zimbabwe Group.

**Our History:**
• Founded: 1949
• Headquartered in Harare, Zimbabwe
• Nationwide branch network
• Pioneer in mortgage financing

**Core Values:**
1. **Customer Focus:** Putting customers first
2. **Integrity:** Ethical banking practices
3. **Innovation:** Embracing digital transformation
4. **Excellence:** Striving for service excellence

**Services Offered:**
• Retail and Corporate Banking
• Mortgage and Home Loans
• Investment Services
• Treasury Services
• International Banking
• Digital Banking Solutions

**Deposit Protection:**
CABS is a member of the Deposit Protection Corporation, ensuring your deposits are protected up to prescribed limits.

**Awards & Recognition:**
• Multiple awards for customer service
• Recognized for digital innovation
• Leading mortgage provider

**Vision:** To be Zimbabwe's preferred financial partner
**Mission:** Providing innovative financial solutions for growth and prosperity

**Contact Corporate Affairs:**
• Email: corporate@cabs.co.zw
• Phone: +263 242 707 771
• Address: CABS Centre, 1st Street, Harare"""

def about_old_mutual_response():
    return """🤝 **About Old Mutual Zimbabwe**

**Parent Company:** CABS is a proud member of the Old Mutual Zimbabwe Group.

**Old Mutual Overview:**
• **Founded:** 1845 in South Africa
• **Zimbabwe Operations:** Since 1902
• **Listed:** Zimbabwe Stock Exchange
• **Sector:** Financial Services

**Group Structure in Zimbabwe:**
1. **Old Mutual Life Assurance Company**
2. **CABS (Central Africa Building Society)**
3. **Old Mutual Investment Group**
4. **Old Mutual Properties**
5. **Old Mutual Unit Trusts**

**Core Business Areas:**
• **Life Insurance & Pensions**
• **Banking & Lending** (through CABS)
• **Asset Management**
• **Property Investment**
• **Health Insurance**

**Values & Principles:**
• **Ubuntu:** We are because of others
• **Integrity:** Doing what's right
• **Customer First:** Exceptional service
• **Innovation:** Forward thinking

**Commitment to Zimbabwe:**
• Major investor in local economy
• Significant employer
• Community development initiatives
• Financial inclusion programs

**Contact Old Mutual Zimbabwe:**
• Website: www.oldmutual.co.zw
• Email: info@oldmutual.co.zw
• Phone: +263 242 707 771
• Address: Old Mutual Centre, Harare

**Together, we're building a better financial future for Zimbabwe.**"""

def omari_info_response():
    """Enhanced O'mari response with registration and card information"""
    return """📱 **O'mari Digital Wallet by CABS**

**What is O'mari?**
O'mari is CABS's digital wallet that allows you to send, receive, and store money digitally in both USD and ZiG currencies.

**Key Features:**
• **Dual Currency:** Separate USD and ZiG wallets
• **Multiple Access:** USSD, Mobile App, WhatsApp
• **Card Options:** VISA and ZimSwitch debit cards available
• **Nationwide Access:** Available across Zimbabwe

**How to Register for O'mari Digital Wallet:**

**You can register for O'mari through these simple methods:**

**1. USSD Registration (Any Network):**
   • Dial *707# from your mobile phone
   • Follow the on-screen prompts
   • Works on Econet, NetOne, and Telecel

**2. WhatsApp Registration:**
   • Message 'hi' to 0774 707 707
   • Follow the automated registration process

**3. Mobile App Registration:**
   • Download 'O'mari' from Google PlayStore or Apple AppStore
   • Complete registration in the app

**📋 Registration Requirements:**
• Valid Zimbabwean ID
• Active mobile number
• No documents needed (paperless registration)

**💡 Registration is FREE and instant!**

**O'mari Card Information:**

**Available Card Types:**

• **ZimSwitch Debit Card**: For ZiG transactions
• **VISA Debit Card**: For USD transactions (works online & internationally)

**🎨 Color Options Available:**
Black, White, Navy Blue, Neon Pink, Orange, Green

**How to Get Your Card:**
1. Register for O'mari first
2. Visit any CABS branch to apply for your card
3. Card delivery takes 7-14 working days

**Card Fees:**
• Card issuance fee: $5 (one-time)
• Annual maintenance fee: $2

**USSD Banking:**
• **Dial *707#** from any mobile network
• **No internet required**
• **Available 24/7**

**Services Available:**
• Send money to any mobile number
• Receive money from anyone
• Pay bills and merchants
• Buy airtime and data
• Check balances and transaction history
• Transfer between USD and ZiG wallets

**Contact O'mari Support:**
• WhatsApp: 0777 227 227
• Phone: +263 242 707 771
• Email: omari@cabs.co.zw

**Experience convenient digital banking with O'mari today!**"""

def management_info_response():
    response = """👥 **CABS Board of Directors**

**Leadership Team:**

"""
    
    for director in MANAGEMENT_TEAM["board_of_directors"]:
        response += f"• **{director['name']}** - {director['position']}\n"
    
    response += """
**Corporate Governance:**
CABS operates under a robust corporate governance framework with oversight from our experienced Board of Directors.

**Management Structure:**
• **Board of Directors:** Strategic oversight and governance
• **Executive Management:** Day-to-day operations
• **Senior Leadership:** Departmental leadership

**Contact the Board Secretary:**
• Email: boardsecretary@cabs.co.zw
• Phone: +263 242 707 771

*Note: Management appointments are subject to regulatory approvals and may change.*"""
    
    return response

def transactional_accounts_response():
    return """💳 **Transactional Accounts at CABS**

**Gold Account (Gold Class):**
• **Minimum Balance:** USD $3
• **Monthly Fees:** None (if minimum balance maintained)
• **Features:**
  - Unlimited transactions
  - Gold Debit Card (ZimSwitch & VISA)
  - Access to Gold Class Banking Halls
  - Priority customer service
  - Free cheque book
  - Overdraft facility available
  - Higher daily withdrawal limits

**Blue Account (Blue Class):**
• **Minimum Balance:** USD $2
• **Monthly Fees:** None (if minimum balance maintained)
• **Features:**
  - Blue Debit Card (ZimSwitch)
  - Standard banking services
  - Basic transaction limits
  - Online banking access
  - Affordable banking solution

**Senior Citizen Benefits:**
• Special discounts on transaction fees
• Priority service in branches
• Dedicated relationship managers for Gold Account holders
• Special interest rates on savings

**Account Comparison:**
| Feature | Gold Account | Blue Account |
|---------|-------------|-------------|
| Min Balance | $3 | $2 |
| Card Type | ZimSwitch & VISA | ZimSwitch |
| Banking Hall | Gold Class | Standard |
| Withdrawal Limits | Higher | Standard |
| Fees | None (if min balance) | None (if min balance) |

**Open an Account Today:**
Visit any CABS branch or call +263 242 707 771 to get started with the account that suits your needs!"""

def savings_plan_response():
    return """💰 **CABS Savings Plans**

**Platinum Savings:**
• **Target:** High-net-worth individuals
• **Minimum Deposit:** USD $1,000
• **Features:**
  - Highest interest rates
  - Dedicated relationship manager
  - Priority banking services
  - Investment advisory
  - Exclusive financial products

**Gold Savings:**
• **Target:** Regular savers
• **Minimum Deposit:** USD $100
• **Features:**
  - Competitive interest rates
  - Flexible deposit amounts
  - Monthly statements
  - Easy withdrawal options
  - Linked to Gold Account

**Blue Savings:**
• **Target:** Beginners and students
• **Minimum Deposit:** USD $20
• **Features:**
  - No monthly fees
  - Low minimum balance
  - Easy access to funds
  - Educational savings options
  - Linked to Blue Account

**Savings Benefits:**
1. **Earn Interest:** Grow your money safely
2. **Financial Discipline:** Regular saving habit
3. **Goal Achievement:** Save for specific objectives
4. **Emergency Fund:** Financial security
5. **Future Planning:** Education, retirement, property

**How to Start Saving:**
1. **Choose your plan** based on your goals
2. **Visit any CABS branch** with ID and proof of residence
3. **Make your initial deposit**
4. **Set up automatic transfers** for regular savings

**Interest Rates:**
• Platinum: 5.0% - 7.0% p.a.
• Gold: 3.5% - 5.0% p.a.
• Blue: 2.5% - 4.0% p.a.

*Rates subject to change. Visit cabs.co.zw for current rates.*"""

def investment_products_response():
    return """📊 **Investment Products at CABS**

**1. Fixed/Term Deposits:**
• **Investment Period:** 30 days to 5 years
• **Minimum Amount:** USD $500
• **Features:**
  - Guaranteed returns
  - Fixed interest rates
  - Various tenure options
  - Interest paid monthly/quarterly/at maturity

**2. Unit Trusts:**
• **Managed by:** Old Mutual Investment Group
• **Types:**
  - Money Market Funds
  - Equity Funds
  - Balanced Funds
  - Property Funds
• **Features:**
  - Professional fund management
  - Diversified portfolios
  - Regular income options
  - Easy entry and exit

**3. Money Market:**
• **Liquidity:** High
• **Returns:** Competitive short-term rates
• **Features:**
  - Easy access to funds
  - Low risk
  - Suitable for idle funds
  - Regular interest payments

**4. Investment Services:**
• **Financial Advisory:** Personalized investment advice
• **Portfolio Management:** For high-net-worth clients
• **Retirement Planning:** Pension and annuity products
• **Education Planning:** Save for education expenses

**Investment Benefits:**
• **Wealth Creation:** Grow your capital
• **Income Generation:** Regular returns
• **Inflation Protection:** Beat inflation
• **Financial Security:** Long-term stability
• **Tax Efficiency:** Tax-advantaged products

**How to Invest:**
1. **Consultation:** Meet with our investment advisors
2. **Risk Assessment:** Understand your risk profile
3. **Product Selection:** Choose suitable investments
4. **Documentation:** Complete application forms
5. **Funding:** Transfer investment amount

**Contact Investment Desk:**
• Phone: +263 242 707 771
• Email: investments@cabs.co.zw
• Visit: Any CABS branch

*Investments carry risks. Past performance is not indicative of future results.*"""

def equity_release_response():
    return """🏠 **Equity Release Solutions**

**What is Equity Release?**
Access the value tied up in your fully-paid property while you continue to live in it.

**Eligibility:**
• Property must be fully paid/owned
• Property in Zimbabwe
• Owner aged 18+ years
• Property properly registered

**How It Works:**
1. **Property Valuation:** We assess your property's current market value
2. **Loan Amount:** Typically up to 50% of property value
3. **Loan Term:** Flexible repayment periods (up to 10 years)
4. **Interest Rates:** Competitive secured loan rates
5. **Ownership:** You retain ownership and can live in the property

**Uses of Released Equity:**
• Home improvements/renovations
• Debt consolidation
• Business investment
• Education funding
• Medical expenses
• Retirement income supplement

**Benefits:**
• **Access Capital:** Unlock tied-up property value
• **Continue Living at Home:** No need to move out
• **Flexible Repayment:** Various options available
• **Competitive Rates:** Lower than unsecured loans
• **Tax Efficiency:** Interest may be tax-deductible

**Requirements:**
1. Title deeds for the property
2. Recent property valuation report
3. Proof of identity and residence
4. Income proof (for repayment capacity)
5. Insurance on the property

**Process:**
1. Initial consultation and application
2. Property valuation and assessment
3. Credit assessment and approval
4. Legal documentation
5. Funds disbursement

**Contact Mortgage Department:**
• Phone: +263 242 707 771 (ext. 234)
• Email: mortgages@cabs.co.zw
• Visit: Any CABS branch

*Terms and conditions apply. Your home may be repossessed if you do not keep up repayments.*"""

def other_loans_response():
    return """🚀 **Other Loan Products**

**1. Short-Term Loans:**
• **Amount:** USD $100 - $5,000
• **Term:** 1-12 months
• **Purpose:** Emergency expenses, small projects
• **Features:** Quick approval, minimal documentation

**2. Investor Loans:**
• **Amount:** USD $5,000 - $50,000
• **Term:** 6-36 months
• **Purpose:** Investment in stocks, bonds, unit trusts
• **Features:** Secured by investment portfolio

**3. Quick Loans:**
• **Amount:** Up to USD $2,000
• **Term:** 1-6 months
• **Purpose:** Urgent cash needs
• **Features:** Same-day approval for existing customers

**4. Emergency Loans:**
• **Amount:** Up to USD $1,000
• **Term:** 1-3 months
• **Purpose:** Medical emergencies, urgent repairs
• **Features:** Fast processing, compassionate terms

**5. Loan Against Investments:**
• **Amount:** Up to 70% of investment value
• **Term:** Flexible
• **Purpose:** Access liquidity without selling investments
• **Features:** Keep investments growing while accessing cash

**General Features:**
• **Competitive Interest Rates**
• **Flexible Repayment Terms**
• **Online Application Available**
• **Quick Processing Time**
• **Dedicated Loan Officers**

**Requirements:**
• Valid ID and proof of residence
• Proof of income (for unsecured loans)
• Bank statements (3-6 months)
• Completed application form
• Collateral/security (for larger loans)

**Apply Today:**
1. **Online:** cabs.co.zw/loans
2. **Phone:** +263 242 707 771
3. **Branch:** Visit any CABS branch
4. **WhatsApp:** 0777 227 227

**Interest Rates:** Vary from 12% to 24% p.a. based on loan type, amount, and security.

*Credit approval subject to assessment. Terms and conditions apply.*"""

def bancassurance_response():
    return """🛡️ **Bancassurance Products**

**Insurance Solutions through Old Mutual:**

**1. Short-Term Insurance:**
• **Motor Insurance:** Comprehensive, third party, theft
• **Home Insurance:** Building and contents cover
• **Fire Insurance:** Property protection
• **Business Insurance:** Commercial risks coverage
• **Travel Insurance:** Local and international travel

**2. Long-Term Insurance:**
• **Life Insurance:** Financial protection for loved ones
• **Funeral Plans:** Dignified farewell arrangements
• **Education Plans:** Secure children's future
• **Retirement Annuities:** Guaranteed retirement income
• **Investment-Linked Policies:** Insurance with investment growth

**3. EasyInsure Products:**
• **Diamond Plan:** Comprehensive life and funeral cover
• **Life Plan:** Pure life insurance protection
• **Funeral Plan:** Affordable funeral coverage
• **Hospital Cash Plan:** Daily hospital allowance
• **Education Protector:** Education funding security

**Key Benefits:**
• **Financial Security:** Protect against unexpected events
• **Peace of Mind:** Know your family is protected
• **Tax Benefits:** Premiums may be tax-deductible
• **Convenience:** One-stop banking and insurance
• **Expert Advice:** Professional insurance consultants

**Why Choose CABS Bancassurance?**
1. **Trusted Partner:** Backed by Old Mutual's 175+ years experience
2. **Comprehensive Coverage:** Wide range of insurance products
3. **Competitive Premiums:** Affordable protection
4. **Quick Claims:** Efficient claims processing
5. **Financial Strength:** Strong backing and stability

**How to Get Covered:**
1. **Consultation:** Meet with our insurance advisors
2. **Needs Analysis:** Assess your insurance requirements
3. **Product Selection:** Choose suitable coverage
4. **Application:** Complete simple forms
5. **Policy Issuance:** Receive your policy documents

**Contact Insurance Desk:**
• Phone: +263 242 707 771 (ext. 456)
• Email: insurance@cabs.co.zw
• WhatsApp: 0777 227 227
• Visit: Any CABS branch

*Insurance products are underwritten by Old Mutual Life Assurance Company. Terms and conditions apply.*"""

def safe_deposit_response():
    return """🔒 **Safe Deposit Box Services**

**Secure Storage at Northridge Park Vault**

**Available Box Sizes:**
1. **Small Box:** (3" x 5" x 24")
   • Ideal for: Documents, jewelry, small valuables
   • Annual Rental: USD $50

2. **Medium Box:** (5" x 5" x 24")
   • Ideal for: Laptops, tablets, important files
   • Annual Rental: USD $80

3. **Large Box:** (10" x 10" x 24")
   • Ideal for: Larger items, multiple documents
   • Annual Rental: USD $120

4. **Extra Large Box:** (15" x 15" x 24")
   • Ideal for: Business records, bulk storage
   • Annual Rental: USD $200

**What You Can Store:**
• Important documents (titles, deeds, wills, passports)
• Jewelry and precious metals
• Digital media (hard drives, USBs)
• Family heirlooms
• Coin collections
• Business records
• Confidential documents

**Security Features:**
• **24/7 Armed Security:** Professional guards on duty
• **Advanced Surveillance:** CCTV monitoring system
• **Access Control:** Biometric entry systems
• **Fire Protection:** Fire-resistant vault construction
• **Climate Control:** Temperature and humidity regulation
• **Insurance:** Optional insurance coverage available

**Access Hours:**
• **Monday - Friday:** 8:00 AM - 4:00 PM
• **Saturday:** 8:00 AM - 12:00 PM
• **Sunday:** Closed (emergency access by appointment)

**Location:**
**Northridge Park Vault**
Northridge Park, Borrowdale
Harare, Zimbabwe

**How to Rent a Box:**
1. **Visit Northridge Park** during business hours
2. **Provide Identification:** Valid ID/passport
3. **Choose Box Size:** Based on your needs
4. **Complete Agreement:** Sign rental contract
5. **Make Payment:** Annual rental in advance
6. **Receive Keys:** Two keys provided (you keep one)

**Important Notes:**
• Only registered renters can access the box
• Contents are not insured by default (optional insurance available)
• No illegal or hazardous materials allowed
• Regular access during business hours only

**Contact Safe Deposit:**
• Phone: +263 242 885 000
• Email: safedeposit@cabs.co.zw
• Address: Northridge Park, Borrowdale, Harare

**Your valuables deserve maximum security!**"""

def custodial_services_response():
    return """📋 **Custodial & Trustee Services**

**Professional Asset Safekeeping Solutions**

**Services Offered:**

**1. Share Custody Services:**
• **ZSE Listed Securities:** Safekeeping of Zimbabwe Stock Exchange shares
• **International Securities:** Custody of foreign investments
• **Dividend Collection:** Automatic collection and crediting
• **Corporate Actions:** Handling rights issues, bonuses, mergers
• **Statement Services:** Regular portfolio statements

**2. Trustee Services:**
• **Will Execution:** Acting as executor of estates
• **Trust Administration:** Managing family or charitable trusts
• **Estate Planning:** Professional estate administration
• **Guardianship Services:** Managing assets for minors
• **Pension Fund Trusteeship:** Corporate pension fund management

**3. Safe Custody:**
• **Document Storage:** Secure storage of legal documents
• **Title Deed Custody:** Safekeeping of property titles
• **Bond Certificates:** Storage of bond and debt instruments
• **Valuables Storage:** Secure storage of other valuable items

**4. Share Registration:**
• **Corporate Registry:** Maintaining shareholder registers
• **Dividend Distribution:** Processing and paying dividends
• **Share Transfers:** Recording and processing transfers
• **Annual General Meetings:** Proxy and voting management

**Benefits of Our Custodial Services:**
• **Security:** Bank-grade security for your assets
• **Expertise:** Professional asset management
• **Convenience:** Hassle-free administration
• **Compliance:** Regulatory compliance assured
• **Reporting:** Detailed regular statements
• **Peace of Mind:** Knowing your assets are protected

**Ideal For:**
• **Individual Investors:** Managing share portfolios
• **Corporate Clients:** Employee share schemes
• **Trusts & Estates:** Professional administration
• **Institutional Investors:** Large investment portfolios
• **Executors:** Professional will execution

**Fees:**
• Based on asset value and services required
• Competitive rates
• Transparent fee structure
• No hidden charges

**Requirements:**
1. Valid identification
2. Complete application forms
3. Asset documentation
4. Compliance with regulatory requirements

**Contact Custodial Services:**
• Phone: +263 242 707 771 (ext. 789)
• Email: custody@cabs.co.zw
• Visit: CABS Centre, 1st Street, Harare

**Let us safeguard your valuable assets with professional custodial care.**"""

def international_payments_response():
    return """🌍 **International Payments & Transfers**

**Global Banking Solutions**

**Services Available:**

**1. Telegraphic Transfers (TT):**
• **Outward Remittances:** Send money abroad
• **Inward Remittances:** Receive funds from overseas
• **Currencies:** USD, EUR, GBP, ZAR, AUD, and more
• **Speed:** 1-3 business days
• **Channels:** SWIFT, direct bank transfers

**2. SWIFT Transfers:**
• **Global Network:** Send to any bank worldwide
• **Secure:** International banking security standards
• **Traceable:** Full transaction tracking
• **Reliable:** Established global network

**3. Cross-Border Payments:**
• **Trade Finance:** Import/export payments
• **Education Fees:** Tuition and living expenses
• **Medical Payments:** International treatment costs
• **Family Support:** Regular remittances
• **Investment Payments:** International investments

**4. Diaspora Services:**
• **Diaspora Accounts:** Special accounts for Zimbabweans abroad
• **Regular Remittances:** Scheduled money transfers
• **Property Payments:** Mortgage and property-related payments
• **Investment Channels:** Local investment opportunities

**How to Send Money Abroad:**
1. **Visit Branch:** With required documents
2. **Provide Details:**
   - Beneficiary name and address
   - Beneficiary bank details (SWIFT/BIC, account number)
   - Amount and currency
   - Purpose of transfer
3. **Submit Documents:** Compliance requirements
4. **Make Payment:** Transfer amount plus fees
5. **Receive Reference:** Tracking number for your transfer

**How to Receive Money from Abroad:**
1. **Provide Your Details** to sender:
   - Your CABS account number
   - CABS SWIFT code: CABZZWHX
   - Bank name: Central Africa Building Society
   - Bank address: CABS Centre, 1st Street, Harare, Zimbabwe
2. **Monitor Your Account:** Funds credited upon receipt
3. **Receive Notification:** SMS/email when funds arrive

**Required Documents:**
• Valid ID (passport, national ID)
• Proof of address
• Proof of source of funds
• Invoice/contract (for trade payments)
• Student admission letter (for education fees)
• Medical documents (for medical payments)

**Fees:**
• Outward transfers: From USD $30 (depending on amount)
• Inward transfers: No fee for receiving funds
• Currency conversion: Competitive exchange rates
• Correspondent bank charges: May apply

**Processing Time:**
• Standard transfers: 1-3 business days
• Urgent transfers: Same/next day (higher fees)
• Weekend/holidays: Next business day

**SWIFT Code:** CABZZWHX
**Bank Code:** 10011

**Contact International Banking:**
• Phone: +263 242 707 771 (ext. 123)
• Email: international@cabs.co.zw
• WhatsApp: 0777 227 227
• Visit: CABS Centre, 1st Street, Harare

**Bank without borders with CABS International Banking!**"""

def products_services_response():
    return """📦 **Complete CABS Products & Services Portfolio**

**Personal Banking:**
1. **Transactional Accounts:**
   - Gold Account (Gold Class)
   - Blue Account (Blue Class)
   - Senior Citizen Accounts

2. **Savings Products:**
   - Platinum Savings
   - Gold Savings
   - Blue Savings
   - Fixed Deposits
   - Call Accounts

3. **Loan Products:**
   - Personal Loans
   - Civil Servants Loans
   - Salary-Based Loans
   - Home Loans/Mortgages
   - Vehicle Loans
   - Business Loans
   - Short-Term Loans
   - Equity Release Loans
   - Emergency Loans

4. **Card Services:**
   - Gold Debit Card (ZimSwitch & VISA)
   - Blue Debit Card (ZimSwitch)
   - O'mari VISA Debit Card
   - O'mari ZimSwitch Debit Card

**Digital Banking:**
5. **O'mari Digital Wallet:**
   - USD and ZiG wallets
   - USSD (*707#) banking
   - Mobile app
   - WhatsApp integration

6. **Digital Channels:**
   - Internet Banking
   - Mobile App Banking
   - WhatsApp Banking (0777 227 227)
   - USSD Banking (*227#)

**Investment & Wealth Management:**
7. **Investment Products:**
   - Unit Trusts
   - Money Market Funds
   - Fixed/Term Deposits
   - Retirement Annuities

8. **Custodial Services:**
   - Share Custody (ZSE and international)
   - Safe Custody of documents
   - Trustee Services
   - Share Registration

**Insurance (Bancassurance):**
9. **Short-Term Insurance:**
   - Motor Insurance
   - Home Insurance
   - Travel Insurance
   - Business Insurance

10. **Long-Term Insurance:**
    - Life Insurance
    - Funeral Plans
    - Education Plans
    - EasyInsure Products

**Specialized Services:**
11. **International Banking:**
    - Telegraphic Transfers
    - SWIFT Transfers
    - Diaspora Banking
    - Foreign Currency Accounts

12. **Safe Deposit Boxes:**
    - Northridge Park Vault
    - Multiple size options
    - Maximum security

13. **Business Banking:**
    - Corporate Accounts
    - Merchant Services
    - Trade Finance
    - Cash Management

**Additional Services:**
• Cheque Books
• Overdraft Facilities
• Standing Orders
• Debit Orders
• Bill Payments
• Airtime Purchases
• Tax Payments
• Salary Processing

**Getting Started:**
1. **Visit any CABS branch** nationwide
2. **Call us:** +263 242 707 771
3. **WhatsApp:** 0777 227 227
4. **Online:** cabs.co.zw

**Tailored Solutions:**
Our relationship managers can create customized banking packages based on your specific needs and financial goals.

**Experience comprehensive banking with CABS – Your complete financial partner!**"""

def card_types_response():
    response = """💳 **CABS Card Portfolio**

**Available Debit Cards:**

"""
    
    for card_key, card_data in CARD_TYPES.items():
        response += f"**{card_data['name']}**\n"
        response += f"• **Type:** {card_data['type']}\n"
        response += f"• **Linked to:** {card_data['account_link']}\n"
        response += f"• **Fees:** {card_data['fees']}\n"
        response += f"• **Eligibility:** {card_data['eligibility']}\n"
        response += "• **Key Features:**\n"
        for feature in card_data['features']:
            response += f"  - {feature}\n"
        response += "\n"
    
    response += """**Card Comparison:**

| Feature | Gold Debit Card | Blue Debit Card | O'mari VISA Card | O'mari ZimSwitch Card |
|---------|----------------|-----------------|------------------|----------------------|
| **Network** | ZimSwitch & VISA | ZimSwitch | VISA | ZimSwitch |
| **Currency** | Multi-currency | Multi-currency | USD | ZiG |
| **Int'l Use** | Yes | No | Yes | No |
| **Online Shopping** | Worldwide | Local only | Worldwide | Local only |
| **Linked Account** | Gold Account | Blue Account | O'mari USD Wallet | O'mari ZiG Wallet |
| **Monthly Fee** | None* | None* | $2/year | $2/year |
| **Issuance Fee** | None* | None* | $5 | $5 |

*For account holders maintaining minimum balance

**How to Get a Card:**
1. **Open an Account:** Gold or Blue account for debit cards
2. **Register for O'mari:** For O'mari cards
3. **Visit Branch:** With required documents
4. **Apply:** Complete card application form
5. **Wait:** Card ready in 7-10 working days

**Card Security Tips:**
• Never share your PIN with anyone
• Sign the card immediately upon receipt
• Keep card in secure location
• Report lost/stolen cards immediately
• Use secure ATMs in well-lit areas
• Check statements regularly

**Lost/Stolen Cards:**
🚨 **Emergency Contact:** +263 242 707 771-9
Available 24/7 for immediate card blocking

**Card Limits:**
• Daily ATM withdrawal limits apply
• POS transaction limits vary by card type
• International limits for VISA cards

**Contact Card Services:**
• Phone: +263 242 707 771
• Email: cardservices@cabs.co.zw
• WhatsApp: 0777 227 227

**Choose the card that fits your lifestyle and banking needs!**"""
    
    return response

def extract_location(user_input):
    """Extract location/town/city from user input for branch lookup"""
    user_input = user_input.lower().strip()
    
    # Remove common punctuation
    user_input = re.sub(r'[^\w\s]', ' ', user_input)
    
    # Check if the input contains any city name directly
    all_cities = list(BRANCHES.keys())
    
    # Enhanced location detection - check if any city name is in the input
    for city in all_cities:
        # Check for exact city match
        if city in user_input:
            return city
        
        # Check for partial matches (for multi-word city names like "victoria falls")
        if " " in city:
            city_parts = city.split()
            for part in city_parts:
                if part in user_input and len(part) > 3:  # Only if part is meaningful (more than 3 chars)
                    # Additional check to ensure it's not part of another word
                    words_in_input = user_input.split()
                    if any(part == word or part in word for word in words_in_input):
                        return city
    
    # Check for common variations and abbreviations
    location_variations = {
        "harare": ["harare", "hare", "hre"],
        "bulawayo": ["bulawayo", "byo", "bula", "bul"],
        "chiredzi": ["chiredzi", "chiredz"],
        "masvingo": ["masvingo", "mv", "mass"],
        "mutare": ["mutare", "umtali", "mut"],
        "gweru": ["gweru", "gw"],
        "kadoma": ["kadoma", "kad"],
        "chinhoyi": ["chinhoyi", "chinoyi", "chinh"],
        "marondera": ["marondera", "mar"],
        "bindura": ["bindura", "bind"],
        "kariba": ["kariba", "kar"],
        "victoria falls": ["victoria falls", "vic falls", "vicfalls", "victoria", "falls", "vic", "v.falls"],
        "chitungwiza": ["chitungwiza", "chitungwisa", "chitown", "chitung", "ctu"],
        "beitbridge": ["beitbridge", "beith", "beit", "bridge"],
        "chipinge": ["chipinge", "chip"],
        "rusape": ["rusape", "rus"],
        "gokwe": ["gokwe", "gok"],
        "murewa": ["murewa", "mur"],
        "hauna": ["hauna", "hun"]
    }
    
    # Check for variations
    for canonical_city, variations in location_variations.items():
        for variation in variations:
            if variation in user_input and len(variation) > 2:
                # Check if variation appears as a separate word or part of a word
                words_in_input = user_input.split()
                if any(variation == word or variation in word for word in words_in_input):
                    return canonical_city
    
    # Try to extract location from words like "chipinge branch" - check last word
    words = user_input.split()
    if len(words) > 0:
        last_word = words[-1].strip()
        if last_word:
            # Check if last word is a city
            for city in all_cities:
                if city == last_word or last_word in city:
                    return city
            
            # Check variations for last word
            for canonical_city, variations in location_variations.items():
                if last_word in variations:
                    return canonical_city
    
    # Check if any city name appears as a substring in any word
    for word in user_input.split():
        for city in all_cities:
            if city in word and len(city) > 3:
                return city
    
    return None

def branch_lookup_response(user_input):
    """Generate response for branch lookup queries"""
    location = extract_location(user_input)
    
    if not location:
        # If no location found, check if user just said "branch" or similar
        user_input_lower = user_input.lower()
        if "branch" in user_input_lower and len(user_input_lower.split()) <= 3:
            # User might have said something like "chipinge branch" but location wasn't detected
            # Try to extract the word before "branch"
            words = user_input_lower.split()
            for i, word in enumerate(words):
                if word == "branch" and i > 0:
                    possible_location = words[i-1]
                    # Check if this is a known location
                    for city in BRANCHES.keys():
                        if city == possible_location or possible_location in city:
                            location = city
                            break
            
            # If still no location, check all words
            if not location:
                for word in words:
                    for city in BRANCHES.keys():
                        if city == word or word in city:
                            location = city
                            break
                    if location:
                        break
    
    if not location:
        available_cities = ", ".join(sorted([city.title() for city in BRANCHES.keys()]))
        return f"I couldn't determine which location you're asking about. CABS has branches in: {available_cities}. Please specify the town or city name. For example: 'Do you have a branch in Harare?' or 'Branches in Bulawayo?'"
    
    if location not in BRANCHES:
        available_cities = ", ".join(sorted([city.title() for city in BRANCHES.keys()]))
        return f"Sorry, I don't have information about branches in {location.title()}. CABS has branches in these locations: {available_cities}."
    
    branches = BRANCHES[location]
    location_display = location.title()
    
    response = f"CABS has {'branch' if len(branches) == 1 else 'branches'} in {location_display}!**\n\n"
    
    if len(branches) == 1:
        branch = branches[0]
        response += f"**📍 {branch['name']}**\n"
        response += f"**Address:** {branch['address']}\n"
        response += f"**Hours:** {branch['hours']}\n"
        response += f"**Phone:** {branch['phone']}\n"
        response += f"**Services:** {', '.join(branch['services'])}\n"
    else:
        response += f"**CABS has {len(branches)} branches in {location_display}:**\n\n"
        
        for i, branch in enumerate(branches, 1):
            response += f"**{i}. {branch['name']}**\n"
            response += f"   • **Address:** {branch['address']}\n"
            response += f"   • **Hours:** {branch['hours']}\n"
            response += f"   • **Phone:** {branch['phone']}\n"
            response += f"   • **Services:** {', '.join(branch['services'])}\n\n"
    
    response += "\n**📞 Need directions or more information?**\n"
    response += "• Call our customer service: +263 242 707 771\n"
    response += "• WhatsApp: 0777 227 227\n"
    response += "• Visit our website: cabs.co.zw for more branch details\n\n"
    response += f"**Operating Hours Note:** Most CABS branches operate Monday-Friday: 8:00 AM - 3:00 PM, Saturday: 8:00 AM - 11:30 AM."
    
    return response

# Improved intent matching function with enhanced branch detection and better keyword weighting
def match_intent(user_input):
    user_input_lower = user_input.lower().strip()
    
    # Remove common punctuation
    user_input_lower = re.sub(r'[^\w\s]', ' ', user_input_lower)
    
    # FIRST: Check for branch lookup - enhanced detection
    # Check if the input contains any city name from our branch database
    all_cities = list(BRANCHES.keys())
    
    # Check for simple patterns like "chipinge branch" or "harare branch"
    words = user_input_lower.split()
    
    # If input is short (1-3 words) and contains "branch", prioritize branch lookup
    if len(words) <= 3 and "branch" in user_input_lower:
        # Check if any city name is in the input
        for city in all_cities:
            if city in user_input_lower:
                return "branch_lookup"
        
        # Check for city variations
        location_variations = {
            "harare": ["harare", "hare", "hre"],
            "bulawayo": ["bulawayo", "byo", "bula", "bul"],
            "chiredzi": ["chiredzi", "chiredz"],
            "masvingo": ["masvingo", "mv", "mass"],
            "mutare": ["mutare", "umtali", "mut"],
            "gweru": ["gweru", "gw"],
            "kadoma": ["kadoma", "kad"],
            "chinhoyi": ["chinhoyi", "chinoyi", "chinh"],
            "marondera": ["marondera", "mar"],
            "bindura": ["bindura", "bind"],
            "kariba": ["kariba", "kar"],
            "victoria falls": ["victoria falls", "vic falls", "vicfalls", "victoria", "falls", "vic", "v.falls"],
            "chitungwiza": ["chitungwiza", "chitungwisa", "chitown", "chitung", "ctu"],
            "beitbridge": ["beitbridge", "beith", "beit", "bridge"],
            "chipinge": ["chipinge", "chip"],
            "rusape": ["rusape", "rus"],
            "gokwe": ["gokwe", "gok"],
            "murewa": ["murewa", "mur"],
            "hauna": ["hauna", "hun"]
        }
        
        for canonical_city, variations in location_variations.items():
            for variation in variations:
                if variation in user_input_lower:
                    return "branch_lookup"
    
    # Check for explicit branch lookup patterns
    branch_patterns = [
        "do you have a branch in", "is there a branch in", "branches in", "branch at", 
        "branch in", "cabs branch in", "cabs branches in", "cabs at", "cabs near", 
        "find branch in", "locate branch in", "where is cabs in", "where is branch in",
        "are there branches in", "do you have branches in", "is there cabs in",
        "branch near", "locate branch", "branch address", "where can i find cabs branch",
        "find cabs branch", "locate cabs branch", "cabs location"
    ]
    
    for pattern in branch_patterns:
        if pattern in user_input_lower:
            return "branch_lookup"
    
    # Check for city names alone (like "chipinge", "harare", etc.)
    for city in all_cities:
        if city == user_input_lower or city in user_input_lower:
            # Check if it's not part of another word
            words = user_input_lower.split()
            for word in words:
                if city == word or city in word:
                    return "branch_lookup"
    
    # Create a dictionary to track match scores
    intent_scores = {}
    
    # Check all intents
    for intent_tag, intent_data in INTENTS.items():
        score = 0
        
        # Check for exact pattern matches (highest priority - score 20)
        for pattern in intent_data["patterns"]:
            if pattern == user_input_lower or pattern in user_input_lower:
                # For exact matches, give very high score
                if pattern == user_input_lower:
                    score += 30
                else:
                    # Check if it's a meaningful substring
                    # Don't give too much weight to generic patterns that are substrings
                    if len(pattern) > 3:  # Only if pattern is meaningful (more than 3 chars)
                        # Check if pattern is a separate word or meaningful part
                        if pattern in user_input_lower.split() or f" {pattern} " in f" {user_input_lower} ":
                            score += 20
                        else:
                            score += 10  # Lower score for partial matches
        
        # Check for keyword matches with better weighting
        if "keywords" in intent_data:
            user_words = set(user_input_lower.split())
            intent_keywords = set(intent_data["keywords"])
            
            # Count matching keywords
            matching_keywords = user_words.intersection(intent_keywords)
            
            # Apply keyword weights based on importance
            for keyword in matching_keywords:
                # High priority keywords get more weight
                if keyword in ["exchange", "rate", "rates"]:
                    score += 8  # High weight for exchange rate keywords
                elif keyword in ["interest", "loan", "insurance", "card", "account"]:
                    score += 6  # Medium-high weight for main banking terms
                elif keyword == "cabs":
                    # Reduce weight for "cabs" keyword since it's too common
                    score += 2  # Lower weight for generic "cabs" keyword
                else:
                    score += 3  # Standard weight for other keywords
            
            # Special handling for exchange rates
            if "exchange" in user_words or "rate" in user_words or "rates" in user_words:
                # If user mentions exchange or rate, strongly favor exchange_rates intent
                if intent_tag == "exchange_rates":
                    score += 15  # Very strong bonus for exchange_rates intent
            
            # Special handling for "cabs exchange rate" phrase
            if "cabs" in user_words and ("exchange" in user_words or "rate" in user_words or "rates" in user_words):
                if intent_tag == "exchange_rates":
                    score += 25  # Very strong bonus for this specific phrase
            
            # Priority keywords that should strongly influence intent matching
            priority_keywords = {
                "exchange": "exchange_rates",
                "rate": "exchange_rates", 
                "rates": "exchange_rates",
                "currency": "exchange_rates",
                "forex": "exchange_rates",
                "products": "products_services",
                "services": "products_services",
                "equity": "equity_release",
                "release": "equity_release",
                "bancassurance": "bancassurance",
                "insurance": "bancassurance",
                "custodial": "custodial_services",
                "trustee": "custodial_services",
                "safe": "safe_deposit",
                "deposit": "safe_deposit",
                "international": "international_payments",
                "swift": "international_payments",
                "transactional": "transactional_accounts",
                "gold": "transactional_accounts",
                "blue": "transactional_accounts",
                "savings": "savings_plan",
                "investment": "investment_products",
                "loan": "loan_information",
                "loans": "loan_information",
                "board": "management_info",
                "directors": "management_info",
                "management": "management_info",
                "cards": "card_types",
                "card": "card_types",
                "visa": "card_types",
                "zimswitch": "card_types",
                "omari": "omari_info",
                "cabs": ["about_cabs", "products_services"],
                "account": ["transactional_accounts", "account_types", "account_opening"]
            }
            
            # Apply priority keyword bonuses
            for word in matching_keywords:
                if word in priority_keywords:
                    target_intents = priority_keywords[word]
                    if isinstance(target_intents, list):
                        if intent_tag in target_intents:
                            # For "cabs" keyword, give lower weight to about_cabs
                            if word == "cabs" and intent_tag == "about_cabs":
                                score += 3  # Lower weight for generic "cabs" to about_cabs
                            else:
                                score += 5  # Standard bonus
                    elif intent_tag == target_intents:
                        # For exchange rates, give higher bonus
                        if word == "exchange" or word == "rate" or word == "rates":
                            score += 10  # Very high bonus for exchange rates
                        else:
                            score += 5  # High bonus for matching specific intent
        
        # Store the score
        if score > 0:
            intent_scores[intent_tag] = score
    
    # Special case: If user mentions "cabs exchange rate" or similar, strongly favor exchange_rates
    if "cabs exchange" in user_input_lower or "exchange rate" in user_input_lower or "exchange rates" in user_input_lower:
        if "exchange_rates" in intent_scores:
            intent_scores["exchange_rates"] += 30  # Very strong bonus
        else:
            # Add exchange_rates with high score
            intent_scores["exchange_rates"] = 30
    
    # Special case: If user mentions "cabs cards" or "cabs card", strongly favor card_types
    if "cabs cards" in user_input_lower or "cabs card" in user_input_lower:
        if "card_types" in intent_scores:
            intent_scores["card_types"] += 20  # Very strong bonus
        else:
            # Add card_types with high score
            intent_scores["card_types"] = 20
    
    # Special case: If user mentions "cabs loans" or "cabs loan", strongly favor loan_information
    if "cabs loans" in user_input_lower or "cabs loan" in user_input_lower:
        if "loan_information" in intent_scores:
            intent_scores["loan_information"] += 20  # Very strong bonus
        else:
            # Add loan_information with high score
            intent_scores["loan_information"] = 20
    
    # Special case: If user mentions "cabs account", strongly favor transactional_accounts
    if "cabs account" in user_input_lower:
        if "transactional_accounts" in intent_scores:
            intent_scores["transactional_accounts"] += 20  # Very strong bonus
        else:
            # Add transactional_accounts with high score
            intent_scores["transactional_accounts"] = 20
    
    # Special case: If user mentions "cabs insurance" or "insurance", strongly favor bancassurance
    user_words = set(user_input_lower.split())
    if "cabs insurance" in user_input_lower or ("cabs" in user_words and "insurance" in user_words):
        if "bancassurance" in intent_scores:
            intent_scores["bancassurance"] += 20  # Very strong bonus
        else:
            # Add bancassurance with high score
            intent_scores["bancassurance"] = 20
    
    # Special case: If user mentions "insurance", strongly favor bancassurance
    if "insurance" in user_words and "cabs" not in user_input_lower:
        if "bancassurance" in intent_scores:
            intent_scores["bancassurance"] += 15  # Strong bonus
        else:
            # Add bancassurance with high score
            intent_scores["bancassurance"] = 15
    
    # Special case: If user mentions "products" or "services", strongly favor products_services
    if "products" in user_words or "services" in user_words:
        if "products_services" in intent_scores:
            intent_scores["products_services"] += 10  # Very strong bonus
    
    # Special case: If user mentions "equity" and "release", strongly favor equity_release
    if "equity" in user_words and "release" in user_words:
        if "equity_release" in intent_scores:
            intent_scores["equity_release"] += 10  # Very strong bonus
    
    # Find the intent with the highest score
    if intent_scores:
        # Sort by score (descending) and return the highest
        sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Debug output - uncomment to see scores
        # print(f"Debug scores for '{user_input}': {sorted_intents}")
        
        return sorted_intents[0][0]
    
    return None

# Get response based on intent
def get_response(intent_tag, user_input=None):
    if intent_tag is None:
        return "I'm sorry, I don't understand that. Please ask about CABS banking services, accounts, loans, cards, or contact information. You can also try greetings like 'hello' or 'hi'."
    
    intent_data = INTENTS.get(intent_tag)
    if not intent_data:
        return "I'm not sure how to respond to that. Can you rephrase your question?"
    
    # Check if it's a special function response
    response = random.choice(intent_data["responses"])
    
    # Map to special response functions
    response_functions = {
        "account_opening": account_opening_response,
        "loan_information": loan_information_response,
        "online_banking": online_banking_response,
        "account_types": account_types_response,
        "interest_rates": interest_rates_response,
        "exchange_rates": exchange_rates_response,
        "website_info": website_info_response,
        "about_cabs": about_cabs_response,
        "about_old_mutual": about_old_mutual_response,
        "omari_info": omari_info_response,
        "management_info": management_info_response,
        "transactional_accounts": transactional_accounts_response,
        "savings_plan": savings_plan_response,
        "investment_products": investment_products_response,
        "equity_release": equity_release_response,
        "other_loans": other_loans_response,
        "bancassurance": bancassurance_response,
        "safe_deposit": safe_deposit_response,
        "custodial_services": custodial_services_response,
        "international_payments": international_payments_response,
        "products_services": products_services_response,
        "card_types": card_types_response,
        "branch_lookup": lambda: branch_lookup_response(user_input) if user_input else "Please specify which location you're asking about. For example: 'Do you have a branch in Harare?'"
    }
    
    if response in response_functions:
        if intent_tag == "branch_lookup":
            return response_functions[response]()
        else:
            return response_functions[response]()
    
    return response

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
    
    # Reduce context length for faster responses - DEFAULT CHANGED TO 9
    context_length = st.slider("Chat history (messages to remember):", 2, 10, 9)  # Changed from 4 to 9
    
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
            # Clean the response to remove <s> tokens
            response_text = data["choices"][0]["message"]["content"]
            # Remove <s> and </s> tags from the response
            response_text = response_text.replace('<s>', '').replace('</s>', '').strip()
            
            return {
                "response": response_text,
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
                              temperature=0.7, max_tokens=300, context_length=9):  # Default changed to 9
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
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": """Hello! I'm **Tino**, your CABS Banking Assistant. 🏦

I can help you with:
• **Account Information** (opening, types, fees)
• **Loan Services** (personal, civil servants, home loans)
• **Digital Banking** (O'mari, mobile banking, USSD)
• **Card Services** (debit cards, O'mari cards)
• **Branch Locations** (nationwide branches)
• **Exchange Rates** (current forex rates)
• **Insurance Products** (bancassurance)
• **Investment Services**
• **Contact Information**

**How can I assist you with your banking needs today?**"""
        }
    ]

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
    
    # First check if we have a direct intent match using local database
    intent = match_intent(prompt)
    
    if intent and intent != "branch_lookup":
        # Use local database response for known intents (except branch_lookup which needs user input)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("💭 Thinking...")
            
            # Get response from local database
            start_time = time.time()
            response = get_response(intent, prompt)
            end_time = time.time()
            
            # Calculate total time
            total_time = end_time - start_time
            
            # Store response time
            st.session_state.response_times.append(total_time)
            
            # Display response
            message_placeholder.markdown(response)
            
            # Show timing info
            st.caption(f"⏱️ Response time: {total_time:.1f}s")
        
        # Add to history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
    elif not api_key:
        # No API key provided
        with st.chat_message("assistant"):
            st.error("Please provide an API key in the sidebar")
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "I need an API key to respond. Please enter your OpenRouter API key in the sidebar. For now, I can only answer questions that match my local database."
            })
    
    else:
        # Use AI for complex or unmatched queries
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("💭 Thinking...")
            
            # Get sidebar settings
            context_len = context_length if 'context_length' in locals() else 9  # Default changed to 9
            max_tokens_val = max_tokens if 'max_tokens' in locals() else 300
            temp_val = temperature if 'temperature' in locals() else 0.7
            
            # Get AI response
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