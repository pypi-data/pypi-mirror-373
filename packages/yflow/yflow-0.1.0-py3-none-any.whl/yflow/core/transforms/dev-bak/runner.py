# yflow/core/transform/runner.py
from typing import List, Dict, Any
import polars as pl
from .registry import get_transformation, load_external_transformations
import logging

logger = logging.getLogger(__name__)

def transform_polars_lazyframes(
    lf: pl.LazyFrame,
    transformations: List[Dict[str, Any]],
    plugins: List[str] | None = None
) -> pl.LazyFrame:
    """
    transformations: list các dict đọc từ YAML. Mỗi dict phải có key 'function' (tên hoặc path)
    plugins: list module paths để import (plugin modules)
    """
    if plugins:
        load_external_transformations(plugins)

    for step, transforms in enumerate(transformations):
        function = transforms.get("function")
        logger.info(f"Thực hiện bước {step + 1}: {function}")

        # Lấy class (hoặc import từ path)
        TransformationClass = get_transformation(function)
        tr = TransformationClass(transforms)
        print(tr)
        # lf = tr.apply(lf)

    return lf
