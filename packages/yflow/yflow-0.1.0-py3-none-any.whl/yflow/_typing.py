"""
This module contains all dataclass typing for yflow
"""


from dataclasses import dataclass
from typing import Any, Dict, Optional

from hydra.types import TaskFunction
from .utils import (
    read_file_yaml,
    resolve_config_path
)


@dataclass
class ArgsReturn:
    """
    This class is used to store the return value of get_args function
    """
    args: Any
    parser: Any


@dataclass
class PipelinePathConfig:
    """
    This class is used to store the pipeline path configuration
    """
    root_folder_path: str
    pipeline_key: str


@dataclass
class BasePipelineConfig:
    """
    This class is used to store the base pipeline configuration
    """
    sources: Dict[str, Any]
    destination: Dict[str, Any]
    join_configs: Dict[str, Any]


@dataclass
class YflowConfig:
    """
    This class reference the config in file yflow_config.yaml
    This config is used to store the path of source, connection, destination, pipeline
    and other yflow related configuration.
    """
    source_path: str
    connection_path: str
    destination_path: str
    pipeline_path: str
    launcher: Optional[str] = None
    ray_address: Optional[str] = None
    libraries: Optional[list[str]] = None

    @classmethod
    def generate_from_file(cls, file_path: str):
        """
        Creates an instance of YflowConfig from a YAML file.
        """
        return cls(
            **read_file_yaml(
                resolve_config_path(file_path)
            )
        )
    
    def __post_init__(self):
        if self.launcher == "ray":
            if self.libraries is None:
                self.libraries = []


@dataclass
class YflowDatabaseConfig:
    """
    This class is used to store the database configuration for Yflow.
    """
    source_config: Any
    connection_config: Any
    destination_config: Any


_UNSPECIFIED_: Any = object()


@dataclass
class TaskParams:
    """
    Parameters for executing a task function with Hydra.
    Attributes:
        cli_args (Any): Command-line arguments for the task.
        cli_args_parser (Any): Parser for the command-line arguments.
        task_function (TaskFunction): The function to execute as the task.
        config_path (str): Path to the configuration file.
        config_name (str): Name of the configuration to use.
    """
    task_function: TaskFunction
    cli_args: Any
    cli_args_parser: Any
    config_path: str
    config_name: str


@dataclass
class CliArgs:
    """
    Command-line arguments for Hydra configuration.
    Attributes:
        config_path (str): Path to the configuration file.
        config_name (str): Name of the configuration to use.
        yflow_config_path (str): Path to the Yflow configuration file.
    """
    config_path: str
    config_name: str
    yflow_config_path: str
