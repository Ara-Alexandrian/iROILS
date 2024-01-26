import json
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer
from sentencetransformers import SentenceTransformer
from transformers import pipeline

def fetch_data_from_redis(r):
    keys = r.keys('*')
    data = {}
    for key in keys:
        narrative = r.hget(key, 'Narrative')
        summary = r.hget(key, f'{model_name}:LLM Summary')
        data[key] = {'narrative': narrative, 'summary': summary}
    return data

# Generate N-grams
def generate_ngrams(text, n=2):
    vectorizer = CountVectorizer(ngram_range=(n, n))
    ngrams = vectorizer.fit_transform([text]).todense().tolist()
    return ngrams

# Generate embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')  # Example model, you can choose any
def generate_embeddings(text):
    embeddings = model.encode(text)
    return embeddings

# Named Entity Recognition
ner = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english", device=0)  # Example model
def generate_tags(text):
    tags = ner(text)
    return tags

def cluster_embeddings(embeddings, num_clusters=5):
    kmeans = KMeans(n_clusters=num_clusters)
    kmeans.fit(embeddings)
    labels = kmeans.labels_
    return labels

def store_results_to_redis(r, key, ngrams, tags, cluster_label):
    # Clear existing fields if they exist
    if r.hexists(key, 'Ngrams'):
        r.hdel(key, 'Ngrams')
    if r.hexists(key, 'Tags'):
        r.hdel(key, 'Tags')
    if r.hexists(key, 'Cluster'):
        r.hdel(key, 'Cluster')
    
    # Set new values
    r.hset(key, 'Ngrams', json.dumps(ngrams))
    r.hset(key, 'Tags', json.dumps(tags))
    r.hset(key, 'Cluster', cluster_label)


if redis_conn:
    data = fetch_data_from_redis(redis_conn)
    for key, content in data.items():
        narrative = content['narrative']
        summary = content['summary']
        
        # Generate N-grams
        ngrams = generate_ngrams(narrative + ' ' + summary)
        
        # Generate embeddings and cluster
        embeddings = generate_embeddings(narrative + ' ' + summary)
        cluster_label = cluster_embeddings(embeddings)
        
        # Generate tags
        tags = generate_tags(narrative + ' ' + summary)
        
        # Store results back to Redis
        store_results_to_redis(redis_conn, key, ngrams, tags, cluster_label)
