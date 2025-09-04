
import logging       

# Thiết lập logging cho môi trường production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extractor(config):
    logger.info(f'config: {config}')



