# yflow/core/transform/base.py
from __future__ import annotations
import polars as pl
from typing import Dict, Any

class BaseTransformation:
    """
    Interface cho transformation.
    - name: định danh dùng để registry (lowercase)
    - __init__(config): config là dict đọc từ YAML
    - apply(lf): trả về pl.LazyFrame đã được transform
    """
    name: str = "base_transformation"

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def apply(self, lf: pl.LazyFrame) -> pl.LazyFrame:
        raise NotImplementedError("Subclasses must implement apply()")
