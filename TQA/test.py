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


