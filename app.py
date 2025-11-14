import streamlit as st
import pandas as pd
from fun import load_data_robust, lookup_medicine   # Import correct functions

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

st.title("💊 AI Medicine Lookup Tool")
st.info("⚠ ALWAYS consult a qualified doctor or pharmacist before using any medication. "
        "This tool provides general information only.")

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