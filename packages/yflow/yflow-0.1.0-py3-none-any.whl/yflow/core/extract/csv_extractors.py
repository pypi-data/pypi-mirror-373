import polars as pl
import logging
from yflow.config.pipeline import SourceConfig
from typing import Dict, List, Any

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)


def extractor(source_config: SourceConfig, connection_config) -> pl.LazyFrame:
    try:
        select_columns = source_config.select_columns
        # 1. Nguồn dữ liệu
        minio_path = "s3://" + source_config.bucket.strip('/') + '/' + source_config.prefix.strip('/')
        storage_options = connection_config[source_config.connection_name]
        schema = source_config.data_types

        logger.info(f'Select Columns: {select_columns}')
        logger.info(f'MinIO Path: {minio_path}')
        logger.info(f'Schema: {schema}')
        # logger.info(f'Storage Options: {storage_options}')

        # Đọc file CSV từ MinIO và tạo Lazy Frame
        lf = pl.scan_csv( 
            source=minio_path,
            storage_options=storage_options,
            schema=schema,
            infer_schema=False,
        ).select(pl.col(select_columns))

        return lf

    except Exception as e:
        print(f"Đã xảy ra lỗi khi đọc file csv: {e}")
