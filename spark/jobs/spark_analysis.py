from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    count,
    hour,
    concat_ws,
    input_file_name,
    regexp_extract,
    lit,
    when,
    monotonically_increasing_id,
    to_timestamp,
)
# start spark session
spark = SparkSession.builder.appName("SparkLogDataAnalysis(coalesce8)").getOrCreate()

# optimize execution: 
# - dynamically adjust query execution plan based on data on runtime
# - Setting shuffle partitions to 16 to help balance the workload
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.shuffle.partitions", "16") 


base_dir = "data/"
log_df = spark.read.text(f"{base_dir}/**/*.log")

# define regular expression pattern to parse the raw logs data
pattern = r"(\d{2}/\d{2}/\d{2})\s(\d{2}:\d{2}:\d{2})\s([A-Z]+)\s([^\s]+)\s(.*)"

# extract relevant fields using regular expressions and transformations
# Transformations:
# - Drop the original 'value' column after extracting necessary fields
# - Remove rows where Date is missing or empty
# - Fill missing Date or Time with default values
# - Combine Date and Time and convert to timestamp
# - Extract the hour from the timestamp for aggregation
parsed_df = (
    log_df.withColumn("Date", regexp_extract("value", pattern, 1))
    .withColumn("Time", regexp_extract("value", pattern, 2))
    .withColumn("Level", regexp_extract("value", pattern, 3))
    .withColumn("Component", regexp_extract("value", pattern, 4))
    .withColumn("Content", regexp_extract("value", pattern, 5))
    .drop("value") #
    .filter(col("Date") != "")
    .fillna({"Date": "00/00/00", "Time": "00:00:00"})
    .withColumn("Timestamp", to_timestamp(concat_ws(" ", col("Date"), col("Time")), "yy/MM/dd HH:mm:ss"))
    .withColumn("Hour", hour(col("Timestamp")))
)

# Coalesce reduces the number of partitions for aggregation efficiency
parsed_df = parsed_df.coalesce(8) 

# Perform aggregation by Component and Hour, counting the number of logs per combination
aggregated_df = parsed_df.groupBy("Component", "Hour").agg(count("*").alias("LogCount"))

aggregated_df.show(truncate=False)


spark.stop()
