from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType
from datetime import datetime

def get_spark_session():
    try:
        # Tries to get the current SparkSession, which is the standard Databricks behavior
        return SparkSession.builder.getOrCreate()
    except Exception:
        # If the SparkSession is not defined, this block will be executed
        raise NameError("SparkSession is not defined. Please ensure your notebook is attached to a Spark cluster.")

def create_catalog(catalogName, managedLocation):
    """Creates a Unity Catalog if it doesn't exist."""
    spark = get_spark_session()
    spark.sql(f"""CREATE CATALOG IF NOT EXISTS {catalogName} MANAGED LOCATION '{managedLocation}' ;""")

def create_database(catalogName, databaseName, databaseLocation):
    """Creates a database within a specified catalog."""
    spark = get_spark_session()
    spark.sql(f"""USE CATALOG {catalogName};""")
    spark.sql(f"""CREATE DATABASE IF NOT EXISTS {databaseName} MANAGED LOCATION '{databaseLocation}';""")

def catalog_exists(catalog_name):
    """Checks if a Catalog exists."""
    try:
        spark = get_spark_session()
        spark.sql(f"USE CATALOG `{catalog_name}`")
        print(f"Catalog '{catalog_name}' exists.")
        return True
    except Exception as e:
        print(f"Catalog '{catalog_name}' does not exist. Error: {e}")
        return False

def database_exists(catalog_name, db_name):
    """Checks if a database exists within the Catalog."""
    try:
        spark = get_spark_session()
        spark.sql(f"USE CATALOG `{catalog_name}`")
        spark.sql(f"DESCRIBE DATABASE `{db_name}`")
        print(f"Database '{db_name}' exists in catalog '{catalog_name}'.")
        return True
    except Exception as e:
        print(f"Database '{db_name}' does not exist in catalog '{catalog_name}'. Error: {e}")
        return False
        
def create_delta_external_table(catalog_name: str, db_name: str, table_name: str, s3_path: str, comment: str, partition_column: str = None):
    """Creates an external Delta table."""
    spark = get_spark_session()
    print(f"Creating external table '{table_name}' at location '{s3_path}'...")
    try:
        spark.sql(f"USE CATALOG `{catalog_name}`")
        partition_clause = ""
        if partition_column:
            partition_clause = f"PARTITIONED BY ({partition_column})"
        spark.sql(f"""
            CREATE TABLE IF NOT EXISTS `{db_name}`.`{table_name}`
            USING DELTA
            COMMENT '{comment}'
            {partition_clause}
            LOCATION '{s3_path}'
        """)
        print(f"External table '{table_name}' created successfully.")
    except Exception as e:
        print(f"Error creating external table '{table_name}': {e}")
        raise e

def create_log_table(log_table_name):
    """
    Creates the pipeline log table with a predefined schema using a three-level namespace.
    """
    spark = get_spark_session()
    try:
        spark.sql(f"""
            CREATE TABLE IF NOT EXISTS {log_table_name} (
                pipeline_id STRING,
                job_id STRING,
                business_unit STRING,
                data_product_name STRING,
                source STRING,
                source_s3_path STRING,
                run_status STRING,
                error_message STRING,
                records_copied INT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                duration STRING,
                frequency STRING,
                load_type STRING
            ) USING DELTA
        """)
        print(f"Successfully created or ensured existence of log table: {log_table_name}")
    except Exception as e:
        raise Exception(f"Failed to create log table. Error: {e}")