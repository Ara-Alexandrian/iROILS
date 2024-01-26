'''
Author: Ara Alexandrian
Date: September 28, 2023

This script demonstrates how to read and access values from a configuration file using the configparser module.

The script includes the following steps:

Initialize the ConfigParser object.
Read the config.ini file.
Access the value of the FILE_PATH key under the SPREADSHEET section of the configuration file.
Print the value of the FILE_PATH key.
Please note that the config.ini file should be in the same directory as the script, or you need to provide the correct path to the file.

The script also includes a note about the different file path formats when using an IPython notebook (config.ini) and a Python script (r'TQA/config.ini').

Please make sure to have the configparser module installed in order to run this script.
'''

import configparser

# Initialize the ConfigParser
config = configparser.ConfigParser()

try:
    # Read the config.ini file
    config.read(r'TQA/config.ini')
    # Access the spreadsheet path
    spreadsheet_path = config['SPREADSHEET']['FILE_PATH']
    print(spreadsheet_path)
except KeyError as e:
    print(f"The key {e} was not found in the configuration file.")



# when using ipynb, it likes the format 'config.ini'
# when using .py, it likes the format r'TQA/config.ini'
# lol