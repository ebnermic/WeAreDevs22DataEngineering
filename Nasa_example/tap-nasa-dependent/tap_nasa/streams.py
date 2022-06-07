class Stream:

    def __init__(self, client, config, stream):
        self.client = client
        self.config = config

        self.api_key = config.get('api_key')

        self.key_properties = stream.key_properties
        self.replication_key = stream.replication_key
        metadata_json_object = stream.metadata[0]
        self.endpoint = metadata_json_object.get('endpoint')

        # Variables for streams depending on others
        self.dependencie = None
        if 'dependencie' in metadata_json_object:
            self.dependencie = metadata_json_object.get('dependencie')
        self.dependencie_key = None
        if 'dependencie_key' in metadata_json_object:
            self.dependencie_key = metadata_json_object.get('dependencie_key')

    def sync(self):
        if self.dependencie != None:
            for rec in self.get_records_with_dependencie():
                yield rec

        else:
            for rec in self.get_records_without_dependencie():
                yield rec
        

    def get_records_without_dependencie(self):
        page = 0

        while True:

            records = self.client.get(self.endpoint, 
                                        params={'api_key': self.api_key,
                                                'page': str(page)})

            near_earth_objects = records.get('near_earth_objects')
            
            for near_earth_object in near_earth_objects:
                yield near_earth_object
            
            if not 'next' in records.get('links') or page >= 5:
                break
            
            page += 1
        
        # return records

    def get_records_with_dependencie(self):
        records = []

        for entry in self.dependencie_values:
            entry_id = entry[self.dependencie_key]
            format_values = [entry_id]

            json_data = self.client.get(self.format_endpoint(format_values),
                                        params={'api_key': self.api_key})

            records.append(json_data)

        return records

    def format_endpoint(self, format_values):
        return self.endpoint.format(*format_values)