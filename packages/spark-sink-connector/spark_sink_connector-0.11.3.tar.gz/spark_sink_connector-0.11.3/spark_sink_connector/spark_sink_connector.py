import logging
import os
from datetime import date, timedelta, datetime
from typing import Callable, Optional

from pyspark.conf import SparkConf
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.protobuf.functions import from_protobuf

from .enums import *
from .schema_helper import apply_avro_schema_from_registry
from .spark_sink_config import SparkSinkConfig


class SparkSinkConnector:
    """
    A connector for reading data from Kafka and writing to S3 in Delta or Hudi format.
    """

    def __init__(self,
                 connector_mode: ConnectorMode,
                 open_table_format: OpenTableFormat = None,
                 output_mode: ConnectorOutputMode = None,
                 config: Optional[SparkSinkConfig] = None,
                 logger: Optional[logging.Logger] = None,
                 logging_level: str = 'INFO'):
        """
        Initialize the SparkSinkConnector with configuration.

        Args:
            connector_mode: Whether to use streaming mode or batch mode
            open_table_format: OpenTableFormat to use
            output_mode: Output mode to use
            config: Configuration object for the connector
            logger: Optional logger instance
        """
        self.connector_mode = connector_mode
        self.foreach_batch_fn = None
        self.config = config or SparkSinkConfig()
        self._setup_logger(logger, logging_level)
        if open_table_format is not None:
            self.config.open_table_format = open_table_format
        if output_mode is not None:
            self.config.output_mode = output_mode
        self.dataframe = None
        self.writer = None
        self._log_configurations()
        self.spark_session = self._create_spark_session(logging_level)

    def _setup_logger(self, logger: Optional[logging.Logger] = None, logging_level: str = 'INFO'):
        """Set up the logger for this class."""
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
            logging.basicConfig(
                format=self.config.logger_format,
                level=logging_level
            )

    def _create_spark_session(self, logging_level: str = 'INFO') -> SparkSession:
        """
        Create and configure a Spark session.

        Returns:
            SparkSession: Configured Spark session

        Raises:
            Exception: If Spark session creation fails
        """
        try:
            spark_conf = SparkConf()
            spark_conf.set("spark.appName", f"s3_sink_{os.path.basename(__file__)}")

            # S3 configuration
            spark_conf.set("spark.hadoop.fs.s3a.access.key", self.config.s3_access_key)
            spark_conf.set("spark.hadoop.fs.s3a.secret.key", self.config.s3_secret_key)
            spark_conf.set("spark.hadoop.fs.s3a.endpoint", self.config.s3_endpoint)
            spark_conf.set("spark.hadoop.fs.s3a.path.style.access", self.config.s3a_path_style_access)
            spark_conf.set("spark.hadoop.fs.s3a.impl", self.config.s3a_impl)
            spark_conf.set("spark.hadoop.fs.s3a.connection.ssl.enabled", self.config.s3a_connection_ssl_enabled)

            # Packages
            spark_conf.set("spark.jars.packages", self.config.spark_jars)

            # Extra configurations
            if self.config.spark_extra_configs is not None:
                for key, value in self.config.spark_extra_configs.items():
                    spark_conf.set(key, value)

            if self.config.open_table_format == OpenTableFormat.HUDI:
                if self.config.hudi_spark_extra_configs is not None:
                    for key, value in self.config.hudi_spark_extra_configs.items():
                        spark_conf.set(key, value)

            if self.config.open_table_format == OpenTableFormat.DELTA:
                if self.config.delta_spark_extra_configs is not None:
                    for key, value in self.config.delta_spark_extra_configs.items():
                        spark_conf.set(key, value)

            spark = SparkSession.builder.config(conf=spark_conf)

            if ((self.config.open_table_format == OpenTableFormat.DELTA and
                    "spark.hive.metastore.uris" in self.config.delta_spark_extra_configs) or
                (self.config.open_table_format == OpenTableFormat.HUDI and
                    "spark.hive.metastore.uris" in self.config.hudi_spark_extra_configs)):
                spark = spark.enableHiveSupport()

            spark = spark.getOrCreate()
            spark.sparkContext.setLogLevel(logging_level)
            self.logger.info("✅ Spark session created successfully.")
            return spark
        except Exception as e:
            self.logger.error(f"❌ Failed to create Spark session: {e}")
            raise

    def _log_configurations(self):
        self.logger.info(f"running_mode: {self.config.running_mode}")
        self.logger.info(f"open_table_format: {self.config.open_table_format}")
        self.logger.info(f"output_mode: {self.config.output_mode}")
        self.logger.info(f"hoodie_options: {self.config.hoodie_options}")
        self.logger.info(f"write_to_s3_options: {self.config.write_to_s3_options}")
        self.logger.info(f"delta_table_properties: {self.config.delta_table_properties}")
        self.logger.info(f"hudi_table_properties: {self.config.hudi_table_properties}")
        self.logger.info(f"s3_endpoint: {self.config.s3_endpoint}")
        self.logger.info(f"table_path: {self.config.table_path}")
        self.logger.info(f"checkpoint_path: {self.config.checkpoint_path}")
        self.logger.info(f"partition_key: {self.config.partition_key}")
        self.logger.info(f"database: {self.config.database}")
        self.logger.info(f"table: {self.config.table}")
        self.logger.info(f"schema_registry_url: {self.config.schema_registry_url}")
        self.logger.info(f"trigger_mode: {self.config.trigger_mode}")
        self.logger.info(f"spark_jars: {self.config.spark_jars}")
        self.logger.info(f"spark_extra_configs: {self.config.spark_extra_configs}")
        self.logger.info(f"apply_table_properties: {self.config.apply_table_properties}")
        self.logger.info(f"delta_zorder_columns: {self.config.delta_zorder_columns}")
        self.logger.info(f"delta_vacuum_retain_hours: {self.config.delta_vacuum_retain_hours}")
        self.logger.info(f"delta_optimize_criteria: {self.config.delta_optimize_criteria}")
        self.logger.info(f"delta_optimize_period_days: {self.config.delta_optimize_period_days}")
        self.logger.info(f"delta_table_properties: {self.config.delta_table_properties}")
        self.logger.info(f"hudi_table_properties: {self.config.hudi_table_properties}")


    def read_from_kafka(self, **kwargs) -> 'SparkSinkConnector':
        """
        Read data from Kafka topic.

        Returns:
            self: For method chaining
        """
        self.config.update_configs(**kwargs)
        self.logger.info(f"Reading from read Kafka...")
        kafka_options = {
            "kafka.bootstrap.servers": self.config.kafka_broker,
            "subscribe": self.config.kafka_topic,
            "minOffsetsPerTrigger": self.config.min_offset,
            "maxOffsetsPerTrigger": self.config.max_offset,
            "failOnDataLoss": self.config.fail_on_data_loss,
            "startingOffsets": self.config.starting_offsets,
            "kafkaConsumer.pollTimeoutMs": self.config.kafka_session_timeout,
            "kafka.request.timeout.ms": self.config.kafka_request_timeout,
            "kafka.session.timeout.ms": self.config.kafka_session_timeout,
        }
        self.logger.info(f"Kafka configurations: ")
        self.logger.info(kafka_options)

        # Add authentication options if credentials are provided
        if self.config.kafka_user and self.config.kafka_password:
            kafka_options.update({
                "kafka.sasl.mechanism": "SCRAM-SHA-512",
                "kafka.security.protocol": "SASL_PLAINTEXT",
                "kafka.sasl.jaas.config": (
                    f"org.apache.kafka.common.security.scram.ScramLoginModule required "
                    f"username='{self.config.kafka_user}' password='{self.config.kafka_password}';"
                )
            })

        # Extra options
        if self.config.kafka_extra_options is not None:
            kafka_options.update(self.config.kafka_extra_options)

        # Build the reader with all options
        reader = self.spark_session.readStream if self.connector_mode == ConnectorMode.STREAM else self.spark_session.read
        reader = reader.format("kafka")
        for key, value in kafka_options.items():
            reader = reader.option(key, value)

        self.dataframe = reader.load()
        self.logger.info(f"✅ Successfully read Kafka batch.")
        return self

    def read_from_clickhouse(self, **kwargs) -> 'SparkSinkConnector':
        """
        Read data from a ClickHouse table or query.
        Note: This method is intended for BATCH mode.

        The following configurations must be set either in the SparkSinkConfig or passed as kwargs:
        - clickhouse_host
        - clickhouse_database
        - clickhouse_table (or clickhouse_query)
        - clickhouse_user
        - clickhouse_password

        Returns:
            self: For method chaining
        """
        self.config.update_configs(**kwargs)
        self.logger.info(f"Reading from ClickHouse...")

        if self.connector_mode == ConnectorMode.STREAM:
            self.logger.error("❌ Reading from ClickHouse (JDBC) is only supported in BATCH mode.")
            raise ValueError("ClickHouse source does not support streaming mode.")

        if not self.config.clickhouse_table and not self.config.clickhouse_query:
            self.logger.error("❌ Either 'clickhouse_table' or 'clickhouse_query' must be provided.")
            raise ValueError("No ClickHouse table or query specified.")

        # Construct JDBC URL
        jdbc_url = (f"jdbc:clickhouse://{self.config.clickhouse_host}:{self.config.clickhouse_port}/"
                    f"{self.config.clickhouse_database}")

        # Determine if we are reading a full table or a custom query
        # Spark's JDBC 'dbtable' option can be a table name or a subquery in parentheses
        dbtable = (f"({self.config.clickhouse_query})" if self.config.clickhouse_query
                   else self.config.clickhouse_table)

        jdbc_options = {
            "url": jdbc_url,
            "dbtable": dbtable,
            "user": self.config.clickhouse_user,
            "password": self.config.clickhouse_password,
            "driver": self.config.clickhouse_driver
        }

        # Add any extra JDBC options
        if self.config.clickhouse_extra_options:
            jdbc_options.update(self.config.clickhouse_extra_options)

        # Log options safely without printing password
        logged_options = jdbc_options.copy()
        if 'password' in logged_options:
            logged_options['password'] = '********'
        self.logger.info(f"ClickHouse JDBC configurations: {logged_options}")

        try:
            reader = self.spark_session.read.format("jdbc")
            if self.config.clickhouse_num_partition:
                reader = reader.option("numPartitions", self.config.clickhouse_num_partition)
                self.logger.info(f"Spark reader numPartitions: {self.config.clickhouse_num_partition}")
            if self.config.clickhouse_partition_column:
                reader = reader.option("partitionColumn", self.config.clickhouse_partition_column)
                self.logger.info(f"Spark reader partitionColumn: {self.config.clickhouse_partition_column}")
            if self.config.clickhouse_lower_bound:
                reader = reader.option("lowerBound", self.config.clickhouse_lower_bound)
                self.logger.info(f"Spark reader lower_bound: {self.config.clickhouse_lower_bound}")
            if self.config.clickhouse_upper_bound:
                reader = reader.option("upperBound", self.config.clickhouse_upper_bound)
                self.logger.info(f"Spark reader upper_bound: {self.config.clickhouse_upper_bound}")
            if self.config.clickhouse_fetch_size:
                reader = reader.option("fetchsize", self.config.clickhouse_fetch_size)
                self.logger.info(f"Spark reader fetchsize: {self.config.clickhouse_fetch_size}")

            self.dataframe = reader.options(**jdbc_options).load()
            self.logger.info(f"✅ Successfully read from ClickHouse source: {dbtable}")
        except Exception as e:
            self.logger.error(f"❌ Failed to read from ClickHouse: {e}")
            raise

        return self

    def get_dataframe(self) -> DataFrame:
        """
        Returns the Spark DataFrame.

        Returns:
            self.dataframe
        """
        return self.dataframe

    def get_logger(self) -> logging.Logger:
        """
        Returns the logger.

        Returns:
            self.logger
        """
        return self.logger

    def set_dataframe(self, dataframe: DataFrame):
        """
        Sets the Spark DataFrame.

        Args:
            dataframe: Spark DataFrame
        """
        self.dataframe = dataframe

    def apply_schema_from_file(self, kind: SchemaKind, file_name: str, message_name: str) -> 'SparkSinkConnector':
        """
        Apply schema from a file to the DataFrame.

        Args:
            kind: Type of schema (AVRO or PROTOBUF)
            file_name: Path to the schema file
            message_name: Name of the message in the schema

        Returns:
            self: For method chaining
        """
        if not self.dataframe:
            self.logger.error("❌ DataFrame not initialized. Call read_from_kafka() first.")
            raise ValueError("DataFrame not initialized")

        if kind == SchemaKind.PROTOBUF:
            self.dataframe = self.dataframe.select(
                from_protobuf("value", message_name, file_name).alias("event")
            )
            self.dataframe = self.dataframe.select("event.*")
            self.logger.info(f"✅ Applied Protobuf schema from file: {file_name}")
        else:
            self.logger.warning(f"⚠️ Schema kind {kind} not implemented for file-based schemas")

        return self

    def apply_schema_from_registry(self, kind: SchemaKind = SchemaKind.AVRO) -> 'SparkSinkConnector':
        """
        Apply schema from registry to the DataFrame.

        Args:
            kind: Type of schema (AVRO or PROTOBUF)

        Returns:
            self: For method chaining
        """
        if not self.dataframe:
            self.logger.error("❌ DataFrame not initialized. Call read_from_kafka() first.")
            raise ValueError("DataFrame not initialized")

        if kind == SchemaKind.AVRO:
            self.dataframe = apply_avro_schema_from_registry(self.dataframe, self.config.schema_registry_url, self.logger)
        else:
            self.logger.warning(f"⚠️ Schema kind {kind} not implemented for registry-based schemas")

        return self

    def foreach_batch(self,
                      foreach_batch_fn: Optional[Callable[[DataFrame, int], None]] = None) -> 'SparkSinkConnector':
        """
        Gets a foreach batch function.

        Args:
            foreach_batch_fn: Function that takes a DataFrame and int
        """
        self.foreach_batch_fn = foreach_batch_fn
        return self

    def transform(self, transformation_fn: Optional[Callable[[DataFrame], DataFrame]] = None) -> 'SparkSinkConnector':
        """
        Apply transformations to the DataFrame.

        Args:
            transformation_fn: Function that takes a DataFrame and returns a transformed DataFrame

        Returns:
            self: For method chaining
        """
        if not self.dataframe:
            self.logger.error("❌ DataFrame not initialized. Call read_from_kafka() first.")
            raise ValueError("DataFrame not initialized")

        if transformation_fn:
            self.dataframe = transformation_fn(self.dataframe)
            self.logger.info("✅ Custom transformations applied to DataFrame")

        return self

    def write_to_s3(self, **kwargs) -> 'SparkSinkConnector':
        """
        Configure writing data to S3 in Hudi format.

        Args:
            kwargs: All the configuration parameters can be overridden here.

        Returns:
            self: For method chaining
        """
        self.config.update_configs(**kwargs)

        if not self.dataframe:
            self.logger.error("❌ DataFrame not initialized. Call read_from_kafka() first.")
            raise ValueError("DataFrame not initialized")

        if self.connector_mode == ConnectorMode.STREAM:
            self.writer = self.dataframe.writeStream
        else:
            self.writer = self.dataframe.write

        if self.config.open_table_format is not None:
            self.writer = self.writer.format(self.config.open_table_format.value)
        if self.config.partition_key is not None:
            self.writer = self.writer.partitionBy(self.config.partition_key)
        if self.config.hoodie_options is not None and self.config.open_table_format == OpenTableFormat.HUDI:
            self.writer = self.writer.options(**self.config.hoodie_options)
        if self.config.write_to_s3_options is not None:
            self.writer = self.writer.options(**self.config.write_to_s3_options)
        if self.config.checkpoint_path is not None:
            self.writer = self.writer.option("checkpointLocation", self.config.checkpoint_path)
        if self.config.table_path is not None:
            self.writer = self.writer.option("path", self.config.table_path)

        if self.foreach_batch_fn is not None:
            self.writer = self.writer.foreachBatch(self.foreach_batch_fn)

        if self.connector_mode == ConnectorMode.BATCH and self.config.output_mode is not None:
            self.writer = self.writer.mode(self.config.output_mode)

        if self.connector_mode == ConnectorMode.STREAM:
            self.writer = self.writer.trigger(**self.config.trigger_mode)

        self.logger.info(f"✅ Configured to write to {self.config.table_path}.")

        return self

    def _apply_table_properties(self):
        try:
            self.logger.info("Registering the database in meta store if not exists ...")
            create_database_command = f"CREATE DATABASE IF NOT EXISTS {self.config.database}"  # LOCATION 's3a://your-bucket/path/to/snapp_logs.db'
            self.logger.info(create_database_command)
            self.spark_session.sql(create_database_command)

            self.logger.info("Registering the table in meta store if not exists ...")
            create_table_command = (f"CREATE TABLE IF NOT EXISTS {self.config.database}.{self.config.table} "
                                    f"USING {self.config.open_table_format.upper()} "
                                    f"LOCATION '{self.config.table_path}'")
            self.logger.info(create_table_command)
            self.spark_session.sql(create_table_command)

            self.logger.info("Applying table properties...")
            # df_properties = self.spark_session.sql(f"SHOW TBLPROPERTIES {self.config.database}.{self.config.table}")
            table_properties = None
            if self.config.open_table_format == OpenTableFormat.DELTA:
                table_properties = self.config.delta_table_properties
            if self.config.open_table_format == OpenTableFormat.HUDI:
                table_properties = self.config.hudi_table_properties
            if table_properties is not None:
                formatted_properties = [
                    f"'{key}' = '{value}'" for key, value in table_properties.items()
                ]
                alter_table_command = (f"ALTER TABLE {self.config.database}.{self.config.table} "
                                       f"SET TBLPROPERTIES ({', '.join(formatted_properties)})")
                self.logger.info(alter_table_command)
                self.spark_session.sql(alter_table_command)
        except Exception as e:
            self.logger.error(e)

    def start(self) -> None:
        """
        Start the writing job and await termination.
        """
        if not self.writer:
            self.logger.error("❌ Writer not initialized. Call write_to_s3() first.")
            raise ValueError("Writer not initialized")

        if self.connector_mode == ConnectorMode.STREAM:
            self.writer.start().awaitTermination()
        else:
            self.writer.save()

        if self.config.apply_table_properties == "enabled":
            self._apply_table_properties()

    def optimize(self, **kwargs) -> 'SparkSinkConnector':
        """
        Optimize the data on S3 in Hudi and Delta format to reduce the number of small objects.

        Args:
            kwargs: All the configuration parameters can be overridden here.

        Returns:
            self: For method chaining
        """
        self.config.update_configs(**kwargs)

        if self.config.table_path is None:
            self.logger.error("❌ Database and Table names should be completed. Provide a valid SparkSinkConfig instance.")
            raise ValueError("table_path not initialized")

        if self.config.open_table_format==OpenTableFormat.DELTA:
            self.logger.info(f"Optimizing the table {self.config.table_path} ...")
            the_command = f"OPTIMIZE delta.`{self.config.table_path}`"
            if self.config.delta_optimize_criteria is None:
                if self.config.execution_date is None:
                    the_day = date.today()
                else:
                    the_day = datetime.strptime(self.config.execution_date, "%Y-%m-%d").date()
                self.config.delta_optimize_criteria = f"{self.config.partition_key}>='{(the_day - timedelta(days=int(self.config.delta_optimize_period_days))).strftime('%Y-%m-%d')}'"
            if self.config.delta_optimize_criteria.strip() != "":
                the_command += f" WHERE {self.config.delta_optimize_criteria}"
            if self.config.delta_zorder_columns is not None:
                the_command += f" ZORDER BY ({self.config.delta_zorder_columns})"
            self.logger.info(the_command)
            self.spark_session.sql(the_command)
        if self.config.open_table_format==OpenTableFormat.HUDI:
            pass
            # self.spark_session.sql(f"CALL run_clustering(table => 'hudi.`{self.config.table_path}`')")

        self.logger.info(f"✅ Optimizations have been ran successfully. To remove the marked files from storage, vacuum is needed.")

        return self

    def vacuum(self, **kwargs) -> 'SparkSinkConnector':
        """
        Remove the unnecessary objects from S3.

        Args:
            kwargs: All the configuration parameters can be overridden here.

        Returns:
            self: For method chaining
        """
        self.config.update_configs(**kwargs)

        if self.config.table_path is None:
            self.logger.error("❌ Database and Table names should be completed. Provide a valid SparkSinkConfig instance.")
            raise ValueError("table_path not initialized")

        if self.config.open_table_format==OpenTableFormat.DELTA:
            self.logger.info(f"Vacuuming the table {self.config.table_path} ...")
            the_command = f"VACUUM delta.`{self.config.table_path}` RETAIN {self.config.delta_vacuum_retain_hours} HOURS"
            self.logger.info(the_command)
            self.spark_session.sql(the_command)
        if self.config.open_table_format==OpenTableFormat.HUDI:
            pass
            # self.spark_session.sql(f"CALL run_compaction(op => 'scheduleAndExecute', table => 'hudi.`{self.config.table_path}`')")

        self.logger.info(f"✅ Vacuum has been ran successfully.")

        return self