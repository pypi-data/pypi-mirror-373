from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class MinIOConnectionConfig:
    AWS_ENDPOINT_URL: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_ALLOW_HTTP: bool = "true"