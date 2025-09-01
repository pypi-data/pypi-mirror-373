from unittest.mock import MagicMock
from unittest.mock import patch
from utils import copy_release_files_and_restart
from utils import copy_sub_files
from utils import download_update
from utils import get_dated_backup_dir
from utils import get_download_dir_path
from utils import get_last_dated_backup_dir
from utils import get_latest_release_version
from utils import get_main_backup_dir
from utils import get_parameter
from utils import get_scan_profiles_dir
from utils import read_dir
from utils import send_log_message
from utils import set_parameter

import os
import shutil
import unittest


def p(path):
    return os.path.join(*(path.split("/")))


class TestUtils(unittest.TestCase):
    def test_copy_sub_files(self):
        dated_backup_dir = get_dated_backup_dir(p("test_env/kofax_backup"), day="2000-01-01")
        copy_sub_files(p("test_env/ProgramData/Kofax/Kofax Express 3.2/Jobs"), dated_backup_dir, files=["IMIO ENTRANT"])
        self.assertTrue(os.path.exists(p("test_env/kofax_backup/2000-01-01/IMIO ENTRANT/file1")))
        self.assertFalse(os.path.exists(p("test_env/kofax_backup/2000-01-01/IMIO SORTANT")))
        shutil.rmtree(p("test_env/kofax_backup/2000-01-01"))

    def test_copy_release_files_and_restart(self):
        copy_release_files_and_restart("anything", "test_env")
        self.assertTrue(os.path.exists(p("test_env/copy_release_files_and_restart.bat")))
        with open(p("test_env/copy_release_files_and_restart.bat"), "r") as file:
            content = file.read()
            self.assertIn('xcopy /s /e /h /r /y /q "anything\\*" "test_env"', content)
        os.remove(p("test_env/copy_release_files_and_restart.bat"))

    def test_download_update(self):
        download_update(
            "https://github.com/IMIO/imio.scan_helpers/raw/main/requirements.txt", p("test_env/download.txt")
        )
        self.assertTrue(os.path.exists(p("test_env/download.txt")))
        with open(p("test_env/download.txt"), "r") as file:
            content = file.read()
            self.assertIn("pip-system-certs\npyinstaller", content)
        os.remove(p("test_env/download.txt"))

    def test_get_dated_backup_dir(self):
        self.assertFalse(os.path.exists(p("test_env/kofax_backup/2000-01-01")))
        result = get_dated_backup_dir(p("test_env/kofax_backup"), day="2000-01-01")
        self.assertEqual(result, p("test_env/kofax_backup/2000-01-01"))
        self.assertTrue(os.path.exists(p("test_env/kofax_backup/2000-01-01")))
        shutil.rmtree(p("test_env/kofax_backup/2000-01-01"))

    def test_get_download_dir_path(self):
        self.assertTrue(get_download_dir_path().endswith(p("helpers/_downloads")))

    def test_get_last_dated_backup_dir(self):
        self.assertIsNone(get_last_dated_backup_dir(p("test_env/kofax_backup")))
        os.makedirs(p("test_env/kofax_backup/2000-01-01"))
        os.makedirs(p("test_env/kofax_backup/2000-01-02"))
        self.assertEqual(get_last_dated_backup_dir(p("test_env/kofax_backup")), p("test_env/kofax_backup/2000-01-02"))
        shutil.rmtree(p("test_env/kofax_backup/2000-01-01"))
        shutil.rmtree(p("test_env/kofax_backup/2000-01-02"))

    def test_get_latest_release_version(self):
        tag_name, download_url = get_latest_release_version({}, release="0.2.5")
        self.assertEqual(tag_name, "0.2.5")
        self.assertTrue(download_url.endswith("imio-scan-helpers-0.2.5.zip"))
        tag_name, download_url = get_latest_release_version({})
        self.assertTrue(tag_name >= "0.3.0")

    @patch("utils.json_request")
    def test_get_latest_release_version_bad_request(self, mock_json_request):
        mock_json_request.return_value = {}
        self.assertTupleEqual((None, None), get_latest_release_version({}, release="0.2.5"))

    def test_get_main_backup_dir(self):
        self.assertEqual(get_main_backup_dir(create=False), p("test_env/kofax_backup"))

    def test_get_set_parameter(self):
        self.assertEqual(get_parameter(p("test_env/configuration.json")), {})
        self.assertIsNone(get_parameter(p("test_env/configuration.json"), "a_key"))
        dic = set_parameter(p("test_env/configuration.json"), "a_key", "a_value")
        self.assertTrue(os.path.exists(p("test_env/configuration.json")))
        self.assertEqual(get_parameter(p("test_env/configuration.json"), "a_key"), "a_value")
        self.assertDictEqual(dic, {"a_key": "a_value"})
        os.remove(p("test_env/configuration.json"))

    def test_get_scan_profiles_dir(self):
        self.assertEqual(get_scan_profiles_dir(), p("test_env/ProgramData/Kofax/Kofax Express 3.2/Jobs"))

    def test_read_dir(self):
        self.assertEqual(
            read_dir(p("test_env/ProgramData/Kofax/Kofax Express 3.2/Jobs")), ["IMIO ENTRANT", "IMIO SORTANT"]
        )
        self.assertEqual(
            read_dir(p("test_env/ProgramData/Kofax/Kofax Express 3.2/Jobs"), with_path=True),
            [
                p("test_env/ProgramData/Kofax/Kofax Express 3.2/Jobs/IMIO ENTRANT"),
                p("test_env/ProgramData/Kofax/Kofax Express 3.2/Jobs/IMIO SORTANT"),
            ],
        )
        self.assertEqual(
            read_dir(p("test_env/ProgramData/Kofax/Kofax Express 3.2/Jobs"), only_folders=True),
            ["IMIO ENTRANT", "IMIO SORTANT"],
        )
        self.assertEqual(read_dir(p("test_env/ProgramData/Kofax/Kofax Express 3.2/Jobs"), only_files=True), [])
        self.assertEqual(
            read_dir(p("test_env/ProgramData/Kofax/Kofax Express 3.2/Jobs"), to_skip=["IMIO ENTRANT"]), ["IMIO SORTANT"]
        )

    @patch("requests.post")
    def test_send_log_message(self, mock_post):
        params = {
            "CLIENT_ID": "010001",
            "hostname": "pc1",
            "PLONE_PWD": "password",
            "SERVER_URL": "http://example.com",
        }
        logs = []
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        send_log_message("My message", params, log_method=logs.append, level="ERROR")
        self.assertListEqual(logs, ["My message"])


if __name__ == "__main__":
    unittest.main()
