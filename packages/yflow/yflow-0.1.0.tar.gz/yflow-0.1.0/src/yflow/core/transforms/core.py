import polars as pl
from typing import Dict, Any, List
import logging
from yflow.config.transformer.function import TransformationFunctionManager
from yflow.core import get_config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)


def transform_polars_lazyframes(lf: pl.LazyFrame, transformations: List[Dict[str, Any]]) -> pl.LazyFrame:
    cfg = TransformationFunctionManager()

    for step, transforms in enumerate(transformations):
        function = transforms.function
        logger.info(f"Step {step + 1}: {function}")

        transform_func: callable = get_config(cfg, name=function)
        lf = transform_func(lf, config=transforms)
    
    return lf