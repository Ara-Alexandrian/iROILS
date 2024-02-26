import pandas as pd
import spacy
import re
from tqdm.auto import tqdm

"""
This script performs text preprocessing and normalization on a dataset of narrative summaries from a Radiation Oncology department's incident learning system. The dataset, originally containing user-submitted narratives along with language-model refined summaries, is further cleaned and processed to enhance data quality for subsequent analysis. The steps include:

Cleaning: Standardizes the text by converting to lowercase, removing punctuation, numbers, and excess whitespace.
Processing: Applies Natural Language Processing (NLP) techniques to refine the summaries further. This involves:
Tokenization: Splits the text into individual words or tokens.
Stop Word Removal: Eliminates common words that are unlikely to be useful for analysis.
Lemmatization: Reduces words to their base or dictionary form, facilitating a more straightforward comparison of word frequencies and meanings.
The output is a structured dataset with added columns for cleaned and processed summaries, ready for NLP tasks such as keyword extraction, sentiment analysis, or topic modeling. This preprocessing pipeline enhances the usability of the dataset for machine learning models and analytical purposes, ensuring a cleaner, more consistent input that can help uncover insights from the narrative summaries.
"""


# Ensure tqdm.pandas() is used to enable progress_apply
tqdm.pandas(desc="Processing Text")

# Load spaCy model for English
nlp = spacy.load("en_core_web_sm")

def clean_text(text):
    """
    Cleans the input text by lowercasing, removing punctuation,
    numbers, and extra whitespaces.
    """
    text = text.lower()  # Convert text to lowercase
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = re.sub(r'\d+', '', text)  # Remove numbers
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra whitespace and tabs
    return text

def process_text(text):
    """
    Process the text with spaCy to remove stop words and lemmatize.
    """
    doc = nlp(text)
    # Remove stop words and lemmatize
    return " ".join([token.lemma_ for token in doc if not token.is_stop and not token.is_punct])

# Load the data from the Excel file
file_path = 'LLM-inferencing/extract_summary.xlsx'
df = pd.read_excel(file_path)

# Apply the cleaning function to the 'mistral Summary'
df['Cleaned Summary'] = df['mistral Summary'].progress_apply(clean_text)

# Apply the processing function to clean and lemmatize text
df['Processed Text'] = df['Cleaned Summary'].progress_apply(process_text)

# Display the first few rows to understand the data structure
print("Initial data preview:")
print(df.head())

# Save the DataFrame with the new columns to a new Excel file
cleaned_file_path = 'LLM-inferencing/cleaned_extract_summary.xlsx'
df.to_excel(cleaned_file_path, index=False)

print(f"\nThe cleaned data has been saved to {cleaned_file_path}")
