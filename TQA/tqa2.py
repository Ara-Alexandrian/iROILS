import pandas as pd
from pyTQA import tqa
import sys
import json
import requests
import datetime
import configparser  # Import the configparser module
from dateutil import parser

# Read the config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

def connect_to_tqa():
    # Use the configuration values
    tqa.client_id = config['TQA']['CLIENT_ID']
    tqa.client_key = config['TQA']['CLIENT_KEY']
    tqa.base_url = config['TQA']['BASE_URL']  # Assuming you need base_url for API calls
    tqa.set_tqa_token()

    if len(tqa.access_token) == 0:
        print("TQA Connection failed")
        return False
    else:
        print("TQA Connection Established: Access Token {}".format(tqa.access_token))
        return True

def read_spreadsheet(file_path):
    data = pd.read_excel(file_path)
    return data

def upload_ils_incident(site, reporter="", description="", occurred_date_time=-1, date_format=-1, gold_star=-1, custom_field=None):
    if custom_field is None:
        custom_field = {}

    if occurred_date_time != -1:
        if date_format != -1:
            dt_occ = datetime.datetime.strptime(occurred_date_time, date_format)
        else:
            dt_occ = parser.parse(occurred_date_time)
    else:
        dt_occ = datetime.datetime.now()

    incident_dt = dt_occ.strftime('%Y-%m-%d %H:%M')

    els_upload_data = {"site": str(site), "description": description, "reporterName": reporter, "occurred": incident_dt}

    if gold_star != -1:
        els_upload_data["goldStar"] = str(gold_star)

    if custom_field:
        els_upload_data["customFields"] = custom_field

    json_ils_data = json.dumps(els_upload_data)
    std_headers = tqa.get_standard_headers()
    url_process = ''.join([tqa.base_url, '/ils'])
    response = requests.post(url_process, headers=std_headers, data=json_ils_data)
    return response

def process_entries(file_path):
    data = read_spreadsheet(file_path)
    
    for index, row in data.iterrows():
        site = row['site']
        reporter = row['reporter']
        description = row['description']
        occurred_date_time = row['occurred_date_time'] if 'occurred_date_time' in row else -1
        date_format = row['date_format'] if 'date_format' in row else -1
        gold_star = row['gold_star'] if 'gold_star' in row else -1
        custom_field = row['custom_field'] if 'custom_field' in row else None
        
        response = upload_ils_incident(site, reporter, description, occurred_date_time, date_format, gold_star, custom_field)
        print(f"Upload response for row {index}: {response}")

if __name__ == '__main__':
    connection_success = connect_to_tqa()
    if not connection_success:
        sys.exit(3)

    # Use the FILE_PATH from your configuration file or use the following line directly.
    # file_path = "extracted.xlsx"
    
    process_entries(config['SPREADSHEET']['EXTRACTED_FILE_PATH'])  # Process the entire sheet.
