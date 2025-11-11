import streamlit as st
import pandas as pd
import os
from fuzzywuzzy import fuzz

# --- 1. DATA LOADING AND PREPARATION ---

@st.cache_data
def load_and_prepare_data():
    """
    Loads data from 'data.csv', standardizes column names, and converts it
    into a dictionary for fast, case-insensitive lookup.
    """
    file_path = 'data.csv'
    medicine_data = {}
    
    # 1. File Existence Check
    if not os.path.exists(file_path):
        st.error(f"Data file not found: {file_path}. Please ensure it is in the same folder.")
        st.stop()
        
    try:
        # Load the CSV file
        df = pd.read_csv(file_path)

        # 2. Standardize column names
        df.columns = [col.strip() for col in df.columns]

        # Get the name of the first column (assumed to be the medicine name)
        first_col_name = df.columns[0] 

        # 3. Prepare the dictionary for quick lookup
        for index, row in df.iterrows():
            # Use the first column value as the key (lowercased and stripped)
            medicine_name_key = str(row.iloc[0]).lower().strip()

            # Store all other row data (excluding the name itself)
            row_details = row.to_dict()
            
            # CRITICAL FIX: Delete the medicine name entry using the COLUMN NAME
            if first_col_name in row_details:
                del row_details[first_col_name]
            
            # Store the details against the lowercased key
            medicine_data[medicine_name_key] = row_details
            
        return medicine_data

    except Exception as e:
        # Stop execution if data loading fails
        st.error(f"Error loading or processing data.csv: {e}")
        st.stop()

# --- Load the data right when the application starts ---
MEDICINE_DATA = load_and_prepare_data()
MEDICINE_NAMES = list(MEDICINE_DATA.keys())


# --- 2. MAIN LOOKUP FUNCTION (The core logic with fuzzy matching) ---

def lookup_medicine(name):
    """Searches the pre-loaded data structure for a medicine name, including fuzzy matching."""
    name_lower = name.lower().strip()
    
    # 1. Exact Match Check (Highest priority)
    if name_lower in MEDICINE_DATA:
        return MEDICINE_DATA[name_lower], name_lower

    # 2. Partial/Prefix Match Check (Handles users typing the start of a word)
    for key in MEDICINE_NAMES:
        if key.startswith(name_lower):
            return MEDICINE_DATA[key], key
            
    # --- 3. FUZZY MATCH CHECK (For misspellings) ---
    FUZZY_THRESHOLD = 80 # Requires an 80% or higher match score
    
    best_match_name = None
    best_score = 0
    
    for key in MEDICINE_NAMES:
        # Use token_set_ratio for better matching when words are out of order, 
        # or fuzz.ratio for general similarity
        score = fuzz.ratio(name_lower, key) 
        
        if score > best_score and score >= FUZZY_THRESHOLD:
            best_score = score
            best_match_name = key
            
    if best_match_name:
        return MEDICINE_DATA[best_match_name], best_match_name
        
    # 4. No Match Found
    return None, None


# --- 3. STREAMLIT APP LAYOUT ---

st.set_page_config(page_title="AI Medicine Lookup Tool", page_icon="💊", layout="wide")

st.title("💊 AI Medicine Lookup Tool")

# Display a standard warning as a safety measure
st.warning("⚠ *ALWAYS consult a qualified doctor or pharmacist* before using medicine. This tool is for general information only.")
st.markdown("---")


# 1. User Input Section
user_input = st.text_input(
    "### What medicine would you like to know about?",
    placeholder="e.g., Crocin, Nutrich Capsule, Aspirin, etc."
)


# 2. Lookup and Display Logic
if user_input:
    with st.spinner(f"Searching for '{user_input}'..."):
        # Call the lookup function
        details, name_found = lookup_medicine(user_input)
submitted = s.t form_submit_button

    # Display Results
    if details:
        # Check if the name found is different from the original input (indicating a fuzzy match)
        if name_found != user_input.lower().strip():
            st.info(f"💡 Showing results for *{name_found.title()}* (Closest match found for '{user_input}').")

        st.success(f"✅ Found Information for: *{name_found.title()}*")
        
        # Convert the dictionary of details into a clean, two-column table for display
        display_data = pd.DataFrame(details.items(), columns=['Attribute', 'Detail'])
        
        # Display the table cleanly
        st.dataframe(
            display_data, 
            hide_index=True,
            use_container_width=True,
            column_config={
                "Attribute": st.column_config.Column("Attribute", width="small"),
                "Detail": st.column_config.Column("Detail", width="large"),
            }
        )
            
    else:
        # No match found
        st.error(f"😔 Could not find information for *{user_input}*.")
        st.info("Try checking your spelling or search for the full medicine name.")

st.markdown("---")
st.caption("Application powered by Streamlit and your custom data lookup logic.")