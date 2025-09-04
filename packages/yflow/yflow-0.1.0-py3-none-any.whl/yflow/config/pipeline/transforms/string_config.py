from dataclasses import dataclass, field
from typing import Dict, List, Any
from .base_config import TransformationConfig

@dataclass(kw_only=True)
class SplitColumn(TransformationConfig):
    output_col1: str
    output_col2: str
    separator: str = ','