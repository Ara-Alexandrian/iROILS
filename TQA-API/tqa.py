'''
Author: Ara Alexandrian
Date: September 28, 2023

This script demonstrates how to connect to TQA (Threat and Vulnerability Assessment) using the pyTQA library, read data from a spreadsheet using pandas, and upload incidents to TQA using the TQA API.

The script includes the following functions:

connect_to_tqa: Connects to TQA using the configuration values from the config.ini file.
read_spreadsheet: Reads data from a spreadsheet using pandas.
upload_ils_incident: Uploads an ILS (Incident Logging System) incident to TQA using the TQA API.
process_entries: Processes entries from a spreadsheet and uploads incidents to TQA.
To use this script, you need to have the pyTQA, pandas, requests, datetime, configparser, and dateutil modules installed. You also need to provide the necessary configuration values in the config.ini file.

The script demonstrates an example usage where it connects to TQA, reads data from a spreadsheet, and uploads incidents to TQA based on the data in the spreadsheet. You can choose to process the entire sheet or a specific range of rows by uncommenting the appropriate line in the __main__ block.

Please make sure to replace the placeholder values in the config.ini file with your actual TQA configuration values and adjust the code according to your specific needs.
'''

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

    ils_upload_data = {"site": str(site), "description": description, "reporterName": reporter, "occurred": incident_dt}

    if gold_star != -1:
        ils_upload_data["goldStar"] = str(gold_star)

    if custom_field:
        ils_upload_data["customFields"] = custom_field

    json_ils_data = json.dumps(ils_upload_data)
    std_headers = tqa.get_standard_headers()
    url_process = ''.join([tqa.base_url, '/ils'])
    response = requests.post(url_process, headers=std_headers, data=json_ils_data)
    return response

def process_entries(file_path, start_row=None, end_row=None):
    data = read_spreadsheet(file_path)
    
    if start_row is None and end_row is None:
        entries_to_process = data
    else:
        entries_to_process = data.loc[start_row:end_row-1 if end_row is not None else None]
    
    for index, row in entries_to_process.iterrows():
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

    # Use the FILE_PATH from your configuration file
    file_path = config['SPREADSHEET']['FILE_PATH']
    
    # Uncomment one of the below lines depending on the requirement:
    # process_entries(file_path)  # Process the entire sheet.
    # process_entries(file_path, start_row=5, end_row=10)  # Process a specific range.
    # process_entries(file_path, start_row=7)  # Process from a specific row to the end.
