from yflow.config.base_config import BaseConfig
from typing import Dict
import yaml
from pathlib import Path
from dataclasses import dataclass

@dataclass
class Config:
    extractor: Dict[str, str]


class ExtractorConfigManager(BaseConfig):
    def __init__(self, yaml_path: str | None = None):
        super().__init__()

        if yaml_path is None:
            yaml_path = Path(__file__).with_name("extractor_config.yaml")

        with open(yaml_path, "r", encoding="utf-8") as f:
            config = Config(**yaml.safe_load(f))

        for source_system, path in config.extractor.items():
            self.add_func(source_system, path)

    def add_func(self, source_system: str, path: Dict[str, str] | str):
        """
        Đăng ký func cho một source_system.
        - Nếu source_system không cần phân loại -> truyền path string
        - Nếu source_system cần sử dụng source_type để phân loại -> truyền dict {source_type: path}
        """
        if isinstance(path, dict):
            for source_type, p in path.items():
                self._registry[(source_system.lower(), source_type.lower())] = p
        else:
            self._registry[source_system.lower()] = path


    def get_func_path(self, source_system: str, source_type:str | None = None) -> str:
        if source_type is not None:
            key = (source_system.lower(), source_type.lower())
        else:
            key = source_system.lower()

        if key not in self._registry:
            raise KeyError(f"Func '{key}' chưa được đăng ký")
        return self._registry[key]
