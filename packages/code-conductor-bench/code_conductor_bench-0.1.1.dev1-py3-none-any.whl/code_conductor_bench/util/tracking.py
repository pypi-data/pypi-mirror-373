from loguru import logger
import os
import sys
import uuid
import datetime
from tqdm.asyncio import tqdm

logging_level = os.getenv("LOGGING_LEVEL", "TRACE")
logger.remove()
# logger.add(sys.stderr, level=logging_level)
logger.add((lambda x: tqdm.write(x[:-1])), colorize=True, level=logging_level)
logging_dir = os.getenv("LOGGING_DIR")
if logging_dir is not None:
    os.makedirs(logging_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())
    log_filename = f"{timestamp}_{unique_id}.log"
    log_filepath = os.path.join(logging_dir, log_filename)
    logger.info(f"log file path: {log_filepath}")
    logger.add(log_filepath, level=logging_level)