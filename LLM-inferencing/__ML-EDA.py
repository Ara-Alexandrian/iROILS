from collections import Counter
from collections import defaultdict
import pandas as pd
import spacy
from tqdm.auto import tqdm
from nltk.util import ngrams
from nltk.tokenize import word_tokenize
import nltk
nltk.download('punkt')

# Function to efficiently process large texts with spaCy and tqdm
def process_text(texts, model):
    # Process texts and return a list of docs
    docs = list(tqdm(model.pipe(texts, batch_size=20), total=len(texts), desc="Processing Texts"))
    return docs

# Extract noun phrases from the documents
def extract_noun_phrases(docs):
    noun_phrases = [chunk.text for doc in docs for chunk in doc.noun_chunks]
    return noun_phrases


# Function to generate n-grams from a list of documents
def generate_ngrams(docs, n):
    n_grams = Counter()
    for doc in docs:
        # Tokenize the document's text
        tokens = [token.text for token in doc if not token.is_stop and not token.is_punct and not token.is_space]
        # Generate n-grams for the current document and update the counter
        n_grams.update(Counter(ngrams(tokens, n)))
    return n_grams


# Initialize spaCy model
nlp = spacy.load("en_core_web_sm")

# Load the processed data
file_path = 'LLM-inferencing/cleaned_extract_summary.xlsx'  # Update with your file path
df = pd.read_excel(file_path)

# Process each summary to create a list of docs
docs = process_text(df['Processed Text'].tolist(), nlp)

# Combine all docs to generate term frequency
word_freq = Counter(token.text for doc in docs for token in doc if not token.is_stop and not token.is_punct)

# Display the 50 most common words
print("Top 50 Words:")
for word, freq in word_freq.most_common(50):
    print(f"{word}: {freq}")

# Extract and count entities from all docs
entity_freq = Counter(ent.text for doc in docs for ent in doc.ents)

# Display the 50 most common entities
print("\nTop 50 Entities:")
for entity, freq in entity_freq.most_common(50):
    print(f"{entity}: {freq}")

# Extract noun phrases and their frequency
noun_phrases = extract_noun_phrases(docs)
noun_phrase_freq = Counter(noun_phrases)

# Display the 50 most common noun phrases
print("\nTop 50 Noun Phrases:")
for phrase, freq in noun_phrase_freq.most_common(50):
    print(f"{phrase}: {freq}")


# Generate and display n-grams for n=3, 4, 5
for n in [3, 4, 5]:
    n_grams = generate_ngrams(docs, n)
    print(f"\nTop 20 {n}-grams:")
    for n_gram, freq in n_grams.most_common(50):
        print(f"{' '.join(n_gram)}: {freq}")


#tag generation step

from collections import defaultdict

# Assume 'analysis_results' is a dict containing your analysis outputs
analysis_results = {
    'words': word_freq.most_common(50),
    'entities': entity_freq.most_common(50),
    'noun_phrases': noun_phrase_freq.most_common(50),
    'ngrams': {
        3: n_grams_3.most_common(50),
        4: n_grams_4.most_common(50),
        5: n_grams_5.most_common(50),
    }
}

# Function to generate tag rules based on analysis results
def generate_tag_rules(analysis_results):
    tag_rules = defaultdict(list)
    # Example logic to generate rules
    for tag, items in analysis_results.items():
        for item, _ in items:
            # This is a simplified example; you'll need to tailor the logic
            # to how you define tags based on your specific analysis results
            if 'delay' in item:
                tag_rules['Treatment Delay'].append(item)
            elif 'missing' in item or 'unsigned' in item:
                tag_rules['Documentation Issue'].append(item)
    return dict(tag_rules)

# Generate tag rules
tag_rules = generate_tag_rules(analysis_results)

# Example output of generated rules
for tag, rules in tag_rules.items():
    print(f"Tag: {tag}, Rules: {rules}\n")
