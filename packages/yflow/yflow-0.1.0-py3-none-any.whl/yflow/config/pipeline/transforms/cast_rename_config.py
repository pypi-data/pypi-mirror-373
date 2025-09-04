from dataclasses import dataclass, field
from typing import Dict, List, Any
from .base_config import TransformationConfig

@dataclass(kw_only=True)
class RenameColumns(TransformationConfig):
    input_cols: Dict[str, str]
