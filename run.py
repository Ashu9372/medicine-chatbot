import pandas as pd
import os
from fuzzywuzzy import fuzz, process #

# --- CRITICAL SAFETY DISCLAIMER ---
print("")
print("⚠ DISCLAIMER: This is an AI lookup tool for general info.")
print("ALWAYS consult a qualified doctor or pharmacist before using medicine.")
print("")

# 1. Load the database (data.csv) using a robust method
def load_data_robust(filename='data.csv'):
    """Tries to load the CSV file using several common methods and encodings."""
    
    # 1. Try simple file name with common encodings
    for encoding in ['utf8', 'latin1', 'cp1252']:
        try:
            # We use the simple, relative path since the command prompt is in the right folder.
            data = pd.read_csv('data.csv', encoding=encoding)
            print(f"✅ Data loaded successfully using '{encoding}' encoding!")
            return data
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            # If the file is not found by the simple name, continue to next block
            break
        except Exception as e:
            # Handle other pandas reading errors
            continue

    # 2. Try searching for the file using its full absolute path (forward slashes)
    try:
        # NOTE: This is your specific full path used as a backup!
        full_path = 'C:\\Users\\ashraf khan\\Dropbox\\data.csv'
        data = pd.read_csv(full_path, encoding='utf8')
        print("✅ Data loaded successfully using full path!")
        return data
    except Exception:
        pass

    # If all methods fail
    print("\n------------------------------------------------------------")
    print(f"❌ FATAL ERROR: Data file '{filename}' could not be found or read.")
    print("Please confirm the file is named 'data.csv' and is in this folder.")
    print("------------------------------------------------------------")
    exit()

# Load the data using the robust function
data = load_data_robust()

# Create a lowercase column for easy, non-case-sensitive searching
data['Name_Lower'] = data['Name'].str.lower() 

def get_medicine_info(query, data, data_lower, threshold_strict=45, threshold_partial=40):
    """Searches the database, using fuzzy matching to find the closest medicine name."""

    query_lower = query.lower().strip()
    
    # --- 1. Fuzzy Matching Logic (Score 80/100 required for a match) ---
    # Create a list of all medicine names in lowercase
    medicine_names = data_lower.tolist()
    
    # Use fuzzywuzzy to find the best match
    best_match = process.extractOne(
        query_lower, 
        medicine_names, 
        scorer=fuzz.ratio, 
        score_cutoff=80
    )
    
    # Check if a good match was found
    if not best_match:
        return f"I could not find information for '{query}'. Please check the spelling or try a partial name."

    # The best match is the name from the database that scored highest
    matched_name_lower = best_match[0]
    
    # --- 2. Retrieve Data using the Best Match ---
    result = data[data_lower == matched_name_lower]

    # Match found! Get the data from the first matching row
    info = result.iloc[0]
        
    # 3. Format the response (Keys must match your spreadsheet)
    response = (
        f"\n✅ Found Match: {info['Name']}\n"
        f"--- \n"
        f"💊 Uses: {info['Uses']}\n"
        f" Dosage (Adult): {info['Dosage']}\n"
        f"🚫 Age Restriction: {info['Age Restriction']}\n"
        f"⚠ Common Side Effects: {info['Side Effect']}\n" 
    )
    return response

# --- Main Chatbot Interaction Loop ---
if __name__ == "__main__":
    # 1. Load data and setup (THIS WAS MISSING)
    data = load_data_robust() 
    # Assuming you also need this line for fuzzy matching:
    data_lower = data['Name'].str.lower()

    # 2. Start interaction loop
    print("\u26A0 Hello! What medicine would you like to know about? (Type 'exit' to quit)")

    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == 'exit':
            print("Thank you for using the medicine lookup tool.")
            break
        
        if user_input:
            response_text = get_medicine_info(user_input, data, data_lower) # Make sure 'data' is passed if needed
            print(f"Chatbot: {response_text}")
            print(f"Chatbot: {response_text}")
