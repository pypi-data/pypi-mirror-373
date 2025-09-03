from typing import List, Union

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, lit
from pyspark.sql.types import (
    BooleanType,
    DateType,
    DoubleType,
    FloatType,
    IntegerType,
    LongType,
    StringType,
    TimestampType,
)

spark = SparkSession.builder.getOrCreate()


# Check if a Delta table exists at the given ABFSS path
def table_exists(table_path: str) -> bool:
    hconf = spark._jsc.hadoopConfiguration()
    fs = spark.sparkContext._jvm.org.apache.hadoop.fs.FileSystem.get(hconf)
    path = spark.sparkContext._jvm.org.apache.hadoop.fs.Path(table_path)
    return fs.exists(path)


# Read a PostgreSQL table using JDBC
def query_postgres_table(
    hostname: str, database: str, table: str, user: str, password: str, port: int = 5432
) -> DataFrame:
    jdbc_url = f"jdbc:postgresql://{hostname}:{port}/{database}?sslmode=require"
    connection_props = {
        "user": user,
        "password": password,
        "driver": "org.postgresql.Driver",
    }
    return (
        spark.read.format("jdbc")
        .option("url", jdbc_url)
        .option("dbtable", f"public.{table}")
        .options(**connection_props)
        .load()
    )


# Map Spark types to SQL types (for schema ALTER statements)
def spark_type_to_sql(data_type):
    if isinstance(data_type, StringType):
        return "STRING"
    if isinstance(data_type, IntegerType):
        return "INT"
    if isinstance(data_type, LongType):
        return "BIGINT"
    if isinstance(data_type, DoubleType):
        return "DOUBLE"
    if isinstance(data_type, FloatType):
        return "FLOAT"
    if isinstance(data_type, BooleanType):
        return "BOOLEAN"
    if isinstance(data_type, TimestampType):
        return "TIMESTAMP"
    if isinstance(data_type, DateType):
        return "DATE"
    return data_type.simpleString().upper()


# Align DataFrame to Delta schema (adds missing columns with nulls)
def align_df_to_delta_schema(df: DataFrame, table_path: str) -> DataFrame:
    if not table_exists(table_path):
        print(f"⚠ Target table at {table_path} does not exist. Returning original DataFrame.")
        return df

    target_schema = spark.read.format("delta").load(table_path).schema
    df_cols = set(df.columns)
    aligned = df

    for f in target_schema:
        if f.name not in df_cols:
            aligned = aligned.withColumn(f.name, lit(None).cast(f.dataType))

    return aligned.select([f.name for f in target_schema])


# Create or update Delta table schema from a DataFrame
def create_or_update_table_from_df_schema(df: DataFrame, table_path: str):
    if not table_exists(table_path):
        if df.count():
            df.limit(0).write.format("delta").mode("overwrite").option(
                "overwriteSchema", "true"
            ).option("path", table_path).save()
        else:
            df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").option(
                "path", table_path
            ).save()
        print(f"✅ Created new table at {table_path}")
        return

    existing = spark.read.format("delta").load(table_path).schema
    existing_fields = {f.name for f in existing.fields}
    additions = [f for f in df.schema.fields if f.name not in existing_fields]

    if not additions:
        print("ℹ️ No schema changes.")
        return

    for fld in additions:
        sql_type = spark_type_to_sql(fld.dataType)
        null_clause = "" if fld.nullable else "NOT NULL"
        spark.sql(
            f"""
            ALTER TABLE delta.`{table_path}`
            ADD COLUMNS ({fld.name} {sql_type} {null_clause})
        """
        )
        print(f"➕ Added column {fld.name} to {table_path}")


# Perform a Delta MERGE (upsert) into the given table path
def merge_df_to_table(source_df: DataFrame, target_table_path: str, pk_cols: Union[List[str], str]):
    if isinstance(pk_cols, str):
        pk_cols = [pk_cols]

    deduped = source_df.dropDuplicates(pk_cols)
    deduped.createOrReplaceTempView("_stg")

    on_clause = " AND ".join(f"target.{c} = src.{c}" for c in pk_cols)

    merge_sql = f"""
      MERGE INTO delta.`{target_table_path}` AS target
      USING _stg AS src
        ON {on_clause}
      WHEN MATCHED THEN
        UPDATE SET *
      WHEN NOT MATCHED THEN
        INSERT *
    """
    spark.sql(merge_sql)
    print(f"✅ Merged {deduped.count()} records into delta.`{target_table_path}` on {pk_cols}")


# Get watermark value from Delta table
def get_watermark(wm_table_path: str, table_name: str) -> int:
    if not table_exists(wm_table_path):
        print(f"⚠ Watermark table {wm_table_path} not found.")
        return 0

    df = spark.read.format("delta").load(wm_table_path).filter(col("table_name") == table_name)
    return df.collect()[0]["ts"] if df.count() else 0


# Update watermark value in Delta table
def update_watermark(wm_table_path: str, table_name: str, ts: int):
    wm_df = spark.createDataFrame([(table_name, ts)], ["table_name", "ts"])
    wm_df.createOrReplaceTempView("new_wm")

    spark.sql(
        f"""
      MERGE INTO delta.`{wm_table_path}` AS target
      USING new_wm AS src
        ON target.table_name = src.table_name
      WHEN MATCHED THEN
        UPDATE SET ts = src.ts
      WHEN NOT MATCHED THEN
        INSERT (table_name, ts) VALUES (src.table_name, src.ts)
    """
    )
    print(f"✅ Watermark for '{table_name}' set to {ts}")
