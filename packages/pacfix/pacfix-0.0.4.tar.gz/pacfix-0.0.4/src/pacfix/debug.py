import logging

logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(message)s")
logger = logging.getLogger("pacfix-python-logger")

def check_debug() -> bool:
    return logger.level <= logging.DEBUG

def enable_debug():
    logger.setLevel(logging.DEBUG)

def disable_debug():
    logger.setLevel(logging.WARNING)

def print_debug(s: str):
    logger.debug(s)

def print_warning(s: str):
    logger.warning(f"[WARN] {s}")