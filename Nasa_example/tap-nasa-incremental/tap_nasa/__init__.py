import singer
from singer.catalog import Catalog
from tap_nasa.sync import do_sync
from tap_nasa.client import Client

def main():
    # define required config file keys
    required_config_keys = ['api_key', 'domain']
    
    # check if required keys are in the config file
    args = singer.parse_args(required_config_keys)

    # get the input
    config = args.config
    catalog = args.catalog or Catalog([])
    state = args.state
    
    # instatiate the client
    client = Client(config)

    do_sync(client, config, state, catalog)

if __name__ == '__main__':
    main()