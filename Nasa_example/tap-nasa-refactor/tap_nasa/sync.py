import singer
from singer import Transformer, metadata
from tap_nasa.streams import Stream

LOGGER = singer.get_logger()

global stream_data
   
def do_sync(client, config, state, catalog):
    selected_streams = list(catalog.get_selected_streams(state))

    for stream in selected_streams:
        stream_id = stream.tap_stream_id
        stream_schema = stream.schema

        stream_object = Stream(client, config, stream)

        singer.write_schema(
            stream_id,
            stream_schema.to_dict(),
            stream_object.key_properties,
            stream_object.replication_key,
        )
        
        LOGGER.info('Syncing stream: %s', stream_id)


        with Transformer() as transformer:
            stream_records = []
            transformed_stream_records = []

            for rec in stream_object.sync():

                tranformed_rec = transformer.transform(
                                    rec, stream.schema.to_dict(), metadata.to_map(stream.metadata),
                                )
                stream_records.append(rec)
                transformed_stream_records.append(tranformed_rec)

                for entry in transformed_stream_records:
                    singer.write_record(
                        stream_id,
                        entry
                    )