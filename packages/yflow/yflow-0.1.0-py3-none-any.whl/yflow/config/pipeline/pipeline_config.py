from dataclasses import dataclass, field
from typing import Dict, List, Any
from .destinations import DestinationConfig
from .joins import JoinConfig
from .sources import MinIOConfig
from .connections import MinIOConnectionConfig, ClickHouseConnectionConfig

@dataclass
class PipelineConfig:
    sources: MinIOConfig
    destination: DestinationConfig
    join_configs: Dict[str, JoinConfig]
    connections: Dict[str, MinIOConnectionConfig | ClickHouseConnectionConfig]