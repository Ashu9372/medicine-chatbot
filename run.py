import pandas as pd
import os

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
            data = pd.read_csv('data.csv')
            print(f"✅ Data loaded successfully using '{encoding}' encoding!")
            return data
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            # If the file is not found by the simple name, continue to next block
            break
        except Exception as e:
            # Handle other pandas reading errors
            print(f"Error reading file with {encoding}: {e}")
            continue

    # 2. Try searching for the file using its full absolute path (in case of hidden characters)
    try:
        # NOTE: This uses the exact path format (forward slashes)
        full_path = 'C:/Users/ashraf khan/Dropbox/data.csv'
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

def get_medicine_info(query):
    """Searches the database for medicine information based on the query."""

    # Clean the user's input for searching
    query_lower = query.lower().strip()
    
    # 2. Search the DataFrame for the matching medicine name
    result = data[data['Name_Lower'] == query_lower]

    if result.empty:
        # If not found by exact name, try partial match (e.g., searching for 'crocin' when the data says 'Crocin tablet')
        partial_match = data[data['Name_Lower'].str.contains(query_lower, na=False)]
        
        if partial_match.empty:
            return f"I could not find information for '{query}'. Please check the spelling or try a partial name."
        else:
            # If partial match found, use the first result
            result = partial_match

    # Match found! Get the data from the first matching row
    info = result.iloc[0]
    
    # 3. Format the response for the chatbot
    response = (
        f"\n✅ Information for *{info['Name']}*:\n"
        f"--- \n"
        f"💊 *Uses:* {info['Uses']}\n"
        f" Dosage (Adult): {info['Dosage']}\n"
        f"🚫 *Age Restriction:* {info['Age_Restriction']}\n"
        f"⚠ *Common Side Effects:* {info['Side Effect']}\n" 
    )
    return response

# --- Main Chatbot Interaction Loop ---
import pandas as pd
import os

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
            data = pd.read_csv(filename, encoding=encoding)
            print(f"✅ Data loaded successfully using '{encoding}' encoding!")
            return data
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            # If the file is not found by the simple name, continue to next block
            break
        except Exception as e:
            # Handle other pandas reading errors
            print(f"Error reading file with {encoding}: {e}")
            continue

    # 2. Try searching for the file using its full absolute path (in case of hidden characters)
    try:
        # NOTE: This uses the exact path format (forward slashes)
        full_path = 'C:/Users/ashraf khan/Dropbox/data.csv'
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

def get_medicine_info(query):
    """Searches the database for medicine information based on the query."""

    # Clean the user's input for searching
    query_lower = query.lower().strip()
    
    # 2. Search the DataFrame for the matching medicine name
    result = data[data['Name_Lower'] == query_lower]

    if result.empty:
        # If not found by exact name, try partial match (e.g., searching for 'crocin' when the data says 'Crocin tablet')
        partial_match = data[data['Name_Lower'].str.contains(query_lower, na=False)]
        
        if partial_match.empty:
            return f"I could not find information for '{query}'. Please check the spelling or try a partial name."
        else:
            # If partial match found, use the first result
            result = partial_match

    # Match found! Get the data from the first matching row
        info = result.iloc[0]
        
        # 3. Format the response for the chatbot
        # NOTE: Keys are updated to match your spreadsheet's headers (e.g., 'Age Restriction')
        response = (
            f"\n✅ Information for *{info['Name']}*:\n"
            f"--- \n"
            f"💊 *Uses:* {info['Uses']}\n"
            f" Dosage (Adult): {info['Dosage']}\n" 
            f"🚫 *Age Restriction:* {info['Age Restriction']}\n" 
            f"⚠ *Common Side Effects:* {info['Side Effect']}\n" 
        )
        return response

# --- Main Chatbot Interaction Loop ---
if __name__ == "__main__": 
    print("\nHello! What medicine would you like to know about? (Type 'exit' to quit)")
    
    while True:
        # Get input from the person using the chatbot
        user_input = input("You: ").strip()

        if user_input.lower() == 'exit':
            print("Thank you for using the medicine lookup tool. Remember to consult a doctor!")
            break
        
        if user_input:
            # Get the structured information and print the response
            response_text = get_medicine_info(user_input)
            print(f"Chatbot: {response_text}") 
    print("\nHello! What medicine would you like to know about? (Type 'exit' to quit)")
    
    while True:
        # Get input from the person using the chatbot
        user_input = input("You: ").strip()

        if user_input.lower() == 'exit':
            print("Thank you for using the medicine lookup tool. Remember to consult a doctor!")
            break
        
        if user_input:
            # Get the structured information and print the response
            response_text = get_medicine_info(user_input)
            print(f"Chatbot: {response_text}")