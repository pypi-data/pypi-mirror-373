#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the imio.scan_helpers distribution (https://github.com/IMIO/imio.scan_helpers).
# Copyright (c) 2023 IMIO
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
from config import get_bundle_dir
from config import PARAMS_FILE_NAME
from config import PROFILES_DIRS
from datetime import datetime
from logger import close_logger
from logger import log
from utils import copy_sub_files
from utils import exception_infos
from utils import get_dated_backup_dir
from utils import get_main_backup_dir
from utils import get_parameter
from utils import get_scan_profiles_dir
from utils import read_dir
from utils import send_log_message
from utils import stop

import argparse
import os


# Argument parsing
parser = argparse.ArgumentParser()
# parser.add_argument("-v", "--version", action="store_true", dest="version", help="Show version")
# parser.add_argument("-r", "--release", dest="release", help="Get this release")
ns = parser.parse_args()

log.info("Starting backup script")
bundle_dir = get_bundle_dir()
params_file = os.path.join(bundle_dir, PARAMS_FILE_NAME)
parameters = get_parameter(params_file)
try:
    main_prof_dir = get_scan_profiles_dir()
    if not os.path.exists(main_prof_dir):
        stop(f"Profiles dir not found: {PROFILES_DIRS}", params=parameters)
    prof_dirs = read_dir(main_prof_dir, with_path=False, only_folders=True)
    if not prof_dirs:
        stop(f"No profiles found in '{main_prof_dir}'", params=parameters)
    main_backup_dir = get_main_backup_dir()
    day = datetime.now().strftime("%Y-%m-%d")
    dated_backup_dir = get_dated_backup_dir(main_backup_dir, day=day)
    copy_sub_files(main_prof_dir, dated_backup_dir, files=prof_dirs)
    input("Press Enter to exit...")
except Exception as ex:
    send_log_message(f"General error in profiles-backup script, {exception_infos(ex)}", parameters)

log.info("Finished backup script")
close_logger()
