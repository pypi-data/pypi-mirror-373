# Spark Sink Connector

A flexible connector for reading data from Kafka and writing to S3 in Delta or Hudi format, with support for Avro and Protobuf schema formats.
Published in
https://pypi.org/project/spark-sink-connector/#history


Find more examples in `/examples/original` and `/examples/refactored`.

## Features

- Stream data from Kafka topics to S3 storage
- Support for both Avro and Protobuf schemas
- Schema Registry integration
- Delta Lake and Hudi output formats
- Configurable partitioning and output modes
- Custom data transformation capabilities
- Fluent API with method chaining

## Usage

Install from gitlab package registry ([Read More](https://confluence.snapp.ir/display/DEVOPS/GitLab+Package+Registry+User+Guide#GitLabPackageRegistryUserGuide-SampleCI/CDJob)):

    wget --header "PRIVATE-TOKEN: THE-TOKEN" \
         --user "username: THE-TOKEN"
         "https://gitlab.snapp.ir/api/v4/projects/6311/packages/generic/spark-sink-connector/$VERSION/spark_sink_connector.whl"
    pip install spark_sink_connector.whl

Released package versions history:  
https://gitlab.snapp.ir/navid.farhadi/spark-sink-connector/-/packages/


or, install from pypi:

    pip install spark-sink-connector==VERSION

## Development

### Prerequisites

- Python 3.7+
- Apache Spark 3.5.1+
- Access to Kafka cluster
- Access to S3-compatible storage (AWS S3, MinIO, etc.)

### Manual Build

```bash
python -m build
```

### Dependencies

```bash
pip install delta-spark==3.3.0 confluent-kafka==2.7.0 requests==2.32.3 pyspark==3.5.1
```

## Configuration

The connector can be configured through environment variables or by passing parameters directly:

### Environment Variables

```bash
# Kafka Configuration
export KAFKA_BROKER="kafka.example.com:9092"
export KAFKA_TOPIC="your-topic"
export KAFKA_USER="your-username"  # Optional for SASL authentication
export KAFKA_PASSWORD="your-password"  # Optional for SASL authentication
export KAFKA_REQUEST_TIMEOUT="30000"
export KAFKA_SESSION_TIMEOUT="30000"
export MIN_OFFSET="1"
export MAX_OFFSET="2000000"
export STARTING_OFFSET="earliest"  # or "latest"

# Schema Registry
export SCHEMA_REGISTRY_URL="http://schema-registry.example.com:8081"

# S3 Configuration
export S3_ACCESS_KEY="your-access-key"
export S3_SECRET_KEY="your-secret-key"
```

## Basic Usage

### Simple Example

```python
from spark_sink_connector.spark_sink_connector import SparkSinkConnector, SchemaKind, ConnectorOutputMode

# Create connector with default configuration (from environment variables)
connector = SparkSinkConnector()

# Read from Kafka, apply schema, and write to S3 in Delta format
connector.read_from_kafka()
    .apply_schema_from_registry(SchemaKind.AVRO)
    .write_delta_to_s3(
        partition_key="created_at",
        output_mode=ConnectorOutputMode.APPEND,
        bucket_name="your-data-bucket"
    )
    .start()
```

### Advanced Example with Custom Configuration and Transformations

```python
from spark_sink_connector.spark_sink_connector import SparkSinkConnector, SparkSinkConfig, SchemaKind, ConnectorOutputMode
from pyspark.sql.functions import col, to_timestamp, current_timestamp
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

# Create custom configuration
config = SparkSinkConfig(
    kafka_broker="kafka.example.com:9092",
    kafka_topic="user-events",
    s3_access_key="my-access-key",
    s3_secret_key="my-secret-key",
    s3_endpoint="http://s3.example.com",
    schema_registry_url="http://schema-registry.example.com:8081"
)


# Define a custom transformation function
def transform_data(df):
    return df
        .withColumn("created_at_ts", to_timestamp(col("created_at")))
        .withColumn("processing_time", current_timestamp())
        .filter(col("deleted_at").isNull())


# Create connector with custom config and logger
connector = SparkSinkConnector(config=config, logger=logger)

# Execute the pipeline with custom transformation
connector.read_from_kafka()
    .apply_schema_from_registry(SchemaKind.AVRO)
    .transform(transform_data)
    .write_delta_to_s3(
        partition_key="created_at_ts",
        output_mode=ConnectorOutputMode.APPEND,
        bucket_name="user-events-bucket"
    )
    .start()
```

### Using Protobuf Schema from File

```python
from spark_sink_connector.spark_sink_connector import SparkSinkConnector
from spark_sink_connector.enums import SchemaKind, ConnectorOutputMode

connector = SparkSinkConnector()

# Read from Kafka and apply Protobuf schema from file
connector.read_from_kafka()
    .apply_schema_from_file(
        kind=SchemaKind.PROTOBUF,
        file_name="path/to/schema.desc",
        message_name="Event"
    )
    .write_delta_to_s3(
        partition_key="timestamp",
        output_mode=ConnectorOutputMode.APPEND,
        bucket_name="events-bucket"
    )
    .start()
```

## API Reference

### `SparkSinkConnector`

The main connector class for reading from Kafka and writing to S3.

#### Constructor

```python
SparkSinkConnector(config=None, logger=None)
```

- `config`: Optional `SparkSinkConfig` object. If not provided, configuration is loaded from environment variables.
- `logger`: Optional logger instance. If not provided, a default logger is created.

#### Methods

- `read_from_kafka()`: Configures and reads data from Kafka.
- `apply_schema_from_file(kind, file_name, message_name)`: Applies schema from a file.
- `apply_schema_from_registry(kind)`: Applies schema from Schema Registry.
- `transform(transformation_fn)`: Applies custom transformations to the DataFrame.
- `write_delta_to_s3(partition_key, output_mode, bucket_name)`: Configures writing to S3 in Delta format.
- `write_hudi_to_s3(partition_key, output_mode, bucket_name)`: Configures writing to S3 in Hudi format.
- `start()`: Starts the streaming job and awaits termination.

### `SparkSinkConfig`

Configuration container for `SparkSinkConnector`.

#### Constructor

```python
SparkSinkConfig(**kwargs)
```

Accepts keyword arguments for any configuration parameter. Missing parameters are loaded from environment variables.

### Enums

#### `SchemaKind`

Enum for schema types:
- `SchemaKind.AVRO`: For Avro schemas
- `SchemaKind.PROTOBUF`: For Protobuf schemas

#### `ConnectorOutputMode`

Enum for output modes:
- `ConnectorOutputMode.APPEND`: Append mode
- `ConnectorOutputMode.UPSERT`: Upsert mode
- `ConnectorOutputMode.OVERWRITE`: Overwrite mode


#### `ConnectorMode`

Enum for connector modes:
- `ConnectorMode.STREAM` = Stream mode
- `ConnectorMode.BATCH` = Batch mode


## Versioning

Automatic versioning is handled by commit message in CICD. Commit message should be started with fix, feat or feat!.

 - `fix: message` to increase patch version
 - `feat: message` to increase minor version
 - `feat!: message` to increase major version

A complete version number is like: `major.minor.patch`
