import pendulum
import logging
import re
from yflow._typing import BasePipelineConfig, YflowDatabaseConfig
from yflow.config.pipeline import MinIOConfig
import polars as pl

from typing import Dict, List, Any

# Thiết lập logging cho môi trường production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)


def merge_sub_dicts(sub_dicts):
    merged_dict = {}
    for item in sub_dicts:
        merged_dict.update(item)
    
    return merged_dict


def filter_data_types(config: MinIOConfig):
    select_columns = config.select_columns

    if select_columns != '*':
        data_types = {col: data_types[col] for col in select_columns if col in data_types}

    return data_types

def parse_polars_type(type_str):
    """
    Chuyển đổi chuỗi kiểu dữ liệu từ YAML thành kiểu Polars thực tế.
    Hỗ trợ tất cả các kiểu dữ liệu Polars và xử lý định dạng như pl.Enum([...]).
    """
    # Loại bỏ khoảng trắng thừa
    type_str = type_str.strip()

    # Ánh xạ các kiểu dữ liệu Polars cơ bản
    type_mapping = {
        'pl.Int8': pl.Int8,
        'pl.Int16': pl.Int16,
        'pl.Int32': pl.Int32,
        'pl.Int64': pl.Int64,
        'pl.UInt8': pl.UInt8,
        'pl.UInt16': pl.UInt16,
        'pl.UInt32': pl.UInt32,
        'pl.UInt64': pl.UInt64,
        'pl.Float32': pl.Float32,
        'pl.Float64': pl.Float64,
        'pl.Boolean': pl.Boolean,
        'pl.Utf8': pl.Utf8,
        'pl.String': pl.String,
        'pl.Binary': pl.Binary,
        'pl.Date': pl.Date,
        'pl.Datetime': pl.Datetime(time_unit='ms', time_zone=None),
        'pl.Datetime64': pl.Datetime(time_unit='us', time_zone=None),
        'pl.Time': pl.Time,
        'pl.Duration': pl.Duration(time_unit='ms'),
        'pl.Categorical': pl.Categorical,
        'pl.Null': pl.Null,
    }

    # Xử lý kiểu cơ bản
    if type_str in type_mapping:
        # logger.info(f'type_str: {type_str}')
        # logger.info(f'normalized type_str: {type_mapping[type_str]}')
        return type_mapping[type_str]

    # Xử lý pl.Enum([...])
    if type_str.startswith('pl.Enum'):
        match = re.match(r'pl\.Enum\(\[(.*?)\]\)', type_str)
        if not match:
            raise ValueError(f"Không thể phân tích pl.Enum từ {type_str}")
        categories_str = match.group(1)
        # Tách danh sách categories, loại bỏ khoảng trắng và xử lý dấu ngoặc kép
        categories = [cat.strip().strip("'\"") for cat in categories_str.split(',') if cat.strip()]
        if not categories:
            raise ValueError(f"Danh sách categories rỗng trong {type_str}")
        return pl.Enum(categories)

    # Xử lý pl.List(inner_type)
    if type_str.startswith('pl.List'):
        match = re.match(r'pl\.List\((.*?)\)', type_str)
        if not match:
            raise ValueError(f"Không thể phân tích pl.List từ {type_str}")
        inner_type_str = match.group(1).strip()
        inner_type = parse_polars_type(inner_type_str)  # Đệ quy để xử lý kiểu bên trong
        return pl.List(inner_type)

    # Xử lý pl.Array(inner_type, size)
    if type_str.startswith('pl.Array'):
        match = re.match(r'pl\.Array\((.*?),\s*(\d+)\)', type_str)
        if not match:
            raise ValueError(f"Không thể phân tích pl.Array từ {type_str}")
        inner_type_str, size = match.group(1).strip(), int(match.group(2))
        inner_type = parse_polars_type(inner_type_str)
        return pl.Array(inner_type, size)

    # Xử lý pl.Struct(fields)
    if type_str.startswith('pl.Struct'):
        match = re.match(r'pl\.Struct\(\{(.*?)\}\)', type_str)
        if not match:
            raise ValueError(f"Không thể phân tích pl.Struct từ {type_str}")
        fields_str = match.group(1)
        # Phân tích các trường trong struct (ví dụ: 'field1: pl.Int32, field2: pl.Utf8')
        fields = {}
        for field in re.split(r',\s*(?![^{]*\})', fields_str):
            if not field.strip():
                continue
            field_name, field_type_str = [part.strip() for part in field.split(':', 1)]
            fields[field_name.strip("'\"")] = parse_polars_type(field_type_str)
        return pl.Struct(fields)

    # Xử lý Nullable(type)
    if type_str.startswith('Nullable'):
        match = re.match(r'Nullable\((.*?)\)', type_str)
        if not match:
            raise ValueError(f"Không thể phân tích Nullable từ {type_str}")
        inner_type_str = match.group(1).strip()
        inner_type = parse_polars_type(inner_type_str)
        return inner_type  # Trong Polars, Nullable được xử lý tự động, không cần bọc

    raise ValueError(f"Kiểu dữ liệu không hỗ trợ: {type_str}")




#################################################
#                                               #
#          UDF: Gen Source Configs              #
#                                               #
#################################################


import json

def format_json_string(json_data):
    """
    Hàm chuẩn hóa định dạng chuỗi JSON cho dễ đọc.

    Args:
        json_data (dict or str): Dữ liệu JSON dạng dict hoặc chuỗi JSON.

    Returns:
        str: Chuỗi JSON đã được định dạng lại.
    """
    # Nếu đầu vào là chuỗi, chuyển thành dict
    if isinstance(json_data, str):
        try:
            json_data = json.loads(json_data)
        except json.JSONDecodeError as e:
            return f"Lỗi định dạng JSON: {e}"

    # Trả về chuỗi JSON đã được format
    return json.dumps(json_data, indent=4, ensure_ascii=False)




    


#################################################
#                                               #
#          UDF: Gen Polars Objects              #
#                                               #
#################################################



def str_date_to_timestamp(date_string, format=None, mini_timestamp=False):
    """
    Chuyển chuỗi thời gian thành chuỗi timestamp
    
    Args:
        date_string (str): Chuỗi thời gian đầu vào (VD: '2025-07-24 11:04:00')
        format (str, optional): Định dạng của chuỗi thời gian (VD: '%d/%m/%Y %H:%M')
    
    Returns:
        str: Chuỗi timestamp
    """
    try:
        if format:
            dt = pendulum.datetime.strptime(date_string, format)
        else:
            dt = pendulum.parse(date_string, strict=False)
        
        # Chuyển datetime thành chuỗi timestamp
        timestamp = str(int(dt.timestamp()) * 1000) if mini_timestamp else str(int(dt.timestamp()))

        return timestamp
    
    except ValueError as e:
        return f"Error: Invalid date string or format. {str(e)}"


def replace_exec_date(query_string, exec_date):

    if not query_string:
        return query_string
    
    result = query_string
    if '@exec_date' in result:
        result = result.replace('@exec_date', f"'{exec_date}'")
    elif '@exec_ms_unix_tsmp' in result:
        ms_unix_tsmp = str_date_to_timestamp(exec_date, mini_timestamp=True)
        result = result.replace('@exec_ms_unix_tsmp', f"'{ms_unix_tsmp}'")
    elif '@exec_unix_tsmp' in result:
        unix_tsmp = str_date_to_timestamp(exec_date)
        result = result.replace('@exec_unix_tsmp', f"'{unix_tsmp}'")
    
    return result





from typing import List, Dict, Any
import pendulum
import polars as pl
import logging



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



def create_lazyframes(
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
            data_types = config.get('data_types')
            transformations = config.get('transformations')
            
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
            lf, count = extract_functions.gen_lazyframe(config=config, exec_date=exec_date)
                
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




if __name__ == '__main__':
    # logger = get_ogger(__name__)
    # logger.info(f'project_root: {project_root}')   
    # logger.info(f'config_path: {config_path}')  
    tables = load_config(config_file='etl_config.yaml').get('dim_category__scd1').get('sources')
    logger.info(tables)
    print('\n')

    src_config_list = gen_src_config_list(tables)
    logger.info(src_config_list)