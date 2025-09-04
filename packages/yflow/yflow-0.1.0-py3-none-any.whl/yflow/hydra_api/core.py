"""
Core utilities for integrating Hydra configuration management into YFlow.

This module provides functions and decorators to facilitate the registration of configuration
classes, manipulation of Hydra's search path, argument parsing, and execution of tasks using Hydra.
It is designed to streamline the process of configuring and running tasks within the YFlow project,
leveraging Hydra's flexible configuration system.
"""


import os
import functools
from typing import Any, Callable, List
from dataclasses import (
    field,
    make_dataclass
)
from omegaconf import MISSING
from hydra._internal.utils import (
    _run_hydra as run_hydra,
    get_args_parser as get_hydra_args_parser
)
from hydra.core.config_store import ConfigStore
from hydra.core.config_search_path import ConfigSearchPath
from hydra.core.plugins import Plugins
from hydra.plugins.search_path_plugin import SearchPathPlugin
from yflow._typing import CliArgs, TaskFunction, TaskParams
from yflow.config import (
    LIBRARY_NAME,
    CONFIG_CLASS_NAME,
    get_default_config_name,
    get_default_config_path,
    get_default_yflow_config_path
)


def add_folder_to_hydra_search_path(root_group_path):
    """
    Adds a specified folder to the Hydra configuration search path.
    This function defines and registers a custom Hydra SearchPathPlugin that appends
    the given folder path to Hydra's configuration search path. This allows Hydra to
    discover configuration files located in the specified folder.
    Args:
        root_group_path (str): The path to the folder to be added to Hydra's search path.
    Example:
        add_folder_to_hydra_search_path("/path/to/configs")
    Note:
        The folder will be appended to the search path with the provider set to LIBRARY_NAME.
    """
    class AdditionalSearchPathPlugin(SearchPathPlugin):
        """
        A plugin that adds an additional search path to the Hydra configuration search path.

        Inherits from:
            SearchPathPlugin

        Methods:
            manipulate_search_path(search_path: ConfigSearchPath) -> None:
                Appends a new search path to the provided ConfigSearchPath instance using
                the specified provider and path.
        """
        def is_valid_path(self, search_path: ConfigSearchPath):
            """
            Checks if the given search path is a valid directory.

            Args:
                search_path (ConfigSearchPath): The path to check.

            Returns:
                bool: True if the search_path is a valid directory, False otherwise.
            """
            return map(os.path.isdir, search_path.get_path())

        def manipulate_search_path(self, search_path: ConfigSearchPath) -> None:
            if self.is_valid_path(search_path):
                search_path.append(provider=LIBRARY_NAME, path=root_group_path)
            else:
                raise ValueError(f"Invalid path: {root_group_path}")

    Plugins.instance().register(AdditionalSearchPathPlugin)


def execute_task(task_params: TaskParams) -> Callable:
    """
    Executes a task using the provided TaskParams and returns a callable object.
    This function wraps the `run_hydra` function, passing in the necessary parameters from the
    `task_params` object to configure and execute the desired task.
    Args:
        task_params (TaskParams): An object containing the following attributes:
            - cli_args: Command-line arguments for the task.
            - cli_args_parser: Parser for the command-line arguments.
            - task_function: The function to execute as the task.
            - config_path: Path to the configuration file.
            - config_name: Name of the configuration to use.
    Returns:
        Callable: A callable object that, when invoked, executes the specified task with the 
        given parameters.
    """

    return run_hydra(
        args=task_params.cli_args,
        args_parser=task_params.cli_args_parser,
        task_function=task_params.task_function,
        config_path=task_params.config_path,
        config_name=task_params.config_name,
    )


def register_config_to_store(config_class: Any, config_name="config"):
    """
    Registers a configuration class to the Hydra ConfigStore.

    Args:
        config_class (Any): The configuration class or object to register.
        config_name (str, optional): The name under which to store the configuration.
        Defaults to "config".

    Returns:
        None
    """
    cs = ConfigStore.instance()
    cs.store(name=config_name, node=config_class)


def create_config_object(
    must_provide_keys: List[str], 
    defaults_list: List[dict[str, str]] = None):
    """
    Dynamically creates a dataclass configuration object with specified keys.

    Each key in `list_keys` becomes a field in the dataclass, initialized to `MISSING`.
    Additionally, a 'defaults' field is added, which is a list of dictionaries 
    mapping each key to `MISSING`.

    Args:
        list_keys (List[str]): 
        A list of strings representing the field names for the configuration object.

    Returns:
        type: A dynamically generated dataclass type with the specified 
        fields and a 'defaults' field.
    """
    if defaults_list is None:
        defaults_list = ["_self_"]
    else:
        defaults_list.append("_self_")
    config_fields = [
        *[(key, type(MISSING), MISSING) for key in must_provide_keys],
        (
            "defaults",
            List[Any],
            field(default_factory=lambda:
                [{key: MISSING} for key in must_provide_keys]
                + defaults_list
            )
        )
    ]

    return make_dataclass(CONFIG_CLASS_NAME, config_fields)


def get_args():
    """
    Parses command-line arguments for the Yflow Hydra API, providing default values for
    missing configuration paths and names.

    Returns:
        Tuple[CliArgs, argparse.ArgumentParser]: A tuple containing the parsed arguments 
            and the argument parser instance.
    """
    args_parser = get_hydra_args_parser()

    args_parser.add_argument(
        "--yflow-config-path",
        "-ycp",
        help="Yflow's config path file",
    )

    args: CliArgs = args_parser.parse_args()

    if not args.config_path:
        args.config_path = get_default_config_path()

    if not args.config_name:
        args.config_name = get_default_config_name()

    if not args.yflow_config_path:
        args.yflow_config_path = get_default_yflow_config_path()

    return args, args_parser


def main(pre_config_func=lambda x: None, config_path=None, config_name=None):
    """
    Decorator factory for configuring and executing a task function with optional pre-configuration.

    Args:
        pre_config_func (Callable, optional): A function to preprocess CLI 
            arguments before task execution. Defaults to a no-op function.
        config_path (str, optional): Path to the configuration file. Defaults to None.
        config_name (str, optional): Name of the configuration to use. Defaults to None.

    Returns:
        Callable: A decorator that wraps a task function, handling argument 
            parsing, pre-configuration, and execution with the specified configuration.
    """
    def main_decorator(task_function: TaskFunction) -> Callable[[], None]:
        @functools.wraps(task_function)
        def decorated_main() -> Any:
            cli_args, cli_args_parser = get_args()
            pre_config_result = pre_config_func(cli_args)
            return execute_task(
                TaskParams(
                    task_function=lambda cfg: task_function(cfg, pre_config_result),
                    cli_args=cli_args,
                    cli_args_parser=cli_args_parser,
                    config_path=config_path,
                    config_name=config_name
                )
            )
        return decorated_main
    return main_decorator


def setup_launcher(launcher: str):
    """
    Sets up the Hydra launcher configuration based on the specified launcher type.

    Args:
        launcher (str): The type of launcher to set up. Currently supports "ray".

    Raises:
        ValueError: If an unsupported launcher type is provided.

    Returns:
        None
    """
    if launcher == "ray":
        from yflow.hydra_api.ray_launcher import create_ray_config
        create_ray_config()
    else:
        raise ValueError(f"Unsupported launcher type: {launcher}")
