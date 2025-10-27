import pandas as pd
from kafka import KafkaProducer
from time import sleep
from json import dumps
import json

producer = KafkaProducer(bootstrap_servers=['3.137.155.232:9092'], #change ip here
                         value_serializer=lambda x: 
                         dumps(x).encode('utf-8'))

producer.send('data_real_time_stream', value={'firstName':'Deepeka', 'lastName':'Sabapathy', 'age':26})

df = pd.read_csv("stock-trading-data.csv")

df.head()
#df.sample(1)

while True:
    dict_stock = df.sample(1).to_dict(orient="records")[0]
    producer.send('data_real_time_stream', value=dict_stock)
    sleep(1)
    
#producer.flush()
#producer.close()