import logging


def config_logger(level=logging.INFO):
    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s')
