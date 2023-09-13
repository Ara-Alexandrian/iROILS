import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from transformers import BertTokenizer, BertModel
import torch
from sklearn.cluster import DBSCAN

# Step 1: Data Loading & Preprocessing

# Load data
df = pd.read_excel("Events_runninglist.xlsx")

# Check for the narrative column name
narrative_column = "105.Narrative"
if narrative_column not in df.columns:
    raise ValueError(f"Column '{narrative_column}' not found in the provided Excel file.")

# Preprocess the narratives
nltk.download('punkt')
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

def preprocess(text):
    tokens = word_tokenize(text)
    filtered_tokens = [word for word in tokens if word.lower() not in stop_words]
    return " ".join(filtered_tokens)

df['preprocessed_narrative'] = df[narrative_column].apply(preprocess)

# Step 2: Embeddings Generation

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

def embed(text):
    inputs = tokenizer(text, return_tensors="pt", max_length=512, truncation=True, padding="max_length")
    with torch.no_grad():
        output = model(**inputs)
    return output.last_hidden_state.mean(dim=1).squeeze().numpy()

df['embeddings'] = df['preprocessed_narrative'].apply(embed)

# Step 3: Clustering

X = list(df['embeddings'])
clustering = DBSCAN(eps=0.5, min_samples=5).fit(X)
df['cluster_label'] = clustering.labels_

# Step 4: Tagging & Storing in Database

df.to_excel("/mnt/data/Clustered_Events_runninglist.xlsx", index=False)
