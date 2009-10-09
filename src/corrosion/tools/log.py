# -*- coding: utf-8 -*-

import os
import logging


LOG_DIR = '/tmp'

def get_logger(name):
    logger_path = os.path.join(LOG_DIR, name + '.log')
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(message)s")
    handler = logging.FileHandler(logger_path)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
