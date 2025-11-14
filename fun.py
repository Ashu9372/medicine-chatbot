import pandas as pd
from fuzzywuzzy import fuzz, process
import os

print("⚠ DISCLAIMER: This is an AI lookup tool for general information only.")
print("Always consult a qualified doctor before using medicine.\n")

# ============================================================
#  LOAD DATA (Robust loader)
# ============================================================
def load_data_robust(filename='data.csv'):
    """
    Loads the medicine CSV file using multiple fallback paths and encodings.
    Returns pandas DataFrame.
    """

    possible_paths = [
        filename,
        os.path.join(os.getcwd(), filename),
        r"C:\Users\ashraf khan\Dropbox\data.csv"
    ]

    encodings = ["utf8", "latin1", "cp1252"]

    # Try every combination
    for path in possible_paths:
        for encoding in encodings:
            try:
                df = pd.read_csv(path, encoding=encoding)
                print(f"✅ Data loaded successfully from '{path}' using '{encoding}' encoding!")
                return df
            except (UnicodeDecodeError, FileNotFoundError):
                continue
            except Exception:
                continue

    # If all failed
    print("❌ ERROR: Could not load 'data.csv'. Please check its location.")
    raise FileNotFoundError("data.csv not found in any tested paths.")

# ============================================================
#  ORIGINAL MEDICINE LOOKUP (Preserved functionality)
# ============================================================
def get_medicine_info(query, data, data_lower):
    """
    Fuzzy-matches medicine name and returns formatted information text.
    Returns formatted string.
    """

    query_lower = query.lower().strip()
    medicine_names = data_lower.tolist()

    # Fuzzy match (80 score cutoff)
    best_match = process.extractOne(
        query_lower,
        medicine_names,
        scorer=fuzz.ratio,
        score_cutoff=80
    )

    if not best_match:
        return f"❌ I could not find information for '{query}'."

    matched_lower_name = best_match[0]
    row = data[data_lower == matched_lower_name].iloc[0]

    response = (
        f"\n"
        f"✅ Found Match: *{row['Name']}*\n"
        f"----------------------------------\n"
        f"💊 Uses: {row['Uses']}\n"
        f"📏 Dosage (Adult): {row['Dosage']}\n"
        f"🚫 Age Restriction: {row['Age Restriction']}\n"
        f"⚠ Side Effects: {row['Side Effect']}\n"
    )
    return response

# ============================================================
#  WRAPPER FOR STREAMLIT (returns dictionary + matched name)
# ============================================================
def lookup_medicine(query, data):
    """
    Safe, reliable lookup for Streamlit.
    Returns:
        (details_dict, matched_name)
        OR
        (None, None) if not found.
    """

    # lowercase names
    names_lower = data["Name"].str.lower().tolist()
    query_lower = query.lower().strip()

    # Perform fuzzy match directly (90% score recommended)
    best_match = process.extractOne(
        query_lower,
        names_lower,
        scorer=fuzz.ratio,
        score_cutoff=70       # Lower threshold → catches more matches
    )

    if not best_match:
        return None, None

    matched_lower = best_match[0]

    # Get the row
    row = data[data["Name"].str.lower() == matched_lower]

    if row.empty:
        return None, None

    row = row.iloc[0]

    # Prepare dictionary
    details = {
        "Name": row["Name"],
        "Uses": row["Uses"],
        "Dosage": row["Dosage"],
        "Age Restriction": row["Age Restriction"],
        "Side Effects": row["Side Effect"]
    }

    return details, row["Name"]

# ============================================================
#   INTERACTIVE MODE (Optional, unchanged)
# ============================================================
if __name__ == "__main__":
    try:
        df = load_data_robust()
        df_lower = df["Name"].str.lower()
    except Exception as e:
        print("❌ Unable to load data:", e)
        exit()

    print("💬 Welcome! Type a medicine name (or 'exit'):\n")

    while True:
        user = input("You: ").strip()
        if user.lower() == "exit":
            print("Goodbye! Stay safe.")
            break

        details, name = lookup_medicine(user, df)

        if details is None:
            print("❌ Not found. Try again.\n")
        else:
            print(f"\n✔ Matched: {name}\n")
            for k, v in details.items():
                print(f"{k}: {v}")
            print("\n")