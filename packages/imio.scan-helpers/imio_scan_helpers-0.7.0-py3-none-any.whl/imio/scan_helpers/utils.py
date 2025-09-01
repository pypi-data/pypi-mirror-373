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
from config import COPY_BAT_NAME
from config import DOWNLOAD_DIR
from config import get_bundle_dir
from config import GITHUB_REPO
from config import IS_PROD
from config import MAIN_BACKUP_DIR
from config import MAIN_EXE_NAME
from config import PROFILES_DIRS
from logger import close_logger
from logger import log
from requests.exceptions import ConnectionError
from requests.exceptions import RequestException
from requests.exceptions import Timeout

import json
import os
import re
import requests
import shutil
import subprocess
import sys
import traceback
import zipfile


def copy_sub_files(src_dir, dest_dir, files=()):
    """Copy content from src to dest"""
    for item in os.listdir(src_dir):
        if files and item not in files:
            continue
        s = os.path.join(src_dir, item)
        d = os.path.join(dest_dir, item)
        log.info(f'Copying "{s}" to "{dest_dir}"')
        if os.path.isdir(s):
            if os.path.exists(d):
                shutil.rmtree(d)
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)


def copy_release_files_and_restart(src_dir, dest_dir):
    """Will create a bat to copy files after main process has ended and restart the main process without upgrade"""
    exe_path = os.path.join(dest_dir, f"{MAIN_EXE_NAME}.exe")
    script_path = os.path.join(dest_dir, COPY_BAT_NAME)

    with open(script_path, "w") as script:
        script.write("@echo off\n")
        script.write(f'echo Copying "{src_dir}" files to "{dest_dir}""\n')
        script.write("timeout /t 3\n")  # waits for main script to end
        script.write(f'xcopy /s /e /h /r /y /q "{src_dir}\\*" "{dest_dir}"\n')
        script.write(f'start "" "{exe_path}" -nu\n')
        script.write(f'rmdir /s /q "{src_dir}"\n')
        # script.write(f'del "{script_path}"\n')

    if IS_PROD:
        subprocess.Popen(["cmd", "/c", script_path])


def download_update(url, download_path):
    """Download github zip file"""
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(download_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)


def exception_infos(ex):
    """Get exception infos"""
    tb_list = traceback.extract_tb(ex.__traceback__)
    filename, line_number, func_name, text = tb_list[-1]
    return f"in {filename} at line {line_number}: '{ex}'"


def get_dated_backup_dir(backup_dir, day):
    """Get dated backup dir"""
    dated_dir = os.path.join(backup_dir, day)
    if not os.path.exists(dated_dir):
        os.makedirs(dated_dir)
    return dated_dir


def get_download_dir_path():
    """Get download dir path for new version zip files"""
    # maybe use tempdir
    # temp_dir = tempfile.gettempdir()
    return os.path.join(get_bundle_dir(), DOWNLOAD_DIR)


def get_last_dated_backup_dir(backup_dir):
    """Get last dated backup dir"""
    subdirs = read_dir(backup_dir, with_path=False, only_folders=True)
    subdirs = [adir for adir in subdirs if re.match(r"^\d{4}-\d{2}-\d{2}$", adir)]
    if subdirs:
        subdirs.sort(reverse=True)
        return os.path.join(backup_dir, subdirs[0])
    return None


def get_latest_release_version(params, release=None):
    """Get GitHub latest or specified release info"""
    if release:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases"
        ret = json_request(url, params)
        if not ret:
            return None, None
        for dic in ret:
            if dic["tag_name"] == release:
                url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/{dic['id']}"
                break
        else:
            stop(f"The release with tag '{release}' cannot be found", params=params)
    else:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    latest_release = json_request(url, params)
    if not latest_release:
        return None, None
    return latest_release["tag_name"], latest_release["assets"][0]["browser_download_url"]


def get_main_backup_dir(create=True):
    """Get main backup dir"""
    if not os.path.exists(MAIN_BACKUP_DIR):
        if create:
            os.makedirs(MAIN_BACKUP_DIR)
        else:
            return None
    return MAIN_BACKUP_DIR


def get_parameter(params_file, param=None, default=None):
    """Get a specific parameter or the full dic"""
    dic = {}
    if os.path.exists(params_file):
        with open(params_file) as pf:
            dic = json.load(pf)
    if param:
        return dic.get(param, default)
    else:
        return dic


def get_scan_profiles_dir():
    """Get profile dir to read or write"""
    for prof_dir in PROFILES_DIRS:
        if os.path.exists(prof_dir):
            return prof_dir


def json_request(url, params):
    """Simple json request"""
    proxies = {}
    if params.get("PROXY"):
        for protocol in ["http", "https"]:
            if params.get("PROXY_USER") and params.get("PROXY_PWD"):
                proxies[protocol] = f"{params['PROXY_USER']}:{params['PROXY_PWD']}@{params['PROXY']}"
            else:
                proxies[protocol] = params["PROXY"]
    try:
        response = requests.get(url, proxies=proxies)
        response.raise_for_status()
    except requests.exceptions.ProxyError as err:
        send_log_message(f"Cannot request '{url}' : '{err}' with proxies {proxies}", params)
        return {}
    except Exception as err:
        send_log_message(f"Cannot request '{url}' : '{err}'", params)
        return {}
    return response.json()


def read_dir(dirpath, with_path=False, only_folders=False, only_files=False, to_skip=[]):
    """Read the dir and return files"""
    files = []
    for filename in os.listdir(dirpath):
        if filename in to_skip:
            continue
        if only_folders and not os.path.isdir(os.path.join(dirpath, filename)):
            continue
        if only_files and not os.path.isfile(os.path.join(dirpath, filename)):
            continue
        if with_path:
            files.append(os.path.join(dirpath, filename))
        else:
            files.append(filename)
    return files


def send_log_message(message, params, log_method=log.error, level="ERROR"):
    """Send log message to webservice.

    :param message: The message to send
    :param params: The parameters dic containing webservice info
    :param log_method: The log method to use
    :param level: The log level to include: ERROR or INFO
    :return: True if the message was sent successfully, False otherwise
    """
    data = {
        "client_id": params["CLIENT_ID"],
        "hostname": params["hostname"],
        "message": message,
        "level": level,
        "version": params.get("version"),
    }
    if log_method:
        log_method(message)
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    try:
        response = requests.post(
            params["SERVER_URL"],
            headers=headers,
            data=json.dumps(data),
            auth=("loguser", params["PLONE_PWD"]),
            timeout=30,  # time in seconds for connexion + read
        )
        response.raise_for_status()  # raises exception when status not 200
        return True
    except Timeout:
        log_method("Timeout while sending log message to %s", params["SERVER_URL"])
        return False
    except ConnectionError:
        log_method("Connection error while sending log message to %s", params["SERVER_URL"])
        return False
    except RequestException as e:
        log_method("Failed to send log message to %s: %s", params["SERVER_URL"], str(e))
        return False


def set_parameter(params_file, key, value):
    """Store client_id in file"""
    if key == "CLIENT_ID" and not re.match(r"^0\d{5}$", value):
        stop(f"Given client_id '{value}' not well formed !")
    dic = get_parameter(params_file)
    dic[key] = value
    with open(params_file, "w") as pf:
        json.dump(dic, pf)
    return dic


def stop(msg="", intup=True, params=None, exit_code=1):
    """Stop the script and log the message.

    :param msg: The message to log
    :param intup: Flag to wait for input before closing
    :param params: The parameters dic containing webservice info. If given the message is sent to the webservice
    :param exit_code: The exit code to return
    """
    if msg:
        log.error(msg)
        if params:
            send_log_message(msg, params, log_method=None)
    if intup:
        input("Press Enter to exit...")
    close_logger()
    sys.exit(exit_code)


def unzip_file(zip_path, extract_to):
    """Unzip downloaded archive and delete it"""
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)
    os.remove(zip_path)
