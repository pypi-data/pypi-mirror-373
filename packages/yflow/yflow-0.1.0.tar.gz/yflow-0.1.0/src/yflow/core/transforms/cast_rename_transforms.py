from typing import List, Dict, Any
import pendulum
from datetime import datetime
import polars as pl
import logging
import re 
from yflow.config.pipeline.transforms.cast_rename_config import RenameColumns

# Thiết lập logging cho môi trường production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)


def rename_columns(lf: pl.LazyFrame, config: RenameColumns) -> pl.LazyFrame:
    """
    Chuyển đổi các cột chuỗi sang kiểu dữ liệu mới và đổi tên cột nếu cần

    Parameters:
    - input_cols: Tên cột hoặc danh sách tên cột cần chuyển đổi
    - new_dtype: Kiểu dữ liệu mới (mặc định là pl.String)
    - new_col_name: Tên cột mới (mặc định là tên cột gốc)

    Returns:
    - pl.Expr: Biểu thức Polars
    """
    
    input_cols = config.input_cols
    old_columns = [key for key in input_cols]
    new_columns = [value for key, value in input_cols.items()]

    logger.info(f"Đổi tên các cột {old_columns} thành {new_columns}")

    lf = lf.rename(input_cols)

    return lf
