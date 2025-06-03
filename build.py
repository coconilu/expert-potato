#!/usr/bin/env python3
"""构建脚本 - 自动化打包过程"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def build_app():
    """构建应用程序（文件夹版本，推荐）"""
    print("🚀 开始构建 Expert Potato (优化版本)...")
    print("📝 注意: 使用优化的spec文件来减小构建产物大小")
    print("🎯 策略: 排除模型缓存，运行时自动下载")

    # 检查是否存在 src/main.py
    if not Path("src/main.py").exists():
        print("❌ 错误: 找不到 src/main.py 文件")
        return False

    # 检查是否存在优化的spec文件
    spec_file = "Expert Potato.spec"
    if not Path(spec_file).exists():
        print(f"❌ 错误: 找不到 {spec_file} 文件")
        return False

    # 使用优化的spec文件构建（排除模型缓存和大型模块）
    cmd = [
        "uv",
        "run",
        "pyinstaller",
        spec_file,
        "--clean",
        "--noconfirm",
    ]

    try:
        # 执行构建
        print("📦 正在执行构建命令...")
        result = subprocess.run(cmd, check=True)
        print("✅ 构建成功！")

        # 检查输出文件夹
        app_dir = Path("dist/Expert Potato")
        if app_dir.exists():
            print(f"📦 应用程序文件夹: {app_dir}")
            exe_path = app_dir / "Expert Potato.exe"
            if exe_path.exists():
                file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
                print(f"🎯 主执行文件: {exe_path}")
                print(f"📏 主文件大小: {file_size:.1f} MB")

                # 计算整个文件夹大小
                total_size = sum(
                    f.stat().st_size for f in app_dir.rglob("*") if f.is_file()
                ) / (1024 * 1024)
                print(f"📊 总文件夹大小: {total_size:.1f} MB")
                print(f"💡 提示: 首次运行时会自动下载模型文件")
            else:
                print("⚠️  警告: 未找到预期的主执行文件")
        else:
            print("⚠️  警告: 未找到预期的应用程序文件夹")

        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return False
    except FileNotFoundError:
        print("❌ 错误: 找不到 uv 命令，请确保已安装 uv")
        return False


def build_folder():
    """构建文件夹版本（启动更快）"""
    print("🚀 开始构建 Expert Potato (文件夹版本)...")
    print("📝 注意: 文件夹版本启动更快，但文件较多")

    # 检查是否存在 src/main.py
    if not Path("src/main.py").exists():
        print("❌ 错误: 找不到 src/main.py 文件")
        return False

    # 构建命令（不使用 --onefile）
    cmd = [
        "uv",
        "run",
        "pyinstaller",
        "src/main.py",
        "--name=Expert Potato",
        "--windowed",
        "--add-data=src/config;config",
        "--add-data=src/ui;ui",
        "--add-data=src/pages;pages",
        "--add-data=src/core;core",
        "--hidden-import=PyQt6",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=qfluentwidgets",
        "--hidden-import=faster_whisper",
        "--hidden-import=torch",
        "--hidden-import=torchaudio",
        "--hidden-import=requests",
        "--hidden-import=hupper",
        # 排除模型缓存和大文件
        "--exclude-module=transformers",
        "--exclude-module=huggingface_hub.file_download",
        "--exclude-module=torch.distributed",
        "--exclude-module=torch.testing",
        "--exclude-module=torchaudio.datasets",
        "--exclude-module=torchaudio.models",
        "--clean",
        "--noconfirm",
    ]

    try:
        # 执行构建
        print("📦 正在执行构建命令...")
        result = subprocess.run(cmd, check=True)
        print("✅ 构建成功！")

        # 检查输出文件夹
        app_dir = Path("dist/Expert Potato")
        if app_dir.exists():
            print(f"📦 应用程序文件夹: {app_dir}")
            exe_path = app_dir / "Expert Potato.exe"
            if exe_path.exists():
                print(f"🎯 主执行文件: {exe_path}")
        else:
            print("⚠️  警告: 未找到预期的应用程序文件夹")

        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return False
    except FileNotFoundError:
        print("❌ 错误: 找不到 uv 命令，请确保已安装 uv")
        return False


def clean_build():
    """清理构建文件"""
    print("🧹 清理构建文件...")

    dirs_to_clean = ["build", "dist"]
    files_to_clean = ["*.spec"]

    # 清理目录
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"🧹 已清理目录: {dir_name}")

    # 清理 .spec 文件
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"🧹 已清理文件: {spec_file}")

    # 清理 __pycache__ 目录
    for pycache in Path(".").rglob("__pycache__"):
        if pycache.is_dir():
            shutil.rmtree(pycache)
            print(f"🧹 已清理缓存: {pycache}")

    print("✅ 清理完成！")


def install_pyinstaller():
    """安装 PyInstaller"""
    print("📦 安装 PyInstaller...")

    try:
        cmd = ["uv", "add", "pyinstaller", "pyinstaller-hooks-contrib"]
        subprocess.run(cmd, check=True)
        print("✅ PyInstaller 安装成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 安装失败: {e}")
        return False
    except FileNotFoundError:
        print("❌ 错误: 找不到 uv 命令，请确保已安装 uv")
        return False


def build_legacy():
    """传统构建方法（备选方案）"""
    print("🚀 开始构建 Expert Potato (传统方法)...")
    print("📝 注意: 这是备选构建方法，可能产生较大的文件")

    # 检查是否存在 src/main.py
    if not Path("src/main.py").exists():
        print("❌ 错误: 找不到 src/main.py 文件")
        return False

    # 传统构建命令
    cmd = [
        "uv",
        "run",
        "pyinstaller",
        "src/main.py",
        "--name=Expert Potato",
        "--onefile",
        "--windowed",
        "--add-data=src/config;config",
        "--add-data=src/ui;ui",
        "--add-data=src/pages;pages",
        "--add-data=src/core;core",
        "--hidden-import=PyQt6",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=qfluentwidgets",
        "--hidden-import=faster_whisper",
        "--hidden-import=torch",
        "--hidden-import=torchaudio",
        "--hidden-import=requests",
        "--hidden-import=hupper",
        "--clean",
        "--noconfirm",
    ]

    try:
        # 执行构建
        print("📦 正在执行传统构建命令...")
        result = subprocess.run(cmd, check=True)
        print("✅ 构建成功！")

        # 检查输出文件
        exe_path = Path("dist/Expert Potato.exe")
        if exe_path.exists():
            file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
            print(f"📦 可执行文件位置: {exe_path}")
            print(f"📏 文件大小: {file_size:.1f} MB")
            if file_size > 500:  # 如果超过500MB
                print("⚠️  警告: 文件较大，可能包含了模型缓存")
                print("💡 建议: 使用 'python build.py build' 命令进行优化构建")
        else:
            print("⚠️  警告: 未找到预期的可执行文件")

        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return False
    except FileNotFoundError:
        print("❌ 错误: 找不到 uv 命令，请确保已安装 uv")
        return False


def show_help():
    """显示帮助信息"""
    print("Expert Potato 构建脚本")
    print("=" * 50)
    print("使用方法:")
    print("  python build.py [命令]")
    print("")
    print("可用命令:")
    print("  build      - 构建单文件版本（推荐，优化大小）")
    print("  folder     - 构建文件夹版本（启动更快）")
    print("  legacy     - 传统构建方法（备选方案）")
    print("  clean      - 清理构建文件")
    print("  install    - 安装 PyInstaller")
    print("  help       - 显示此帮助信息")
    print("")
    print("构建方法说明:")
    print("  build   - 使用优化的spec文件，排除模型缓存，文件更小")
    print("  folder  - 文件夹版本，启动速度快，但文件数量多")
    print("  legacy  - 传统方法，可能包含模型缓存，文件较大")
    print("")
    print("示例:")
    print("  python build.py build")
    print("  python build.py folder")
    print("  python build.py legacy")
    print("  python build.py clean")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        command = "build"
    else:
        command = sys.argv[1].lower()

    if command == "build":
        success = build_app()
    elif command == "folder":
        success = build_folder()
    elif command == "legacy":
        success = build_legacy()
    elif command == "clean":
        clean_build()
        success = True
    elif command == "install":
        success = install_pyinstaller()
    elif command == "help" or command == "-h" or command == "--help":
        show_help()
        success = True
    else:
        print(f"❌ 未知命令: {command}")
        show_help()
        success = False

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
