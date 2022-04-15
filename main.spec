import sys


block_cipher = None


a = Analysis(
    ["rubberfroggy\\main.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("rubberfroggy/editing", "rubberfroggy/editing"),
        ("rubberfroggy/sprites", "rubberfroggy/sprites"),
        ("rubberfroggy/static", "rubberfroggy/static"),
    ],
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
    name="main",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True, upx_exclude=[], name="RubberFroggy")

if sys.platform == "darwin":
    app = BUNDLE(exe, name="DesktopPet", icon=None)
