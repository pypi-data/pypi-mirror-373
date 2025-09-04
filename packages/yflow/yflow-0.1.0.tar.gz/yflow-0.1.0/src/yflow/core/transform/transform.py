import transform_functions.utils as utils
import extract_functions.extract_functions as extract_functions

from typing import List, Dict, Any
import pendulum
import polars as pl
import logging

# Thiết lập logging cho môi trường production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


#################################################
#                                               #
#          UDF: Gen Polars Objects              #
#                                               #
#################################################


def transform_polars_lazyframes(lf: pl.LazyFrame, transformations: list[dict]) -> pl.LazyFrame:
    for step, transforms in enumerate(transformations):
        # logger.info(transforms)
        function = transforms.get('function')

        logger.info(f"  Bước {step + 1}: {function}")

        if function.strip().lower() == 'round_datetime':
            lf = lf.with_columns(round_datetime(config=transforms))

        elif function.strip().lower() == 'split_str_col_to_columns':
            input_cols = transforms.get('input_cols')
            output_col_suffix = transforms.get('output_col_suffix', 'struc')
            is_rewrite = transforms.get('is_rewrite', True)
            output_col = input_cols if is_rewrite else input_cols + '_' + output_col_suffix
            lf = lf.with_columns(split_str_col_to_columns(config=transforms)).unnest(output_col)
            
        elif function.strip().lower() == 'convert_str_bool_columns':
            lf = lf.with_columns(convert_str_bool_columns(config=transforms))
            
        elif function.strip().lower() == 'replace_column_values':
            lf = lf.with_columns(replace_column_values(config=transforms))
            
        elif function.strip().lower() == 'strip_suffix_column_values':
            lf = lf.with_columns(strip_suffix_column_values(config=transforms))

        elif function.strip().lower() == 'lower_column_values':
            lf = lf.with_columns(lower_column_values(config=transforms))

        elif function.strip().lower() == 'extract_column_by_regex':
            lf = lf.with_columns(extract_column_by_regex(config=transforms))

        elif function.strip().lower() == 'cast_str_columns':
            strip_suffix_expr, replace_expr, cast_expr = cast_str_columns(config=transforms)
            lf = lf.with_columns(strip_suffix_expr).with_columns(replace_expr).with_columns(cast_expr)

        elif function.strip().lower() == 'rename_columns':
            new_columns = rename_columns(config=transforms)
            lf = lf.rename(new_columns)
            lf = filter_columns(lf, config=transforms)

        elif function.strip().lower() == 'replace_null_or_empty':
            lf = lf.with_columns(replace_null_or_empty(config=transforms))
        elif function.strip().lower() == 'fill_null':
            lf = lf.with_columns(fill_null(config=transforms))

        elif function.strip().lower() == 'convert_timestamp_to_datetime':
            strip_suffix_expr, replace_expr, datetime_expr, round_datetime_expr = convert_timestamp_to_datetime(config=transforms)
            lf = lf.with_columns(strip_suffix_expr).with_columns(replace_expr).with_columns(datetime_expr).with_columns(round_datetime_expr)

        elif function.strip().lower() == 'cast_and_rename_str_columns':
            strip_suffix_expr, replace_expr, round_datetime_expr, cast_columns, cast_date_columns, new_columns = cast_and_rename_str_columns(config=transforms)

            lf = (lf.with_columns(strip_suffix_expr).with_columns(replace_expr)
                  .cast(cast_columns).cast(cast_date_columns).with_columns(round_datetime_expr).rename(new_columns)
                  )
            lf = filter_columns(lf, config=transforms)

        elif function.strip().lower() == 'filter':
            lf = lf.filter(filter_polars_lazyframes(config=transforms))

        elif function.strip().lower() == 'custom_transformation':
            expr = eval(transforms.get('input_expr'))
            logger.info(f'Custom Expression: {expr}')
            lf = lf.with_columns(expr)

    return lf



def create_polars_lazyframes(
    cursor: Any,
    table_configs: List[Dict[str, Any]],
    exec_date: str = None
) -> Dict[str, pl.LazyFrame]:
    """
    Tạo một Dictionary chứa các Polars LazyFrame lấy dữ liệu từ nguồn theo cấu hình tương ứng

    Args:
        table_configs (List[Dict[str, Any]]): Danh sách các Dictionary chứa thông tin bảng, điều kiện, biến đổi và kiểu dữ liệu
        exec_date (str): Ngày thực thi để thay thế @exec_date trong where_condition. Mặc định là ngày T - 1  (YYYY-MM-DD)

    Returns:
        Dict[str, pl.LazyFrame]: Dictionary với key là table_name và value là Polars LazyFrame

    Raises:
        ValueError: Nếu table_configs rỗng hoặc thiếu thông tin cần thiết.
        Exception: Nếu có lỗi khi truy vấn hoặc xử lý dữ liệu.
    """
    try:
        if not table_configs:
            raise ValueError("List table_configs không được rỗng")

        # Nếu không cung cấp exec_date, mặc định sử dụng ngày T-1
        if exec_date is None:
            exec_date = pendulum.today().subtract(days=1).strftime('%Y-%m-%d')

        logger.info(f'Execution Date: {exec_date}')
        
        result_lfs = {}

        for config in table_configs:
            source_type = config.get('source_type', 'files')
            table_name = config.get('table_name')
            select_columns = config.get('select_columns', '*') if config.get('select_columns') else '*'
            config['select_columns'] = select_columns
            data_types = config.get('data_types', None)
            transformations = config.get('transformations', None)
            
            logger.info(f"\n\nĐang xử lý bảng {table_name} ...\n")
            
            # Lọc data_types nếu select_columns có giá trị --> Chỉ ép các trường tồn tại trong LazyFrame
            
            if select_columns != '*' and data_types and source_type != 'files':
                # columns_list = [col.strip() for col in select_columns.split(',') if col]
                data_types = {
                    col: data_types[col] for col in select_columns 
                    if col in data_types
                    }
                logger.info(f"Data types sau khi lọc: {data_types}")


            logger.info('Chuyển đổi config schema về đúng dạng của Polars LazyFrame')
            logger.info(f'Schema bảng {table_name}: {data_types}')
            data_types = {col: utils.parse_polars_type(type_str) for col, type_str in data_types.items()}
            logger.info(f'Data Types đã chuẩn hóa" {data_types}')
            config['data_types'] = data_types

            # logger.info(config)
            lf, count = extract_functions.gen_lazyframe(cursor=cursor, config=config, exec_date=exec_date)  
                
            logger.info(f"Đã tạo LazyFrame cho bảng {table_name}")  

            if count != 0 and transformations:
                logger.info(f'\nÁp dụng các biến đổi cho bảng {table_name}')
                lf = transform_polars_lazyframes(lf, transformations)
            
            # Lưu LazyFrame vào kết quả
            result_lfs[table_name] = lf

        return result_lfs

    except Exception as e:
        logger.error(f"Lỗi khi tạo LazyFrame: {str(e)}")
        raise