from pyTQA import tqa
import sys
import json
import requests
import datetime
from dateutil import parser


def connect_to_tqa():
    # tqa.load_json_credentials("my_credentials.json")
    # fill with your key
    tqa.client_id = '209:iROILS'
    tqa.client_key = '3d5b914a45d02ea532a6b7bd53dbee7c9751de81beff8df2cb1973cfef218cbc'
    tqa.set_tqa_token()
    # tqa.save_json_credentials("my_credentials.json")

    if len(tqa.access_token) == 0:
        print("TQA Connection failed")
        return False
    else:
        print("TQA Connection Established: Access Token {}".format(tqa.access_token))
        return True


def upload_ils_incident(site, reporter="", description="", occurred_date_time=-1, date_format=-1, gold_star=-1,
                        custom_field=None):
    if custom_field is None:
        custom_field = {}

    if occurred_date_time != -1:
        if date_format != -1:
            dt_occ = datetime.datetime.strptime(occurred_date_time, date_format)
        else:
            # no format specified
            dt_occ = parser.parse(occurred_date_time)
    else:
        # no date specified, default to current date and time
        dt_occ = datetime.datetime.now()

    incident_dt = dt_occ.strftime('%Y-%m-%d %H:%M')

    ils_upload_data = {"site": str(site), "description": description, "reporterName": reporter,
                       "occurred": incident_dt}

    if gold_star != -1:
        ils_upload_data["goldStar"] = str(gold_star)

    if custom_field:
        ils_upload_data["customFields"] = custom_field

    json_ils_data = json.dumps(ils_upload_data)
    std_headers = tqa.get_standard_headers()
    url_process = ''.join([tqa.base_url, '/ils'])
    response = requests.post(url_process, headers=std_headers, data=json_ils_data)
    return response


def get_machine_id(machine_name):
    idx = tqa.get_machine_id_from_str(machine_name)
    print("Machine Name: {} ".format(machine_name) + " (ID: {})".format(str(idx)))
    return idx


def get_schedule_id(schedule_name, machine_idx):
    idx = tqa.get_schedule_id_from_string(schedule_name, machine_idx)
    print("Schedule Name: {}".format(schedule_name) + " (ID: {})".format(str(idx)))
    return idx


def get_variable_id(var_name, schedule_id):
    idx = tqa.get_variable_id_from_string(var_name, schedule_id)
    print("Variable Name: {}".format(var_name) + " (ID: {})".format(str(idx)))
    return idx


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    connection_success = connect_to_tqa()
    if not connection_success:
        sys.exit(3)

    categories = tqa.get_request('/ils-categories')
    print(categories)

    hazards = tqa.get_request('/ils-hazards')
    print(hazards)

    custom_fields = tqa.get_request('/ils-custom-fields')
    print(json.dumps(custom_fields["json"], indent=4, sort_keys=True))

    # dumps all the incidents
    # ils_incidents = tqa.get_request('/ils')
    # print(json.dumps(ils_incidents["json"], indent=4, sort_keys=True))

    ils_incidents_filtered = tqa.get_request('/ils?site=265&reporterName=Matt')
    print(json.dumps(ils_incidents_filtered["json"], indent=4, sort_keys=True))

    upload_response = upload_ils_incident(site=265, description="a report of something", reporter="Matt")
    print(upload_response)

    # # fill in with yours
    # machine = "L2023_1"
    # schedule = "Upload Demo"
    #
    # # get the machine's id number
    # machine_id = get_machine_id(machine)
    #
    # # get the schedule's id number
    # schedule_id = get_schedule_id(schedule, machine_id)
    #
    # # # schedule variables
    # schedule_var = tqa.get_schedule_variables(schedule_id)
    # print(json.dumps(schedule_var["json"], indent=4, sort_keys=True))
    #
    # numeric_test_id = 34491
    # numeric_test_value = 42
    # meta_item_id = 11480
    # meta_item_value = "meta Meta"
    # file_attachment_test_id = 34492
    # file_to_attach = 'taos 2019.png'
    # file_value = tqa.encode_file_attachment_for_upload(file_to_attach)
    #
    # upload_data = [{'id': numeric_test_id, 'value': numeric_test_value,
    #                 'metaItems': [{'id': meta_item_id, 'value': meta_item_value}]},
    #                {'id': file_attachment_test_id, 'value': file_value, 'filename': file_to_attach}]
    #
    # response = tqa.upload_test_results(schedule_id, upload_data, finalize=1)
    # print(response)