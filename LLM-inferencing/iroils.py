import json
import redis
from sklearn.cluster import KMeans
import spacy
import numpy as np
from sentence_transformers import SentenceTransformer
from nltk.util import ngrams
import configparser

# Read configuration from config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

redis_host = config['Redis']['host']
redis_port = int(config['Redis']['port'])
redis_password = config['Redis']['password']

# Connect to Redis server
r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

def connect_to_redis(host, port, password):
    try:
        return redis.StrictRedis(host=host, port=port, password=password, decode_responses=True)
    except Exception as e:
        print(f"Failed to connect to Redis server: {e}")
        return None
        
# Add some sample data to Redis
r.hset('narratives', 'key1', json.dumps({'text': 'Sample narrative 1'}))
r.hset('summaries', 'key1', json.dumps({'text': 'Sample summary 1'}))

# Retrieve the data from Redis and process it using your code
narrative_key = 'key1'
summary_key = 'key1'
narrative_data = r.hget('narratives', narrative_key)
summary_data = r.hget('summaries', summary_key)
if narrative_data and summary_data:
    narrative = json.loads(narrative_data)['text']
    summary = json.loads(summary_data)['text']
    processed_pair = process_pair(narrative, summary)
    r.hset('processed_pair', narrative_key, json.dumps(processed_pair))
else:
    print("Error: Narrative or summary not found in Redis")



# r = connect_to_redis('192.168.1.4', 6379, '')
# ner_model = spacy.load('de_core_news_lg')
# embedder = SentenceTransformer('all-MiniLM-L6-v2')

# def process_pair(narrative, summary):
#     # Generate N-grams
#     ngrams = {'narrative': generate_ngrams(narrative), 'summary': generate_ngrams(summary)}
#     # Extract named entities
#     ner_narrative = extract_ner(narrative)
#     ner_summary = extract_ner(summary)
#     # Generate embeddings
#     embeddings = {'narrative': generate_embeddings(narrative), 'summary': generate_embeddings(summary)}
#     # Perform clustering
#     clusters = {'narrative': cluster_embeddings(embeddings['narrative']), 'summary': cluster_embeddings(embeddings['summary'])}
#     return {
#         'narrative': {
#             'ngrams': ngrams['narrative'],
#             'ner': ner_narrative,
#             'clusters': clusters['narrative']
#         },
#         'summary': {
#             'ngrams': ngrams['summary'],
#             'ner': ner_summary,
#             'clusters': clusters['summary']
#         }
#     }

# def extract_ner(text):
#     doc = ner_model(text)
#     entities = [(X.text, X.label_) for X in doc.ents]
#     return entities

# def extract_narratives_summaries(r):
#     narratives_summaries = []
#     keys = r.keys('*')
#     for key in keys:
#         if r.type(key) == 'hash':
#             value = r.hgetall(key)
#             narratives_summaries.append({"key": key, "value": value})
#     return narratives_summaries

# def generate_ngrams(text, n=3):
#     words = text.split()
#     ngrams = zip(*[words[i:] for i in range(n)])
#     ngrams = [' '.join(ngram) for ngram in ngrams]
#     return ngrams

# def process_narrative_summary(narrative_summary):
#     narrative = json.loads(narrative_summary["value"]["Narrative"])
#     summary = json.loads(narrative_summary["value"]["mistral:LLM Summary"])
#     processed_pair = process_pair(narrative, summary)
#     return {
#         "Event Number": narrative_summary["key"],
#         "Type": "Summary",
#         "Text": summary,
#         "Original Text": narrative_summary["value"]["Narrative"],
#         **processed_pair
#     }

# def extract_narratives_summaries(r):
#     narratives_summaries = []
#     keys = r.keys('*')
#     for key in keys:
#         if r.type(key) == 'hash':
#             value = r.hgetall(key)
#             narratives_summaries.append({"key": key, "value": value})
#     return narratives_summaries

# # Fetch narrative and summary from Redis
# narratives_summaries = extract_narratives_summaries(r)
# for narrative_summary in narratives_summaries:
#     narrative = json.loads(narrative_summary["value"]["Narrative"])
#     summary = json.loads(narrative_summary["value"]["mistral:LLM Summary"])
#     processed_pair = process_pair(narrative, summary)
#     # Store results back in Redis
#     r.hset('processed_pair', narrative_summary["key"], json.dumps(processed_pair))
# else:
#     print("Error: Narrative or summary not found in Redis")

