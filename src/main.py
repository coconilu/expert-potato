"""主应用程序入口文件"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from config.core import Messages


def create_app():
    """创建应用程序实例"""
    app = QApplication(sys.argv)
    return app


def run_app():
    """运行应用程序"""
    app = create_app()

    # 创建主窗口
    window = MainWindow()
    window.show()

    # 运行应用程序
    return app.exec()


def main():
    """主函数"""
    # 检查是否启用热更新
    if (
        os.environ.get(Messages.HOT_RELOAD_ENV_VAR, "").lower()
        in Messages.HOT_RELOAD_TRUE_VALUES
    ):
        import hupper

        # 启动热更新监控
        reloader = hupper.start_reloader(Messages.HOT_RELOAD_MODULE_PATH)
        # 监控src目录下的所有Python文件
        reloader.watch_files([Messages.HOT_RELOAD_WATCH_PATTERN])

    # 运行应用程序
    sys.exit(run_app())


if __name__ == Messages.CONDITION_MAIN_MODULE:
    main()
