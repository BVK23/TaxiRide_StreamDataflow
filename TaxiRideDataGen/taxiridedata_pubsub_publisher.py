from google.cloud import pubsub_v1
from avro.io import DatumWriter, BinaryEncoder
from avro.schema import parse
from datetime import datetime, timedelta
import random
from faker import Faker
import time
import io

# Set up your GCP project and Pub/Sub topic
project_id = "taxiridestream"
topic_id = "ridesdata"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

fake = Faker()

# Load Avro schema
with open("ridedata_schema.avsc", "r") as file:
    schema_json = file.read()
schema = parse(schema_json)

# Create a writer for Avro
writer = DatumWriter(schema)
def generate_timestamp_within_last_n_minutes(n):
    now = datetime.now()
    timestamp = now - timedelta(minutes=random.randint(0, n))
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')


def generate_ride_data():
    estimated_time = random.randint(10, 60)  # Estimated ride duration in minutes
    actual_time = estimated_time + (random.randint(-5, 5))  # Actual ride duration can be less or more than estimated

    estimated_cost = round(random.uniform(10, 100), 2)  # Estimated cost in pounds
    actual_cost = estimated_cost + round(random.uniform(-5, 5), 2)
    ride_data = {
        "ride_id": fake.uuid4(),
        "timestamp": generate_timestamp_within_last_n_minutes(5),
        "driver_id": fake.uuid4(),
        "passenger_id": fake.uuid4(),
        "start_location": fake.address(),
        "end_location": fake.address(),
        "distance": round(random.uniform(1, 50), 1), 
        "estimated_time": estimated_time,  
        "actual_time": actual_time,
        "estimated_cost": estimated_cost,
        "actual_cost": actual_cost,
        "rating": round(random.uniform(1, 5), 1),  # Rating between 1 to 5
        "ride_type" : random.choice(['standard', 'premium', 'shared'])  # Types of rides
    }
    
    return ride_data

def serialize_avro(data):
    bytes_writer = io.BytesIO()
    encoder = BinaryEncoder(bytes_writer)
    writer.write(data, encoder)
    return bytes_writer.getvalue()

while True:
    ride_data = generate_ride_data()
    
    serialized_data = serialize_avro(ride_data)
    future = publisher.publish(topic_path, data=serialized_data)
    print(f"Published message ID {future.result()}")
    time.sleep(random.randint(1, 5))
