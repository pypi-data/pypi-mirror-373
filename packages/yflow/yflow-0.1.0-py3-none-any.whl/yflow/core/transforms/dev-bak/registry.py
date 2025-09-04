# yflow/core/transform/registry.py
import importlib
import logging
from typing import Dict, Type, List
from .base import BaseTransformation

# Thiết lập logging cho môi trường production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

# name (lower) -> class (subclass của BaseTransformation)
TRANSFORMATION_REGISTRY: Dict[str, Type[BaseTransformation]] = {}

def register_transformation(cls: Type[BaseTransformation]):
    """Decorator để đăng ký class transformation.
       Sử dụng: @register_transformation trên class.
    """
    if not hasattr(cls, "name"):
        raise AttributeError("Transformation class must define 'name' attribute")
    
    key = cls.name.lower()
    if key in TRANSFORMATION_REGISTRY:
        logger.warning(f"Transformation '{key}' đang được ghi đè")

    TRANSFORMATION_REGISTRY[key] = cls
    logger.debug(f"Registered transformation '{key}' -> {cls}")
    return cls


def get_transformation(name_or_path: str) -> Type[BaseTransformation]:
    """
    Trả về class transformation theo tên hoặc theo path 'module:ClassName'
    - Nếu name_or_path tồn tại trong registry -> trả class
    - Nếu không, nếu chứa ':' -> import module và register class tự động
    """

    key = name_or_path.lower()
    if key in TRANSFORMATION_REGISTRY:
        return TRANSFORMATION_REGISTRY[key]

    # hỗ trợ path dạng 'module.path:ClassName'
    if ":" in name_or_path:
        cls = register_from_path(name_or_path)
        return cls

    raise KeyError(f"Transformation '{name_or_path}' chưa được đăng ký. Có sẵn: {list(TRANSFORMATION_REGISTRY.keys())}")


def register_from_path(path: str):
    """
    Import class từ path dạng 'module.path:ClassName' và register
    Trả về class đã register
    """
    try:
        module_name, class_name = path.split(":")
    except ValueError:
        raise ValueError("Path cần dạng 'module.path:ClassName'")

    module = importlib.import_module(module_name)

    cls = getattr(module, class_name)
    if not issubclass(cls, BaseTransformation):
        raise TypeError("Class import lên phải kế thừa BaseTransformation")
    
    return register_transformation(cls)


def load_external_transformations(modules: List[str]):
    """
    Import các module plugin (module paths). Khi import, các plugin nên gọi @register_transformation để tự động đăng ký
    """
    for m in modules:
        try:
            importlib.import_module(m)
            logger.info(f"Loaded plugin module {m}")
        except Exception:
            logger.exception(f"Không load được plugin module {m}")


def list_registered() -> list[str]:
    return list(TRANSFORMATION_REGISTRY.keys())
