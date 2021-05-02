import http.client
import json
import time
from datetime import datetime, timedelta
import os
import requests
from requests.auth import HTTPBasicAuth 
from influxdb import InfluxDBClient
import schedule
from pprint import pprint

# .ENV FILE FOR TESTING
# if os.path.exists('.env'):
#     from dotenv import load_dotenv
#     load_dotenv()

# GLOBALS
LIVE_CONN = bool(os.environ['LIVE_CONN'])
INFLUX_HOST = os.environ['INFLUX_HOST']
INFLUX_HOST_PORT = int(os.environ['INFLUX_HOST_PORT'])
INFLUX_DATABASE = os.environ['INFLUX_DATABASE']
APIKEY = os.environ['APIKEY']
ELECMPAN = os.environ['ELECMPAN']
ELECSERIAL = os.environ['ELECSERIAL']
GASMPAN = os.environ['GASMPAN']
GASSERIAL = os.environ['GASSERIAL']
RUNMINS =  int(os.environ['RUNMINS'])

JSON_OUTPUT = 'output.json'

INFLUX_CLIENT = InfluxDBClient(host=INFLUX_HOST, port=INFLUX_HOST_PORT, database=INFLUX_DATABASE)

def construct_url(*args):
    if args[0] == 'electricty':
        url = f'https://api.octopus.energy/v1/electricity-meter-points/{ELECMPAN}/meters/{ELECSERIAL}/consumption/'
    if args[0] == 'gas':
        url = f'https://api.octopus.energy/v1/gas-meter-points/{GASMPAN}/meters/{GASSERIAL}/consumption/'
    return url

# Get json data
def get_json(*args): 
    resp = requests.get(args[0], auth = HTTPBasicAuth(APIKEY,''))
    payload_data = resp.json()
    with open(JSON_OUTPUT, 'w') as outfile:
        json.dump(payload_data, outfile)

def get_saved_data(*args):
    if LIVE_CONN == True:
        get_json(args[0])

    with open(JSON_OUTPUT) as json_file:
        working_data = json.load(json_file)
    return working_data

def write_to_influx(data_payload):
    INFLUX_CLIENT.write_points(data_payload)
    pass    

def sort_json(working_data, energy_type):
    if energy_type == 'electricty':
        unit_type = 'kWh'
    if energy_type == 'gas':
        unit_type = 'm3'
    
    for result in working_data['results']:
        print(result['consumption'])
        print(result['interval_end'])
        base_dict = {'measurement' : energy_type, 'tags' : {'name': energy_type}}
        base_dict.update({'time': result['interval_end']})
        fields_data = {unit_type : float(result['consumption'])}
        base_dict.update({'fields' : fields_data})
        data_payload = [base_dict]
        print("SUBMIT:" + str(data_payload))
        print('#'*30)
        write_to_influx(data_payload)


def do_it(*args):
    url = construct_url('electricty')
    working_data = get_saved_data(url)
    sort_json(working_data, 'electricty')

    url = construct_url('gas')
    working_data = get_saved_data(url)
    sort_json(working_data, 'gas')


def main():
    ''' Main entry point of the app '''
    do_it()
    schedule.every(RUNMINS).minutes.do(do_it)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    ''' This is executed when run from the command line '''
    main()