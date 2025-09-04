from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class JoinConfig:
    main: str
    name: str
    other: List[Dict[str, Any]]
    select_columns: List[str]
    transformations: List[Dict[str, Any]]