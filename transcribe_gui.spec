# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['transcribe_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('./downloads/README.txt', './downloads/'), ('./downloads/subs/README.txt', './downloads/subs/'), ('./ffmpeg.exe', '.'), ('./ffprobe.exe', '.'), ('C:\\Python312\\envs\\videosubs\\Lib\\site-packages\\whisper\\assets\\', './whisper/assets/')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='transcribe_gui',
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
    contents_directory='.',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='transcribe_gui',
)
