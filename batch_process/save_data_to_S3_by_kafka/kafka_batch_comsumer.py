# prerequesation: 
# insatll kafka
# 1. tar -xzf kafka_2.13-3.2.1.tgz
# 2. cd kafka_2.13-3.2.1
# 3. bin/zookeeper-server-start.sh config/zookeeper.properties # start zookeeper
# 4. bin/kafka-server-start.sh config/server.properties # start kafka


import json
from kafka import KafkaConsumer
import boto3
from kafka.admin import KafkaAdminClient, NewTopic
import uuid


class Batch_consumer:

    """
    create a class of kafka consumer which read data from kafka topics,
    and save to AWS S3 bucket

    """

    def __init__(self):
        pass

    def create_bucket(self, bucket_name):

        s3 = boto3.resource("s3")
        # create a unique bucket name
        self.bucket_name = bucket_name
        s3.create_bucket(Bucket=self.bucket_name)

    def create_kafka_topic(self, topic_name, n_partitions, n_replication_factors):

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

    def get_data_from_topic(self, topic_name, hostname='localhost'):

        # assuming that the data has already been sent to kafka by producer
        server_host = hostname + ":9092"
        consumer = KafkaConsumer(
            topic_name,
            bootstrap_servers=server_host,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id="pinterest_id",
            value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        )
        consumer.subscribe(topics=topic_name)
        return consumer

    def generate_unique_id(self):
        return uuid.uuid4()

    def get_event(self, message):
        return json.dumps(message.value)

    def get_file_name(self, unique_id, index):
        filename = (
            "pinterest_events_"
            + unique_id
            + "/"
            + unique_id
            + "_"
            + str(index)
            + ".json"
        )

    def send_data_to_s3(self, event, filename, bucket_name):
        self.s3 = boto3.resource("s3")
        self.s3.put_object(Body=event, Bucket=bucket_name, Key=filename)

    def send_data_to_cassandra():
        pass


if __name__ == "__main__":
    # start a batch consumer instance
    Batch_consumer = Batch_consumer()
    # enter your bucker name to create bucket in AWS S3
    Batch_consumer.create_bucket()
    Batch_consumer.get_data_from_topic()
    Batch_consumer.create_kafka_topic

    # for index, message in enumerate(messages):
    #     pass
