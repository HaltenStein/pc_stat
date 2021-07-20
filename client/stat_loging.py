import logging
from logging.handlers import RotatingFileHandler
import socket


pc_name = socket.gethostname()
pc_ip = socket.gethostbyname(socket.gethostname())
file_name = pc_ip.replace('.', '_')

# creating an instance of the logging class
logger = logging.getLogger(str((pc_name, pc_ip)))
logger.setLevel(logging.INFO)

# create the logging file handler
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# one file ≈ 5 hour operation
handler = RotatingFileHandler('{}.log'.format(file_name), maxBytes=1024*1125) 

# add handler to logger object
handler.setFormatter(log_formatter)
logger.addHandler(handler)


def add_info(text):
    """
    writing to the `.log` file\n
    "TIME - PC NAME - PC IP - LEVEL - MESSAGE"
    """
    logger.info(text)
