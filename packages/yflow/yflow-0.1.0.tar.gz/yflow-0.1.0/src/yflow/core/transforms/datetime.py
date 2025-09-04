from typing import List, Dict, Any
import pendulum
from datetime import datetime
import polars as pl
import logging
import re 


# Thiết lập logging cho môi trường production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)
