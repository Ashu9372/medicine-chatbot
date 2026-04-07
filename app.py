import streamlit as st
# from openai import OpenAI
import pandas as pd
from fuzzywuzzy import fuzz, process
# import google.generativeai as genai
# from streamlit_mic_recorder import mic_recorder, speech_to_text
import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F
import time
import random
import sqlite3
from groq import Groq

# Page configuration :
st.set_page_config(
    page_title="AI Health Assistant",
    page_icon="🧠",
    layout="wide"
)

# Premium SaaS UI - Production Grade
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    html, body {
        background: linear-gradient(135deg, #0a0f1a 0%, #0f1419 50%, #1a1f2e 100%) !important;
        color: #e2e8f0 !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }
    
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0a0f1a 0%, #0f1419 50%, #1a1f2e 100%) !important;
    }
    
    [data-testid="stAppViewContainer"] > div:first-child {
        max-width: 920px !important;
        margin: 0 auto !important;
        width: 100% !important;
    }
    
    /* Chat container for bottom-flow messages */
    .chat-container {
        height: 70vh;
        max-height: 600px;
        overflow-y: auto;
        overflow-x: hidden;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        padding: 16px;
        gap: 12px;
        scroll-behavior: smooth;
        border-radius: 12px;
        background: rgba(15, 23, 42, 0.3);
        border: 1px solid rgba(71, 85, 105, 0.2);
    }
    
    /* Auto-scroll to bottom using CSS */
    .chat-container::after {
        content: '';
        display: block;
        height: 1px;
        visibility: hidden;
    }
    
    /* Custom scrollbar for chat */
    .chat-container::-webkit-scrollbar {
        width: 6px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 3px;
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: rgba(59, 130, 246, 0.5);
        border-radius: 3px;
    }
    
    .chat-container::-webkit-scrollbar-thumb:hover {
        background: rgba(59, 130, 246, 0.7);
    }
    
    .main {
        max-width: 920px !important;
        margin: 0 auto !important;
    }
    
    main.css-1r6slb0 {
        max-width: 920px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    
    header[data-testid="stHeader"] {
        display: none !important;
    }
    
    h1 {
        font-size: 36px !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        margin-bottom: 12px !important;
    }
    
    h2 {
        font-size: 24px !important;
        font-weight: 600 !important;
        color: #f1f5f9 !important;
    }
    
    h3 {
        font-size: 18px !important;
        font-weight: 500 !important;
        color: #cbd5e1 !important;
    }
    
    button[data-baseweb="tab"] {
        background-color: rgba(30, 41, 59, 0.6) !important;
        color: #94a3b8 !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
        padding: 12px 20px !important;
        border: 1px solid rgba(51, 65, 85, 0.4) !important;
        margin-right: 8px !important;
        transition: all 0.3s ease !important;
    }
    
    button[data-baseweb="tab"]:hover {
        background-color: rgba(51, 65, 85, 0.8) !important;
        border-color: rgba(148, 163, 184, 0.5) !important;
    }
    
    button[aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
        color: #ffffff !important;
        border-color: #2563eb !important;
    }
    
    input, textarea, .stTextInput input, .stTextArea textarea {
        background-color: rgba(26, 35, 50, 0.8) !important;
        color: #e2e8f0 !important;
        border: 1.5px solid rgba(51, 65, 85, 0.6) !important;
        border-radius: 14px !important;
        padding: 12px 16px !important;
        transition: all 0.3s ease !important;
    }
    
    input:focus, textarea:focus, .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 12px rgba(59, 130, 246, 0.3) !important;
        background-color: rgba(26, 35, 50, 0.95) !important;
    }
    
    [data-testid="stChatInput"] {
        background-color: transparent !important;
        border: none !important;
    }
    
    [data-testid="stChatInput"] input {
        background-color: rgba(26, 35, 50, 0.9) !important;
        border: 1.5px solid rgba(51, 65, 85, 0.6) !important;
        border-radius: 20px !important;
        padding: 14px 20px !important;
        color: #e2e8f0 !important;
        font-size: 15px !important;
    }
    
    [data-testid="stChatInput"] input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 16px rgba(59, 130, 246, 0.4) !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3) !important;
    }
    
    .card-container {
        background: rgba(26, 35, 50, 0.4) !important;
        border: 1px solid rgba(51, 65, 85, 0.5) !important;
        border-radius: 18px !important;
        padding: 24px !important;
        margin: 16px 0 !important;
        backdrop-filter: blur(10px) !important;
        transition: all 0.3s ease !important;
    }
    
    .card-container:hover {
        background: rgba(26, 35, 50, 0.6) !important;
        border-color: rgba(59, 130, 246, 0.5) !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3) !important;
        transform: translateY(-2px) !important;
    }
    
    .chat-bubble {
        max-width: 70%;
        margin: 8px 0;
        padding: 13px 18px;
        border-radius: 18px;
        font-size: 14px;
        line-height: 1.5;
        word-wrap: break-word;
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .chat-bubble.user {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        margin-left: auto !important;
        text-align: right;
        border-bottom-right-radius: 4px;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .chat-bubble.assistant {
        background: rgba(30, 41, 59, 0.7) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(59, 130, 246, 0.3);
        margin-right: auto !important;
        text-align: left;
        border-bottom-left-radius: 4px;
        backdrop-filter: blur(8px);
    }
    
    .stWarning {
        background: rgba(251, 146, 60, 0.15) !important;
        border: 1px solid rgba(251, 146, 60, 0.4) !important;
        border-radius: 14px !important;
        padding: 14px 16px !important;
        color: #fed7aa !important;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.15) !important;
        border: 1px solid rgba(239, 68, 68, 0.4) !important;
        border-radius: 14px !important;
        padding: 14px 16px !important;
        color: #fca5a5 !important;
    }
    
    .stSuccess {
        background: rgba(34, 197, 94, 0.15) !important;
        border: 1px solid rgba(34, 197, 94, 0.4) !important;
        border-radius: 14px !important;
        padding: 14px 16px !important;
        color: #86efac !important;
    }
    
    .stInfo {
        background: rgba(59, 130, 246, 0.15) !important;
        border: 1px solid rgba(59, 130, 246, 0.4) !important;
        border-radius: 14px !important;
        padding: 14px 16px !important;
        color: #93c5fd !important;
    }
    
    hr {
        border: none !important;
        border-top: 1px solid rgba(51, 65, 85, 0.5) !important;
        margin: 20px 0 !important;
    }
    
    [data-testid="stDataFrame"] {
        border-radius: 14px !important;
        background-color: rgba(26, 35, 50, 0.5) !important;
    }
    
    .footer-premium {
        text-align: center;
        margin-top: 40px;
        padding: 24px;
        background: rgba(26, 35, 50, 0.4);
        border: 1px solid rgba(51, 65, 85, 0.5);
        border-radius: 16px;
        color: #94a3b8;
        font-size: 12px;
        backdrop-filter: blur(10px);
    }
    
    .integrated-input-container {
        display: flex;
        gap: 8px;
        align-items: flex-end;
        background: rgba(26, 35, 50, 0.6);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 20px;
        padding: 8px 12px;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .integrated-input-container:focus-within {
        background: rgba(26, 35, 50, 0.8);
        border-color: rgba(59, 130, 246, 0.6);
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    .integrated-input-container textarea {
        flex: 1;
        background: transparent;
        border: none;
        color: #e2e8f0;
        font-size: 14px;
        resize: none;
        max-height: 120px;
        outline: none;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        line-height: 1.5;
    }
    
    .integrated-input-container textarea::placeholder {
        color: #64748b;
    }
    
    .integrated-input-container textarea::-webkit-scrollbar {
        width: 6px;
    }
    
    .integrated-input-container textarea::-webkit-scrollbar-track {
        background: transparent;
    }
    
    .integrated-input-container textarea::-webkit-scrollbar-thumb {
        background: rgba(59, 130, 246, 0.3);
        border-radius: 3px;
    }

    .chat-input-sticky {
        position: sticky;
        bottom: 0;
        background: rgba(15, 23, 42, 0.95);
        border-top: 1px solid rgba(59, 130, 246, 0.3);
        padding: 16px;
        margin: 0 -24px -24px -24px;
        backdrop-filter: blur(10px);
        z-index: 100;
    }

    /* Modern Chat UI */
    .message-container {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        margin-bottom: 16px;
        animation: fadeIn 0.3s ease-out;
    }

    .message-container.user-message {
        flex-direction: row-reverse;
    }

    .avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        flex-shrink: 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }

    .user-avatar {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
    }

    .bot-avatar {
        background: rgba(30, 41, 59, 0.8);
        color: #e2e8f0;
        border: 2px solid rgba(59, 130, 246, 0.3);
    }

    .chat-bubble {
        max-width: 70%;
        padding: 12px 16px;
        border-radius: 20px;
        font-size: 15px;
        line-height: 1.4;
        word-wrap: break-word;
        position: relative;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .chat-bubble:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.2);
    }

    .chat-bubble.user {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        border-bottom-right-radius: 4px;
    }

    .chat-bubble.assistant {
        background: rgba(30, 41, 59, 0.8) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-bottom-left-radius: 4px;
        backdrop-filter: blur(8px);
    }

    /* Typing indicator */
    .typing-dots {
        display: inline-flex;
        gap: 4px;
    }

    .typing-dots span {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #64748b;
        animation: typing 1.4s infinite ease-in-out;
    }

    .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
    .typing-dots span:nth-child(2) { animation-delay: -0.16s; }

    @keyframes typing {
        0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
        40% { transform: scale(1); opacity: 1; }
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Scrollable chat container */
    [data-testid="stVerticalBlock"] [data-testid="stVerticalBlock"] {
        max-height: 500px;
        overflow-y: auto;
        padding-right: 8px;
    }

    [data-testid="stVerticalBlock"] [data-testid="stVerticalBlock"]::-webkit-scrollbar {
        width: 6px;
    }

    [data-testid="stVerticalBlock"] [data-testid="stVerticalBlock"]::-webkit-scrollbar-track {
        background: rgba(30, 41, 59, 0.3);
        border-radius: 3px;
    }

    [data-testid="stVerticalBlock"] [data-testid="stVerticalBlock"]::-webkit-scrollbar-thumb {
        background: rgba(59, 130, 246, 0.4);
        border-radius: 3px;
    }

    [data-testid="stVerticalBlock"] [data-testid="stVerticalBlock"]::-webkit-scrollbar-thumb:hover {
        background: rgba(59, 130, 246, 0.6);
    }

    /* Clear button styling */
    [data-testid="stButton"] button {
        border-radius: 12px !important;
        font-size: 14px !important;
        padding: 6px 12px !important;
        min-height: 36px !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="stButton"] button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
    }

    /* Chat input styling */
    [data-testid="stChatInput"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }

    [data-testid="stChatInput"] > div {
        background: rgba(26, 35, 50, 0.6) !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        border-radius: 24px !important;
        backdrop-filter: blur(10px) !important;
        transition: all 0.3s ease !important;
    }

    [data-testid="stChatInput"] > div:focus-within {
        background: rgba(26, 35, 50, 0.8) !important;
        border-color: rgba(59, 130, 246, 0.6) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }

    [data-testid="stChatInput"] input {
        background: transparent !important;
        border: none !important;
        color: #e2e8f0 !important;
        font-size: 15px !important;
        padding: 12px 20px !important;
    }

    [data-testid="stChatInput"] input::placeholder {
        color: #64748b !important;
    }
</style>
""", unsafe_allow_html=True)

# Custom chat bubble renderer
def render_chat_bubble(role, content):
    """Modern chat bubble with avatars and improved styling"""
    if role == "user":
        avatar = '<div class="avatar user-avatar">👤</div>'
        bubble_class = "chat-bubble user"
        container_class = "message-container user-message"
    else:
        avatar = '<div class="avatar bot-avatar">🤖</div>'
        bubble_class = "chat-bubble assistant"
        container_class = "message-container bot-message"

    html = f"""
    <div class="{container_class}">
        {avatar}
        <div class="{bubble_class}">
            {content}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# Groq API key :
client = Groq(api_key=os.getenv["GROQ_API_KEY"])

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "stage" not in st.session_state:
    st.session_state.stage = "initial"

if "user_symptom" not in st.session_state:
    st.session_state.user_symptom = ""

if "category" not in st.session_state:
    st.session_state.category = ""

# AI function to detect condition
def detect_condition(user_input):
    messages = [
        {"role": "system", "content": "You are a helpful medical assistant."}
    ]

    # Add last 5 messages for context
    for msg in st.session_state.messages[-5:]:
        messages.append(msg)

    messages.append({
        "role": "user",
        "content": f"Identify disease category for: {user_input}. Only return category name."
    })

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages
    )

    return response.choices[0].message.content.strip()

# AI generate response function
def generate_response(category, medicines, user_input):
    try:
        # Include recent chat history for context to avoid repetition
        messages = [
            {"role": "system", 
            "content": (
            "You are a friendly and simple medical assistant.\n"

            "Rules:\n"
            "- Keep answers SHORT (2-4 lines max)\n"
            "- Use very simple language\n"
            "- Avoid long explanations\n"
            "- Do NOT overload with bullet points unless necessary\n"
            "- Speak like a normal human, not a doctor\n"
            "- Give only the most useful advice\n"
            "- If needed, ask 1 small follow-up question\n"
            "- Make it engaging and friendly\n"
            "- Dont panic the user, even if symptoms sound bad. Be calm and reassuring.\n"
            "- only suggest hospital if symptoms sound like an emergency.\n"
            "- otherwise give calm advice\n"
            "- Do not suggest specific medicines unless it's very common\n"
            "- Keep advice general and safe\n"
            
            "Style:\n"
            "- Friendly\n"
            "- Calm\n"
            "- Straight to the point\n"
            )
          }
         ]
    
        # Add last 3 messages for context
        for msg in st.session_state.messages[-3:]:
            messages.append(msg)

        messages.append({
            "role": "user",
            "content": f"User symptoms: {user_input}\nDiagnosed condition: {category}\nRecommended medicines: {', '.join(medicines)}\n\nProvide a short response with:\n- Brief explanation (1-2 sentences)\n- Key advice in bullet points\n- Mention medicines if relevant\nKeep it human-like and relevant. Feel free to add emojis and make it engaging, but do NOT be repetitive or generic."
        })

        chat = client.chat.completions.create(
            messages=messages,
            model="llama3-8b-8192",
            max_tokens=150  # Limit length 
        )

        return chat_completion.choices[0].message.content.strip()

    except Exception as e:
        return f"Error: {str(e)}"
        
return ( 
     f"🧠 Based on your symptoms, this may be {category}."
     f"💊 Consider: {", ".join(medicines)}"
     "Please consult a doctor for proper diagnosis."
)

# AI intent detection function
def detect_intent(user_input):
    try:
        messages = [
            {"role": "system", "content": "You are an intent classifier for a medical chatbot. Classify the user's message into one of: greeting, thanks, symptom, emergency, or casual. Return only the intent category. If the message indicates a medical symptom, return 'symptom'. If it indicates a potential emergency, return 'emergency'. If it's a casual conversation or unrelated, return 'casual'. If it's a greeting, return 'greeting'. If it's a thank you, return 'thanks'."}
        ]

        # Add last 2 messages for context
        for msg in st.session_state.messages[-2:]:
            messages.append(msg)

        messages.append({
            "role": "user",
            "content": f"Classify this message: '{user_input}'. Intent: "
        })

        response = client.chat.completions.create(
            messages=messages,
            model="llama-3.1-8b-instant",
            max_tokens=10
        )

        intent = response.choices[0].message.content.strip().lower()
        return intent

    except Exception as e:
        return "casual"  # Default fallback

# DB function
def get_medicine_from_db(disease):
    conn = sqlite3.connect("tab3_medicines.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT medicine FROM medicines WHERE disease=?",
        (disease,)
    )

    results = cursor.fetchall()
    conn.close()

    return [r[0] for r in results]

# Load the model
@st.cache_resource
def load_model():
    tokenizer = AutoTokenizer.from_pretrained("symptom_model")
    model = AutoModelForSequenceClassification.from_pretrained("symptom_model")
    return tokenizer, model

tokenizer, model = load_model()

# Emergency keywords
emergency_keywords = [
    "chest pain",
    "breathing difficulty",
    "breathless",
    "heavy bleeding",
    "unconscious",
    "severe headache",
    "seizure",
    "stroke",
    "heart attack"
]

# Prediction Function
def predict_symptom(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    outputs = model(**inputs)
    probs = F.softmax(outputs.logits, dim=1)
    confidence, predicted_class = torch.max(probs, dim=1)
    confidence = round(confidence.item() * 100, 2)
    categories = {
        0: "General Fever & Pain",
        1: "Digestive Issue",
        2: "Skin / Allergy",
        3: "Emergency Symptom"
    }

    return categories[predicted_class.item()], confidence

# Emergency override function
def emergency_override(text):
    text = text.lower()
    for word in emergency_keywords:
        if word in text:
            return True
    return False

# Database connection
conn = st.connection("mediciines.db", type="sql", url="sqlite:///medicines.db")

# Load and prepare data
@st.cache_data
def load_and_prepare_data():
    try:
        df = conn.query("SELECT * FROM medicines", ttl=3600)
    except Exception as e:
        st.error(f"Error loading database: {e}. Please check 'medicines.db'.")
        st.stop()

    df.columns = [col.strip() for col in df.columns]
    first_col_name = df.columns[0]

    medicine_data = {}
    for index, row in df.iterrows():
        medicine_name_key = str(row[first_col_name]).lower().strip()
        details = {}
        for col in df.columns:
            if col != first_col_name:
                details[col] = row[col]
        details['Name'] = row[first_col_name]
        medicine_data[medicine_name_key] = details

    return medicine_data, df

MEDICINE_DATA, medicine_df = load_and_prepare_data()
MEDICINE_NAMES = list(MEDICINE_DATA.keys())

# Lookup medicine function
def lookup_medicine(name):
    name_lower = name.lower().strip()

    if name_lower in MEDICINE_DATA:
        return MEDICINE_DATA[name_lower], MEDICINE_DATA[name_lower]['Name']

    best_match = process.extractOne(name_lower, MEDICINE_NAMES, score_cutoff=80)

    if best_match:
        matched_key = best_match[0]
        return MEDICINE_DATA[matched_key], MEDICINE_DATA[matched_key]['Name']

    return None, None

# Lookup by symptom
def lookup_by_symptom(query, df, cutoff=70):
    results = []

    if 'Symptoms' not in df.columns:
        st.error("Error: 'Symptoms' column not found in data.")
        return []

    for index, row in df.iterrows():
        if pd.isna(row['Symptoms']):
            continue

        score = fuzz.token_set_ratio(query.lower(), str(row['Symptoms']).lower())

        if score >= cutoff:
            results.append((row['Name'], score))

    results.sort(key=lambda x: x[1], reverse=True)
    return [name for name, score in results]

# Advice and followup maps
advice_map = {
    "General Fever & Pain": [
        "Rest and stay hydrated",
        "Take paracetamol if needed",
        "Monitor temperature"
    ],
    "Digestive Issue": [
        "Drink plenty of water or oral rehydration solution",
        "Avoid oily, spicy, or heavy foods",
        "Eat light meals like rice, bananas, or toast"
    ],
    "Skin / Allergy": [
        "Avoid known allergens",
        "Use antihistamines if recommended",
        "Keep skin clean and dry"
    ],
    "Emergency Symptom": [
        "Seek immediate medical attention",
        "Do not delay visiting the nearest hospital",
        "Call emergency services if symptoms worsen"
    ]
}

followup_questions = {
    "Digestive Issue": "Do you also have vomiting, nausea, or diarrhea?",
    "General Fever & Pain": "Do you have high temperature or body chills?",
    "Skin / Allergy": "Do you see redness, rash, or itching?",
    "Emergency Symptom": "Are you experiencing severe pain or difficulty breathing?"
}

SYMPTOM_MAP = {
    "General Fever & Pain": ["fever", "body pain", "headache", "weakness", "chills", "fatigue", "muscle ache", "joint pain", "bone pain"],
    "Digestive Issue": ["stomach pain", "vomiting", "nausea", "diarrhea", "constipation", "bloating", "acid reflux", "indigestion"],
    "Cold & Cough": ["cough", "cold", "sneezing", "sore throat", "runny nose", "congestion"],
    "Skin / Allergy": ["rash", "redness", "itching", "hives", "swelling", "dry skin", "eczema", "psoriasis"],
    "Emergency Symptom": ["chest pain", "breathing difficulty", "breathless", "heavy bleeding", "unconscious", "severe headache", "seizure", "stroke", "heart attack"]
}

# Streamlit app layout
st.set_page_config(page_title="AI Health Assistant", page_icon="🧠", layout="wide")

# Hero header
st.markdown(
    '<div style="text-align: center; margin-bottom: 32px; margin-top: 24px;">'
    '<h1 style="font-size: 42px; margin-bottom: 8px;"> AI Health Assistant</h1>'
    '<p style="font-size: 16px; color: #94a3b8; margin: 0;">Your personal AI-powered health companion</p>'
    '</div>',
    unsafe_allow_html=True
    )

st.markdown('''<div class="card-container"><p style="margin: 0; color: #fca5a5;">⚠️ <strong>Disclaimer:</strong> Always consult a qualified doctor or pharmacist before using medicine. This tool is for general information only.</p></div>''', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Search by Medicine Name", "Search by Symptom", "AI Assistant"])

# TAB 1: SEARCH BY NAME
with tab1:
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown("### 💊 Search by Medicine Name")
    name_input = st.text_input(
        "What medicine would you like to know about?",
        placeholder="e.g., Crocin, Nutrich Capsule, Aspirin, etc.",
        key="name_search",
        label_visibility="collapsed"
    )

    if name_input:
        with st.spinner(f"Searching for '{name_input}'..."):
            details, name_found = lookup_medicine(name_input)

            if details:
                st.success(f"✅ Found Information for: *{name_found}*")
                display_data = pd.DataFrame(details.items(), columns=['Attribute', 'Detail'])
                st.dataframe(display_data, hide_index=True, use_container_width=True)
            else:
                st.info(f"❌ Could not find information for '{name_input}'. Try again or be more precise.")
    st.markdown('</div>', unsafe_allow_html=True)

# TAB 2: SEARCH BY SYMPTOM
with tab2:
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown("### 🔍 Search by Symptom")

    if st.button("🔄 Start New Diagnosis"):
        st.session_state.stage = "initial"
        st.session_state.user_symptom = ""
        st.session_state.category = ""
        st.rerun()

    st.divider()

    symptom_input = st.text_input(
        "Describe your symptoms in plain language:",
        placeholder="e.g., headache, fever, nausea, etc."
    )

    if symptom_input and st.session_state.stage == "initial":
        with st.spinner("🤖 Understanding your symptoms..."):
            time.sleep(1.5)
            category, confidence = predict_symptom(symptom_input)
        st.session_state.user_symptom = symptom_input
        st.session_state.category = category
        st.session_state.stage = "followup"
        st.rerun()

# Calculate the confidence score based on symptom matches :
    def calculate_confidence(user_input, detected_category):
        user_input = user_input.lower()
        symptoms = SYMPTOM_MAP.get(detected_category, [])

        match_count = 0

        for symptom in symptoms:
            if symptom in user_input:
                match_count += 1

        total = len(symptoms)

        if total == 0:
            return 50.0

        confidence = (match_count / total) * 100

# Minimum confidence cap
        if confidence < 30:
            confidence = 30 + confidence

        return round(confidence, 2)
    
    if st.session_state.stage in ["followup", "analysis"]:
        st.divider()
        st.success(f"🧠 Diagnosis: **{st.session_state.category}**")
        confidence = calculate_confidence(st.session_state.user_symptom, st.session_state.category)
        st.metric("AI Confidence", f"{confidence}%")
        st.divider()

        if st.session_state.category in followup_questions:
            st.warning(f"❓ Follow-up question: {followup_questions[st.session_state.category]}")

        if st.session_state.stage == "followup":
            followup_answer = st.text_input("Your answer:", placeholder="Example: yes, vomiting")
            if followup_answer:
                st.session_state.stage = "analysis"
                st.rerun()

        if st.session_state.stage == "analysis":
            st.divider()
            st.write("### 🔎 AI Analyzed")
            st.info(f"Based on the symptoms you described (**{st.session_state.user_symptom}**) and your response, the AI believes this may indicate **{st.session_state.category}**.")
            st.divider()
            st.success("✅ Preparing health advice...")
            time.sleep(1)

            if st.session_state.category in advice_map:
                st.subheader("💡 General Advice")
                for tip in advice_map[st.session_state.category]:
                    st.write(f"• {tip}")

            if emergency_override(st.session_state.user_symptom):
                st.error(
"return🚨 **Emergency symptoms detected**\n"
"These symptoms may indicate a serious medical condition.\n"
"Please seek **immediate medical attention** or contact emergency services.\n"
)

            st.divider()

            with st.spinner(f"Searching medicines related to '{st.session_state.user_symptom}'..."):
                medicine_list = lookup_by_symptom(st.session_state.user_symptom, medicine_df)

            if medicine_list:
                st.success(f"✅ Found {len(medicine_list)} medicine(s)")
                for med_name in medicine_list:
                    st.markdown(f"- **{med_name}**")
                st.divider()
                st.warning("⚠️ If symptoms persist for more than 2 days or become severe, please consult a doctor.")
            else:
                st.info(f"❌ Could not find medicines for '{st.session_state.user_symptom}'.")
    st.markdown('</div>', unsafe_allow_html=True)

# TAB 3: AI ASSISTANT :
with tab3:
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown("### 🤖 AI Health Assistant")
    st.markdown("<p style='color: #94a3b8; margin-bottom: 16px;'>Chat naturally about your health concerns. Type symptoms or casual messages.</p>", unsafe_allow_html=True)

    # Clear Chat button - top right, smaller
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🗑️", help="Clear Chat"):
            st.session_state.messages = []
            st.rerun()

    # STEP 1: Chat container FIRST
    chat_container = st.container(height=500, border=False)

    # STEP 2: Input AFTER container
    user_input = st.chat_input("How are you feeling?", key="chat_input")

    # STEP 3: Process input
    if user_input and user_input.strip():
        # Append user message
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Show typing indicator
        with chat_container:
            st.markdown(
            '<div style="display: flex; align-items: center; gap: 8px; margin: 12px 0; color: #64748b;">'
                '<div style="width: 24px; height: 24px; border-radius: 50%; background: rgba(59, 130, 246, 0.2); display: flex; align-items: center; justify-content: center;">'
                    'return🤖'
                '</div>'
                '<div>AI is typing...</div>'
                '<div class="typing-dots">'
                    '<span></span><span></span><span></span>'
                '</div>'
            '</div>',
            unsafe_allow_html=True)

        # Check emergency condition
        danger_words = ["chest pain", "breathing", "unconscious", "severe", "blood"]
        if any(word in user_input.lower() for word in danger_words):
            st.error("⚠️ This may be serious. Please seek immediate medical help.")

        # Process input with AI intent detection
        intent = detect_intent(user_input)

        if intent in ["symptom", "emergency"]:
            # Medical response
            try:
                category = detect_condition(user_input)
                medicines = get_medicine_from_db(category)
                if not medicines:
                    medicines = ["Consult a doctor"]
                response = generate_response(category, medicines, user_input)
            except Exception as e:
                response = "Sorry, I couldn't process that. Please try again."
        else:
            # Casual or general response
            try:
                messages = [
                    {
                        "role": "system",
                        "content": (
                    "You are a friendly and simple medical assistant.\n"
                    "Rules:\n"
                    "- Keep answers SHORT (1-4 lines max)\n"
                    "- Use very simple language\n"
                    "- Do not panic the user, even if symptoms sound bad. Be calm and reassuring.\n"
                    "- If the message indicates a greeting, respond with a friendly greeting.\n"
                    "- If the message indicates a thank you, respond with a polite acknowledgment.\n"
                    "- Make it engaging and human-like.\n"
                        )
                    }
                ]

                # Add last 3 messages for context
                for msg in st.session_state.messages[-3:]:
                    messages.append(msg)

                messages.append({
                    "role": "user",
                    "content": user_input
                })

                chat = client.chat.completions.create(
                    messages=messages,
                    model="llama-3.1-8b-instant",
                    max_tokens=120
                )

                response = chat.choices[0].message.content.strip()

            except Exception as e:
                # Fallback responses
                if intent == "greeting":
                    response = "👋 Hi! How can I help you today?"
                elif intent == "goodbye" or intent == "bye" or intent == "byy" or intent == "exit":
                    response = "👍 Take care! Stay healthy."
                elif intent == "casual":
                    response = "That's interesting! If you have any health questions, feel free to ask."
                else:
                    response = "I'm here to help. What can I do for you?"

        # Append assistant message
        if response:
            st.session_state.messages.append({"role": "assistant", "content": response})

        st.rerun()

    # STEP 4: Inside chat_container - display messages
    with chat_container:
        if len(st.session_state.messages) == 0:
            # Empty state
            st.markdown(
                '<div style="text-align: center; padding: 60px 20px; color: #64748b;">'
                '<div style="font-size: 48px; margin-bottom: 16px;">💬</div>'
                '<div style="font-size: 18px; margin-bottom: 8px;">Start a conversation</div>'
                '<div style="font-size: 14px;">Ask about symptoms or health concerns</div>'
                '</div>'
                unsafe_allow_html=True)
        else:
            # Display messages directly (Streamlit container handles scrolling)
            for msg in st.session_state.messages:
                render_chat_bubble(msg["role"], msg["content"])

    st.markdown("---")
    st.caption("⚠️ This is not medical advice. Always consult a doctor.")

    st.markdown('</div>', unsafe_allow_html=True)  # close section-card

# Footer for professional look
st.markdown(
    '<div class="footer-premium">'
    '<p style="margin: 0; font-size: 12px;">Build by Ashraf & shoaib ❤️ | AI Health Assistant v3.0</p>'
    '<p style="margin: 8px 0 0 0; font-size: 11px; color: #64748b;">© 2026 AI Health Assistant. Not a substitute for professional medical advice.</p>'
    '</div>',
    unsafe_allow_html=True
)
