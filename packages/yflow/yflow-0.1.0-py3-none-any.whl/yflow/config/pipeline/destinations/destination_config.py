from dataclasses import dataclass, field
from typing import Dict

@dataclass(kw_only=True)
class DestinationConfig:
    database: str
    table_name: str
    metadata: Dict[str, str] = field(default_factory=dict)
    engine: str
    order_by: str