imio.scan_helpers
=================
Various script files to handle MS Windows scan tool

Installation
------------
Use virtualenv in bin directory destination

Build locally
-------------
bin/pyinstaller -y imio-scan-helpers.spec

GitHub actions
--------------
On each push or tag, the github action will build the package and upload it to the github release page.
https://github.com/IMIO/imio.scan_helpers/releases

Windows installation
--------------------
The zip archive must be decompressed in a directory (without version reference) that will be the execution directory.

Windows usage
-------------
* imio-scan-helpers.exe -h : displays the help
* imio-scan-helpers.exe : updates the software based on version and restarts it
* imio-scan-helpers.exe -r tag_name: updates the software with specific release and restarts it
* imio-scan-helpers.exe -c client_id: stores client_id in configuration file
  (used as identification when sending info to imio)
* imio-scan-helpers.exe -p plone_password: stores webservice password in configuration file
  (used when sending info to imio)
* imio-scan-helpers.exe -nu : runs without update
* imio-scan-helpers.exe --startup : adds the software to the windows startup
* imio-scan-helpers.exe --startup-remove : removes the software from the windows startup
* profiles-backup.exe : backups profiles
* profiles-restore.exe : restores profiles
