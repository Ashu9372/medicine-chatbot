import streamlit as st
import pandas as pd
import os
from fuzzywuzzy import fuzz, process #

# Connect to your new database
conn = st.connection("medicines_db", type="sql", url="sqlite:///medicines.db")

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

# --- 3. STREAMLIT APP LAYOUT ---

st.set_page_config(page_title="AI Medicine Lookup Tool", page_icon="💊", layout="wide")
st.title("💊 AI Medicine Lookup Tool")
st.warning("⚠ ALWAYS consult a qualified doctor or pharmacist before using medicine. This tool is for general information only.")

tab1, tab2 = st.tabs(["Search by Medicine Name", "Search by Symptom"])

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

# --- TAB 2: SEARCH BY SYMPTOM ---
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
                
                # Display the results as a list
                for med_name in medicine_list:
                    st.markdown(f"- *{med_name}*")
                
            else:
                st.info(f"❌ Could not find any medicines for '{symptom_input}'.")
    Loads data from 'data.csv', standardizes column names, and converts it
    into a dictionary for fast, case-insensitive lookup.
    """
    file_path = 'data.csv'
    medicine_data = {}
    
    # 1. File Existence Check
    if not os.path.exists(file_path):
        st.error(f"Data file not found: {file_path}. Please ensure it is in the same folder.")
        # If the file is missing, we stop the app execution
        st.stop()
        
    try:
        # Load the CSV file
        df = pd.read_csv(file_path)

        # 2. Standardize column names (optional, but good practice)
        df.columns = [col.strip() for col in df.columns]

        # Get the name of the first column (assumed to be the medicine name)
        # We need this to exclude it later from the details dictionary.
        first_col_name = df.columns[0] 

        # 3. Prepare the dictionary for quick lookup
        for index, row in df.iterrows():
            # Use the first column value as the key (lowercased and stripped)
            medicine_name_key = str(row.iloc[0]).lower().strip()

            # Store all other row data (excluding the name itself)
            row_details = row.to_dict()
            
            # --- CRITICAL FIX: Delete the medicine name entry using the COLUMN NAME ---
            # This prevents the medicine name from being duplicated in the details
            if first_col_name in row_details:
                del row_details[first_col_name]
            
            # Store the details against the lowercased key
            medicine_data[medicine_name_key] = row_details
            
        return medicine_data

    except Exception as e:
        # If any other error occurs during loading (e.g., CSV format issue)
        st.error(f"Error loading or processing data.csv: {e}")
        st.stop() # Stop execution if data loading fails

# --- Load the data right when the application starts ---
# Correct function call: NO arguments are passed since the file_path is internal
MEDICINE_DATA = load_and_prepare_data()
MEDICINE_NAMES = list(MEDICINE_DATA.keys())


# --- 2. MAIN LOOKUP FUNCTION (The core logic) ---

def lookup_medicine(name):
    """Searches the pre-loaded data structure for a medicine name."""
    name_lower = name.lower().strip()
    
    # 1. Exact Match Check (Most efficient)
    if name_lower in MEDICINE_DATA:
        return MEDICINE_DATA[name_lower], name_lower

    # 2. Partial Match Check (Less efficient, used as fallback)
    # Check if the key starts with the user's input for better accuracy than substring match
    for key in MEDICINE_NAMES:
        if key.startswith(name_lower):
            return MEDICINE_DATA[key], key
            
    return None, None # Return None if no match is found

# --- 3. STREAMLIT APP LAYOUT ---

st.set_page_config(page_title="AI Medicine Lookup Tool", page_icon="💊", layout="wide")

st.title("💊 AI Medicine Lookup Tool")

# Display a standard warning as a safety measure
st.warning("⚠ ALWAYS consult a qualified doctor or pharmacist before using medicine. This tool is for general information only.")
st.markdown("---")


# 1. User Input Section
user_input = st.text_input(
    "### What medicine would you like to know about?",
    placeholder="e.g., Crocin, Nutrich Capsule, Aspirin, etc."
)
st.button("Search Medicines")

# 2. Lookup and Display Logic
if user_input:
    # Use st.spinner for a professional look while the search runs
    with st.spinner(f"Searching for '{user_input}'..."):
        # Call the lookup function
        details, name_found = lookup_medicine(user_input)

    # Display Results
    if details:
        st.success(f"✅ Found Information for: {name_found.title()}")
        
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
        st.error(f"😔 Could not find information for {user_input}.")
        st.info("Try checking your spelling or search for the full medicine name.")

>>>>>>> b718c84c54cb7a919a7b8d01663d66db26f0cf11
st.markdown("---")
st.caption("Application powered by Streamlit (Ashraf) and your custom data lookup logic.")