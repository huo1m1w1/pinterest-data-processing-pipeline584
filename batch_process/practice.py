import findspark
findspark.init()
import pyspark
import findspark
import multiprocessing
from pyspark.sql import SparkSession
from pyspark import SparkConf
from pyspark.sql.functions import when, regexp_replace, regexp_extract, col
import requests
from time import sleep
import random
from multiprocessing import Process
import boto3
import json
import sqlalchemy
import uuid
import os 


# initialise pyspark session

spark = SparkSession.builder \
        .master("local[*]")\
        .appName("pin_app") \
        .config("spark.cassandra.connection.host", "127.0.0.1")\
        .getOrCreate()

df = spark.read.json("/home/kafka/Documents/pinterest_project/data/*.json")

df =df.dropDuplicates()

df.write\
    .format("org.apache.spark.sql.cassandra")\
    .mode('append')\
    .options(table="users", keyspace="moviesdata")\
    .save()