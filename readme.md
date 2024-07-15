
# Octopus Energy Data to InfluxDB
Pulls data from Octopus Energy API and sends to Influx per developer guide https://developer.octopus.energy/docs/api/#list-consumption-for-a-meter

### Environment Variables
| Settings | Description | Inputs |
| :----: | --- | --- |
| `CRON_MODE` | Allows the service to be run in a single pass cron mode rather than long lived | `False` |
| `LIVE_CONN` | Enables live lookups on website | `True` |
| `INFLUX_HOST` | InfluxDB host | `influx.test.local` |
| `INFLUX_HOST_PORT` | InfluxDB port  | `8086` |
| `INFLUX_DATABASE` | InfluxDB databse  | `test` |
| `RUNMINS` | Run every x mins | `20` |
| `APIKEY` | API key issued by Octopus | `SOMEAPIKEY` |
| `ELECMPAN` | Electric meter MPAN | `123456789` |
| `ELECSERIAL` | Electric meter serial | `123456789` |
| `GASMPAN` | Gas meter MPAN | `123456789` |
| `GASSERIAL` | Gas meter serial | `123456789` |


### Requirements
```sh
pip install -p requirements.txt
```

### Execution 
```sh
python3 .\main.py
```

### Docker Compose
```sh 
  octopus2influx:
    image: ghcr.io/stuartgraham/octopus2influx:latest
    restart: always
    container_name: octopus2influx
    environment:
      - LIVE_CONN=True
      - INFLUX_HOST=influx.test.local
      - INFLUX_HOST_PORT=8086
      - INFLUX_DATABASE=energy
      - APIKEY=SOMEKEY
      - ELECMPAN=123456789
      - ELECSERIAL=123456789
      - GASMPAN=123456789
      - GASSERIAL=123456789
      - RUNMINS=20
```