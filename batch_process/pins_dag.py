
from airflow.operators.python import PythonOperator, BranchOperator
from datetime   import datetime
from textwrap import dedent
# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
# Operators; we need this to operate!
from airflow.operators.python import PythonOperator
# prerequeste including maven dependencies preinstalled by cloudformation.
# start pyspark: spark/bin/pyspark 
import findspark
findspark.init()
import multiprocessing
from pyspark.sql import SparkSession
from os.path import expanduser
import os
from airflow.models import DAG
from datetime import datetime
from datetime import timedelta
import pyspark.sql.functions as F
from pathlib import Path
import findspark
findspark.init()
from cassandra.cluster import Cluster
from pyspark.sql.functions import when, regexp_replace, regexp_extract, col
from time import sleep
from multiprocessing import Process
from airflow.operators.python import PythonOperator


home = expanduser("~")
airflow_dir = os.path.join(home, 'airflow')
Path(f"{airflow_dir}/dags").mkdir(parents=True, exist_ok=True)

def ETL():

    '''
    Initialise and configure spark setting.
    '''

    spark = SparkSession.builder \
            .master(f"local[{multiprocessing.cpu_count()}]") \
            .appName("s3tospark") \
            .getOrCreate()
    # hadoopConf = sc._jsc.hadoopConfiguration()
    # hadoopConf.set("fs.s3.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    # hadoopConf.set('fs.s3a.access.key',<your access key>)
    # hadoopConf.set('fs.s3a.secret.key', <your secret key>)
    # hadoopConf.set('spark.hadoop.fs.s3a.aws.credentials.provider', 'org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider')


    """
    loading data from aws s3 bucket
    """
    df = spark.read.json("/home/kafka/Documents/pinterest_project/data/*.json")

    """
    Removing duplicates and replace error value with None value
    """   
    
    # remove duplicates
    df = df.dropDuplicates()

    # replace error cells with Nones        
    df = df.replace({'No description available Story format': None}, subset = ['description'])\
                    .replace({'No description available': None}, subset = ['description'])\
                    .replace({'Image src error.': None}, subset = ['image_src'])\
                    .replace({'User Info Error': None}, subset = ['poster_name'])\
                    .replace({'N,o, ,T,a,g,s, ,A,v,a,i,l,a,b,l,e': None}, subset=['tag_list']).replace({'No Title Data Available': None}, subset = ['title'])\
                    .replace({'User Info Error': "0"}, subset = ['follower_count'])# replace error values in follower_count with 0   

    # replace error values with null
    df = df.withColumn('save_location', regexp_replace('save_location', 'Local save in ', '')) 
    # drop the rows with null values in 'image_src' column, as we don't want a row without a pin
    df = df.na.drop(subset=["image_src"])

    df = df.withColumn('follower_count', 
            when(df.follower_count.endswith('M'),regexp_replace(df.follower_count,'M','000000')) \
            .when(df.follower_count.endswith('k'),regexp_replace(df.follower_count,'k','000')) \
            .otherwise(df.follower_count)) 

    # cast follower_count column type as int
    df = df.withColumn("follower_count", F.col("follower_count").cast("int"))
    # cassandra not allow use index as a column name, change "index" to "idx"
    df = df.withColumnRenamed('index', 'idx')
    # reorder selected columns
    df = df.select('idx', 'title', 'poster_name', 'category', 'follower_count', 'description', 'image_src', 'is_image_or_video', 'tag_list', 'unique_id')
    df.write.format("org.apache.spark.sql.redis").option("table", "pins").option("key.column", "index").save()


def preparing_DB():
    # initial cassandra
    # initialise cassandra driver
    cluster = Cluster()
    session = cluster.connect()
    # create a cassandra keyspace
    session.execute("CREATE KEYSPACE pinterest_project WITH replication = {'class':'SimpleStrategy', 'replication_factor' : 3};")

    # create table
    session.execute("CREATE TABLE pinterest(idx int PRIMARY KEY, title text, poster_name text, category text, follower_count int, description text, image_src text, is_image_or_video text, tag_list text, unique_id text);")

def sending_data_to_cassandra():
    cluster = Cluster()
    session = cluster.connect()
    session.execute("USE pinterest_project;") # initial a cassandra database

    # make preparedUpdate statements
    preparedUpdate = session.prepare(
        """ 
        INSERT INTO pinterest (idx, title, poster_name, category, follower_count, description, image_src, is_image_or_video, tag_list, unique_id) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        )
    spark = SparkSession.builder \
            .master(f"local[{multiprocessing.cpu_count()}]") \
            .appName("cassandra") \
            .getOrCreate()
    df = spark.read.format("org.apache.spark.sql.redis").option("table", "pins_redis").option("key.column", "index").load()
    # write df to cassandra
    for item in df.collect():
        session.execute(preparedUpdate, [item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9]])


default_args = {
    'owner': 'Michael',
    'depends_on_past': False,
    'email': ['h1m1w1@googlemail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'start_date': datetime(2023, 1, 10),
    'retry_delay': timedelta(minutes=5),
    'end_date': datetime(2023, 1, 20),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'trigger_rule': 'all_success'
}


with DAG(dag_id='pin_dag',
         default_args=default_args,
         schedule_interval='0 0 * * * *',
         catchup=False,
         tags=['test']
         ) as dag:
     # Define the tasks. Here we are going to define only one bash operator
     pipeline = PythonOperator(
                    task_id="ETL",
                    python_callable=ETL(),
                    )
     preparing_db = PythonOperator(
               task_id="cassandra_DB",
               python_callable=preparing_DB()
               )
     save_to_cassandra = PythonOperator(
                    task_id="save_to_cassandra",
                    python_callable=sending_data_to_cassandra()
                    )
     [pipeline, preparing_db] >> save_to_cassandra















