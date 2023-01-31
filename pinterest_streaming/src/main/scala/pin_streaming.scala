import org.apache.spark.sql.{Row, SparkSession}
import org.apache.spark.sql.types.{StringType, StructType}
import org.apache.spark.sql.types._
import org.apache.spark.sql.functions._
import org.apache.spark.sql.functions.from_json
import org.apache.spark.sql.expressions._
import java.sql.Driver
object pin_streaming {

  val jsonSchema = new StructType()
    .add("index", IntegerType)
    .add("unique_id", StringType)
    .add("title", StringType)
    .add("description", StringType)
    .add("poster_name", StringType)
    .add("follower_count", StringType)
    .add("tag_list", StringType)
    .add("is_image_or_video", StringType)
    .add("image_src", StringType)
    .add("downloaded", IntegerType)
    .add("save_location", StringType)
    .add("category", StringType)


  def main(args: Array[String]): Unit={
    // initialise a spark session
    val spark = SparkSession
          .builder
          .appName("sparkStreaming")
          .master("local[*]")
          .getOrCreate()
//

    // receiving data from kafka
    val df = spark
          .readStream
          .format("kafka")
          .option("kafka.bootstrap.servers", "192.168.1.121:9092")
          .option("subscribe", "streaming")
          .load()

    // transfer json files to dataframe with the column of timestamp
    val df1 = df.selectExpr("timestamp as original_timestamp","cast (value as string) as json")
                .select(from_json(col("json"), jsonSchema) as "data", col("original_timestamp"))
                .selectExpr("data.index as index", "data.unique_id as unique_id", "data.title as title", "data.description as description", "data.poster_name as poster_name", "data.follower_count as follower_count", "data.tag_list as tag_list", "data.is_image_or_video as is_image_or_video", "data.image_src as image_src", "data.downloaded as downloaded", "data.save_location as save_location", "data.category as category", "original_timestamp as timestamp")
//


    df1.printSchema()


    import spark.implicits._


    val transformed_df = df1.withColumn("description",when(col("description").equalTo("No description available Story format"), None)
                             .otherwise(col("description")))
               .withColumn("description", when(col("description").equalTo("No description available"), None)
                             .otherwise(col("description")))
              .withColumn("image_src", when(col("image_src").equalTo("Image src error."), None)
                             .otherwise(col("image_src")))
              .withColumn("poster_name", when(col("poster_name").equalTo("User Info Error"), None)
                             .otherwise(col("poster_name")))
              .withColumn("tag_list", when(col("tag_list").equalTo("N,o, ,T,a,g,s, ,A,v,a,i,l,a,b,l,e"), None)
                             .otherwise(col("tag_list")))
              .withColumn("title", when(col("title").equalTo("No Title Data Available"), None)
                             .otherwise(col("title")))
              .withColumn("follower_count", when(col("follower_count").equalTo("User Info Error"), None)
                             .otherwise(col("follower_count")))
              .withColumn("save_location",regexp_replace(col("save_location"), "Local save in ", ""))
              .withColumn("follower_count", when(col("follower_count").endsWith("M"),regexp_replace(col("follower_count"),"M","000000"))
                                                    .when(col("follower_count").endsWith("k"),regexp_replace(col("follower_count"),"k","000"))
                                                    .otherwise(col("follower_count")))
              .withColumn("follower_count", col("follower_count").cast("int"))

//     val userCounts = transformed_df
//       .withWatermark("timestamp", "10 minutes")
//       .groupBy(
//         session_window($"timestamp", "5 minutes"),
//         $"poster_name")
//       .count()


    val windowedSum = transformed_df.select("timestamp", "poster_name")
        .withColumn("timestamp", to_timestamp(col("timestamp")))
        .withWatermark("timestamp", "1 minute")
        .groupBy(window(col("timestamp"), "1 minute"))
        .agg(sum("poster_name").alias("sum_value"))


    val query = windowedSum.writeStream
        .outputMode("complete")
        .format("console")
        .start()


//////    // reorder selected columns
//////    val updated_df = transformed_df.na.drop("image_src")
//////            .select("idx", "title", "poster_name", "category", "follower_count",  "description", "image_src", "is_image_or_video", "tag_list" , "unique_id" )

    transformed_df.write
          .format("jdbc")
          .option("url", "jdbc:postgresql://nft-ranking.cftyhhxl7vmx.eu-west-2.rds.amazonaws.com:5432/rds_database")
          .option("dbtable", "postgres")
          .option("user", "postgres")
          .option("password", <RDS password>)
          .mode("append")
          .save()

    spark.streams.awaitAnyTermination()


  }

}
