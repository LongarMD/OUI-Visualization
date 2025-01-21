# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

# Get a list of all files in assets directory
assets_dir = "assets"
assets_files = []
for path, dirs, files in os.walk(assets_dir):
    for file in files:
        file_path = os.path.join(path, file)
        dest_path = os.path.join("assets", os.path.relpath(file_path, assets_dir))
        assets_files.append((file_path, os.path.dirname(dest_path)))

print("Bundling assets:", assets_files)

a = Analysis(
    ["src/main.py"],
    pathex=[],
    binaries=[],
    datas=assets_files,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="oui-visualization",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets/favicon.png",
)
