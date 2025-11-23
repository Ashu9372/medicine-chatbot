import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz, process #
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder, speech_to_text #
import os

# --- DATABASE CONNECTION SETUP ---
conn = st.connection("mediciines.db", type="sql", url="sqlite:///medicines.db")

# --- 1. DATA LOADING AND PREPARATION ---

@st.cache_data
def load_and_prepare_data():
    """
    Loads data from 'medicines.db', standardizes column names, 
    AND returns BOTH the fast lookup dictionary AND the full DataFrame.
    """
    
    try:
        # 1. Load the data from the database
        df = conn.query("SELECT * FROM medicines", ttl=3600) 
        
    except Exception as e:
        # Stop the app if the database can't be read
        st.error(f"Error loading database: {e}. Please check 'medicines.db'.")
        st.stop()

    
    # 2. Standardize column names
    df.columns = [col.strip() for col in df.columns]

    # 3. Get the name of the first column
    first_col_name = df.columns[0]
    
    medicine_data = {} # Your dictionary

    # 4. Prepare the dictionary
    for index, row in df.iterrows():
        medicine_name_key = str(row[first_col_name]).lower().strip()
        
        details = {}
        for col in df.columns:
            if col != first_col_name:
                details[col] = row[col]
        
        details['Name'] = row[first_col_name]
        medicine_data[medicine_name_key] = details
    
    # NEW: Return both the dictionary AND the full DataFrame
    return medicine_data, df

# --- Load the data right when the application starts ---
# Correct function call: NO arguments are passed since the file_path is internal
MEDICINE_DATA, medicine_df = load_and_prepare_data()
MEDICINE_NAMES = list(MEDICINE_DATA.keys())


# --- 2. MAIN LOOKUP FUNCTION (The core logic) ---

def lookup_medicine(name):
    """
    Searches the pre-loaded data structure for a medicine name.
    Tries an exact match first, then fuzzy matching.
    """
    name_lower = name.lower().strip()

    # 1. Exact Match Check (Most efficient)
    if name_lower in MEDICINE_DATA:
        # Found a perfect key match (e.g., user typed 'crocin')
        return MEDICINE_DATA[name_lower], MEDICINE_DATA[name_lower]['Name']

    # 2. Fuzzy Match Check (Smarter fallback for typos like 'crocinn')
    best_match = process.extractOne(name_lower, MEDICINE_NAMES, score_cutoff=80)
    
    if best_match:
        matched_key = best_match[0] # This is the key, e.g., 'crocin'
        
        # Now, return the details from the dictionary using the matched key
        return MEDICINE_DATA[matched_key], MEDICINE_DATA[matched_key]['Name']
    
    # 3. Return None if no match is found
    return None, None

def lookup_by_symptom(query, df, cutoff=70):
    """
    Searches the 'Symptoms' column of the DataFrame for matches.
    Tries an exact match first, then fuzzy matching.
    """
    results = []
    
    # Ensure the 'Symptoms' column exists
    if 'Symptoms' not in df.columns:
        st.error("Error: 'Symptoms' column not found in data.")
        return []

    for index, row in df.iterrows():
        # Check for NaN/empty values in 'Symptoms'
        if pd.isna(row['Symptoms']):
            continue
            
        # Use fuzzywuzzy 'token_set_ratio'
        score = fuzz.token_set_ratio(query.lower(), str(row['Symptoms']).lower())
        
        if score >= cutoff:
            # Store the name and its score
            results.append((row['Name'], score))
    
    # Sort results by score, highest first
    results.sort(key=lambda x: x[1], reverse=True)
    
    # Return just the names of the top matches
    return [name for name, score in results]

# --- 4. AI SYMPTOM EXTRACTOR ---
def extract_symptoms_with_ai(user_query):
    """
    Uses the Gemini AI to extract key symptoms from a user's natural language query.
    """
    # Configure the AI with your API key from secrets
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    except Exception as e:
        st.error("Error: Could not configure AI. Have you set your GOOGLE_API_KEY in .streamlit/secrets.toml?")
        return None

    # This line must be correctly indented under the 'def'
    model = genai.GenerativeModel('gemini-2.5-flash') 
    
    # The 'prompt' variable itself must be correctly indented.
    # The text inside the triple quotes should be left-aligned (no indentation).
    prompt = f"""
You are a medical symptom extractor. Analyze the user's text and extract the key medical symptoms.
Return ONLY a comma-separated list of symptoms or the word 'None'. Do not add any explanation.

User Text: "I feel pain in my head, and I need something to fix it."
Symptoms: Headache

User Text: "I can't sleep anymore."
Symptoms: Insomnia

User Text: "{user_query}"
Symptoms: 
"""

    try:
        # Send the prompt to the AI
        response = model.generate_content(prompt)
        # Return the AI's clean list of symptoms
        return response.text.strip()
    except Exception as e:
        st.error(f"AI Error: {e}")
        return None

# --- 3. STREAMLIT APP LAYOUT ---

st.set_page_config(page_title="AI Medicine Lookup Tool", page_icon="💊", layout="wide")
st.title("💊 AI Medicine Lookup Tool")
st.warning("⚠ ALWAYS consult a qualified doctor or pharmacist before using medicine. This tool is for general information only.")

tab1, tab2, tab3 = st.tabs(["Search by Medicine Name", "Search by Symptom", "AI Assistant"])

# --- TAB 1: SEARCH BY NAME ---
with tab1:
    st.header("Search by Medicine Name")
    name_input = st.text_input(
        "What medicine would you like to know about?",
        placeholder="e.g., Crocin, Nutrich Capsule, Aspirin, etc.",
        key="name_search"
    )

    if name_input:
        with st.spinner(f"Searching for '{name_input}'..."):
            # This calls your original lookup_medicine function
            details, name_found = lookup_medicine(name_input) 
            
            if details:
                st.success(f"✅ Found Information for: *{name_found}*")
                
                # Convert dictionary details to a clean DataFrame for display
                display_data = pd.DataFrame(details.items(), columns=['Attribute', 'Detail'])
                st.dataframe(
                    display_data,
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info(f"❌ Could not find information for '{name_input}'. Try again or be more precise.")

# --- TAB 2: SEARCH BY SYMPTOM (Corrected logic) ---
with tab2:
    st.header("Search by Symptom")
    symptom_input = st.text_input(
        "What symptom are you experiencing?",
        placeholder="e.g., Headache, Fever, Runny Nose",
        key="symptom_search"
    )
    
    if symptom_input:
        with st.spinner(f"Searching for medicines related to '{symptom_input}'..."):
            # Call our new function, passing it the full DataFrame
            medicine_list = lookup_by_symptom(symptom_input, medicine_df)
            
            if medicine_list:
                st.success(f"✅ Found {len(medicine_list)} medicine(s) for '{symptom_input}':")
                
                # --- THIS IS THE MISSING PART ---
                # This loop prints each medicine name
                for med_name in medicine_list:
                    st.markdown(f"- *{med_name}*")
                
            else:
                st.info(f"❌ Could not find any medicines for '{symptom_input}'.")
              
# --- TAB 3: AI ASSISTANT (Voice Integration) ---
with tab3:
    st.header("AI Assistant 🤖")
    st.info("Ask in plain English, or click the mic button to speak!")
    
    # 1. VOICE INPUT COMPONENT
    voice_recording = speech_to_text(
        language="en",
        start_prompt="Click to Speak",
        stop_prompt="Analyzing Audio...",
        key='stt_recording',
        just_once=False
    )
    
    st.markdown("---")
    
    # 2. TEXT INPUT (Retained for typing)
    ai_input = st.text_input(
        "How are you feeling? (Or type your question here)",
        placeholder="e.g., I'm feeling really hot and my head hurts...",
        key="ai_search"
    )

# 3. Determine which input to use (speech-to-text output takes priority)
    input_to_use = None
    
    if voice_recording:
        input_to_use = voice_recording
        st.info(f"🎙 *Transcribed Text:* {input_to_use}")
        
    elif ai_input:
        input_to_use = ai_input
    
    if input_to_use:
        # --- AI LOGIC (This starts the processing) ---
        with st.spinner("Asking the AI to understand your symptoms..."):

            # 1. AI extracts keywords
            symptoms_from_ai = extract_symptoms_with_ai(input_to_use) 
        
        if symptoms_from_ai and symptoms_from_ai.lower() != 'none':
            st.write(f"*AI understood your symptoms as:* {symptoms_from_ai}")
            
            with st.spinner(f"Searching your database for '{symptoms_from_ai}'..."):
                # 2. Feed keywords into your existing symptom function
                medicine_list = lookup_by_symptom(symptoms_from_ai, medicine_df)
            
            # --- DISPLAY RESULTS ---
            if medicine_list:
                st.success(f"✅ Found {len(medicine_list)} medicine(s) for your symptoms:")
                for med_name in medicine_list:
                    st.markdown(f"- *{med_name}*")
            else:
                st.info(f"❌ Your database has no medicines for the symptoms: '{symptoms_from_ai}'.")
        else:
            st.error("Could not process your request with the AI.")

        # --- FOOTER ---
            st.markdown("---") # Adds a visible line separator
            st.caption("© 2025 | Developed by **Ashraf & Shoaib**")
