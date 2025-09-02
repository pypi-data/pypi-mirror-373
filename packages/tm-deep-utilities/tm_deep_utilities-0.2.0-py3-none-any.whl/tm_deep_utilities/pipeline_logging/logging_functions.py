from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType
from datetime import datetime

def get_spark_session():
    try:
        return SparkSession.builder.getOrCreate()
    except Exception:
        raise NameError("SparkSession is not defined. Please ensure your notebook is attached to a Spark cluster.")

def log_pipeline_status(log_table_name, pipeline_id, job_id, business_unit, data_product_name, source, source_s3_path, run_status, error_message, records_copied, start_time, end_time, duration, frequency, load_type):
    """
    Logs the status and health of a pipeline run to a specified log table.
    """
    spark = get_spark_session()
    try:
        schema = StructType([
            StructField("pipeline_id", StringType(), True),
            StructField("job_id", StringType(), True),
            StructField("business_unit", StringType(), True),
            StructField("data_product_name", StringType(), True),
            StructField("source", StringType(), True),
            StructField("source_s3_path", StringType(), True),
            StructField("run_status", StringType(), True),
            StructField("error_message", StringType(), True),
            StructField("records_copied", IntegerType(), True),
            StructField("start_time", TimestampType(), True),
            StructField("end_time", TimestampType(), True),
            StructField("duration", StringType(), True),
            StructField("frequency", StringType(), True),
            StructField("load_type", StringType(), True)
        ])
        
        log_data = [(pipeline_id, job_id, business_unit, data_product_name, source, source_s3_path, run_status, error_message, records_copied, start_time, end_time, duration, frequency, load_type)]
        log_df = spark.createDataFrame(log_data, schema=schema)

        log_df.write.format("delta").mode("append").saveAsTable(log_table_name)
        print(f"Successfully logged status for pipeline_id: {pipeline_id}")
    except Exception as e:
        print(f"Failed to log pipeline status. Error: {e}")