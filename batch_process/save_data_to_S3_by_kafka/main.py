from email import message
from kafka_batch_comsumer import Batch_consumer
from user_posting_emulation import AWSDBConnector
from kafka_batch_comsumer import Batch_consumer as bc
from kafka import KafkaClient
from kafka.cluster import ClusterMetadata
from kafka import KafkaConsumer, KafkaProducer
import boto3
from kafka.admin import KafkaAdminClient, NewTopic
import sqlalchemy
import json
from kafka_producer import Kafka_producer


"""
Receiving data from original source and sending data to kafka
"""

# # Initialising an kafka producer instance
# p = Kafka_producer()
# # Initialising kafka producer 
# p.producer()
# #list all topics
# topics = p.list_of_topics()
# # delete all topics for a fresh start
# p.delete_topics(topics)
# # creating an engine to receive data
# p.create_engine()
# # getting the data and sending data to kafka
# ids = 0
# while True:
#     message= p.get_origenal_data(ids)
#     p.sending_data_to_kafka("original", message)
#     ids += 1

"""
creating kafka consumer and receiving data from kafka and sending to AWS S3 bucket
"""

# start an consumer instance
bc = Batch_consumer()
# getting all the messages 
messages = bc.get_data_from_topic('original', "81.144.94.230")
# create an unique id for the bucket or folder
id = bc.generate_unique_id
# define the bucket where the event will be sent to
bucket_name = 'basicaccountstack-pinterestdataeng-proje-datalake-tcvpj2nf0cpq'
# Sending events to AWS s3
for i, message in enumerate(messages):
    # convert dictionary to json
    event = bc.get_event(message=message)

    # generate file name
    filename = bc.get_file_name(unique_id=id, index=i)
    # sending event to AWS S3 designated bucket and folder with given name
    bc.send_data_to_s3(event=event, filename=filename, bucket_name=bucket_name)