
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from collections import Counter
import re
from nltk.corpus import stopwords

# Load the Excel file
input_file_path = "New/Events_runninglist.xlsx"  # Replace with your file path
df = pd.read_excel(input_file_path)

# Text preprocessing
def preprocess_text(text):
    text = re.sub(r'[^a-zA-Z\s]', '', text, re.I|re.A)
    text = text.lower()
    text = text.strip()
    return ' '.join([word for word in text.split() if word not in stopwords.words('english')])

# Apply text preprocessing
df['Preprocessed_Narratives'] = df['105.Narrative'].apply(preprocess_text)

# Extract the top 50 frequent words
vec = CountVectorizer().fit(df['Preprocessed_Narratives'])
bag_of_words = vec.transform(df['Preprocessed_Narratives'])
sum_words = bag_of_words.sum(axis=0)
words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
top_50_words = [word for word, freq in words_freq[:50]]

# Define context-based multi-word tags
context_based_multi_word_tags = [
    {'keywords': ['dosimetric', 'error'], 'tag': 'Dosimetric Error'},
    {'keywords': ['treatment', 'plan'], 'tag': 'Treatment Plan'},
    {'keywords': ['patient', 'delay'], 'tag': 'Patient Delay'},
    # Add more context-based multi-word tags as needed
]

# Function to extract frequent n-grams with at least min_freq occurrences
def extract_frequent_ngrams(corpus, n, min_freq=5):
    vec = CountVectorizer(ngram_range=(n, n), min_df=min_freq).fit(corpus)
    bag_of_words = vec.transform(corpus)
    sum_words = bag_of_words.sum(axis=0)
    words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
    words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
    return [word for word, freq in words_freq]

# Extract frequent bi-grams, tri-grams, and 4-grams
frequent_bigrams = extract_frequent_ngrams(df['Preprocessed_Narratives'], 2)
frequent_trigrams = extract_frequent_ngrams(df['Preprocessed_Narratives'], 3)
frequent_fourgrams = extract_frequent_ngrams(df['Preprocessed_Narratives'], 4)

# Create a combined list of single words, bi-grams, tri-grams, and four-grams for tagging
all_possible_tags = top_50_words + [tag['tag'] for tag in context_based_multi_word_tags] + frequent_bigrams + frequent_trigrams + frequent_fourgrams

# Initialize TF-IDF Vectorizer with the combined list of all possible tags
vectorizer = TfidfVectorizer(vocabulary=all_possible_tags, ngram_range=(1, 4))

# Fit the TF-IDF Vectorizer to the entire corpus
tfidf_matrix = vectorizer.fit_transform(df['Preprocessed_Narratives'].tolist())
feature_names = vectorizer.get_feature_names_out()

# Function to find the top 5 most relevant tags/n-grams
def find_top_relevant_tags(tfidf_vector):
    feature_index = tfidf_vector.nonzero()[1]
    tfidf_scores = zip(feature_index, [tfidf_vector[0, x] for x in feature_index])
    sorted_scores = sorted(tfidf_scores, key=lambda x: x[1], reverse=True)
    top_5_tags = [feature_names[i] for (i, _) in sorted_scores[:5]]
    return ', '.join(top_5_tags)

# Find the top 5 most relevant tags/n-grams for each narrative
df['Top_5_Relevant_Tags'] = [find_top_relevant_tags(tfidf_matrix[i, :]) for i in range(tfidf_matrix.shape[0])]

# Save the final DataFrame to a new Excel file
output_file_path_final = "YOUR_PATH/TaggedEventsList_Final_Optimized.xlsx"  # Replace with your desired output file path
with pd.ExcelWriter(output_file_path_final) as writer:
    df.to_excel(writer, sheet_name='EventList_FinalOptimizedTags', index=False)
    unique_tags_final = pd.DataFrame({'Unique_Tags': list(set(', '.join(df['Top_5_Relevant_Tags']).split(', ')))})
    unique_tags_final.to_excel(writer, sheet_name='Unique_FinalOptimizedTags', index=False)
    pd.DataFrame({'Frequent_Bigrams': frequent_bigrams}).to_excel(writer, sheet_name='Frequent_Bigrams', index=False)
    pd.DataFrame({'Frequent_Trigrams': frequent_trigrams}).to_excel(writer, sheet_name='Frequent_Trigrams', index=False)
    pd.DataFrame({'Frequent_Fourgrams': frequent_fourgrams}).to_excel(writer, sheet_name='Frequent_Fourgrams', index=False)
