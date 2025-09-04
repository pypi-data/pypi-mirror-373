from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from .base_config import TransformationConfig

@dataclass(kw_only=True)
class ReplaceValues(TransformationConfig):
    replace_values: Dict[str, str] = field(default_factory=dict)
    default_col: Optional[bool] = None


@dataclass(kw_only=True)
class ConvertStrToBoolEnum(TransformationConfig):
    true_value: str = '1'
    false_value: str = '0'