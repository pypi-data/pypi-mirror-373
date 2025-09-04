from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass(kw_only=True)
class ClickHouseConnectionConfig:
    host: str = "localhost"
    port: int = 8123
    user: str 
    password: str
    database: str