import configparser
import pandas as pd
import requests
import json
from tqdm.auto import tqdm
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read('LLM-inferencing/config.ini')

# API configuration
api_endpoint = config['API']['endpoint']

# Load data from spreadsheet specified in the SPREADSHEET section
try:
    data_df = pd.read_excel(config['SPREADSHEET']['CLEANED_FILE_PATH'])
except Exception as e:
    logging.error(f"Error while loading excel file: {e}")
    raise

# # Print the first few rows of the DataFrame to check if it's being read correctly
# logging.info(data_df.head())

# # You can also check the data types of the columns
# logging.info(data_df.dtypes)

# # If you want to check a specific column, you can do something like this:
# logging.info(data_df['mistral Summary'].head())

# Helper function to generate event insights using the Expert_Model configuration
def generate_event_insights(mistral_summary, cleaned_summary, processed_text):
    # Construct the prompt using Expert_Model's prompt template
    prompt_template = config['Expert_Model']['prompt']
    prompt = prompt_template.replace("[mistral Summary]", mistral_summary)\
                            .replace("[Cleaned Summary]", cleaned_summary)\
                            .replace("[Processed Text]", processed_text)

    # Construct payload for the API request
    data = {
        "key": "some_key",  # replace with actual key if needed
        "model": config['Expert_Model']['name'],
        "prompt": prompt,
        "raw": True,
        "stream": False,
        "options": {}  # replace with actual options if needed
    }

    try:
        # Send the request to the API
        response = requests.post(api_endpoint, data=json.dumps(data), timeout=45)
    except requests.exceptions.Timeout:
        return "API request timed out"
    except Exception as e:
        return "API request failed"

    # Check the response status code before parsing
    if response.status_code != 200:
        return "API request failed"

    try:
        # Parse the API response
        response_json = response.json()
    except json.JSONDecodeError:
        return "JSON Decode Error"

    if 'response' in response_json and response_json['done']:
        event_insights = response_json['response']
        # Print the resulting 'Event Insight'
        print(f"Event Insights: {event_insights}")
        return event_insights
    else:
        return "Invalid API response format"



# Apply the function to each row in the DataFrame
tqdm.pandas(desc="Generating Event Insights")
data_df['Event Insights'] = data_df.progress_apply(
    lambda row: generate_event_insights(
        row['mistral Summary'], row['Cleaned Summary'], row['Processed Text']
    ), axis=1
)

# Save the updated DataFrame to a new Excel file
output_file_path = 'LLM-inferencing/Event-Insights.xlsx'
try:
    data_df.to_excel(output_file_path, index=False)
except Exception as e:
    logging.error(f"Error while saving excel file: {e}")
    raise

# Confirm the file has been saved
logging.info(f"Updated file saved to {output_file_path}")