## Taxi Ride: Real-Time Data Streaming and Analysis

**In today's transportation landscape, data is pivotal for optimizing and tailoring travel experiences. In this project, I envisioned a system that could leverage the power of real-time data streaming to optimize taxi rides.**

**Every taxi ride generates a plethora of data points - from start and end locations to time taken, ride cost, and customer feedback. While this data holds immense value, its vastness and lack of structure present challenges. Traditional batch processing techniques often fall short, unable to match the dynamic nature of the data and the immediacy of insights it promises.**

> 🏗️ **This hypothetical end-to-end streaming data pipeline solution can ingest, process, and analyze taxi ride data in real-time. This offers the potential to instantly monitor and optimize various facets of the business, including dynamic pricing.**

**Here's how the project was executed:**

### Source Data : Avro, Pub/Sub

To mimic real-world taxi ride data, I employed a Python script that simulates and streams ride information in real-time to a Pub/Sub topic.

Utilizing the **`Faker`** library, I generated attributes like driver and passenger IDs, as well as start and end locations. Other key metrics such as estimated and actual ride times, costs, ratings, and ride types were also simulated, creating a dataset that effectively captures the nuances of an actual **taxi booking system**.

For optimized data transmission and processing, I utilized the **Avro** framework over traditional JSON formats. The Avro format not only assures data compactness. This choice was strategic: Avro's efficiency makes it a more cost-effective solution in terms of resources, especially when deploying the system at a large scale.

Consequently, the serialized ride data is channeled to a **Google Cloud Pub/Sub topic**. This ensures that we simulate a live stream of taxi ride data, providing a real-time data generation and broadcasting experience.

[Checkout the code](https://github.com/BVK23/TaxiRide_StreamDataflow/blob/main/TaxiRideDataGen/taxiridedata_pubsub_publisher.py)

![Screenshot of GCP Pub/Sub Topic ‘ridesdata’](images/Screenshot_of_GCP_Pub_Sub_Topic)

**Screenshot of GCP Pub/Sub Topic ‘ridesdata’**

### Stream Processing : GCP Dataflow, Apache Beam, Big Query, Pub/Sub

> At the heart of this project lies real-time stream processing. Harnessing the might of Google Cloud Platform (GCP) tools coupled with Apache Beam, I targeted two main objectives:
> 

### 1. **Real-time Data Warehousing (ETL)**

> Taxi ride data, originating from our Pub/Sub topic, is channeled into a GCP Dataflow pipeline. With Apache Beam's capabilities, this pipeline efficiently filters, transforms, and loads data directly into Big Query - GCP's data warehouse.
> 

This live integration into Big Query empowers analysts to extract instant insights, enabling on-the-fly data-driven decisions. While the concept of daily batch pipelines was considered, continuous streaming proved more cost-efficient and agile solution.

