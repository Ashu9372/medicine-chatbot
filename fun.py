import pandas as pd
from fuzzywuzzy import fuzz, process

print("⚠ DISCLAIMER: This is an AI lookup tool for general info.")
print("ALWAYS consult a qualified doctor or pharmacist before using medicine.")

def load_data_robust(filename='data.csv'):
    """Tries to load the CSV file using several common methods and encodings."""
    
    # 1. Try simple file name with common encodings
    for encoding in ['utf8', 'latin1', 'cp1252']:
        try:
            data = pd.read_csv('data.csv', encoding=encoding)
            print(f"✅ Data loaded successfully using '{encoding}' encoding!")
            return data
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            # If the file is not found by the simple name, continue to next block
            break
        except Exception as e:
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
    
    if not best_match:
        return f"I could not find information for '{query}'. Please check the spelling or try a partial name."

    matched_name_lower = best_match[0]
    
    result = data[data_lower == matched_name_lower]

    info = result.iloc[0]
        
    response = (
        f"\n✅ Found Match: *{info['Name']}*\n"
        f"--- \n"
        f"💊 *Uses:* {info['Uses']}\n"
        f" Dosage (Adult): {info['Dosage']}\n"
        f"🚫 *Age Restriction:* {info['Age Restriction']}\n"
        f"⚠ *Common Side Effects:* {info['Side Effect']}\n" 
    )
    return response

# --- Main Chatbot Interaction Loop ---
if __name__ == "__main__":
    # 1. Load data and setup
    data = load_data_robust() 
    data_lower = data['Name'].str.lower()

    print("\u26A0 Hello! What medicine would you like to know about? (Type 'exit' to quit)")

    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == 'exit':
            print("Thank you for using the medicine lookup tool. Remember to consult a doctor!")
            break
        
        if user_input:
            response_text = get_medicine_info(user_input, data, data_lower)
            print(f"Chatbot: {response_text}")
