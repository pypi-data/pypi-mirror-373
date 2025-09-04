"""
Utility functions for file operations, YAML handling, and path manipulations.
"""


import os
import functools
import time
from pathlib import Path
from typing import Callable, Type, Tuple
import yaml


def retry(
    times: int = 3,
    base_delay: float = 1.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)) -> Callable:
    """
    A decorator that retries a function call upon specified exceptions.

    Args:
        times (int): Number of retry attempts before giving up. Defaults to 3.
        base_delay (float): Initial delay (in seconds) before retrying. Delay 
            doubles after each attempt. Defaults to 1.0.
        exceptions (tuple): Tuple of exception classes to catch and retry upon.
            Defaults to (Exception,).

    Returns:
        function: A decorated function that will be retried upon specified exceptions.

    Raises:
        Exception: The last exception encountered if all retry attempts fail.

    Example:
        @retry(times=5, base_delay=2, exceptions=(ValueError,))
        def unreliable_function():
            # function implementation
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == times:
                        raise e
                    time.sleep(delay)
                    delay *= 2
            return func(*args, **kwargs)
        return wrapper
    return decorator


@retry(times=3, base_delay=1)
def read_file_yaml(file_path: str) -> dict:
    """
    Reads a YAML file and returns its contents as a dictionary.

    Args:
        file_path (str): The path to the YAML file to be read.

    Returns:
        dict: The contents of the YAML file as a dictionary.

    Raises:
        Exception: If there is an error reading or parsing the YAML file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            return config
    except Exception as err:
        raise err


def split_folder_path(path: str):
    """
    Splits a given folder path into its head (parent directory) and tail (last component).

    Args:
        path (str): The folder path to split.

    Returns:
        Tuple[str, str]: A tuple containing the head (parent directory) 
            and tail (last component) of the path.
    """
    path = os.path.normpath(path)
    head, tail = os.path.split(path)
    return head, tail


def get_call_dir():
    """
    Returns the current working directory.

    Returns:
        str: The absolute path of the current working directory.
    """
    return os.getcwd()


def resolve_config_path(path: str) -> str:
    """
    Resolves the absolute path for a given configuration file path.

    If the provided path is already absolute, returns its absolute form.
    Otherwise, constructs an absolute path by joining the path with the directory
    of the calling script.

    Args:
        path (str): The configuration file path to resolve.

    Returns:
        str: The absolute path to the configuration file.
    """
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(os.path.join(get_call_dir(), path))


@retry(times=3, base_delay=1)
def read_folder_yaml(folder_path: str, file_names: list[str] = None) -> dict:
    """
    Reads and merges YAML files from a specified folder into a single dictionary.

    Args:
        folder_path (str): Path to the folder containing YAML files.
        file_names (list[str], optional): List of file names (without extension) to include. 
            If None, all YAML files are read.

    Returns:
        dict: A dictionary containing the merged contents of the selected YAML files.

    Raises:
        Exception: Propagates any exception encountered during file reading or YAML parsing.
    """
    try:
        result = {}
        for file in Path(folder_path).glob("*.y*ml"):
            if file_names is None or file.stem in file_names:
                with open(file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                    result.update(data)
        return result
    except Exception as err:
        raise err
