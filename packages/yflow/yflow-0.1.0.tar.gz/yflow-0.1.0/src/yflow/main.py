import warnings
from omegaconf import DictConfig
from yflow.config.pipeline import sources
from yflow.hydra_api import (
    add_folder_to_hydra_search_path,
    register_config_to_store,
    create_config_object
)
from yflow.hydra_api import main, create_ray_config
from ._typing import (
    PipelinePathConfig, 
    BasePipelineConfig,
    YflowDatabaseConfig, 
    YflowConfig,
    CliArgs
)
from .utils import (
    read_file_yaml, 
    split_folder_path,
    read_folder_yaml,
    resolve_config_path
)
from yflow.config import (
    DEFAULT_CONFIG_NAME,
    DEFAULT_CONFIG_PATH
)

from yflow.config import PipelineConfig
from yflow.core import merge_source_config, get_transformation_config
from yflow.core.extract import extractor_factory
from pprint import pprint
from yflow.core.transforms import transform_polars_lazyframes


warnings.filterwarnings("ignore", category=UserWarning)


def get_yflow_database_config(
    base_pipeline_config: BasePipelineConfig, 
    yflow_config: YflowConfig) -> YflowDatabaseConfig:

    source_config = read_folder_yaml(folder_path=yflow_config.source_path, file_names=list(base_pipeline_config.sources.keys()))
    connection_config = read_folder_yaml(folder_path=yflow_config.connection_path)
    destination_config = read_folder_yaml(folder_path=yflow_config.destination_path)

    
    return YflowDatabaseConfig(
        source_config,
        connection_config,
        destination_config
    )


def get_yflow_path_config(yflow_config: YflowConfig) -> YflowConfig:
    yflow_config.source_path = resolve_config_path(yflow_config.source_path)
    yflow_config.connection_path = resolve_config_path(yflow_config.connection_path)
    yflow_config.destination_path = resolve_config_path(yflow_config.destination_path)
    yflow_config.pipeline_path = resolve_config_path(yflow_config.pipeline_path)

    return yflow_config

def get_pipeline_config(yflow_config: YflowConfig):    
    root_pipeline_folder, pipeline_key = split_folder_path(
        resolve_config_path(
            yflow_config.pipeline_path
        )
    )
    
    return PipelinePathConfig(
        root_pipeline_folder,
        pipeline_key
    )


def pre_config(cli_args: CliArgs):
    yflow_config = YflowConfig.generate_from_file(cli_args.yflow_config_path)
    pipeline_path_config = get_pipeline_config(yflow_config)
    yflow_path_config = get_yflow_path_config(yflow_config)
    
    add_folder_to_hydra_search_path(
        pipeline_path_config.root_folder_path
    )
    
    default_configs = []
    if yflow_config.launcher == "ray":
        default_configs.append("ray_launcher_values")
        default_configs.append({"override hydra/launcher": "ray"})
        create_ray_config(
            ray_address=yflow_config.ray_address,
            libraries=yflow_config.libraries
        )
    
    config = create_config_object(
        must_provide_keys=[pipeline_path_config.pipeline_key],
        defaults_list=default_configs
    )
    register_config_to_store(config)
    return yflow_path_config


@main(
    pre_config_func=pre_config,
    config_path=resolve_config_path(DEFAULT_CONFIG_PATH),
    config_name=DEFAULT_CONFIG_NAME
)
def controller(
    cfg: DictConfig,
    yflow_config: YflowConfig
):
    # print(cfg)
    # print(yflow_config)
    print("aaaa")
    return
    base_pipeline_config = BasePipelineConfig(**list(cfg.values())[0])
    yflow_database_config = get_yflow_database_config(base_pipeline_config, yflow_config)
    print(f'\nyflow_database_config: {yflow_database_config}')

    full_source_config = {}

    for source_name, base_source_config in base_pipeline_config.sources.items():
        source_config = merge_source_config(base_source_config=base_source_config, yflow_source_config=yflow_database_config.source_config[source_name])
        transformation_config = get_transformation_config(base_transformation_config=source_config.transformations)
        source_config.transformations = transformation_config
        full_source_config[source_name] = source_config

    pipeline_config = PipelineConfig(
        sources=full_source_config,
        destination=base_pipeline_config.destination,
        join_configs=base_pipeline_config.join_configs,
        connections=yflow_database_config.connection_config
    )
    print(f'\npipeline_config: {pipeline_config}')

    lfs = {}
    for table_name, table_config in pipeline_config.sources.items():
        lf = extractor_factory(table_config=table_config, connection_config=pipeline_config.connections)
        print(lf.collect())
        lf = transform_polars_lazyframes(lf=lf, transformations=table_config.transformations)
        lfs[table_name] = lf
        print(lf.collect())




        # # Thu thập dữ liệu để kiểm tra
        # df = lf.head(1).collect()

        # # Kiểm tra nếu DataFrame rỗng
        # count = 1
        # if df.is_empty():
        #     lf = pl.DataFrame({}, schema=schema)
        #     count = 0
