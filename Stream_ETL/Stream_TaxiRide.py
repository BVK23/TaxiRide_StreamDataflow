import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.io.gcp.bigquery import WriteToBigQuery, BigQueryDisposition
from apache_beam.io import ReadFromPubSub
import logging



class ParseAvroDoFn(beam.DoFn):
    def __init__(self):
        self.schema_str = """
        {
            "type": "record",
            "name": "RideData",
            "fields" : [
            {"name": "ride_id", "type": "string"},
            {"name": "timestamp", "type": "string"},
            {"name": "driver_id", "type": "string"},
            {"name": "passenger_id", "type": "string"},
            {"name": "start_location", "type": "string"},
            {"name": "end_location", "type": "string"},
            {"name": "distance", "type": "float"},
            {"name": "estimated_time", "type": "int"},
            {"name": "actual_time", "type": "int"},
            {"name": "estimated_cost", "type": "float"},
            {"name": "actual_cost", "type": "float"},
            {"name": "rating", "type": "float"},
            {"name": "ride_type", "type": "string"}
        ]
        }
    """
       
    def process(self, element):
        import avro
        from avro.io import BinaryDecoder
        import io
        from avro.schema import parse
        from avro.io import DatumReader  

        schema = parse(self.schema_str)
        reader = DatumReader(schema)
        bytes_reader = io.BytesIO(element)
        decoder = BinaryDecoder(bytes_reader)
        try:
            decoded_data = reader.read(decoder)
        except Exception as e:
            # Here you can log the error and potentially the data that caused it
            logging.error(f"Failed to decode Avro record: {e}")
            return []

        return [decoded_data]

class CalculateMetricsDoFn(beam.DoFn):
    def process(self, element):
        # Here we can calculate any metrics we want on our data, for example:
        time_difference = element['actual_time'] - element['estimated_time']
        cost_difference = element['actual_cost'] - element['estimated_cost']

        # Add the calculated metrics back to the dictionary
        element['time_difference'] = time_difference
        element['cost_difference'] = cost_difference

        return [element]

def main(subscription_path):
    table_schema = {
    'fields': [
        {'name': 'ride_id', 'type': 'STRING'},
        {'name': 'timestamp', 'type': 'TIMESTAMP'},
        {'name': 'driver_id', 'type': 'STRING'},
        {'name': 'passenger_id', 'type': 'STRING'},
        {'name': 'start_location', 'type': 'STRING'},
        {'name': 'end_location', 'type': 'STRING'},
        {'name': 'distance', 'type': 'FLOAT'},
        {'name': 'estimated_time', 'type': 'INTEGER'},
        {'name': 'actual_time', 'type': 'INTEGER'},
        {'name': 'estimated_cost', 'type': 'FLOAT'},
        {'name': 'actual_cost', 'type': 'FLOAT'},
        {'name': 'rating', 'type': 'FLOAT'},
        {'name': 'ride_type', 'type': 'STRING'},
        {'name': 'time_difference', 'type': 'INTEGER'},
        {'name': 'cost_difference', 'type': 'FLOAT'}
    ]
    }

    
    options = PipelineOptions(
    runner='DataflowRunner',
    project='taxiridestream',
    staging_location='gs://streamproj/stage_fold', 
    temp_location='gs://streamproj/temp_fold',
    Region='europe-southwest1',    
    streaming=True,
    )

    with beam.Pipeline(options=options) as p:
            rides = (
                p 
                | 'Read from PubSub' >> ReadFromPubSub(subscription=subscription_path)
                | 'Deserialize from Avro' >> beam.ParDo(ParseAvroDoFn())
            )

            processed_rides = rides | 'Calculate Metrics' >> beam.ParDo(CalculateMetricsDoFn())

            result = (
                processed_rides 
                | 'Write to BigQuery' >> WriteToBigQuery(
                    "taxiridestream:ridedataset.rides",
                    schema=table_schema, 
                    write_disposition=BigQueryDisposition.WRITE_APPEND,
                    create_disposition=BigQueryDisposition.CREATE_IF_NEEDED)
             )
            
        
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--subscription_path', required=True, help='Subscription path for Pub/Sub')
    known_args, pipeline_args = parser.parse_known_args()
    main(subscription_path=known_args.subscription_path)