import logging


def config_logger(level=logging.INFO):
    import logging
    from rich.logging import RichHandler

    FORMAT = '%(message)s'
    logging.basicConfig(level=level, handlers=[RichHandler()], datefmt="[%X]", format=FORMAT)
