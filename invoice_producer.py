from confluent_kafka import Producer
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

class InvoiceProducer:
    def __init__(self):
        self.topic = "invoices"
        self.config = {
            'bootstrap.servers': os.getenv('BOOTSTRAP_SERVERS'),
            'security.protocol': os.getenv('SECURITY_PROTOCOL'),
            'sasl.mechanisms': os.getenv('SASL_MECHANISMS'),
            'sasl.username': os.getenv('SASL_USERNAME'),
            'sasl.password': os.getenv('SASL_PASSWORD'),
            'client.id': os.getenv('CLIENT_ID')
            }
    
    def delivery_callback(self, err, msg):
        if err:
            print(f"Message failed delivery: {err}")
        else:
            key = msg.key().decode('utf-8') if msg.key() else None
            invoice_id = json.loads(msg.value().decode('utf-8'))['InvoiceNumber']
            print(f"Message delivered : key={key} value={invoice_id}")
        
    def producer_invoices(self, producer, counts):
        counter = 0
        with open(r"C:\Users\deepe\OneDrive\Desktop\Tech_Stack\kafka-streaming\data\invoice.json") as lines:
            for line in lines:
                invoice = json.loads(line)
                store_id = invoice['StoreID']
                producer.produce(self.topic, key=store_id, value=line, callback=self.delivery_callback)
                time.sleep(1)
                producer.poll(1)
                counter = counter + 1
                if counter == counts:
                    break
    
    def start_producer(self):
        kafka_producer = Producer(self.config)
        self.producer_invoices(kafka_producer, 10)
        kafka_producer.flush(10)

if __name__ == "__main__":
    producer = InvoiceProducer()
    producer.start_producer()        
