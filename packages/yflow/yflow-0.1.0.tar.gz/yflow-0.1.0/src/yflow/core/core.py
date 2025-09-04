import logging
from yflow.config.pipeline import MinIOConfig
from typing import Dict, List, Any, Type
from .utils import parse_polars_type, merge_sub_dicts, filter_data_types
import importlib
from yflow.config.transformer.config import TransformationConfigManager
from yflow.config.source import SourceConfigManager

# Thiết lập logging cho môi trường production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)



def load_callable(path: str):
    """
    Load một callable từ string path dạng 'module.submodule:func'
    Ví dụ:
        'yflow.core.extract.minio_extractors:extractor'
        'project.custom.my_extractor:custom_extractor'
    """
    try:
        module_name, func_name = path.split(":")
    except ValueError:
        raise ValueError(
            f"Path '{path}' không hợp lệ. Cần dạng 'module.submodule:func'"
        )

    module = importlib.import_module(module_name)
    return getattr(module, func_name)

def get_config(cfg, name: str) -> Dict[str, Any]:
    try:
        path = cfg.get_func_path(name=name)
        config: callable = load_callable(path)
        return config
    except ValueError as e:
        return f"Error: {str(e)}"

def get_transformation_config(base_transformation_config: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    transformation_configs = []
    cfg: TransformationConfigManager = TransformationConfigManager()
    try:
        for base_config in base_transformation_config:
            config = get_config(cfg, name=base_config.function)
            transformation_configs.append(config(**base_config))

        return transformation_configs
    except ValueError as e:
        return f"Error: {str(e)}"


def merge_source_config(base_source_config: Dict, yflow_source_config: Dict) -> Dict[str, Type]:
    cfg: SourceConfigManager = SourceConfigManager()
    try:
        config = get_config(cfg, name=yflow_source_config.get("source_system"))
        table_config = config(
            **base_source_config,
            **yflow_source_config,
        )
        
        table_config.data_types = merge_sub_dicts(table_config.data_types)
        table_config.data_types = {col: parse_polars_type(type) for col, type in table_config.data_types.items()}
                        
        return table_config
    
    except ValueError as e:
        return f"Error: {str(e)}"
    
