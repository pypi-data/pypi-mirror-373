from typing import List, Dict, Any
import pendulum
from datetime import datetime
import polars as pl
import logging
import re 
from yflow.config.pipeline.transforms.string_config import SplitColumn



# Thiết lập logging cho môi trường production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)



def split_column(lf: pl.LazyFrame, config: SplitColumn) -> pl.LazyFrame:
    """
    Tách một cột chuỗi thành hai cột mới dựa trên ký tự phân tách.

    Parameters:
    - input_cols: Tên cột chứa chuỗi cần tách
    - separator: Ký tự phân tách (mặc định: ',')
    - output_col1: Tên cột đầu ra thứ nhất (mặc định: 'column_1')
    - output_col2: Tên cột đầu ra thứ hai (mặc định: 'column_2')

    Returns:
    - pl.LazyFrame
    """

    input_cols = config.input_cols
    separator = config.separator
    output_col1 = config.output_col1
    output_col2 = config.output_col2

    logger.info(f"Tách cột {input_cols} thành 2 cột mới {output_col1} và {output_col2} theo ký tự phân tách '{separator}'")

    
    # Áp dụng logic tách chuỗi cho từng cột
    expr = (
        pl.col(input_cols).cast(pl.String).str.split(separator)
        .list.to_struct(fields=[output_col1, output_col2])  # Chuyển thành struct
        .alias(input_cols)
    )

    logger.info(f"Expression: {expr}")
    
    lf = lf.with_columns(expr).unnest(input_cols)

    return lf