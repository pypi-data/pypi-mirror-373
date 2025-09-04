from dataclasses import dataclass, field
from typing import Dict, List, Any

@dataclass(kw_only=True)
class TransformationConfig:
    function: str
    input_cols: Dict[str, str] | str

