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
from logger import close_logger
from logger import log
from utils import copy_sub_files
from utils import exception_infos
from utils import get_last_dated_backup_dir
from utils import get_main_backup_dir
from utils import get_parameter
from utils import get_scan_profiles_dir
from utils import read_dir
from utils import send_log_message
from utils import stop

import argparse
import os
import shutil


def main():
    log.info("Starting restore script")
    bundle_dir = get_bundle_dir()
    params_file = os.path.join(bundle_dir, PARAMS_FILE_NAME)
    parameters = get_parameter(params_file)
    try:
        main_backup_dir = get_main_backup_dir(create=False)
        dated_backup_dir = get_last_dated_backup_dir(main_backup_dir)
        if not dated_backup_dir:
            stop(f"No dated backup dir in  '{main_backup_dir}'", params=parameters)
        prof_dirs = read_dir(dated_backup_dir, with_path=False, only_folders=True)
        if not prof_dirs:
            stop(f"No profiles found in '{dated_backup_dir}'", params=parameters)
        main_prof_dir = get_scan_profiles_dir()
        if not os.path.exists(main_prof_dir):
            stop(f"Profiles dir not found: {PROFILES_DIRS}", params=parameters)
        for prof_dir in prof_dirs:
            adir = os.path.join(main_prof_dir, prof_dir)
            if os.path.exists(adir):
                try:
                    shutil.rmtree(adir)
                    copy_sub_files(dated_backup_dir, main_prof_dir, files=[prof_dir])
                except Exception as ex:
                    send_log_message(f"Error while removing existing dir '{adir}' in profiles-restore script: {exception_infos(ex)}", parameters)
    except Exception as ex:
        send_log_message(f"General error in profiles-restore script, {exception_infos(ex)}", parameters)

    log.info("Finished restore script")
    close_logger()


if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser()
    nsp = parser.parse_args()
    # main(nsp)
    main()
