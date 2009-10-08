# -*- coding: utf-8 -*-

import os
import logging


LOG_DIR = '/tmp'

def get_logger(name):
    file_path = os.path.join(LOG_DIR, name + '.log')
    logging.basicConfig(filename=file_path, level=logging.DEBUG,)
    return logging
