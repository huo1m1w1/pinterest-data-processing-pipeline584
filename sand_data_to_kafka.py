from batch_producer.kafka_producer import Kafka_producer


"""
Receiving data from original source and sending data to kafka
"""
if __name__ == "__main__":
    # Initialising an kafka producer instance
    p = Kafka_producer()
    # Initialising kafka producer
    p.producer()
    # list all topics
    topics = p.list_of_topics()
    # delete all topics for a fresh start
    p.delete_topics(topics)
    # creating an engine to receive data
    p.create_engine()
    # getting the data and sending data to kafka
    ids = 0
    while True:
        # get data from source
        message = p.get_origenal_data(ids)
        # send data to two kafka brokers one for batch processing and streaming
        p.sending_data_to_kafka("batch_processing", message)
        p.sending_data_to_kafka("streaming", message)

        ids += 1
