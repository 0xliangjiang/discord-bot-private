# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

block_cipher = None

# 分析主脚本
a = Analysis(
    ['gui_main.py'],
    pathex=[current_dir],
    binaries=[],
    datas=[
        ('src', 'src'),
        ('accounts.json', '.'),
        ('.env', '.'),
        ('keyword_responses.json', '.'),
        ('GUI_使用说明.md', '.'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'requests',
        'json',
        'threading',
        'logging',
        'datetime',
        'pathlib',
        'dotenv',
        'concurrent.futures',
        'urllib3',
        'certifi',
        'email.mime.text',
        'email.mime.multipart',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'PIL.ImageTk',
        'PIL.ImageDraw',
        'test',
        'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 创建PYZ文件
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 创建可执行文件
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DiscordBotManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 设置为False隐藏控制台窗口
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None
)