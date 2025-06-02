# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec文件 - 用于精确控制Expert Potato的打包过程
排除faster-whisper模型缓存以减小构建产物大小
"""

import os
from pathlib import Path

# 获取用户缓存目录
user_cache_dir = os.path.expanduser("~/.cache")
huggingface_cache = os.path.join(user_cache_dir, "huggingface")

# 需要排除的目录和文件模式
excluded_binaries = [
    # HuggingFace模型缓存
    (huggingface_cache + "/*", "."),
    # PyTorch模型文件
    ("*.bin", "."),
    ("*.pt", "."),
    ("*.pth", "."),
    ("*.onnx", "."),
    ("*.safetensors", "."),
    # 其他大文件
    ("**/models--*", "."),
    ("**/snapshots", "."),
]

# 需要排除的模块
excluded_modules = [
    'transformers',
    'huggingface_hub.file_download',
    'torch.distributed',
    'torch.testing',
    'torchaudio.datasets',
    'torchaudio.models',
    'datasets',
    'tokenizers',
    'accelerate',
    'diffusers',
]

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/config', 'config'),
        ('src/ui', 'ui'),
        ('src/pages', 'pages'),
        ('src/core', 'core'),
    ],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'qfluentwidgets',
        'faster_whisper',
        'torch',
        'torchaudio',
        'requests',
        'hupper',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excluded_modules,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 过滤掉模型文件和缓存
def filter_binaries(binaries):
    filtered = []
    for binary in binaries:
        name, path, kind = binary
        # 排除模型文件
        if any(pattern in name.lower() for pattern in ['whisper', 'model', '.bin', '.pt', '.pth', '.onnx', '.safetensors']):
            continue
        # 排除缓存目录
        if 'cache' in path.lower() or 'huggingface' in path.lower():
            continue
        filtered.append(binary)
    return filtered

a.binaries = filter_binaries(a.binaries)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 单文件版本
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Expert Potato',
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
)

# 文件夹版本（注释掉单文件版本，取消注释以下代码）
# exe = EXE(
#     pyz,
#     a.scripts,
#     [],
#     exclude_binaries=True,
#     name='Expert Potato',
#     debug=False,
#     bootloader_ignore_signals=False,
#     strip=False,
#     upx=True,
#     console=False,
#     disable_windowed_traceback=False,
#     argv_emulation=False,
#     target_arch=None,
#     codesign_identity=None,
#     entitlements_file=None,
# )
# 
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='Expert Potato',
# )