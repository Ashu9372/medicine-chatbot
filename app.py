import streamlit as st
import pandas as pd
from fun import load_data_robust, lookup_medicine   # Correct import


# ----------------------------------------------------
# 0. LOAD DATA (cached)
# ----------------------------------------------------
@st.cache_data
def get_medicine_data():
    try:
        return load_data_robust()
    except Exception:
        return None

MEDICINE_DF = get_medicine_data()


# ----------------------------------------------------
# 1. Streamlit Page Setup
# ----------------------------------------------------
st.set_page_config(page_title="💊 AI Medicine Lookup Tool", layout="centered")

st.title("💊 AI Medicine Lookup Tool")
st.info(
    "⚠ ALWAYS consult a qualified doctor or pharmacist before using any medication.\n"
    "This tool provides general information only."
)


# ----------------------------------------------------
# 2. Check if data is loaded
# ----------------------------------------------------
if MEDICINE_DF is None:
    st.error("❌ Could not load 'data.csv'. Please upload it or check the file path.")
    st.stop()


# ----------------------------------------------------
# 3. Search Form
# ----------------------------------------------------
with st.form(key="medicine_search_form"):
    user_input = st.text_input(
        "Enter a medicine name:",
        placeholder="e.g., Crocin, Nutrich Capsule, Aspirin..."
    )
    submitted = st.form_submit_button("Search Medicine")


# ----------------------------------------------------
# 4. Lookup Logic
# ----------------------------------------------------
if submitted and user_input:
    query = user_input.strip()

    with st.spinner(f"Searching for '{query}'..."):
        details, matched_name = lookup_medicine(query, MEDICINE_DF)

    # No match found
    if details is None:
        st.error(f"❌ No match found for '{query}'.")
        st.info("💡 Try correcting the spelling or entering more letters.")
    else:
        # Fuzzy match message
        if matched_name.lower() != query.lower():
            st.info(f"🔍 Showing results for **{matched_name}** (closest match)")

        st.success(f"✅ Information found for **{matched_name}**")

        # Convert dictionary to DataFrame
        display_df = pd.DataFrame(
            list(details.items()),
            columns=["Attribute", "Detail"]
        )

        # Display data
        st.dataframe(
            display_df,
            hide_index=True,
            use_container_width=True
        )


# ----------------------------------------------------
# 5. Footer
# ----------------------------------------------------
st.markdown("---")
st.caption("Application powered by Streamlit and your custom medicine lookup engine.")
