from typing import List, Dict, Any
import pendulum
from datetime import datetime
import polars as pl
import logging
import re 
from yflow.config.pipeline.transforms.replace_config import ReplaceValues, ConvertStrToBoolEnum

# Thiết lập logging cho môi trường production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)


def replace_values_in_column(lf: pl.LazyFrame, config: ReplaceValues) -> pl.LazyFrame:
    """
    Sử dụng API replace_strict để ánh xạ các giá trị trong cột dựa trên Dict Mapping
    
    Parameters:
    - input_col: Tên cột cần áp dụng ánh xạ
    - mapping: Dict Mapping {giá trị gốc: giá trị mới}
    - default_col: Tên cột mặc định để lấy giá trị nếu không khớp (mặc định: input_col)
    
    Returns:
    - pl.Expr: Biểu thức Polars
    """
    input_cols = config.input_cols
    replace_values = config.replace_values
    default_col = config.default_col

    mapping = {
        '': None,  # Chuyển giá trị rỗng thành None
        **replace_values  # Kết hợp với các giá trị thay thế khác nếu có
    }
    logger.info(f"Ánh xạ các giá trị trong cột {input_cols} dựa trên dict Mapping: {mapping}")

    default = pl.col(default_col if default_col else input_cols)
    expr = (
        pl.col(input_cols).replace_strict(mapping, default=default)
    )

    lf = lf.with_columns(expr)  

    return lf


def convert_str_to_bool_enum(lf: pl.LazyFrame, config: ConvertStrToBoolEnum) -> pl.LazyFrame:
    """
    Chuyển đổi giá trị chuỗi trong các cột thành 1 (true), 0 (false), hoặc 2 (khác) và ép kiểu

    Parameters:
    - df: Polars LazyFrame chứa các cột cần xử lý
    - input_cols: Tên cột hoặc danh sách tên cột chứa chuỗi cần chuyển đổi
    - true_value: Giá trị chuỗi biểu thị 'true' (mặc định: 'true')
    - false_value: Giá trị chuỗi biểu thị 'false' (mặc định: 'false')

    """
    input_cols = config.input_cols
    true_value = config.true_value
    false_value =  config.false_value

    logger.info(f"Ép kiểu Enum với trong cột {input_cols} với {true_value} = 1, {false_value} = 0, và các giá trị khác = 2")
    
    expressions = []

    # Chuyển biến input_cols sang dạng List nếu kiểu dữ liệu truyền vào ban đầu và str
    input_cols = [input_cols] if isinstance(input_cols, str) else input_cols

    for col in input_cols:
        expr = (
            pl.when(pl.col(col).cast(pl.String).str.to_lowercase() == str(true_value).lower())
            .then(pl.lit(1))
            .when(pl.col(col).cast(pl.String).str.to_lowercase() == str(false_value).lower())
            .then(pl.lit(0))
            .otherwise(pl.lit(2))
            .cast(pl.Enum(categories=["0", "1", "2"]))
            .alias(col)
        )
        expressions.append(expr)

    for expr in expressions:
        logger.info(f"Convert str_bool_columns expressions: {expr}")
    expressions = expressions[0] if len(expressions) == 1 else expressions

    lf = lf.with_columns(expressions)
    return lf