import logging
import sys
from logging.handlers import TimedRotatingFileHandler

def init_logger(log_level: str, log_file: str, with_stream=True):
    handlers = []
    if with_stream:
        handlers.append(logging.StreamHandler(sys.stdout))
    if log_file:
        file_handler = TimedRotatingFileHandler(
            log_file, when='D', interval=1, backupCount=7, encoding='utf-8'
        )
        handlers.append(file_handler)

    logger = logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.DEBUG),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers
    )
    return logger