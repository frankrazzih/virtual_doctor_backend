import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    '''set up logging for the application'''
    handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s: %(pathname)s %(lineno)d')
    handler.setFormatter(formatter)

    logger = logging.getLogger('app_logger')
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

logger = setup_logging()