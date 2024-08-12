import logging
from logging.handlers import RotatingFileHandler
logger = logging.getLogger("movieListingApi")
logger.setLevel(logging.DEBUG)
file_handler = RotatingFileHandler("app.log", maxBytes=1024*1024, backupCount=5)
file_handler.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)