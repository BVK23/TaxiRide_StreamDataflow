import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.io import ReadFromPubSub, WriteToPubSub
import logging
import json

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

class CheckSurgeAndPublishToPubSub(beam.DoFn):

    BASE_COUNT = 90  #Base Threshold
    STEP_SIZE = 20  # every increase of 10 rides increase surge
    SURGE_INCREMENT = 0.2  # for every step size, how much to increase the surge factor
    MAX_SURGE_FACTOR = 3  # maximum allowed surge factor

    def process(self, element, window=beam.DoFn.WindowParam):
        count = element
        window_start = window.start.to_utc_datetime().strftime('%Y-%m-%d %H:%M:%S')

        # Calculate steps over BASE_COUNT
        steps_over_base = max(0, count - self.BASE_COUNT) // self.STEP_SIZE

        # Calculate surge factor
        surge_factor = 1 + steps_over_base * self.SURGE_INCREMENT
        surge_factor = min(surge_factor, self.MAX_SURGE_FACTOR)  # Cap at max surge factor
        surge_factor = max(1, surge_factor)  # Ensure minimum surge factor is 1

        result = {
            'timestamp': str(window_start),
            'surge_factor': surge_factor
        }
 
        yield result


def main(subscription_path):
   
    
    options = PipelineOptions(
    runner='DataflowRunner',
    project='taxiridestream',
    staging_location='gs://streamproj/stage_fold', 
    temp_location='gs://streamproj/temp_fold',
    Region='europe-southwest1',    
    streaming=True,
    )

    

    with beam.Pipeline(options=options) as p:

            # Step 1: Read from Pub/Sub
            rides = (p 
                    | 'Read from PubSub' >> ReadFromPubSub(subscription=subscription_path)
                    | 'Deserialize from Avro' >> beam.ParDo(ParseAvroDoFn()))

            # # 2. Windowing
            windowed_rides = rides | "Window into Fixed Intervals" >> beam.WindowInto(beam.window.SlidingWindows(size=5*60, period=1*60))

            
            # 3. Transformation
            extracted_data = (   windowed_rides 
                | "Count Rides" >> beam.combiners.Count.Globally().without_defaults()
                | "Extract Timestamp and Window Start" >> beam.ParDo(CheckSurgeAndPublishToPubSub())
                | 'Serialize to JSON' >> beam.Map(lambda elem: json.dumps(elem).encode('utf-8'))  
                | 'Write to Pub/Sub' >> WriteToPubSub(topic='projects/taxiridestream/topics/surge_data')
                )

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--subscription_path', required=True, help='Subscription path for Pub/Sub')
    known_args, pipeline_args = parser.parse_known_args()
    main(subscription_path=known_args.subscription_path)