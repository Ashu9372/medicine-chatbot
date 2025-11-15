import streamlit as st
import pandas as pd
import os

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

st.markdown("---")
st.caption("Application powered by Streamlit and your custom data lookup logic.")
