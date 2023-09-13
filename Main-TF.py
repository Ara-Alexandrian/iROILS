import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from gensim.models import Word2Vec
import numpy as np
import umap.umap_ as umap
import matplotlib.pyplot as plt
from collections import Counter
import tqdm as tqdm
from sklearn.cluster import DBSCAN
import warnings
from numba import NumbaDeprecationWarning, NumbaPendingDeprecationWarning

warnings.simplefilter('ignore', category=NumbaDeprecationWarning)
warnings.simplefilter('ignore', category=NumbaPendingDeprecationWarning)


# Load data
df = pd.read_excel("Events_runninglist.xlsx")

# Check for the narrative column name
narrative_column = "105.Narrative"
if narrative_column not in df.columns:
    raise ValueError(f"Column '{narrative_column}' not found in the provided Excel file.")

# Better Text Preprocessing
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def preprocess(text):
    sentences = sent_tokenize(text)
    tokens = [word_tokenize(sent) for sent in sentences]
    tokens = [word for sublist in tokens for word in sublist]  # Flatten list
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word.lower() not in stop_words]
    return " ".join(tokens)

df['preprocessed_narrative'] = df[narrative_column].apply(preprocess)
df = df[df['preprocessed_narrative'].str.split().str.len() > 5]  # Filter out short narratives

# Alternate Text Representations - Word2Vec

# Tokenize preprocessed narratives for Word2Vec
df['tokens'] = df['preprocessed_narrative'].apply(word_tokenize)

# Train a Word2Vec model
model = Word2Vec(sentences=df['tokens'], vector_size=300, window=5, min_count=1, workers=4)
model.train(df['tokens'], total_examples=len(df['tokens']), epochs=10)

# Average Word2Vec vectors for each narrative
def average_word_vectors(tokens, model, vocabulary, num_features):
    feature_vector = np.zeros((num_features,), dtype="float64")
    nwords = 0.
    for word in tokens:
        if word in vocabulary: 
            nwords = nwords + 1.
            feature_vector = np.add(feature_vector, model.wv[word])
    if nwords:
        feature_vector = np.divide(feature_vector, nwords)
    return feature_vector

df['avg_word_vec'] = df['tokens'].apply(lambda x: average_word_vectors(x, model, model.wv.index_to_key, 300))
word_vec_array = np.array(df['avg_word_vec'].tolist())

# UMAP exploration function
def draw_umap(data, n_neighbors=15, min_dist=0.1, n_components=2, metric='euclidean', title=''):
    fit = umap.UMAP(
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        n_components=n_components,
        metric=metric
    )
    u = fit.fit_transform(data)
    plt.figure()
    if n_components == 2:
        plt.scatter(u[:,0], u[:,1])
    plt.title(title, fontsize=18)
    plt.show()
    return u

# For now, let's use the function with the parameters you initially specified
umap_vecs = draw_umap(word_vec_array, n_neighbors=5, min_dist=0.3, n_components=2, metric='cosine', title='UMAP with n_neighbors=5')

# Clustering using DBSCAN
print("Clustering data with DBSCAN...")
clustering = DBSCAN(eps=0.5, min_samples=5).fit(umap_vecs)
df['cluster_label'] = clustering.labels_

# Extract Representative Keywords for Each Cluster
def extract_keywords(cluster_texts, top_n=5):
    all_tokens = [word for text in cluster_texts for word in word_tokenize(text)]
    most_common = Counter(all_tokens).most_common(top_n)
    keywords = [word[0] for word in most_common]
    return keywords

# Create a dictionary to store keywords for each cluster
cluster_to_keywords = {}

unique_clusters = df['cluster_label'].unique()

print("Extracting keywords for each cluster...")
for cluster in tqdm(unique_clusters):
    if cluster != -1:  # -1 is for noise in DBSCAN
        cluster_texts = df[df['cluster_label'] == cluster]['preprocessed_narrative'].tolist()
        keywords = extract_keywords(cluster_texts)
        cluster_to_keywords[cluster] = keywords

# Assign tags to each narrative based on its cluster
print("Assigning tags to narratives...")
df['tags'] = df['cluster_label'].apply(lambda x: cluster_to_keywords.get(x, 'Noise'))

# Save results
print("Saving results to Excel...")
df.to_excel("Clustered_Events_runninglist_Word2Vec_UMAP_Tags.xlsx", index=False)
print("Done!")