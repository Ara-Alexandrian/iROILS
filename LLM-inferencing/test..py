import re
from spacy.lang.en import English
from spacy.lang.en.stop_words import STOP_WORDS

# Load English tokenizer, tagger, parser, NER and word vectors
nlp = English()

def clean_text(text):
    # Convert text to lowercase
    text = text.lower()
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # Remove numbers
    text = re.sub(r'\d+', '', text)
    # Remove extra whitespace and tabs
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Example usage:
text = "  Pre-processing is key in ML projects! Especially in NLP.  "
cleaned_text = clean_text(text)
print(cleaned_text)