import logging

# Basic logger setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

def log_info(message: str):
    logging.info(message)

def log_error(message: str):
    logging.error(message)

def log_warn(message: str):
    logging.warning(message)
