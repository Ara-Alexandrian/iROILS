'''
Author: Ara Alexandrian
Date: September 28, 2023

This script contains functions for managing containers through SSH, connecting to a Redis server, clearing previous data from Redis, storing data to Redis, and generating summaries using an API.

The functions included are:

manage_container: SSH-based function for managing containers by executing Docker commands.
restart_container: Restarts a container by calling the manage_container function with the restart action.
connect_to_redis: Connects to a Redis server using the provided host, port, and password.
clear_previous_data: Clears previous data of a specified data type from Redis.
store_data_to_redis: Stores data in Redis under a specified key.
generate_summaries: Generates summaries for entries stored in Redis using an API.
To use these functions, you need to provide the necessary parameters such as the hostname, username, password, container name, Redis server details, and API endpoint. The script demonstrates an example usage where summaries are generated for entries stored in Redis.

Please note that you need to have the redis, requests, json, tqdm, and paramiko libraries installed in order to run this script.
'''

import redis
import requests
import json
import tqdm
import time
import paramiko
import openpyxl


def create_excel_from_redis(r):
    # Create a new workbook and add a worksheet to it
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Extract Summary"

    # Add headers to the worksheet
    headers = ['Key', 'Narrative', 'Summary', 'Evaluation']
    ws.append(headers)

    # Fetch all keys from Redis
    keys = r.keys('*')
    # print(keys)

    for key in keys:
        # Retrieve the narrative and summary from Redis
        narrative = r.hget(key, 'Narrative')
        summary = r.hget(key, 'mistral:LLM Summary')  # Updated this line to fetch 'Summary' as 'LLM Summary'

        # Append the key, narrative, and summary to the worksheet
        ws.append([key, narrative, summary])

    # Save the workbook to a file
    wb.save('extract_summary.xlsx')





# SSH-based container management function
def manage_container(hostname, username, password, container_name, action):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password)

    command = f'docker {action} {container_name}'
    try:
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        if output:
            print(output)
        if error:
            print(error)
    finally:
        ssh.close()

# Function to restart the container
def restart_container(hostname, username, password, container_name):
    print(f"Restarting container '{container_name}'...")
    manage_container(hostname, username, password, container_name, 'restart')
    time.sleep(10)  # Wait a bit for the container to be up again



def connect_to_redis(redis_host, redis_port, redis_password):
    try:
        r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
        return r
    except Exception as e:
        print(f"Failed to connect to Redis server: {e}")
        return None

def clear_model_data(r, model_name):
    try:
        keys = r.keys('*')  # Retrieve all keys
        model_field_suffix = f"{model_name}:LLM Summary"  # Suffix for fields related to the model

        for key in keys:
            # Retrieve all field names for the key
            fields = r.hkeys(key)
            for field in fields:
                # If field name ends with the model-specific suffix, delete it
                if field.endswith(model_field_suffix):
                    r.hdel(key, field)
                    print(f"Cleared '{field}' from '{key}'.")

        print(f"Previous data for model '{model_name}' cleared from Redis.")
    except Exception as e:
        print(f"Failed to clear previous data for model '{model_name}' from Redis: {e}")



def store_data_to_redis(r, key, data):
    try:
        r.set(key, json.dumps(data))
        print(f"Data stored in Redis under key: {key}")
    except Exception as e:
        print(f"Failed to store data to Redis: {e}")

def generate_summaries(r, model_name, hostname, username, password, container_name):
    api_endpoint = 'http://192.168.1.5:11434/api/generate'
    headers = {'Content-Type': 'application/json'}
    keys = r.keys('*')

    # Initialize progress bar
    pbar = tqdm.tqdm(total=len(keys), ncols=70)

    for key in keys:
        summary_field = f'{model_name}:LLM Summary'
        # Check if the summary for this model already exists for this key before making the request
        if r.hexists(key, summary_field):
            print(f"Summary for {model_name} already exists for key: {key}, skipping...")
            pbar.update(1)
            continue

        narrative = r.hget(key, 'Narrative')
        # Adjusted prompt to restrict creativity and specify limitations
        prompt = f"Summarize the following event without adding any information or context not explicitly stated in the narrative: '{narrative}'"
        data = {
            "key": key,
            "model": model_name,
            "prompt": prompt,
            "raw": True,
            "stream": False,
            "options": {
                "num_predict": 500,  # Adjust based on expected summary length; acts more like a max for large narratives
                "top_k": 25,  # Restricts predictions to top 20 tokens
                "top_p": 0.2,  # Considers a wide range of tokens
                "temperature": 0.01,  # More deterministic predictions
                "num_gpu": 2,  # Utilize both GPUs
                "num_thread": 16,  # Number of CPU threads dedicated to task
                "num_ctx" : 16000
            }
        }

        # If summary does not exist for this model, then make the request
        try:
            response = requests.post(api_endpoint, headers=headers, data=json.dumps(data), timeout=45)
            if response.status_code == 200:
                parsed_json = response.json()
                summary = parsed_json.get('response', '')
                # Fetch the narrative from Redis using the key
                narrative = r.hget(key, 'Narrative')
                # Store the summary in Redis under the model-specific field
                r.hset(key, summary_field, summary)
                print(f"\n[Success] Summary for model '{model_name}' successfully generated for key: {key}")
                print(f"\n[Narrative]:\n{narrative}\n")  # This will print the original narrative to the console
                print(f"\n[Summary]:\n{summary}\n")  # This will print the full summary to the console
            else:
                # Print out detailed error information
                print(f"\n[Error] Failed to get a successful response for key {key}, status code: {response.status_code}")
                print(f"Response body: {response.text}\n")  # This will print the error message from the API if any
        except requests.exceptions.Timeout:
            print(f"\n[Timeout] Request timed out for key {key}. Attempting to restart the container...")
            restart_container(hostname, username, password, container_name)
            # Optionally, you can decide to retry the request here

        pbar.update(1)

    pbar.close()





# Example usage:
hostname = '192.168.1.47'
username = 'root'
password = '2Apple@@'
container_name = 'ollama'
redis_host = "192.168.1.4"
redis_port = 6379
redis_password = ""
data_type_to_clear = "LLM Summary"

redis_conn = connect_to_redis(redis_host, redis_port, redis_password)
model_name = 'mistral'  # Specify the model name whose data you want to clear


if redis_conn:
    clear_model_data(redis_conn, model_name)
    generate_summaries(redis_conn, model_name, hostname, username, password, container_name)
    create_excel_from_redis(redis_conn)