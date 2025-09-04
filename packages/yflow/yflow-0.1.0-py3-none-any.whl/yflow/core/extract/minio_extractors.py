import polars as pl
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

  
def extractor(config: dict):
    logger.info(f'MinIO config: {config}')
    extractor_func = get_minio_extractor_func(config["source_type"])

    # table_name = config.get('table_name')
    # data_types = config.get('data_types')
    # source_system = config.get('source_system')
    # data_types = config.get('data_types')
    # bucket = config.get('bucket')
    # prefix = config.get('prefix')
    # where_condition = config.get('where_condition', None)

    # minio_path = "s3://" + bucket.strip('/') + '/' + prefix.strip('/')

    # config['minio_path'] = minio_path
    # config['storage_options'] = cursor

    # lf, count = scan_csv(config=config, schema=data_types)

    # return lf, count
    


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
              'data_types': {
                  'categoryid': pl.Enum(categories=['302', '901', '10', '301', '602', '1201', '902']), 
                  'categoryname': pl.String, 
                  'categorydescription': pl.String}
            }
    extractor(config)

    