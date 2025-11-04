from confluent_kafka import Consumer, KafkaError, KafkaException
import json
import os
from dotenv import load_dotenv

load_dotenv()


class InvoiceConsumer:
    def __init__(self):
        self.topic = "invoices"
        self.config = {
            "bootstrap.servers": os.getenv("BOOTSTRAP_SERVERS"),
            "security.protocol": os.getenv("SECURITY_PROTOCOL"),
            "sasl.mechanisms": os.getenv("SASL_MECHANISMS"),
            "sasl.username": os.getenv("SASL_USERNAME"),
            "sasl.password": os.getenv("SASL_PASSWORD"),
            "client.id": os.getenv("CLIENT_ID", "invoice-consumer-client"),
            # consumer specific
            "group.id": os.getenv("GROUP_ID", "invoice-consumer-group"),
            "auto.offset.reset": "earliest",   # start from earliest if no committed offset
            "enable.auto.commit": True
        }

    def start_consumer(self):
        consumer = Consumer(self.config)
        consumer.subscribe([self.topic])

        print(f"Listening to topic [{self.topic}]... Ctrl+C to stop")

        try:
            while True:
                msg = consumer.poll(1.0)  # 1 second timeout

                if msg is None:
                    continue

                if msg.error():
                    # end of partition event, not really an error
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    raise KafkaException(msg.error())

                key = msg.key().decode("utf-8") if msg.key() else None
                value_str = msg.value().decode("utf-8")
                invoice = json.loads(value_str)

                invoice_id = invoice.get("InvoiceNumber")
                print(
                    f"Consumed message: partition={msg.partition()} "
                    f"offset={msg.offset()} key={key} invoice={invoice_id}"
                )

        except KeyboardInterrupt:
            print("\nStopping consumer...")
        finally:
            consumer.close()


if __name__ == "__main__":
    consumer = InvoiceConsumer()
    consumer.start_consumer()
