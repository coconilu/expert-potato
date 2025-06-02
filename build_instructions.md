# Expert Potato 项目构建打包指南

本文档详细说明如何构建和打包 Expert Potato 项目，生成可分发的 Windows 可执行文件。

## 项目概述

Expert Potato 是一个基于 PyQt6 和 PyQt6-Fluent-Widgets 构建的桌面应用程序，主要功能包括音频提取和文本处理。

## 构建特性

- ✅ 支持 PyQt6 和 PyQt6-Fluent-Widgets
- ✅ 自动包含所有必要依赖
- ✅ 无控制台窗口（GUI 应用）
- ✅ 自动清理和错误处理
- ✅ 支持数据文件和资源打包
- ✅ 跨平台构建支持
- ✅ **优化构建大小** - 排除 faster-whisper 模型缓存
- ✅ **智能模块排除** - 自动排除不必要的大型依赖

## 文件大小优化说明

### 问题背景

faster-whisper 会在用户目录下缓存模型文件（通常在 `~/.cache/huggingface/hub`），这些模型文件可能达到几 GB 大小。默认情况下，PyInstaller 可能会将这些缓存文件打包进最终的可执行文件中，导致构建产物异常庞大。

### 解决方案

我们提供了三种构建方法：

1. **优化构建（推荐）** - `python build.py build`

   - 使用专门的 `expert_potato.spec` 文件
   - 自动排除模型缓存目录和大型模型文件
   - 排除不必要的 PyTorch 和 HuggingFace 模块
   - 预期文件大小：50-200MB

2. **文件夹构建** - `python build.py folder`

   - 同样使用优化配置
   - 生成文件夹而非单文件，启动更快
   - 适合开发和测试环境

3. **传统构建（备选）** - `python build.py legacy`
   - 使用传统的 PyInstaller 命令
   - 可能包含模型缓存，文件较大
   - 仅在优化构建出现问题时使用

### 运行时模型下载

由于排除了预缓存的模型，应用程序在首次使用语音识别功能时会自动下载所需的模型文件。这是正常行为，用户只需等待下载完成即可。

## 环境要求

- Python 3.11.12 或更高版本
- Windows 操作系统（用于构建 Windows 可执行文件）
- uv 包管理器

## 快速开始

### 1. 安装构建依赖

```bash
# 安装开发依赖（包含 PyInstaller）
uv sync --extra dev
```

### 2. 构建应用程序

**方法一：使用批处理脚本（推荐）**

```bash
# Windows
build.bat
```

**方法二：使用 Python 脚本**

```bash
# 优化构建（推荐）- 排除模型缓存，文件更小
python build.py build

# 文件夹版本 - 启动更快，但文件数量多
python build.py folder

# 传统构建 - 备选方案，可能文件较大
python build.py legacy
```

**方法三：直接使用 spec 文件（高级用户）**

```bash
uv run pyinstaller expert_potato.spec
```

## 安装依赖

### 1. 安装项目依赖

```bash
# 使用 uv 安装项目依赖
uv sync
```

### 2. 安装 PyInstaller

```bash
# 安装 PyInstaller 和相关工具
uv add pyinstaller
uv add pyinstaller-hooks-contrib
```

## 构建方法

### 基础构建

1. **进入项目根目录**

   ```bash
   cd c:\Users\admin\Documents\GitHub\expert-potato
   ```

2. **运行基础构建命令**
   ```bash
   # 基础构建（生成文件夹形式的分发包）
   uv run pyinstaller src/main.py --name="Expert Potato" --windowed
   ```

### 高级构建选项

#### 单文件构建

```bash
# 生成单个可执行文件
uv run pyinstaller src/main.py --name="Expert Potato" --onefile --windowed
```

#### 带图标的构建

```bash
# 如果有应用图标文件（.ico格式）
uv run pyinstaller src/main.py --name="Expert Potato" --onefile --windowed --icon=assets/icon.ico
```

#### 完整构建配置

```bash
# 推荐的完整构建命令
uv run pyinstaller src/main.py \
  --name="Expert Potato" \
  --onefile \
  --windowed \
  --add-data="src/config;config" \
  --add-data="src/ui;ui" \
  --hidden-import="PyQt6" \
  --hidden-import="PyQt6.QtWidgets" \
  --hidden-import="qfluentwidgets" \
  --hidden-import="faster_whisper" \
  --hidden-import="torch" \
  --hidden-import="torchaudio"
```

## 构建脚本

### 创建构建脚本

创建 `build.py` 文件来自动化构建过程：

```python
#!/usr/bin/env python3
"""构建脚本 - 自动化打包过程"""

import os
import sys
import subprocess
from pathlib import Path

def build_app():
    """构建应用程序"""
    print("🚀 开始构建 Expert Potato...")

    # 构建命令
    cmd = [
        "uv", "run", "pyinstaller",
        "src/main.py",
        "--name=Expert Potato",
        "--onefile",
        "--windowed",
        "--add-data=src/config;config",
        "--add-data=src/ui;ui",
        "--hidden-import=PyQt6",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=qfluentwidgets",
        "--hidden-import=faster_whisper",
        "--hidden-import=torch",
        "--hidden-import=torchaudio",
        "--clean",
        "--noconfirm"
    ]

    try:
        # 执行构建
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 构建成功！")
        print(f"📦 可执行文件位置: dist/Expert Potato.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def clean_build():
    """清理构建文件"""
    import shutil

    dirs_to_clean = ["build", "dist", "__pycache__"]
    files_to_clean = ["*.spec"]

    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🧹 已清理: {dir_name}")

    # 清理 .spec 文件
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"🧹 已清理: {spec_file}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        clean_build()
    else:
        build_app()
```

### 使用构建脚本

```bash
# 构建应用
python build.py

# 清理构建文件
python build.py clean
```

## 构建输出

构建完成后，你会在项目目录中看到以下文件夹：

- `build/` - PyInstaller 的临时构建文件
- `dist/` - 最终的分发文件
  - `Expert Potato.exe` - 可执行文件（如果使用 --onefile）
  - 或 `Expert Potato/` 文件夹（如果不使用 --onefile）

## 常见问题解决

### 1. 缺少模块错误

如果遇到 "ModuleNotFoundError"，在构建命令中添加 `--hidden-import` 参数：

```bash
--hidden-import=模块名
```

### 2. 数据文件缺失

使用 `--add-data` 参数包含必要的数据文件：

```bash
--add-data="源路径;目标路径"
```

### 3. 更新 PyInstaller

如果遇到兼容性问题，更新 PyInstaller：

```bash
uv add --upgrade pyinstaller pyinstaller-hooks-contrib
```

### 4. 调试构建问题

添加调试参数获取更多信息：

```bash
uv run pyinstaller src/main.py --debug=all --log-level=DEBUG
```

## 分发说明

### 单文件分发

如果使用 `--onefile` 选项，只需分发 `dist/Expert Potato.exe` 文件。

### 文件夹分发

如果不使用 `--onefile`，需要分发整个 `dist/Expert Potato/` 文件夹。

### 系统要求

生成的可执行文件需要在目标系统上满足：

- Windows 7 或更新版本
- 64 位系统（如果在 64 位系统上构建）
- Visual C++ Redistributable（通常已预装）

## 性能优化

### 减小文件大小

1. **排除不必要的模块**

   ```bash
   --exclude-module=模块名
   ```

2. **使用 UPX 压缩**（可选）
   ```bash
   # 安装 UPX
   # 然后在构建时添加
   --upx-dir=UPX安装路径
   ```

### 提高启动速度

- 使用文件夹分发而不是单文件
- 减少不必要的依赖

## 自动化构建

### 批处理脚本

创建 `build.bat` 文件：

```batch
@echo off
echo 构建 Expert Potato...
uv run pyinstaller src/main.py --name="Expert Potato" --onefile --windowed --clean --noconfirm
echo 构建完成！
echo 可执行文件位置: dist\Expert Potato.exe
pause
```

### GitHub Actions（可选）

如果需要自动化构建，可以配置 GitHub Actions 工作流。

## 总结

通过以上步骤，你可以成功构建和打包 Expert Potato 项目。建议：

1. 首先尝试基础构建确保可行性
2. 根据需要添加高级选项
3. 测试生成的可执行文件
4. 根据实际情况调整构建参数

如有问题，请检查构建日志并根据错误信息进行调整。
