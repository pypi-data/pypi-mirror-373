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

# This enable the cert handling in requests/pip/etc.
# This must be run before requests is imported.
import pip_system_certs.wrapt_requests  # isort: skip

from config import get_bundle_dir
from config import get_current_version
from config import MAIN_EXE_NAME
from config import PARAMS_FILE_NAME
from config import SERVER_URL
from logger import close_logger
from logger import log
from profiles_restore import main as profiles_restore_main
from utils import copy_release_files_and_restart
from utils import download_update
from utils import exception_infos
from utils import get_download_dir_path
from utils import get_last_dated_backup_dir
from utils import get_latest_release_version
from utils import get_main_backup_dir
from utils import get_parameter
from utils import read_dir
from utils import send_log_message
from utils import set_parameter
from utils import stop
from utils import unzip_file

import argparse
import os
import platform


def handle_startup(main_dir, params, action="add"):
    """Add/remove exe to/from startup"""
    exe_path = os.path.join(main_dir, f"{MAIN_EXE_NAME}.exe")
    key = r"Software\Microsoft\Windows\CurrentVersion\Run"
    value_name = "IMIO_Scan_Helpers_Scripts"
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE) as reg_key:
            if action == "add":
                winreg.SetValueEx(reg_key, value_name, 0, winreg.REG_SZ, f'"{exe_path}" --is-auto-started')
                log.info(f"'{exe_path} --is-auto-started' added to startup")
            elif action == "remove":
                winreg.DeleteValue(reg_key, value_name)
                log.info(f"'{exe_path}' removed from startup")
    except ImportError:
        send_log_message("Cannot import winreg: add to startup failed !!", params)
    except Exception as e:
        send_log_message(f"Error in handle_startup, {exception_infos(e)}", params)


def check_for_updates(main_dir, cur_vers, params):
    """Check for updates"""
    latest_version, download_url = get_latest_release_version(params, ns.release)
    if latest_version is not None and (latest_version > cur_vers or ns.release):
        log.info(f"New version available: {latest_version}")
        download_dir_path = get_download_dir_path()
        if not os.path.exists(download_dir_path):
            os.makedirs(download_dir_path)
        download_path = os.path.join(download_dir_path, download_url.split("/")[-1])
        log.info(f"Downloading {download_url} to {download_path}")
        download_update(download_url, download_path)
        log.info(f"Unzipping {download_path} to {download_dir_path}")
        unzip_file(download_path, download_dir_path)
        copy_release_files_and_restart(download_dir_path, main_dir)
        log.info("Will replace files and restart")
        stop(intup=False, exit_code=0)


# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--version", action="store_true", dest="version", help="Show version")
parser.add_argument("-c", "--client-id", dest="client_id", help="Set client id")
parser.add_argument("-p", "--password", dest="password", help="Set password")
parser.add_argument("-nu", "--no-update", action="store_true", dest="no_update", help="Do not check for updates")
parser.add_argument("-r", "--release", dest="release", help="Get this release")
parser.add_argument("-tm", "--test-message", action="store_true", dest="test_message", help="Send a test message")
parser.add_argument("--proxy", dest="proxy", help="Proxy url")
parser.add_argument("--proxy-user", dest="proxy_user", help="Proxy user")
parser.add_argument("--proxy-pwd", dest="proxy_pwd", help="Proxy password")
parser.add_argument("--startup", action="store_true", dest="startup", help="Add exe to startup")
parser.add_argument("--startup-remove", action="store_true", dest="startup_remove", help="Remove exe from startup")
parser.add_argument(
    "--is-auto-started", action="store_true", dest="auto_started", help="Flag when script is auto started"
)
ns = parser.parse_args()

if ns.version:
    print(f"imio.scan_helpers version {get_current_version()}")
    stop(intup=False, exit_code=0)
bundle_dir = get_bundle_dir()
log.info(f"dir={bundle_dir}")

params_file = os.path.join(bundle_dir, PARAMS_FILE_NAME)
if ns.client_id:
    set_parameter(params_file, "CLIENT_ID", ns.client_id)
if ns.password:
    set_parameter(params_file, "PLONE_PWD", ns.password)
if ns.proxy:
    set_parameter(params_file, "PROXY", ns.proxy)
if ns.proxy_user:
    set_parameter(params_file, "PROXY_USER", ns.proxy_user)
if ns.proxy_pwd:
    set_parameter(params_file, "PROXY_PWD", ns.proxy_pwd)
parameters = set_parameter(params_file, "hostname", platform.node())
if "CLIENT_ID" not in parameters or "PLONE_PWD" not in parameters:
    stop("CLIENT_ID or PLONE_PWD not found in parameters")
if "SERVER_URL" not in parameters:
    parameters = set_parameter(params_file, "SERVER_URL", SERVER_URL)
current_version = get_current_version()
if "version" not in parameters:
    parameters = set_parameter(params_file, "version", current_version)
if current_version != parameters["version"]:
    old_version = parameters["version"]
    parameters = set_parameter(params_file, "version", current_version)
    send_log_message(
        f"Product updated from {old_version} to {current_version}",
        parameters,
        log_method=log.info,
        level="INFO",
    )

try:
    if ns.startup:
        handle_startup(bundle_dir, parameters)
    if ns.startup_remove:
        handle_startup(bundle_dir, parameters, action="remove")
    if ns.no_update or ns.test_message:
        pass
    else:
        check_for_updates(bundle_dir, current_version, parameters)
except Exception as ex:
    send_log_message(f"General error in main script, {exception_infos(ex)}", parameters)

# will do something
log.info(f"Current version is {get_current_version()}")
main_backup_dir = get_main_backup_dir(create=False)
if ns.auto_started and not get_parameter(params_file, "various"):
    back_dirs = []
    if main_backup_dir:
        dated_backup_dir = get_last_dated_backup_dir(main_backup_dir)
        if dated_backup_dir:
            back_dirs = read_dir(dated_backup_dir, with_path=False, only_folders=True)
    send_log_message(
        f"Script started automatically !\nInstalled in '{bundle_dir}'.\n"
        f"Version is {parameters['version']}\nParameters: {sorted(parameters.keys())}\n"
        f"Backuped dirs: {back_dirs}",
        parameters,
        log_method=log.info,
    )
    set_parameter(params_file, "various", "auto_started")
if ns.test_message:
    send_log_message(
        f"Test message\nInstalled in '{bundle_dir}'.",
        parameters,
        log_method=log.info,
    )
elif get_main_backup_dir(create=False):
    profiles_restore_main()
close_logger()
