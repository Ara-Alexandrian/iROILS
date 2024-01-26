import redis
import requests
import json
import tqdm
import time
import paramiko  # for SSH

def connect_to_redis(redis_host, redis_port, redis_password):
    try:
        r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
        return r
    except Exception as e:
        print(f"Failed to connect to Redis server: {e}")
        return None

# Add function to restart the Ollama container
def restart_ollama_container():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('daedalisto.local', username='root', password='2Apple@@')
    
    try:
        stdin, stdout, stderr = ssh.exec_command('docker restart ollama_container_name')
        print(stdout.read().decode())
        print(stderr.read().decode())
    finally:
        ssh.close()
    print("Ollama container restarted. Waiting for it to become operational...")
    time.sleep(30)  # Wait for the container to restart

def generate_summaries(r, model_name):
    api_endpoint = 'http://192.168.1.5:11434/api/generate'
    headers = {'Content-Type': 'application/json'}
    keys = r.keys('*')
    
    pbar = tqdm.tqdm(total=len(keys), ncols=70)
    
    for key in keys:
        if r.hexists(key, f'{model_name}:LLM Summary'):
            print(f"Summary already exists for key: {key}, skipping...")
            continue
        
        narrative = r.hget(key, 'Narrative')
        data = {
            "key": key,
            "model": model_name,
            "prompt": narrative,
            "raw": True,
            "stream": False,
            "options": {
                "temperature": 0.01,
                "top_p": 0.5
            }
        }
        
        try:
            response = requests.post(api_endpoint, headers=headers, data=json.dumps(data), timeout=2.5)
        except requests.exceptions.Timeout:
            print(f"Request timed out for entry {key}. Attempting to restart the Ollama container...")
            restart_ollama_container()
            continue  # Optionally, retry the current key or move to the next one
        
        if response.status_code == 200:
            try:
                parsed_json = response.json()
                summary = parsed_json.get('response', '')
                r.hset(key, f'{model_name}:LLM Summary', summary)
                print(f"Sample summary: {summary[:50]}...")
            except json.JSONDecodeError as e:
                print(f'Failed to parse JSON for entry {key}: {e}')
        else:
            print(f'Failed to get a successful response for entry {key}, status code: {response.status_code}')
        
        pbar.update(1)
    
    pbar.close()

redis_host = "192.168.1.4"
redis_port = 6379
redis_password = ""
data_type_to_clear = "llm-summaries"

redis_conn = connect_to_redis(redis_host, redis_port, redis_password)

if redis_conn:
    generate_summaries(redis_conn, 'mistral')
