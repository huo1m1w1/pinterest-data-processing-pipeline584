package h1m1w1.pinterest_streaming

import org.apache.spark.log4j.Logger
import org.apache.spark.sql.SparkSession

import java.util.logging.Logger

object pinterest_streaming extends Serializable {
  @transient lazy val logger: Logger = Logger.getLogger(getClass.getName)

  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("spark-streaming")
      .master("local[*]")
      .config("spark.streaming.stopGracefullyOnShutdown", "true")
      .getOrCreate()

    val linesDF = spark.readStream
      .format("socket")
      .option("host", "localhost")
      .option("port", "9999") // going to replay from the beginning each time
      .load()

    val wordsDF = linesDF.select()
//    val inputDf = spark.readStream
//      .format("kafka")
//      .option("kafka.bootstrap.servers", BROKERS)
//      .option("subscribe", "streaming")
//      .option("startingOffsets", "earliest") // going to replay from the beginning each time
//      .load()

  }

}
