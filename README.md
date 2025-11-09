# 💊 Intelligent Medicine Search Chatbot

This is a functional Python command-line tool designed for quick, non-case-sensitive lookups of medicine information from a structured data source.

## ✨ Features
- *Robust Data Loading:* Attempts to load data using multiple common file encodings.
- *Fuzzy Matching:* Uses the fuzzywuzzy library to find the closest match for user input, even with spelling mistakes or partial names.
- *Structured Output:* Displays retrieved information (Uses, Dosage, Side Effects, etc.) in a clear, formatted console output.

## 🛠 Requirements
This project requires the following Python libraries:
- pandas
- fuzzywuzzy
- python-Levenshtein (Recommended for faster fuzzy matching)

## 🚀 How to Run
1. *Ensure Python 3 is installed.*
2. *Install dependencies* (or use the requirements.txt file once created):
   ```bash
   pip install pandas fuzzywuzzy python-Levenshtein
