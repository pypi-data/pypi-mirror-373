import json
import requests
from pyspark.sql.avro.functions import from_avro
from pyspark.sql.functions import col, udf
from pyspark.sql.types import IntegerType
from pyspark.sql import DataFrame
from pyspark.sql.functions import expr


def get_schemas_from_registry(schema_ids, schema_registry_url: str, logger):
    schemas = {}
    for schema_id in schema_ids:
        schema_url = f"{schema_registry_url}/schemas/ids/{schema_id}"
        try:
            response = requests.get(schema_url)
            response.raise_for_status()
            schema_json = response.json()["schema"]
            schemas[schema_id] = json.loads(schema_json)

            logger.info(f"✅ Successfully fetched schema ID {schema_id}")
        except requests.RequestException as e:
            logger.error(f"❌ Failed to fetch schema ID {schema_id}: {e}")
            raise
    return schemas


def process_data_with_schema_evolution(df, schemas, logger):
    schema_dfs = []
    for schema_id, schema in schemas.items():
        try:
            # Filter records for this schema ID
            df_filtered = df.filter(col("schema_id") == schema_id)

            # Deserialize using `from_avro`
            df_schema = df_filtered.withColumn(
                "data",
                from_avro(col("avro_payload"), json.dumps(schema))
            ).select("data.*")

            schema_dfs.append(df_schema)
        except Exception as e:
            logger.warning(f"⚠️ Skipping schema {schema_id} due to error: {e}")

    if not schema_dfs:
        raise ValueError("No valid schema could be applied to the batch.")

    # Merge all schema variations dynamically
    merged_df = schema_dfs[0]
    for additional_df in schema_dfs[1:]:
        merged_df = merged_df.unionByName(additional_df, allowMissingColumns=True)

    logger.info("✅ Schema evolution successfully handled within batch.")
    return merged_df


def byte_array_to_int(byte_array):
    return int.from_bytes(byte_array, byteorder="big")


schema_id_udf = udf(byte_array_to_int, IntegerType())


def add_avro_columns_transform(df: DataFrame) -> DataFrame:
    df = df.withColumn("schema_id_bytes", expr("substring(value, 2, 4)"))
    df = df.withColumn("schema_id", schema_id_udf(col("schema_id_bytes")))
    df = df.withColumn("avro_payload", expr("substring(value, 6, length(value)-5)"))
    return df


def apply_avro_schema_from_registry(dataframe: DataFrame, schema_registry_url: str, logger) -> DataFrame:
    """
    Apply schema from registry to the DataFrame.

    Args:
        dataframe:
        schema_registry_url:
        logger:

    Returns:
        DataFrame
    """
    # Extract schema ID from Kafka message
    dataframe = add_avro_columns_transform(df=dataframe)

    # Get unique schema IDs
    unique_schema_ids = [row["schema_id"] for row in dataframe.select("schema_id").distinct().collect()]
    record_count = dataframe.count()
    logger.info(
        f"✅ Successfully read Kafka batch. Loaded {record_count} records from Kafka "
        f"with {len(unique_schema_ids)} unique schema IDs"
    )

    # Fetch schemas and process data
    schemas = get_schemas_from_registry(
        schema_ids=unique_schema_ids,
        schema_registry_url=schema_registry_url,
        logger=logger
    )

    dataframe = process_data_with_schema_evolution(df=dataframe, schemas=schemas, logger=logger)

    return dataframe
