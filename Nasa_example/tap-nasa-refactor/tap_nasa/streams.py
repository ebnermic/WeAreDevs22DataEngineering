class Stream:

    def __init__(self, client, config, stream):
        self.client = client
        self.config = config

        self.api_key = config.get('api_key')

        self.key_properties = stream.key_properties
        self.replication_key = stream.replication_key
        metadata_json_object = stream.metadata[0]
        self.endpoint = metadata_json_object.get('endpoint')

    def sync(self):
        page = 0

        while True:

            records = self.client.get(self.endpoint, 
                                        params={'api_key': self.api_key,
                                                'page': str(page)})

            near_earth_objects = records.get('near_earth_objects')
            
            for near_earth_object in near_earth_objects:
                    yield near_earth_object
            
            # page >= 5 to test
            if not 'next' in records.get('links') or page >= 3:
                break
            
            page += 1