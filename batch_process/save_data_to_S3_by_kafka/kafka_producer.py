from user_posting_emulation import AWSDBConnector
from kafka import KafkaClient
from kafka.cluster import ClusterMetadata
from kafka import KafkaConsumer, KafkaProducer
import kafka
import boto3
import json
from kafka.admin import KafkaAdminClient, NewTopic
import sqlalchemy
from kafka.errors import (UnknownError, KafkaConnectionError, FailedPayloadsError,
                          KafkaTimeoutError, KafkaUnavailableError,
                          LeaderNotAvailableError, UnknownTopicOrPartitionError,
                          NotLeaderForPartitionError, ReplicaNotAvailableError)


class Kafka_producer:
    """
    This class w=is with functions of creating topics, and sending data to kafka, 
    also with function of receiving data from original source (in user_posting_emulation file) which is blocked in this project.
    """
    def __init__(self) -> None:
        pass

    def create_broker(self, topic_name, n_partitions, n_replication_factors):

        admin_client = KafkaAdminClient(
            bootstrap_servers="localhost:9092",
            # client_id='pinterest_project'
        )
        topic_list = []
        topic_list.append(
            NewTopic(
                name=topic_name,
                num_partitions=n_partitions,
                replication_factor=n_replication_factors,
            )
        )
        admin_client.create_topics(new_topics=topic_list, validate_only=False)

    # initialise kafka producer
    def producer(self):
        self.producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
              api_version=(3,2,1),
              value_serializer=lambda x: json.dumps(x).encode('utf-8'))
    
    def create_engine(self):
        new_connector = AWSDBConnector()
        self.engine = new_connector.create_db_connector()


    def get_origenal_data(self,nth_pin):

        row = self.engine.execute(f"SELECT * FROM pinterest_data LIMIT {nth_pin}, 1")
        message = dict(row.mappings().all()[0])
        return message

    # sending data to kafka, message is expected a json file
    def sending_data_to_kafka(self, topic_name, message):

        self.producer.send(topic_name, message)

    def list_of_topics():
        # list all topics
        consumer = KafkaConsumer( bootstrap_servers=['localhost:9092'])
        consumer.topics()

    def delete_topics(topic_names):
        admin_client = KafkaAdminClient(bootstrap_servers=['localhost:9092'])
        try:
            admin_client.delete_topics(topics=topic_names)
            print("Topic Deleted Successfully")
        except UnknownTopicOrPartitionError as e:
            print("Topic Doesn't Exist")
        except  Exception as e:
            print(e)

if __name__ == "__main__":
    kp = Kafka_producer()
    kp.producer()
    kp.create_engine()
    print(kp.get_origenal_data(6))
