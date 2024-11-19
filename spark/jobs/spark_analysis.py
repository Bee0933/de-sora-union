from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    count,
    hour,
    concat_ws,
    input_file_name,
    regexp_extract,
    lit,
    monotonically_increasing_id,
    to_timestamp,
)

spark = SparkSession.builder.appName("SparkLogDataAnalysis").getOrCreate()

base_dir = "data/"

# Read all log files recursively
log_df = spark.read.text(f"{base_dir}/**/*.log")

log_df = log_df.withColumn("file_path", input_file_name())

# raw log file format
pattern = r"(\d{2}/\d{2}/\d{2})\s(\d{2}:\d{2}:\d{2})\s([A-Z]+)\s([^\s]+)\s(.*)"

# Extract fields using the regular expression
parsed_df = (
    log_df.withColumn("Date", regexp_extract("value", pattern, 1))
    .withColumn("Time", regexp_extract("value", pattern, 2))
    .withColumn("Level", regexp_extract("value", pattern, 3))
    .withColumn("Component", regexp_extract("value", pattern, 4))
    .withColumn("Content", regexp_extract("value", pattern, 5))
    .withColumn("EventId", lit("E22"))
    .withColumn("EventTemplate", lit("Registered signal handlers for [*]"))
    .withColumn("LineId", monotonically_increasing_id())
    .drop("value")
)

# remove records where date is missing
parsed_df = parsed_df.filter(parsed_df.Date != "")

parsed_df = parsed_df.fillna({"Date": "00/00/00", "Time": "00:00:00"})

# transform date column to timestamps and Extract hour field from the timestamp
parsed_df = parsed_df.withColumn(
    "Timestamp",
    to_timestamp(concat_ws(" ", col("Date"), col("Time")), "yy/MM/dd HH:mm:ss"),
)
parsed_df = parsed_df.withColumn("Hour", hour(col("Timestamp")))

parsed_df = parsed_df.coalesce(8)

# Aggregate the logs by Component and Hour
aggregated_df = parsed_df.groupBy("Component", "Hour").agg(count("*").alias("LogCount"))

aggregated_df.show(truncate=False)
spark.stop()
