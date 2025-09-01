# -*- coding: utf-8 -*-
# do not use __init__.py because pyinstaller puts it in _internal/__init__/__init__.pyc
# logger.pyc is well directly in _internal/
from config import get_bundle_dir

import logging
import os
import sys


LOGGER_LEVEL = logging.INFO


log = logging.getLogger()
log.setLevel(LOGGER_LEVEL)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(LOGGER_LEVEL)
file_handler = logging.FileHandler(os.path.join(get_bundle_dir(), "ish.log"))
file_handler.setLevel(LOGGER_LEVEL)
# formatter = logging.Formatter('%(asctime)s %(levelname).1s (%(name)s) %(message)s')
formatter = logging.Formatter("%(asctime)s %(levelname).1s %(message)s")
formatter.datefmt = "%y%m%d %H%M%S"
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
log.addHandler(console_handler)
log.addHandler(file_handler)


def close_logger():
    for handler in log.handlers:
        if isinstance(handler, logging.FileHandler):
            handler.close()
