import configparser
import pandas as pd
import redis
import requests
import json
from tqdm.auto import tqdm
import spacy
import re

class RedisManager2:
    def __init__(self):
        # Create a ConfigParser object
        config = configparser.ConfigParser()

        try:
            # Load Spacy model for text processing
            self.nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            print(f"Failed to load Spacy model: {e}")
            return

        # Read the configuration file
        config.read('LLM-inferencing/config.ini')
        self.config = config  # Store config for later use

        # Redis configuration
        self.redis_host = config.get('Redis', 'host')
        self.redis_port = config.getint('Redis', 'port')
        self.redis_password = config.get('Redis', 'password', fallback=None)

        try:
            # Create a Redis connection
            self.redis_conn = redis.StrictRedis(host=self.redis_host, port=self.redis_port, password=self.redis_password, decode_responses=True)
        except Exception as e:
            print(f"Failed to connect to Redis server: {e}")
            return

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

    def clean_text(self, text):
        """Clean text by removing unwanted characters and formatting."""
        text = re.sub(r'\s+', ' ', text)
        return text

    def process_text(self, text):
        """Process text using Spacy."""
        doc = self.nlp(text)
        processed_text = ' '.join([token.lemma_ for token in doc if not token.is_stop])
        return processed_text

    def generate_event_insights(self, mistral_summary, cleaned_summary, processed_text):
        """Generates event insights for given summaries and processed text."""
        prompt_template = self.config['Expert_Model']['prompt']
        prompt = prompt_template.format(
            mistral_summary=mistral_summary,
            cleaned_summary=cleaned_summary,
            processed_text=processed_text
        )
        payload = {
            "model": self.config['Expert_Model']['name'],
            "prompt": prompt,
            "inputs": {
                "mistral_summary": mistral_summary,
                "cleaned_summary": cleaned_summary,
                "processed_text": processed_text
            }
        }
        response = requests.post(self.api_endpoint, json=payload)
        if response.status_code == 200:
            response_json = response.json()
            if 'response' in response_json and response_json['done']:
                return response_json['response']
            else:
                return "Invalid API response format"
        else:
            return "API request failed"

    def process_and_update_redis_data(self, password):
        """Processes data for every key in Redis and updates it with cleaned and lemmatized summaries."""
        keys = self.redis_conn.keys(pattern="*")  # Adjust pattern as needed
        for key in tqdm(keys):  # tqdm for progress indication if running interactively
            value = self.redis_conn.get(key)
            try:
                value_dict = json.loads(value)
                original_summary = value_dict.get('Summary', '')  # Assuming there's a 'Summary' key
                
                # Apply cleaning and processing
                cleaned_summary = self.clean_text(original_summary)
                lemmatized_summary = self.process_text(original_summary)
                
                # Update the dictionary with new entries
                value_dict['Cleaned Summary'] = cleaned_summary
                value_dict['Lemmatized Summary'] = lemmatized_summary
                
                # Save the updated dictionary back to Redis
                self.redis_conn.set(key, json.dumps(value_dict))
            except json.JSONDecodeError:
                print(f"Skipping key {key}: Value is not valid JSON.")
            except Exception as e:
                print(f"Error processing key {key}: {e}")


