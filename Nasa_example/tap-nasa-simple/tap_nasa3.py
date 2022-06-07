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

# define required config file keys
required_config_keys = ['api_key']

# check if required keys are in the config file
args = singer.parse_args(required_config_keys)

config = args.config
api_key = config.get('api_key')

page = 0

while True:
    url = 'https://api.nasa.gov/neo/rest/v1/neo/browse?api_key=' + str(api_key) + '&page=' + str(page)

    with urllib.request.urlopen(url) as response:
        nasa_neo = response.read().decode('utf-8').strip()
        # LOGGER.fatal('Response: %s', str(nasa_neo))
        nasa_neo_json = json.loads(nasa_neo)
        
        for near_earth_object in nasa_neo_json.get('near_earth_objects'):
            singer.write_schema('nasa_neo', schema, 'id')
            singer.write_records('nasa_neo', [{'id': near_earth_object.get('id'), 'name': near_earth_object.get('name')}])

        if not 'next' in nasa_neo_json.get('links'):
            break
    
    page += 1