import json
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer
from transformers import AutoTokenizer, AutoModel
import redis

redis_server = '192.168.1.4'  # This may vary based on your setup, this is just an example
redis_port = 6379           # Standard Redis port

redis_conn = redis.Redis(host=redis_server, port=redis_port)

model_name = 'sentence-transformers/all-MiniLM-L6-v2'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def fetch_data_from_redis():
    keys = redis_conn.keys('*')
    print("Keys fetched from Redis:", keys[:5])  # Print only the first 5 keys
    data = {} if not keys else {key: {'narrative': narrative, 'summary': summary} for key, (_, narrative, _) in zip(keys, redis_conn.hscan_iter('0', count=len(keys)))}
    return data

data = fetch_data_from_redis()
if not data:
    print("No data found in Redis")
else:
    for key, content in data.items():
        narrative = content['narrative']
        summary = content['summary']





# data[0]

# # Generate N-grams
# def generate_ngrams(text, n=2):
#     vectorizer = CountVectorizer(ngram_range=(n, n))
#     ngrams = vectorizer.fit_transform([text]).todense().tolist()
#     return ngrams

# # Generate embeddings using Hugging Face Transformers
# def generate_embeddings(text):
#     inputs = tokenizer(text, padding=True, truncation=True, return_tensors="pt")
#     outputs = model(**inputs)
#     # Use the mean of the last layer's features as the sentence embedding
#     embeddings = outputs.last_hidden_state.mean(dim=1).detach().numpy()
#     return embeddings

# # Named Entity Recognition
# ner = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english", device=0)  # Example model
# def generate_tags(text):
#     tags = ner(text)
#     return tags

# def cluster_embeddings(embeddings, num_clusters=5):
#     kmeans = KMeans(n_clusters=num_clusters)
#     kmeans.fit(embeddings)
#     labels = kmeans.labels_
#     return labels

#     r.hdel(key, 'Tags')
#     r.hdel(key, 'Cluster')
    
#     # Store N-grams as a Sorted Set with scores
#     ngrams_set = r.zunionstore('ngrams_' + key, [('ngrams_'+key, 1)])
#     for i, ngram in enumerate(ngrams):
#         score = 1 - (i / len(ngrams))  # Assign a descending score to each N-gram
#         r.zadd('ngrams_' + key, [(json.dumps(ngram), score)])
    
#     # Store tags as a Hash with entity type and value fields
#     for tag in tags:
#         r.hset('tags_'+key, tag['entity_group'], json.dumps(tag))
        
#     # Store cluster label as a String
#     r.set('cluster_' + key, str(cluster_label))

# data = fetch_data_from_redis()

# for key, content in data.items():
#     narrative = content['narrative']
#     summary = content['summary']
#     # Generate N-grams
#     ngrams
