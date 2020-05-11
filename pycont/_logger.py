import logging

__logger_root_name__ = 'pycont'


def create_logger(name: str) -> logging.Logger:
    return logging.getLogger(__logger_root_name__ + '.' + name)
