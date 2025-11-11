import streamlit as st
import pandas as pd

# --- 1. CONFIGURATION (Run once) ---
st.set_page_config(page_title="AI Medicine Lookup Tool", layout="centered")


# --- 2. HEADER AND DISCLAIMER ---
st.title("💊 AI Medicine Lookup Tool")
st.info("⚠ ALWAYS consult a qualified doctor or pharmacist before using medicine. This tool is for general information only.")


# --- 3. SEARCH FORM ---
with st.form(key='medicine_search_form'):
    
    user_input = st.text_input(
        "What medicine would you like to know about?", 
        placeholder="e.g., Crocin, Nutrich Capsule, Aspirin, etc."
    )
    
    # The submit button should be inside the form
    submitted = st.form_submit_button(label='Search Medicine')


# --- 4. LOOKUP AND DISPLAY LOGIC ---
# This block runs ONLY when the user clicks the button AND the input is not empty.
if submitted and user_input:
    
    # Call the lookup function, showing a spinner while waiting
    with st.spinner(f"Searching for '{user_input}'..."):
        details, name_found = lookup_medicine (user_input)

    
    if details:
        
        # --- Handle Fuzzy Match Notification ---
        if name_found.lower().strip() != user_input.lower().strip():
             # Show the user the app found a close match
             st.info(f"Showing results for *{name_found.title()}* (closest match found for '{user_input}').")
            
        st.success(f"✅ Found Information for: *{name_found.title()}*")
        
        # --- Display Results in Table ---
        # Convert the dictionary/details into a DataFrame for display
        display_data = pd.DataFrame(details.items(), columns=['Attribute', 'Detail'])
        
        st.dataframe(
            display_data,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Attribute": st.column_config.Column("Attribute", width="small"),
                "Detail": st.column_config.Column("Detail", width="large")
            }
        )
            
    else:
        # --- No Match Found ---
        st.error(f"Could not find information for '{user_input}'.")
        st.info("💡 Try checking your spelling or search for the full medicine name.")

st.markdown("---")
st.caption("Application powered by Streamlit and your custom data lookup logic.")
