# -*- mode: python ; coding: utf-8 -*-
import argparse
import certifi
import shutil


parser = argparse.ArgumentParser()
parser.add_argument("-r", "--release", dest="release", help="release to include in generated zip file")
ns = parser.parse_args()


a0 = Analysis(
    ['imio/scan_helpers/main.py'],
    pathex=['.', 'imio/scan_helpers'],
    binaries=[],
    datas=[("imio/scan_helpers/version.txt", "."), (certifi.where(), "certifi")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz0 = PYZ(a0.pure)

a1 = Analysis(
    ['imio/scan_helpers/profiles_backup.py'],
    pathex=['.', 'imio/scan_helpers'],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz1 = PYZ(a1.pure)

a2 = Analysis(
    ['imio/scan_helpers/profiles_restore.py'],
    pathex=['.', 'imio/scan_helpers'],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz2 = PYZ(a2.pure)

from imio.scan_helpers.config import MAIN_EXE_NAME
from imio.scan_helpers.config import SCRIPT_PROFILES_BACKUP_NAME
from imio.scan_helpers.config import SCRIPT_PROFILES_RESTORE_NAME

exe0 = EXE(
    pyz0,
    a0.scripts,
    [],
    exclude_binaries=True,
    name=MAIN_EXE_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

exe1 = EXE(
    pyz1,
    a1.scripts,
    [],
    exclude_binaries=True,
    name=SCRIPT_PROFILES_BACKUP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

exe2 = EXE(
    pyz2,
    a2.scripts,
    [],
    exclude_binaries=True,
    name=SCRIPT_PROFILES_RESTORE_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

from imio.scan_helpers.config import BUNDLE_NAME

coll = COLLECT(
    exe0,
    exe1,
    exe2,
    a0.binaries + a1.binaries + a2.binaries,
    a0.datas + a1.datas + a2.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=BUNDLE_NAME,
)

# Archive everything into a zip file
zip_name = f'dist/{BUNDLE_NAME}'
if ns.release:
    zip_name += f'-{ns.release}'
print(f'Creating zip file {zip_name}.zip')
shutil.make_archive(zip_name, 'zip', f'dist/{BUNDLE_NAME}')
