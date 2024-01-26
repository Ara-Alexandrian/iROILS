import requests
import json

# Set the API endpoint
api_endpoint = 'http://192.168.1.5:11434/api/generate'

# Define the headers
headers = {
    'Content-Type': 'application/json'
}

# Define the data payload
data = {
    "model": "",
    "prompt": "[INST] why is the sky blue? [/INST]",
    "raw": True,
    "stream": False,
    "options": {
        "temperature": 0.01,  # Already quite low, but you can try lowering it a bit more
        "top_p": 0.5,  # Adjust this to control diversity. Lower values make responses more consistent
        # "max_tokens": 2000  # Adjust this to the average length of the response you are expecting
    }
}


# Make the POST request
response = requests.post(api_endpoint, headers=headers, data=json.dumps(data))

# Check if the response status code is 200 (OK)
if response.status_code == 200:
    try:
        # Parse the response as JSON
        parsed_json = response.json()
        
        # Print the 'response' part of the JSON
        print('Response:', parsed_json.get('response', ''))
    except json.JSONDecodeError as e:
        print('Failed to parse JSON:', e)
else:
    print(f'Failed to get a successful response, status code: {response.status_code}')
