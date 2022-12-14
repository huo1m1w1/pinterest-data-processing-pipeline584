package com.redislabs.provider.redis.env

import com.redislabs.provider.redis.{RedisConfig, RedisEndpoint}
import org.apache.spark.SparkConf

trait RedisStandaloneSSLEnv extends Env {

  override val redisPort = 6380

  override val conf: SparkConf = new SparkConf()
    .setMaster("local[*]").setAppName(getClass.getName)
    .set("spark.redis.host", redisHost)
    .set("spark.redis.port", s"$redisPort")
    .set("spark.redis.auth", redisAuth)
    .set("spark.redis.ssl", "true")
    .set("spark.streaming.stopGracefullyOnShutdown", "true")
    .set("spark.driver.bindAddress", "127.0.0.1")

  override val redisConfig: RedisConfig =
    new RedisConfig(RedisEndpoint(redisHost, redisPort, auth = redisAuth, ssl = true))
}
