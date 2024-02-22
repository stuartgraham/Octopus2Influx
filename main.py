import json
import time
from datetime import datetime, timedelta
import os
import requests
from requests.auth import HTTPBasicAuth 
from icecream import ic
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import WriteOptions
import schedule
from pprint import pprint

# GLOBALS
INFLUX_VERSION = int(os.environ.get("INFLUX_VERSION", 2))
LIVE_CONN = bool(os.environ['LIVE_CONN'])
INFLUX_HOST = os.environ['INFLUX_HOST']
INFLUX_HOST_PORT = int(os.environ['INFLUX_HOST_PORT'])
INFLUX_DATABASE = os.environ['INFLUX_DATABASE']
INFLUX_BUCKET = os.environ.get("INFLUX_BUCKET", "")
INFLUX_TOKEN = os.environ.get("INFLUX_TOKEN", "")
INFLUX_ORG = os.environ.get("INFLUX_ORG", "-")
APIKEY = os.environ['APIKEY']
ELECMPAN = os.environ['ELECMPAN']
ELECSERIAL = os.environ['ELECSERIAL']
GASMPAN = os.environ['GASMPAN']
GASSERIAL = os.environ['GASSERIAL']
RUNMINS =  int(os.environ['RUNMINS'])
LOGGING = bool(os.environ.get("LOGGING", False))

JSON_OUTPUT = 'output.json'

# Logging
if not LOGGING:
    ic.disable()

# Creates a bucket for backward compat
if INFLUX_VERSION == 1:
    INFLUX_BUCKET = f"{INFLUX_DATABASE}/autogen"

# Set up batch write options
BATCH_WRITE_OPTIONS = WriteOptions(batch_size=500, flush_interval=10_000, jitter_interval=2_000, retry_interval=5_000)

# Instantiate Influx Client
INFLUX_CLIENT = InfluxDBClient(
    url=f"http://{INFLUX_HOST}:{INFLUX_HOST_PORT}", org=INFLUX_ORG, token=INFLUX_TOKEN
    )
INFLUX_WRITE_API = INFLUX_CLIENT.write_api(write_options=BATCH_WRITE_OPTIONS)

JSON_OUTPUT = "output.json"

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
    response = INFLUX_WRITE_API.write(INFLUX_BUCKET, INFLUX_ORG, data_payload)
    success = response is None  # In InfluxDB 2.x, a successful write returns None
    ic(success)

    if success:
        data_points = len(data_payload)
        ic(data_points)
        print(f"SUCCESS: {data_points} data points written to InfluxDB")
    else:
        print(f"ERROR: Error writing to InfluxDB: {response}")

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