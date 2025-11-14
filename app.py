import streamlit as st
import pandas as pd
from fun import load_data_robust, lookup_medicine   # Import correct functions

<<<<<<< HEAD
# ----------------------------------------------------
# 0. LOAD DATA (cached so loads only once)
# ----------------------------------------------------
@st.cache_data
def get_medicine_data():
    try:
        return load_data_robust()
    except Exception:
        return None

MEDICINE_DF = get_medicine_data()

# ----------------------------------------------------
# 1. Streamlit Page Settings
# ----------------------------------------------------
st.set_page_config(page_title="💊 AI Medicine Lookup Tool", layout="centered")

=======
# --- 1. CONFIGURATION (run once) ---
st.set_page_config(page_title="AI Medicine Lookup Tool", layout="centered")

# --- 2. HEADER AND DISCLAIMER ---
>>>>>>> 93570be1b0596f80fddfc6392ea31bb5d13eec0f
st.title("💊 AI Medicine Lookup Tool")
st.info("⚠ ALWAYS consult a qualified doctor or pharmacist before using any medication. "
        "This tool provides general information only.")

<<<<<<< HEAD
# ----------------------------------------------------
# 2. Check Data Loading
# ----------------------------------------------------
if MEDICINE_DF is None:
    st.error("❌ CRITICAL ERROR: Could not load 'data.csv'. Please check the file location.")
    st.stop()

# ----------------------------------------------------
# 3. Search Form
# ----------------------------------------------------
with st.form(key="medicine_search_form"):
    user_input = st.text_input(
        "Enter medicine name to search:",
        placeholder="e.g., Crocin, Aspirin, Nutrich Capsule..."
    )
    submitted = st.form_submit_button("Search Medicine")

# ----------------------------------------------------
# 4. Lookup Logic
# ----------------------------------------------------
if submitted and user_input:
    query = user_input.strip()

    with st.spinner(f"Searching for '{query}'..."):
        result_details, matched_name = lookup_medicine(query, MEDICINE_DF)

    if result_details is None:
        st.error(f"❌ No match found for '{query}'.")
        st.info("💡 Try checking spelling or entering more letters.")
    else:
        # Handle fuzzy match (show closest match)
        if matched_name.lower() != query.lower():
            st.info(f"🔍 Showing results for **{matched_name}** (closest match found)")
        
        st.success(f"✅ Found information for **{matched_name}**")

        # Convert details to a DataFrame for display
        display_df = pd.DataFrame(
            list(result_details.items()),
            columns=["Attribute", "Detail"]
        )

        # Display the information table
        st.dataframe(
            display_df,
            hide_index=True,
            use_container_width=True
        )

# ----------------------------------------------------
# 5. Footer
# ----------------------------------------------------
st.markdown("---")
st.caption("App powered by Streamlit and your custom medicine lookup engine.")
=======
# --- 3. SEARCH FORM ---
with st.form(key="medicine_search_form"):
    # The input field for the medicine name
    user_input = st.text_input(
        "What medicine would you like to know about?",
        placeholder="e.g., Crocin, Nutrich Capsule, Aspirin, etc."
    )
    
    # The submit button should be inside the form
    submitted = st.form_submit_button(label="Search Medicine")

# --- 4. LOOKUP AND DISPLAY LOGIC ---
# This block runs ONLY when the user clicks the button AND the input is not empty.
# We check 'submitted' and ensure 'user_input' is not an empty string.
if submitted and user_input:
    # Call the lookup function, showing a spinner while waiting
    with st.spinner(f"Searching for {user_input.strip()}..."):
        # ASSUMPTION: The 'lookup_medicine' function is defined elsewhere (or imported).
        # We assume it returns a dictionary 'details' and a string 'name_found'.
        try:
            # The NameError fix is implemented here by using the 'user_input' defined above
            details, name_found = lookup_medicine(user_input) 
        except NameError:
            # Handle the case where lookup_medicine is not defined/imported
            st.error("❌ Developer Error: 'lookup_medicine' function is not defined or imported.")
            details = None

    if details:
        # --- Handle Fuzzy Match Notification ---
        # Compare the cleaned-up found name with the cleaned-up user input
        if name_found.lower().strip() != user_input.lower().strip():
            # Show the user the app found a close match
            st.info(f"🔍 Showing results for *{name_found.title()}* (closest match found for '{user_input.strip()}')")

        st.success(f"✅ Found Information for: *{name_found.title()}*")

        # --- Display Results in Table ---
        
        # Convert the dictionary/details into a DataFrame for display
        # The .items() creates a list of (key, value) tuples, which becomes the DataFrame rows.
        display_data = pd.DataFrame(details.items(), columns=['Attribute', 'Detail'])
        
        st.dataframe(
            display_data,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Attribute": st.column_config.column(
                    "Attribute",
                    width="small"
                ),
                "Detail": st.column_config.column(
                    "Detail",
                    width="large"
                )
            }
        )

    else:
        # --- No Match Found ---
        st.error(f"❌ Could not find information for '{user_input}'.")
        st.info("💡 Try checking your spelling or search for the full medicine name.")

# --- 5. FOOTER ---
st.markdown("---")
st.caption("Application powered by Streamlit and your custom data lookup logic.")
>>>>>>> 93570be1b0596f80fddfc6392ea31bb5d13eec0f
