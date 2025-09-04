from dataclasses import dataclass, field
from typing import Dict, List, Any
import hydra
from omegaconf import DictConfig, OmegaConf
from .source_config import SourceConfig

@dataclass(kw_only=True)
class MinIOConfig(SourceConfig):
    source_type: str
    bucket: str
    prefix: str