from typing import List, Dict, Any
import polars as pl
from yflow.core import load_callable
from yflow.config.pipeline import PipelineConfig, MinIOConfig
from yflow.config.extractor.extractor_config import ExtractorConfigManager


def extractor_factory(table_config: MinIOConfig, connection_config: Dict[str, Any]) -> pl.LazyFrame:
    # Khởi tạo config manager với extractor mặc định
    cfg = ExtractorConfigManager()

    path = cfg.get_func_path(source_system=table_config.source_system, source_type=table_config.source_type)
    extractor_fn: callable = load_callable(path)
    lf = extractor_fn(source_config=table_config, connection_config=connection_config)

    return lf
