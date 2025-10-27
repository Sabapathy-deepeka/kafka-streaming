# Kafka Stock Market Stream (Producer + Consumer)

This repository contains a simple Kafka producer and consumer pair implemented in Python:

- Producer: reads a CSV file (`stock-trading-data.csv`), samples rows, and streams them to a Kafka topic (`data_real_time_stream`).
- Consumer: consumes messages from the same Kafka topic and writes each message to an S3 bucket as a JSON file.

The code is intended as a minimal example for streaming CSV data into Kafka and persisting consumed messages to S3.

## Contents

- producer_consumer_example.py — example producer and consumer (combined in one file in the snippet you provided)
- stock-trading-data.csv — example CSV used by the producer (place your CSV here)
- README.md — this file

## Prerequisites

- Python 3.8+
- A running Kafka broker accessible from where you run the producer/consumer
- AWS credentials configured (for writing to S3) — see "S3 credentials" below
- Recommended Python packages:
  - pandas
  - kafka-python
  - s3fs
  - boto3 (used implicitly by s3fs for many setups)
- Network access: allow connections to the Kafka broker's host:port

Install dependencies:

```bash
python -m pip install pandas kafka-python s3fs boto3
```

## Producer

Behavior:
- Connects to Kafka broker(s) defined in `bootstrap_servers`.
- Serializes Python dict values to JSON (utf-8) using `dumps`.
- Sends an initial static message:
  {'firstName': 'Deepeka', 'lastName': 'Sabapathy', 'age': 26}
- Loads `stock-trading-data.csv` into a pandas DataFrame and repeatedly samples a random row every second, sending it to the `data_real_time_stream` topic.

Key snippet (from your code):

```python
producer = KafkaProducer(
    bootstrap_servers=['3.137.155.232:9092'],
    value_serializer=lambda x: dumps(x).encode('utf-8')
)

producer.send('data_real_time_stream', value={'firstName':'Deepeka', 'lastName':'Sabapathy', 'age':26})

df = pd.read_csv("stock-trading-data.csv")

while True:
    dict_stock = df.sample(1).to_dict(orient="records")[0]
    producer.send('data_real_time_stream', value=dict_stock)
    sleep(1)
```

Notes:
- Change `3.137.155.232:9092` to your Kafka broker IP/hostname and port.
- The `sleep(1)` controls message rate — adjust as needed.
- Consider calling `producer.flush()` and `producer.close()` on shutdown.

## Consumer

Behavior:
- Connects to the same Kafka broker and topic.
- Deserializes JSON message values.
- Uses s3fs to write each consumed message to S3:
  s3://kafka-stock-market-tutorial-youtube-darshil/stock_market_{count}.json

Key snippet (from your code):

```python
consumer = KafkaConsumer(
    'data_real_time_stream',
    bootstrap_servers=['3.137.155.232:9092'],
    value_deserializer=lambda x: loads(x.decode('utf-8'))
)

s3 = S3FileSystem()

for count, i in enumerate(consumer):
    with s3.open("s3://kafka-stock-market-tutorial-youtube-darshil/stock_market_{}.json".format(count), 'w') as file:
        json.dump(i.value, file)
```

Notes:
- Ensure the S3 bucket exists and your AWS credentials (environment variables, shared credentials file, or IAM role) are configured so `s3fs` can write files.
- If you expect many messages, writing one file per message may create many small objects. Consider batching or aggregating before writing.

## Configuration

Update the following as needed in the scripts:

- Kafka bootstrap servers:
  - bootstrap_servers=['<KAFKA_HOST>:<PORT>']
- Topic name:
  - 'data_real_time_stream' (create it if it doesn't exist)
- CSV path:
  - `"stock-trading-data.csv"`
- S3 path:
  - `"s3://<your-bucket>/<prefix>/stock_market_{count}.json"`

## Running

1. Start Kafka (locally or remote). If local, you can use Docker Compose (example not included here).
2. Place `stock-trading-data.csv` in the same directory as the producer script.
3. Run the producer in one terminal:

```bash
python producer.py
# or if combined file:
python producer_consumer_example.py --role producer
```

4. Run the consumer in another terminal:

```bash
python consumer.py
# or if combined file:
python producer_consumer_example.py --role consumer
```

(If your code is combined, adapt it to accept a CLI flag or separate into two scripts.)

## S3 credentials

s3fs uses the standard AWS credential chain. Provide credentials via:
- Environment variables:
  AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
- AWS shared credentials file (~/.aws/credentials)
- IAM role if running on EC2/ECS/EKS with the role attached

Example (not for production — keep secrets secure):

```bash
export AWS_ACCESS_KEY_ID=YOUR_KEY
export AWS_SECRET_ACCESS_KEY=YOUR_SECRET
```

## Improvements & Best Practices

- Proper shutdown handling: call `producer.flush()` and `producer.close()`; close the consumer gracefully.
- Topic creation: create the topic with an appropriate number of partitions and replication factor.
- Serialization: consider Avro/Schema Registry or JSON Schema for structured messages.
- Error handling: add retries, logging, and exception handling around Kafka and S3 operations.
- Batching: buffer messages and write in larger files to S3 to reduce many small writes.
- Security: use TLS/SASL for Kafka in production, and secure AWS credentials.
- Monitoring: instrument producers/consumers and monitor broker health.

## Troubleshooting

- Connection errors: verify the Kafka bootstrap server IP/port and network access (security groups, firewalls).
- Permission errors writing to S3: verify AWS credentials and S3 bucket permissions.
- Missing packages: ensure dependencies are installed (see prerequisites).
- High number of small S3 objects: implement batching or use an intermediate storage/streaming layer.

## Example: Create topic (Kafka CLI)

If you have kafka-topics.sh available, create the topic:

```bash
kafka-topics.sh --create --bootstrap-server 3.137.155.232:9092 \
  --replication-factor 1 --partitions 3 --topic data_real_time_stream
```

## License

Choose a license for your project (for example, MIT). Add a LICENSE file if desired.

## Contact / Author

Original snippet provided by: Deepeka Sabapathy (Sabapathy-deepeka)

---
