from dataclasses import dataclass, field
from typing import Dict, List, Any, Type

@dataclass
class SourceConfig:
    source_system: str
    connection_name: str
    data_types: List[Dict[str, Any]]
    select_columns: List[str] = '*'
    metadata: Dict[str, Any] = field(default_factory=dict)
    transformations: List[Dict[str, Any] | Type] = field(default_factory=list)

