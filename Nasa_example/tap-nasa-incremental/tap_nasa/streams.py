import singer
from datetime import timedelta

LOGGER = singer.get_logger()

class Stream:

    def __init__(self, client, config, state, stream):
        self.client = client
        self.config = config
        self.state = state

        self.api_key = config.get('api_key')

        self.key_properties = stream.key_properties
        self.replication_key = stream.replication_key

        metadata_json_object = stream.metadata[0]
        self.endpoint = metadata_json_object.get('endpoint')
        self.stream_id = metadata_json_object.get('stream_id')

        # Variables for streams depending on others
        self.dependencie = None
        if 'dependencie' in metadata_json_object:
            self.dependencie = metadata_json_object.get('dependencie')
        self.dependencie_key = None
        if 'dependencie_key' in metadata_json_object:
            self.dependencie_key = metadata_json_object.get('dependencie_key')

    def sync(self):
        for rec in self.get_records():
            yield rec

    def format_endpoint(self, format_values):
        return self.endpoint.format(*format_values)

class FullTableStream(Stream):
    """Class for full table stream sync"""

    def get_records(self):
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

    def get_records_with_dependencie(self):
        records = []

        for entry in self.dependencie_values:
            entry_id = entry[self.dependencie_key]
            format_values = [entry_id]

            json_data = self.client.get(self.format_endpoint(format_values),
                                        params={'api_key': self.api_key})

            records.append(json_data)

        return records

class IncrementalStream(Stream):
    """Class for incremental stream - streams which do not sync full table but only a part"""

    def get_window_state(self):
        """get date window according from config.json and/or state.json"""

        # Get start and end from state
        window_start = singer.get_bookmark(self.state, self.stream_id, 'last_record')
        window_end = singer.get_bookmark(self.state, self.stream_id, 'window_end')

        end_date = singer.utils.strftime(singer.utils.now(), '%Y-%m-%d')

        window_start = singer.utils.strptime_to_utc(window_start)
        window_end = singer.utils.strptime_to_utc(min(window_end, end_date))

        return window_start, window_end

    def on_window_started(self):
        """fill missing bookmarks with now()"""

        if singer.get_bookmark(self.state, self.stream_id, 'last_record') is None:
            singer.write_bookmark(self.state, self.stream_id, 'last_record', self.config.get('start_date'))
        if singer.get_bookmark(self.state, self.stream_id, 'window_end') is None:
            now = singer.utils.strftime(singer.utils.now(), '%Y-%m-%d')
            singer.write_bookmark(self.state, self.stream_id, 'window_end', now)
        singer.write_state(self.state)

    def on_window_finished(self):
        """update bookmark for end state.json"""

        window_start = singer.get_bookmark(self.state, self.stream_id, 'window_end')
        singer.write_bookmark(self.state, self.stream_id, 'last_record', window_start)
        singer.clear_bookmark(self.state, self.stream_id, 'window_end')
        singer.write_state(self.state)

    def get_records(self):
        window_start, window_end = self.get_window_state()
        
        for rec in self.get_records_by_time_window(window_start, window_end):
            yield rec

    def update_bookmark(self, key, value):
        singer.bookmarks.write_bookmark(self.state, self.stream_id, key, singer.utils.strftime(value, '%Y-%m-%d'))

    def get_records_by_time_window(self, window_start, window_end):
        """Get data between start and end window"""

        sub_window_end = window_start

        while True:

            records = self.client.get(self.endpoint,
                                      params={'start_date': singer.utils.strftime(window_start, '%Y-%m-%d'),
                                              'end_date': singer.utils.strftime(sub_window_end, '%Y-%m-%d'),
                                              'api_key': self.api_key})

            near_earth_objects = records.get('near_earth_objects')

            for near_earth_object in near_earth_objects.get(singer.utils.strftime(window_start, '%Y-%m-%d')):
                yield near_earth_object

            if 'next' in records.get('links') and sub_window_end + timedelta(days=1) <= window_end:
                window_start = window_start + timedelta(days=1)
                sub_window_end = sub_window_end + timedelta(days=1)

                self.update_bookmark('sub_window_end', sub_window_end)
                singer.write_state(self.state)
            else:
                singer.bookmarks.clear_bookmark(self.state, self.stream_id,'sub_window_end')
                break
    
    def sync(self):
        """Redefined method due to date windows"""

        self.on_window_started()
        for rec in self.get_records():
            yield rec
        self.on_window_finished()