#                                            Pinterest-data-processing-pipeline
![My Image](Slide2.jpg)  
### Introduction:
1. This project is to build pinterest pipelines of batch processing and streaming processing, see picture above.
2. Firstly, pins will be sent to kafka.
3. In batch processing, written in Python, data will be read from Kafka and saved to AWS S3.
4. Data will be read, cleaned, transformed and saved to cassandra by spark.  
5. I made a batch precessing comparison of spark and spark integrated with redis. Spark with redis performed data processing significantly better than spark alone, also it is much easier to manage data transfering through the pipeline, however large dataset may not be suitable for spark with redis.
6. In streaming process, written in Scala, spark will read streaming data from kakfa, perform ETL, and window function, and save data to AWS RDS postgresql.
7. AirFlow will orchestrate the whole pipelines, including starting runtime environment for example zookeeper kafka, cassandra, performing ETL pipeline,  and staring streaming process. 

### Infrastracture:

The infrastracture, including EC2 instance with security group, git, docker, docker-compose, kafka, spark, cassandra, airflow, promenthues, grafana, and all the dependency packages, will be build by cloudformation. It will be very helpful if we want to build a multiple node clasters or we may need it in the future. 

### The prerequisite:
Creating an aws account with s3-admin role with full access to s3 permission, and a key-pair named 'pin_app.pem' to access to EC2 through the terminal.  
It is recommended to start the cloudformation in console, uploading template.yml file to create the stack, as it is no need to set credential. check the installation process in terminal by command "sudo cat /var/log/cloud-init-output.log". 

### Run the codes:
Two methods to start the pipelines, in terminal run dag.py in root directory of pinterest-data-processing-pipeline584, or simply add code userdata in templet.yml to start the application automatically.
Using default ports to check dags, grafana, spark.
