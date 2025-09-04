import logging       
import polars as pl
import re 


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)



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



if __name__ == '__main__':
    config = {'table_name': 'categorydefinition', 
              'select_columns': ['categoryid', 'categoryname', 'categorydescription'], 
              'where_condition': None, 
              'transformations': [
                  {'function': 'split_str_col_to_columns', 'input_cols': 'categoryname', 'output_col1': 'category_code', 'output_col2': 'category_name'}, 
                  {'function': 'rename_columns', 'input_cols': {'categoryid': 'category_id'}}], 
              'custom_table': None, 
              'custom_query': None, 
              'owner': 'hungdv336', 
              'description': 'Bảng DIM', 
              'source_system': 'MinIO', 
              'source_type': 'files', 
              'bucket': 'sla-helpdesk', 
              'prefix': 'sla/categorydefinition.csv', 
              'data_types': [
                  {'categoryid': "pl.Enum(['302', '901', '10', '301', '602', '1201', '902'])"}, 
                  {'categoryname': 'pl.Utf8'}, 
                  {'categorydescription': 'pl.String'},
                  {'isdeleted': "pl.Enum(['True', 'False'])"}]
            }
    # filter_data_types(config)