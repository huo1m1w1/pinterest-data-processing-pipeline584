ThisBuild / name := "pinterest_streaming"
ThisBuild / organization := "h1m1w1"
ThisBuild / version := "0.1.0-pinterest"

ThisBuild / scalaVersion := "2.12.16"

ThisBuild / autoScalaVersion := false

val sparkVersion = "3.2.3"
val sparkDependencies = seq(
  "org.apache.spark" %% "spark-core" % sparkVersion,
  "org.apache.spark" %% "spark-sql" % sparkVersion
)

libraryDependencies ++= sparkDependencies

lazy val root = (project in file("."))
  .settings(
    name := "Pinterest_streaming"
  )

