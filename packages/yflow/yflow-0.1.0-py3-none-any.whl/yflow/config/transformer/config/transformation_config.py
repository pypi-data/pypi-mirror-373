from yflow.config.base_config import BaseConfig
from typing import Dict
import yaml
from pathlib import Path
from dataclasses import dataclass

@dataclass
class Config:
    transformations: Dict[str, str]

class TransformationConfigManager(BaseConfig):
    def __init__(self, yaml_path: str | None = None):
        super().__init__()

        if yaml_path is None:
            yaml_path = Path(__file__).with_name("transformation_config.yaml")

        with open(yaml_path, "r", encoding="utf-8") as f:
            config = Config(**yaml.safe_load(f))

        for name, path in config.transformations.items():
            super().add_func(name, path)
