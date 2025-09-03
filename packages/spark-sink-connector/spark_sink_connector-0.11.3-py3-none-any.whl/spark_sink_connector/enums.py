from enum import Enum


class SchemaKind(Enum):
    AVRO = 'avro'
    PROTOBUF = 'proto'

class ConnectorOutputMode(str, Enum):
    APPEND = "append"
    OVERWRITE = "overwrite"
    UPSERT = "upsert"

class OpenTableFormat(str, Enum):
    HUDI = "hudi"
    DELTA = "delta"

class ConnectorMode(Enum):
    STREAM = 'stream'
    BATCH = 'batch'

class RunningMode(Enum):
    NORMAL = 'normal'
    OPTIMIZATION = 'optimization'
