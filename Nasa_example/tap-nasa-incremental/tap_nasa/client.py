import requests
import singer
import urllib.parse

LOGGER = singer.get_logger()
API_PATH = '/rest/v1/'

class Client():

    def __init__(self, config):
        """get data from the config"""

        self._client_api_key = config.get('api_key')
        self._domain = config.get('domain')
        self._apiurl = config.get('domain') + API_PATH

    def _make_request(self, method, endpoint, params=None):
        """Make a request to the endpoint"""

        full_url = self._apiurl + endpoint
        LOGGER.info('%s - Making request to %s endpoint %s, with params %s',
                    full_url,
                    method.upper(),
                    endpoint,
                    params)

        params_str = urllib.parse.urlencode(params, safe=':+')

        resp = requests.request(method, full_url, params=params_str)
        
        response_data = resp.json()
        
        return response_data

    def get(self, endpoint, params=None):
        """Get the data by calling the _make_request()"""

        return self._make_request('GET', endpoint, params)