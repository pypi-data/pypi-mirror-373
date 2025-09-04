from yflow.core.extract.csv_extractors import extractor as csv_extractor
from ..base_config import ConfigManager

class MinIOConfig:
    csv = csv_extractor


MinioConfigManager = ConfigManager(MinIOConfig)
