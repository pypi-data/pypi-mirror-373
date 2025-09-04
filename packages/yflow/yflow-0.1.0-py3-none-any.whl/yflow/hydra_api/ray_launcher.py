from omegaconf import MISSING
from dataclasses import dataclass, field, make_dataclass
from typing import Optional, List, Dict, Any
from hydra.core.config_store import ConfigStore


def create_ray_config(
    ray_address: str,
    libraries: List[str]):
    libraries += [
        "hydra-core==1.3.2",
        "hydra-ray-launcher==1.2.1"
    ]
    cs = ConfigStore.instance()
    cs.store(
        name="ray_launcher_values",
        package="hydra.launcher.ray",
        node={
            "init": {
                "address": ray_address,
                "object_store_memory": None,
                "runtime_env": {
                    "pip": libraries,
                },
            }
        },
    )
