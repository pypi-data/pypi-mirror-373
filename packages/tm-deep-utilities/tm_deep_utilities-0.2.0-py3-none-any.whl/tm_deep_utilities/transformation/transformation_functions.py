from pyspark.sql import DataFrame
from pyspark.sql import SparkSession

def get_spark_session():
    try:
        return SparkSession.builder.getOrCreate()
    except Exception:
        raise NameError("SparkSession is not defined. Please ensure your notebook is attached to a Spark cluster.")

def read_data_from_source(source_path:str, source_type:str, source_options:dict=None):
    """
    Purpose : Reads the data from the source based on the input parameters
    Args    : 
              source_type : type of the source (Parquet, CSV, PostgreSQL etc.)
              source_path : path of the source
              source_options : additional parameters to be passed to the source
    """
    spark = get_spark_session()
    if source_options is None:
        source_options = {}
    
    if source_type in ["parquet", "csv", "json"]:
        reader = spark.read.format(source_type)
        if source_type == "csv":
            reader = reader.options(header = source_options.get("header", "true"),
                                     inferSchema = source_options.get("inferSchema", "true"),
                                     sep = source_options.get("sep", ","))

        reader = reader.options(**source_options)

        return reader.load(source_path)

    elif source_type == "jdbc":
        jdbc_url = source_options.get("jdbc_url")
        db_table = source_options.get("db_table")

        db_user = source_options.get("user")
        db_password = source_options.get("password")
        db_driver = source_options.get("driver")

        jdbc_properties = {
            "user": db_user,
            "password": db_password,
            "driver": db_driver
        }   

        return spark.read.jdbc(url=jdbc_url, table=db_table, properties=jdbc_properties)
    
    else:
        raise ValueError(f"Invalid source type: '{source_type}'.")

def write_data_to_delta(df:DataFrame, delta_table_location:str, write_mode:str, partition_column:str=None,
                          coalesce_partitions:int=None):
    """
    Purpose : Writes the dataframe data to delta table
    Args    :
              df : dataframe to be written to delta table
              delta_table_location : S3 Location of the delta table
              mode : The write mode whether to append or overwrite
              partition_column : The column name to partition the delta table by
              coalesce_partitions : The number of partitions to coalesce the data before writing to delta table
    """
    spark = get_spark_session()
    if coalesce_partitions is not None:
        df_to_write = df.coalesce(coalesce_partitions)
    else:
        df_to_write = df
    
    writer = df_to_write.write.format("delta").mode(write_mode)

    if partition_column is not None:
        writer.partitionBy(partition_column).save(delta_table_location)
    else:
        writer.save(delta_table_location)