Changelog
=========

0.7.0 (2025-09-01)
------------------

- Used `pip-system-certs` to resolve certificate problems.
  [chris-adam]
- Unpinned pyinstaller version.
  [sgeulette]
- Improved send_log_message to avoid timeout.
  [sgeulette]
- Added exception handling when removing profiles directory.
  [chris-adam]

0.6.0 (2024-08-28)
------------------

- Improved version update.
  [sgeulette]
- Added `-tm` parameter (test message).
  [sgeulette]

0.5.2 (2024-08-26)
------------------

- Added version in message sent to webservice.
  [sgeulette]

0.5.1 (2024-08-23)
------------------

- Corrected bug with relative path.
  [sgeulette]
- Added backuped dirs in first message.
  [sgeulette]

0.5.0 (2024-08-22)
------------------

- Added certifi pem file to be sure https certificates can be validated.
  [sgeulette]

0.4.1 (2024-08-22)
------------------

- Added more info in first message.
  [sgeulette]

0.4.0 (2024-08-21)
------------------

- Added optional basic proxy configuration.
  [sgeulette]

0.3.2 (2024-08-21)
------------------

- Corrected `utils.json_request`.
  [sgeulette]

0.3.1 (2024-08-20)
------------------

- Added tests.
  [sgeulette]

0.3.0 (2024-08-14)
------------------

- Corrected version.
  [sgeulette]

0.2.5 (2024-08-14)
------------------

- Called profiles_restore in main.
  [sgeulette]

0.2.4 (2024-08-14)
------------------

- Corrected set_parameter. Added hostname information.
  [sgeulette]

0.2.3 (2024-08-14)
------------------

- Send an info message (no mail) when the product is updated.
  [sgeulette]

0.2.2 (2024-08-13)
------------------

- Added `--is-auto-started` parameter in main, passed when app is auto started.
  [sgeulette]

0.2.1 (2024-08-13)
------------------

- Changed backup directory.
  [sgeulette]
- Improved exception logging.
  [sgeulette]

0.2.0 (2024-08-13)
------------------

- Added profiles_backup script.
  [sgeulette]
- Stored client identification, plone password and webservice url in configuration file.
  [sgeulette]
- Added profiles_restore script.
  [sgeulette]

0.1.1 (2024-07-19)
------------------

- Handled Windows startup add or remove following parameters.
  [sgeulette]

0.1.0 (2024-07-18)
------------------

- Initial release.
  [sgeulette]
