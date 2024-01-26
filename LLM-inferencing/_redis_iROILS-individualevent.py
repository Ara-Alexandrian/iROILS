'''
Author: Ara Alexandrian
Date: September 28, 2023

This script contains a function for reanalyzing a summary stored in Redis by making a request to an API. It also includes an example usage of the reanalyze_summary function.

The function included is:

reanalyze_summary: Reanalyzes a summary for a specific key stored in Redis by making a request to an API.
To use the reanalyze_summary function, you need to provide the Redis connection object, the target key, model name, hostname, username, password, container name, API endpoint, and headers. The script demonstrates an example usage where a summary is reanalyzed for a specific key stored in Redis.

Please note that you need to have the redis, requests, json, tqdm, and paramiko libraries installed in order to run this script.
'''

import redis
import requests
import json
import tqdm
import time
import paramiko

def connect_to_redis(redis_host, redis_port, redis_password):
    try:
        r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
        return r
    except Exception as e:
        print(f"Failed to connect to Redis server: {e}")
        return None

def reanalyze_summary(r, target_key, model_name, hostname, username, password, container_name, api_endpoint, headers):
    try:
        # Check if the key exists and has a narrative
        if r.exists(target_key) and r.hexists(target_key, 'Narrative'):
            narrative = r.hget(target_key, 'Narrative')
            prompt = f"Summarize the following event without adding any information or context not explicitly stated in the narrative: '{narrative}'"
            data = {
                "key": target_key,
                "model": model_name,
                "prompt": prompt,
                "raw": True,
                "stream": False,
                "options": {
                    "num_predict": 100,  # Adjust based on expected summary length
                    "top_k": 25,  # Restricts predictions to top 20 tokens
                    "top_p": 0.2,  # Considers a wide range of tokens
                    "temperature": 0.01,  # More deterministic predictions
                    # "max_tokens": 100,  # Maximum token length for the summary
                    "num_gpu": 2,  # Utilize both GPUs
                    "num_thread": 16,  # Number of CPU threads dedicated to task
                    # Other parameters related to GPU setup can be added based on the API and software documentation
                    }
            }

            # Make the request
            response = requests.post(api_endpoint, headers=headers, data=json.dumps(data), timeout=45)
            if response.status_code == 200:
                parsed_json = response.json()
                summary = parsed_json.get('response', '')
                # Use the model name as part of the field name to store model-specific summaries
                summary_field = f'{model_name}:LLM Summary'
                r.hset(target_key, summary_field, summary)
                print(f"Summary successfully reanalyzed for key: {target_key} using model: {model_name}.")
                print("Completed Summary:")
                print(summary)  # This will print the full summary to the console
            else:
                # Print out detailed error information
                print(f'Failed to get a successful response for key {target_key}, status code: {response.status_code}')
                print(f'Response body: {response.text}')  # This will print the error message from the API if any
        else:
            print(f'Key {target_key} does not exist or does not have a narrative.')
    except requests.exceptions.Timeout:
        print(f"Request timed out for key {target_key}. Attempting to restart the container...")
        restart_container(hostname, username, password, container_name)
        # Optionally, you can decide to retry the request here


# Example usage of reanalyze_summary:
target_key = 'event:40677'
api_endpoint = 'http://192.168.1.5:11434/api/generate'
hostname = '192.168.1.47'
username = 'root'
password = '2Apple@@'
container_name = 'ollama'
redis_host = "192.168.1.4"
redis_port = 6379
redis_password = ""
data_type_to_clear = "LLM Summary"
headers = {'Content-Type': 'application/json'}
model_name = 'mistral'

redis_conn = connect_to_redis(redis_host, redis_port, redis_password)

if redis_conn:
    reanalyze_summary(redis_conn, target_key, model_name, hostname, username, password, container_name, api_endpoint, headers)