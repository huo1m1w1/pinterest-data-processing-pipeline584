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
    This class with functions of creating topics, and sending data to kafka, 
    also with function of receiving data from original source (in user_posting_emulation file).
    """
    def __init__(self) -> None:
        pass

    def create_broker(self, topic_name, n_partitions, n_replication_factors):
      
        """
        Create Kafka broker/s
        """

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

    
    def producer(self):
      
        """
        initialise kafka producer
        """
        self.producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
              api_version=(3,2,1),
              value_serializer=lambda x: json.dumps(x).encode('utf-8'))
    
    def create_engine(self):
      
        """
        Create an engine to read data from source
        """
        new_connector = AWSDBConnector()
        self.engine = new_connector.create_db_connector()


    def get_origenal_data(self,nth_pin):
        
        """
        Read data from source
        """
        row = self.engine.execute(f"SELECT * FROM pinterest_data LIMIT {nth_pin}, 1")
        message = dict(row.mappings().all()[0])
        return message

     
    def sending_data_to_kafka(self, topic_name, message):
        
        """
        sending data to kafka, message is expected a json object
        """
        self.producer.send(topic_name, message)

    def list_of_topics():
         
        """
        list all topics in given kafka broker
        """
        consumer = KafkaConsumer( bootstrap_servers=['localhost:9092'])
        consumer.topics()

    def delete_topics(topic_names):
      
        """
        delete topic/s from given kafka topic/s
        """
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
