## Taxi Ride: Real-Time Data Streaming and Analysis

**In today's transportation landscape, data is pivotal for optimizing and tailoring travel experiences. In this project, I envisioned a system that your team could harness to leverage the power of real-time data streaming to optimize taxi rides.**

**Every taxi ride generates a plethora of data points - from start and end locations to time taken, ride cost, and customer feedback. While this data holds immense value, its vastness and lack of structure present challenges. Traditional batch processing techniques often fall short, unable to match the dynamic nature of the data and the immediacy of insights it promises.**

> 🏗️ **This hypothetical end-to-end streaming data pipeline solution can ingest, process, and analyze taxi ride data in real-time. This offers the potential to instantly monitor and optimize various facets of the business, including dynamic pricing.**

**Here's how the project was executed:(expand the drop downs)**

### Source Data : Avro, Pub/Sub

To mimic real-world taxi ride data, I employed a Python script that simulates and streams ride information in real-time to a Pub/Sub topic.

Utilizing the **`Faker`** library, I generated attributes like driver and passenger IDs, as well as start and end locations. Other key metrics such as estimated and actual ride times, costs, ratings, and ride types were also simulated, creating a dataset that effectively captures the nuances of an actual **taxi booking system**.

For optimized data transmission and processing, I utilized the **Avro** framework over traditional JSON formats. The Avro format not only assures data compactness. This choice was strategic: Avro's efficiency makes it a more cost-effective solution in terms of resources, especially when deploying the system at a large scale.

Consequently, the serialized ride data is channeled to a **Google Cloud Pub/Sub topic**. This ensures that we simulate a live stream of taxi ride data, providing a real-time data generation and broadcasting experience.

Here's a snapshot of the code:

![Code Snapshot](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/ec0c817e-979d-4f04-b300-3e885bba7a65/Untitled.png)

[Link to full code ⬇️](https://github.com/BVK23/TaxiRide_StreamDataflow/blob/main/TaxiRideDataGen/taxiridedata_pubsub_publisher.py)

![Screenshot of GCP Pub/Sub Topic ‘ridesdata’](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/07e83f9f-d37d-44f0-b39c-feab56a5f2bd/Untitled.png)

**Screenshot of GCP Pub/Sub Topic ‘ridesdata’**

### Stream Processing : GCP Dataflow, Apache Beam, Big Query, Pub/Sub

