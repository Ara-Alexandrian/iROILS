"""
Author: Ara Alexandrian
Date: January 27, 2024

RedisManager Class

This class provides a set of methods to manage a Redis server, a Docker container, and generate summaries using a specified model. 
It reads the necessary configuration from a `config.ini` file located in the same directory as this script. 

The `config.ini` file should have the following structure:

[Redis]
host = <redis_host>
port = <redis_port>
password = <redis_password>

[Container]
hostname = <hostname>
username = <username>
password = <password>
name = <container_name>

[API]
endpoint = <api_endpoint>

[Model]
name = <model_name>

Replace the placeholders with your actual values.

Usage:

1. Create an instance of the RedisManager class:
    manager = RedisManager()

2. Call the necessary methods on this instance. For example, to clear model data:
    manager.clear_model_data()

Please note that the methods will use the configuration that was read from the `config.ini` file when the instance was created.

"""


import redis
import requests
import json
from tqdm.notebook import tqdm
import time
import paramiko
import openpyxl
import configparser
import re

class RedisManager:
    def __init__(self):
        # Create a ConfigParser object
        config = configparser.ConfigParser()

        # Read the configuration file
        config.read('config.ini')

        # Get the Redis connection information from the configuration file
        self.redis_host = config.get('Redis', 'host')
        self.redis_port = config.getint('Redis', 'port')
        self.redis_password = config.get('Redis', 'password') or None

        # Get the API endpoint from the configuration file
        self.api_endpoint = config.get('API', 'endpoint')

        # Create a Redis connection
        self.redis_conn = redis.Redis(host=self.redis_host, port=self.redis_port, password=self.redis_password)

        # Summary_Model configurations
        self.summary_model_name = config.get('Summary_Model', 'name')
        self.summary_prompt = config.get('Summary_Model', 'prompt')
        self.summary_options = {
            "num_predict": config.getint('Summary_Model', 'num_predict'),
            "top_k": config.getint('Summary_Model', 'top_k'),
            "top_p": config.getfloat('Summary_Model', 'top_p'),
            "temperature": config.getfloat('Summary_Model', 'temperature'),
            "num_gpu": config.getint('Summary_Model', 'num_gpu'),
            "num_thread": config.getint('Summary_Model', 'num_thread'),
            "num_ctx": config.getint('Summary_Model', 'num_ctx')
        }

        # Eval_Model configurations
        self.eval_model_name = config.get('Eval_Model', 'name')
        self.eval_prompt = config.get('Eval_Model', 'prompt')
        self.eval_options = {
            "num_predict": config.getint('Eval_Model', 'num_predict'),
            "top_k": config.getint('Eval_Model', 'top_k'),
            "top_p": config.getfloat('Eval_Model', 'top_p'),
            "temperature": config.getfloat('Eval_Model', 'temperature'),
            "num_gpu": config.getint('Eval_Model', 'num_gpu'),
            "num_thread": config.getint('Eval_Model', 'num_thread'),
            "num_ctx": config.getint('Eval_Model', 'num_ctx')
        }

        # TQA configuration
        self.client_id = config.get('TQA', 'CLIENT_ID')
        self.client_key = config.get('TQA', 'CLIENT_KEY')

        # Spreadsheet configuration
        self.file_path = config.get('SPREADSHEET', 'FILE_PATH')
        self.extracted_file_path = config.get('SPREADSHEET', 'EXTRACTED_FILE_PATH')

        # Container configuration
        self.hostname = config.get('Container', 'hostname')
        self.username = config.get('Container', 'username')
        self.password = config.get('Container', 'password')
        self.container_name = config.get('Container', 'name')


        try:
            self.redis_conn = redis.StrictRedis(host=self.redis_host, port=self.redis_port, password=self.redis_password, decode_responses=True)
        except Exception as e:
            print(f"Failed to connect to Redis server: {e}")

    @staticmethod
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

    def restart_container(self):
        print(f"Restarting container '{container_name}'...")
        self.manage_container(hostname, username, password, container_name, 'restart')
        time.sleep(10)  # Wait a bit for the container to be up again

    @staticmethod
    def connect_to_redis():
        try:
            r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
            return r
        except Exception as e:
            print(f"Failed to connect to Redis server: {e}")
            return None


    def clear_model_data(self, model_name=None, field_name=None):
        try:
            keys = self.redis_conn.keys('*')  # Retrieve all keys

            for key in keys:
                # If key does not start with 'event:', skip this iteration
                if not key.startswith('event:'):
                    continue

                # Retrieve all field names for the key
                fields = self.redis_conn.hkeys(key)
                for field in fields:
                    # If a specific model is provided and it doesn't match the current field's model, skip this iteration
                    if model_name and not field.startswith(f"{model_name}:"):
                        continue
                    
                    # If a specific field name is provided and it doesn't match the current field, skip this iteration
                    if field_name and field_name != field:
                        continue

                    # Delete the field
                    self.redis_conn.hdel(key, field)
                    print(f"Cleared '{field}' from '{key}'.")

            print(f"Previous data cleared from Redis.")
        except Exception as e:
            print(f"Failed to clear previous data from Redis: {e}")




    def generate_summaries(self, resume=True):
        headers = {'Content-Type': 'application/json'}
        keys = self.redis_conn.keys('*')

        pbar = tqdm(total=len(keys), ncols=150)
        for key in keys:
            summary_field = f'{self.summary_model_name}:LLM Summary'
            
            if resume and self.redis_conn.hexists(key, summary_field):
                print(f"Summary for {self.summary_model_name} already exists for key: {key}, skipping...")
                pbar.update(1)
                continue

            narrative = self.redis_conn.hget(key, 'Narrative').strip()
            prompt = self.summary_prompt.format(narrative=narrative)
            data = {
                "key": key,
                "model": self.summary_model_name,
                "prompt": prompt,
                "raw": True,
                "stream": False,
                "options": self.summary_options
            }

            try:
                response = requests.post(self.api_endpoint, headers=headers, data=json.dumps(data), timeout=45)
                if response.status_code == 200:
                    parsed_json = response.json()
                    summary = parsed_json.get('response', '')
                    # Clean up the summary by reducing multiple newlines to single newlines
                    # and removing leading whitespace from each line
                    summary = '\n'.join(line.lstrip() for line in summary.split('\n'))

                    self.redis_conn.hset(key, summary_field, summary)
                    print(f"\n[Success] Summary for model '{self.summary_model_name}' successfully generated for key: {key}")
                    print(f"\n'{self.summary_model_name}' Summary: '{self.summary}.")
                else:
                    print(f"\n[Error] Failed to get a successful response for key {key}, status code: {response.status_code}")
            except requests.exceptions.Timeout:
                print(f"\n[Timeout] Request timed out for key {key}. Attempting to restart the container...")
                self.restart_container()

            pbar.update(1)
        pbar.close()


    def evaluate_summaries(self, resume=True):
        headers = {'Content-Type': 'application/json'}
        evaluations_pending = True

        while evaluations_pending:
            keys = self.redis_conn.keys('*')
            # Check for empty evaluations
            evaluations_pending = False
            pbar = tqdm(total=len(keys), ncols=150)

            # First pass: generate evaluations
            for key in keys:
                self.perform_evaluation(key, headers, resume=True)
                pbar.update(1)
            pbar.close()

            
            for key in keys:
                evaluation_field = f'{self.eval_model_name}:LLM Evaluation'
                evaluation = self.redis_conn.hget(key, evaluation_field)
                if not evaluation:
                    evaluations_pending = True
                    print(f"Evaluation for key {key} is empty, re-performing evaluation...")
                    self.perform_evaluation(key, headers, resume=False)

            if not evaluations_pending:
                print("All evaluations are complete.")
                break  # Exit the loop if there are no pending evaluations

            print("Some evaluations are still pending. Re-scanning the Redis database...")


    def perform_evaluation(self, key, headers, resume=False):
        narrative = self.redis_conn.hget(key, 'Narrative')
        summary_field = f'{self.summary_model_name}:LLM Summary'
        summary = self.redis_conn.hget(key, summary_field)
        evaluation_field = f'{self.eval_model_name}:LLM Evaluation'

        if not narrative or not summary:
            print(f"[Warning] Missing narrative or summary for key: {key}")
            return

        # Use the configured prompt, inserting the narrative and summary
        prompt = self.eval_prompt.format(narrative=narrative, summary=summary)
        data = {
            "key": key,
            "model": self.eval_model_name,
            "prompt": prompt,
            "raw": True,
            "stream": False,
            "options": self.eval_options
        }

        try:
            response = requests.post(self.api_endpoint, headers=headers, data=json.dumps(data), timeout=45)
            if response.status_code == 200:
                parsed_json = response.json()
                evaluation = parsed_json.get('response', '')
                # Strip leading new lines and empty spaces from the evaluation
                evaluation = evaluation.lstrip()
                if evaluation:
                    self.redis_conn.hset(key, evaluation_field, evaluation)
                    print(f"[Success] Evaluation for model '{self.eval_model_name}' successfully generated for key: {key}\n"
                            f"\n[Narrative]:\n{self.narrative}\n"
                            f"\n[Summary]:\n{self.summary}\n"
                            f"\n[Evaluation]:\n{self.evaluation}\n")


                else:
                    print(f"[Warning] Empty evaluation content for key: {key}")
            else:
                print(f"[Error] Failed to get a successful response for key {key}, status code: {response.status_code}, response: {response.text}")
        except requests.exceptions.Timeout:
            print(f"[Timeout] Request timed out for key {key}.")
        except requests.exceptions.RequestException as e:
            print(f"[RequestException] Request exception for key {key}: {e}")



    def clean_text(self, text):
        """Remove extra newlines, leading/trailing whitespace, and ensure text starts with the first word."""
        # Remove leading and trailing whitespace
        text = text.strip()
        # Replace multiple newlines with a single newline
        text = re.sub(r'\n+', '\n', text)
        # Ensure text starts with the first word (remove leading newlines)
        text = re.sub(r'^\n+', '', text)
        return text


    def generate_summaries_for_event(self, event_id, summary_model_name):
        headers = {'Content-Type': 'application/json'}
        key = f'event:{event_id}'

        narrative = self.redis_conn.hget(key, 'Narrative').strip()
        prompt = self.summary_prompt.format(narrative=narrative)
        data = {
            "key": key,
            "model": summary_model_name,
            "prompt": prompt,
            "raw": True,
            "stream": False,
            "options": self.summary_options
        }

        response = requests.post(self.api_endpoint, headers=headers, data=json.dumps(data), timeout=45)
        if response.status_code == 200:
            parsed_json = response.json()
            summary = parsed_json.get('response', '')
            # Clean up the summary by reducing multiple newlines to single newlines
            # and removing leading whitespace from each line
            summary = '\n'.join(line.lstrip() for line in summary.split('\n'))

            self.redis_conn.hset(key, f'{summary_model_name}:LLM Summary', summary)
            print(f"Summary for model '{summary_model_name}' successfully generated for key: {key}")
        else:
            print(f"Failed to generate summary for key: {key}, status code: {response.status_code}")
        return summary


    def evaluate_summaries_for_event(self, event_id, eval_model_name):
        headers = {'Content-Type': 'application/json'}
        key = f'event:{event_id}'

        narrative = self.redis_conn.hget(key, 'Narrative')
        summary = self.redis_conn.hget(key, f'{self.summary_model_name}:LLM Summary')
        prompt = self.eval_prompt.format(narrative=narrative, summary=summary)
        data = {
            "key": key,
            "model": eval_model_name,
            "prompt": prompt,
            "raw": True,
            "stream": False,
            "options": self.eval_options
        }

        response = requests.post(self.api_endpoint, headers=headers, data=json.dumps(data), timeout=45)
        if response.status_code == 200:
            parsed_json = response.json()
            evaluation = parsed_json.get('response', '')
            # Strip leading new lines and empty spaces from the evaluation
            evaluation = evaluation.lstrip()

            self.redis_conn.hset(key, f'{eval_model_name}:LLM Evaluation', evaluation)
            print(f"Evaluation for model '{eval_model_name}' successfully generated for key: {key}")

            # Check if the Redis cache has been updated correctly
            redis_evaluation = self.redis_conn.hget(key, f'{eval_model_name}:LLM Evaluation').strip()
            if redis_evaluation == evaluation:
                print(f"Redis cache updated correctly for key: {key}")
            else:
                print(f"Error: Redis cache not updated correctly for key: {key}")
                print(f"Redis evaluation: {redis_evaluation}")
                print(f"Original evaluation: {evaluation}")
        else:
            print(f"Failed to generate evaluation for key: {key}, status code: {response.status_code}")
        return evaluation



    def regenerate_summary_and_evaluation(self, event_id, summary_model_name=None, eval_model_name=None):
        summary_model_name = summary_model_name or self.summary_model_name
        eval_model_name = eval_model_name or self.eval_model_name
        
        # Generate a new summary
        summary = self.generate_summaries_for_event(event_id, summary_model_name)
        print(f"Generated summary: {summary}")
        
        # Generate a new evaluation
        evaluation = self.evaluate_summaries_for_event(event_id, eval_model_name)
        print(f"Generated evaluation: {evaluation}")





    def create_excel_from_redis(self):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Extract Summary"
        headers = [
            'Key',
            'Narrative',
            f'{self.summary_model_name} Summary',
            f'{self.eval_model_name} Evaluation'
        ]
        ws.append(headers)
        keys = self.redis_conn.keys('*')

        for key in keys:
            narrative = self.redis_conn.hget(key, 'Narrative')
            summary = self.redis_conn.hget(key, f'{self.summary_model_name}:LLM Summary')
            evaluation = self.redis_conn.hget(key, f'{self.eval_model_name}:LLM Evaluation')

            # Clean up the text for narrative, summary, and evaluation
            narrative = self.clean_text(narrative) if narrative else narrative
            summary = self.clean_text(summary) if summary else summary
            evaluation = self.clean_text(evaluation) if evaluation else evaluation

            ws.append([key, narrative, summary, evaluation])

        wb.save('extract_summary.xlsx')
