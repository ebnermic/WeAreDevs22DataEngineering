import singer
import urllib.request
import json

LOGGER = singer.get_logger()

# define schema
schema = {
    'properties':   {
        'id': {'type': 'string'},
        'name': {'type': 'string'},
    },
}

with urllib.request.urlopen('https://api.nasa.gov/neo/rest/v1/neo/browse?api_key=DEMO_KEY') as response:
    nasa_neo = response.read().decode('utf-8').strip()
    nasa_neo_json = json.loads(nasa_neo)
    for near_earth_object in nasa_neo_json['near_earth_objects']:
        singer.write_schema('nasa_neo', schema, 'id')
        singer.write_records('nasa_neo', [{'id': near_earth_object.get('id'), 'name': near_earth_object.get('name')}])