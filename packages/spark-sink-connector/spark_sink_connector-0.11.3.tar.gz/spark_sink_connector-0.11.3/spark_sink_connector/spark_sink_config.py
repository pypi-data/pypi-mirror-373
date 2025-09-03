import json
import os
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class SparkSinkConfig:
    """Configuration container for SparkSinkConnector with dynamic fields and default values support."""
    _dynamic_fields: Dict[str, Any] = field(default_factory=dict, init=False, repr=False)

    _dynamic_defaults: Dict[str, Any] = field(default_factory=lambda: {
        # kafka default configs
        "kafka_broker": "kafka.de.data.snapp.tech:9092",
        "kafka_topic": None,
        "kafka_user": None,
        "kafka_password": None,
        "kafka_request_timeout": "30000",
        "kafka_session_timeout": "30000",
        "min_offset": "1",
        "max_offset": "2000000",
        "starting_offsets": "earliest",
        "kafka_extra_options": None,
        "fail_on_data_loss": "false",

        # s3 default configs
        "s3_endpoint": "http://s3.teh-1.snappcloud.io",
        "s3_access_key": None,
        "s3_secret_key": None,
        "table_path": None,
        "checkpoint_path": None,
        "s3a_path_style_access": "true",
        "s3a_connection_ssl_enabled": "false",
        "s3a_impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",

        # spark session default configs
        "trigger_mode": {"availableNow": True},
        "spark_jars": "org.apache.spark:spark-avro_2.12:3.5.1,"
                      "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,"
                      "org.apache.kafka:kafka-clients:3.9.0,"
                      "org.apache.spark:spark-protobuf_2.12:3.5.1",
        "spark_extra_configs": {
            "spark.sql.session.timeZone": "Asia/Tehran",
            "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",
            "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog",
            "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
            "spark.sql.legacy.timeParserPolicy": "LEGACY",
            "spark.databricks.delta.retentionDurationCheck.enabled": "false",
            "spark.sql.catalogImplementation": "hive",
        },
        "delta_spark_extra_configs": {
            "spark.hive.metastore.uris": "thrift://172.21.88.59:9083"
        },
        "hudi_spark_extra_configs": {
            "spark.hive.metastore.uris": "thrift://172.21.88.94:9083"
        },

        # ClickHouse Configurations
        "clickhouse_host": '172.21.16.1',
        "clickhouse_port": 8123,
        "clickhouse_user": None,
        "clickhouse_password": None,
        "clickhouse_database": 'default',
        "clickhouse_table": None,
        "clickhouse_query": None,
        "clickhouse_driver": 'com.clickhouse.jdbc.ClickHouseDriver',
        "clickhouse_num_partition": None,
        "clickhouse_partition_column": None,
        "clickhouse_fetch_size": 50000,
        "clickhouse_lower_bound": None,
        "clickhouse_upper_bound": None,
        "clickhouse_extra_options": {},

        # open table format shared default configs
        "open_table_format": None,
        "output_mode": None,
        "partition_key": None,
        "database": None,
        "table": None,
        "write_to_s3_options": None,

        # hudi specific default configs
        "hoodie_options": {
            "hoodie.datasource.write.table.type": "COPY_ON_WRITE",
            # hive meta store
            "hoodie.datasource.write.hive_style_partitioning": "true",
            "hoodie.datasource.meta.sync.enable": "true",
            "hoodie.datasource.hive_sync.mode": "hms",
            "hoodie.datasource.hive_sync.metastore.uris": "thrift://172.21.88.94:9083",
            # automatic cleaning
            "hoodie.cleaner.policy": "KEEP_LATEST_COMMITS",
            "hoodie.cleaner.commits.retained": "10",
            "hoodie.clean.automatic": "true",
            "hoodie.clean.async": "true",
            # Controls how often async cleaning is triggered by commits during writes (after every 2 commits)
            'hoodie.cleaner.trigger.strategy': 'NUM_COMMITS',
            'hoodie.cleaner.max_commits': '2',
            # Configurations for scheduling asynchronous compaction (writer schedules, executor runs)
            'hoodie.compaction.trigger.strategy': 'NUM_COMMITS',  # Other options: 'TIME_ELAPSED', 'NUM_AND_TIME'
            # Trigger compaction scheduling based on number of commits
            'hoodie.compaction.delta_commits': '5',  # Schedule compaction after N delta commits
        },
        "hudi_table_properties": None,

        # delta specific default configs
        "delta_table_properties" : {
            'delta.logRetentionDuration': 'interval 1 days',
        },
        "delta_zorder_columns": None,
        "delta_vacuum_retain_hours": 72,
        "delta_optimize_criteria": None,
        "delta_optimize_period_days": 1,

        # schema registry default configs
        "schema_registry_url": "http://schema-registry.de.data.snapp.tech:8081",

        # logger default configs
        "logger_format": "%(asctime)s | %(name)s - %(funcName)s - %(lineno)d | %(levelname)s - %(message)s",

        # connector default configs
        "running_mode": "normal",
        "execution_date": None,
        "configurations_dictionary": None,
        "apply_table_properties": "enabled",
    }, init=False, repr=False)

    def __init__(self, **kwargs):
        """
        Custom __init__ method to allow dynamic fields to be passed as keyword arguments.
        """
        # Explicitly initialize _dynamic_fields
        self._dynamic_fields = {}
        predefined_fields = {f.name for f in self.__dataclass_fields__.values()}

        print("-"*3)
        for field_name in predefined_fields:
            if field_name not in ('_dynamic_defaults', '_dynamic_fields'):
                if os.getenv(field_name.upper()) is not None:
                    setattr(self, field_name, os.getenv(field_name.upper()))
                print(field_name)
            # if not hasattr(self, field_name):
            #     default_value = self.__dataclass_fields__[field_name].default_factory()
            #     setattr(self, field_name, default_value)
            #     if os.getenv(field_name.upper()) is not None:
            #         setattr(self, field_name, os.getenv(field_name.upper()))
        print("-"*3)

        for key, value in kwargs.items():
            if key in predefined_fields:
                setattr(self, key, value)
            else:
                self._dynamic_fields[key] = value

        # Initialize defaults for predefined fields
        field_name = '_dynamic_defaults'
        default_value = self.__dataclass_fields__[field_name].default_factory()
        setattr(self, field_name, default_value)

        # Apply defaults for dynamic fields
        for key, default_value in self._dynamic_defaults.items():
            if key not in self._dynamic_fields:
                self._dynamic_fields[key] = os.getenv(key.upper(), default_value)

        if self.database is not None and self.table is not None:
            self.full_table_name = f'{self.database.replace("_", "-")}-{self.table.replace("_", "-")}'
            if self.checkpoint_path is None:
                self.checkpoint_path = f"s3a://{self.full_table_name}-bucket/checkpoints/{self.full_table_name}"
            if self.table_path is None:
                self.table_path = f's3a://{self.full_table_name}-bucket/{self.full_table_name}'
            self.hoodie_options["hoodie.table.name"] = self.table
            self.hoodie_options["hoodie.database.name"] = self.database

        if self.configurations_dictionary is not None:
            try:
                loaded_configs = json.loads(self.configurations_dictionary)
                self.update_configs(**loaded_configs)
            except Exception as ex:
                print(f"Failed to load configurations dictionary: {ex}")

    def _get_config(self, key, arg_value):
        """
        Retrieves configuration, prioritizing existing attribute value (from constructor),
        then environment variables, then defaults.
        """
        if arg_value is not None:
            return arg_value

        env_key = key.upper()
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value

        # Default values for dynamic fields
        if key in self._dynamic_defaults:
            return self._dynamic_defaults[key]

        return None

    def update_configs(self, **kwargs):
        """
        updates the configurations
        """
        predefined_fields = {f.name for f in self.__dataclass_fields__.values()}
        for key, value in kwargs.items():
            if key in predefined_fields:
                setattr(self, key, value)
            else:
                self._dynamic_fields[key] = value

    def __getattr__(self, key):
        """
        Override __getattr__ to retrieve dynamic fields from _dynamic_fields.
        """
        if key in self._dynamic_fields:
            return self._dynamic_fields[key]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")

    def to_dict(self):
        """
        Convert the entire configuration (predefined and dynamic fields) to a dictionary.
        """
        config = {field: getattr(self, field) for field in self.__dataclass_fields__}
        config.update(self._dynamic_fields)
        return config
