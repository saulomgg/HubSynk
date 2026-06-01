# -*- mode: python ; coding: utf-8 -*-
# HubSynk v2.0 — PyInstaller Spec
#
# IMPORTANTE: rodar de dentro da raiz do repositório (onde está hubsynk.py)
#   pyinstaller build/hubsynk.spec
#
# O executável final sairá em: dist/HubSynk.exe

block_cipher = None

a = Analysis(
    ['hubsynk.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('assets/app_logo.ico', '.'),
        ('assets/app_icon.png', '.'),
        ('assets/app_logo.ico', 'assets'),
        ('assets/app_icon.png', 'assets'),
        ('src',                 'src'),
    ],
    hiddenimports=[
        'cryptography',
        'cryptography.hazmat.primitives.asymmetric.padding',
        'cryptography.hazmat.primitives.hashes',
        'cryptography.hazmat.primitives.serialization',
        'cryptography.hazmat.backends',
        'cryptography.hazmat.backends.default_backend',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'devtools',
        'tkinter.test',
        'unittest',
    ],
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
    name='HubSynk',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/app_logo.ico',
)
