# yflow/core/transform/builtin/round_datetime.py
import polars as pl
from yflow.core.transform.registry import register_transformation
from yflow.core.transform.base import BaseTransformation

@register_transformation
class RoundDatetime(BaseTransformation):
    name = "round_datetime"

    def apply(self, lf: pl.LazyFrame) -> pl.LazyFrame:
        col = self.config.get("column")
        precision = self.config.get("precision", "second")
        if not col:
            return lf
        
        return lf.with_columns(
            pl.col(col)
              .cast(pl.Datetime) 
              .alias(col)
        )
