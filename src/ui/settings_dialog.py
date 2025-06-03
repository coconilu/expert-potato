"""配置弹窗组件模块"""

import os
import shutil
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton,
    QWidget,
    QStackedWidget,
    QSizePolicy,
)
from PyQt6.QtCore import Qt
from qfluentwidgets import (
    Pivot,
    BodyLabel,
    PushButton,
    FluentIcon as FIF,
    MessageBox,
)
from config.core import AppConstants
from config.theme import ThemeConfig


class SettingsDialog(QDialog):
    """配置弹窗"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_window()

    def setup_window(self):
        """设置窗口属性"""
        self.setWindowTitle(AppConstants.SETTINGS_DIALOG_TITLE)
        self.setFixedSize(
            AppConstants.SETTINGS_DIALOG_WIDTH, AppConstants.SETTINGS_DIALOG_HEIGHT
        )
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        self.setModal(True)

    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 创建Pivot导航
        self.pivot = Pivot()
        self.pivot.addItem(
            routeKey="general",
            text=AppConstants.SETTINGS_TAB_GENERAL,
            onClick=lambda: self.stacked_widget.setCurrentIndex(0),
        )
        self.pivot.addItem(
            routeKey="model",
            text=AppConstants.SETTINGS_TAB_MODEL,
            onClick=lambda: self.stacked_widget.setCurrentIndex(1),
        )

        # 创建堆叠窗口
        self.stacked_widget = QStackedWidget()

        # 添加常规标签页
        self.general_tab = self.create_general_tab()
        self.stacked_widget.addWidget(self.general_tab)

        # 添加模型标签页
        self.model_tab = self.create_model_tab()
        self.stacked_widget.addWidget(self.model_tab)

        layout.addWidget(self.pivot)
        layout.addWidget(self.stacked_widget)

        # 设置默认选中第一个标签页
        self.pivot.setCurrentItem("general")
        self.stacked_widget.setCurrentIndex(0)

    def create_general_tab(self) -> QWidget:
        """创建常规标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 占位文本
        placeholder_label = BodyLabel(AppConstants.SETTINGS_GENERAL_PLACEHOLDER)
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(placeholder_label)
        layout.addStretch()

        return widget

    def create_model_tab(self) -> QWidget:
        """创建模型标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 模型管理标题
        title_label = BodyLabel(AppConstants.SETTINGS_MODEL_TITLE)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)

        # 模型列表表格
        self.model_table = QTableWidget()
        self.setup_model_table()
        layout.addWidget(self.model_table)

        return widget

    def setup_model_table(self):
        """设置模型表格"""
        # 设置列数和列标题
        self.model_table.setColumnCount(3)
        headers = [
            AppConstants.SETTINGS_MODEL_TABLE_NAME,
            AppConstants.SETTINGS_MODEL_TABLE_SIZE,
            AppConstants.SETTINGS_MODEL_TABLE_ACTION,
        ]
        self.model_table.setHorizontalHeaderLabels(headers)

        # 设置表格属性
        self.model_table.setAlternatingRowColors(True)
        self.model_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.model_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # 设置列宽
        header = self.model_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        # 加载模型数据
        self.load_model_data()

    def load_model_data(self):
        """加载模型数据"""
        models = self.get_huggingface_models()

        # 清空现有数据
        self.model_table.setRowCount(0)

        self.model_table.setRowCount(len(models))

        for row, model in enumerate(models):
            # 名字列
            name_item = QTableWidgetItem(model["name"])
            self.model_table.setItem(row, 0, name_item)

            # 大小列
            size_item = QTableWidgetItem(model["size"])
            self.model_table.setItem(row, 1, size_item)

            # 操作列 - 删除按钮
            delete_btn = PushButton(AppConstants.SETTINGS_MODEL_DELETE_BUTTON)
            delete_btn.setIcon(FIF.DELETE)
            delete_btn.clicked.connect(lambda checked, r=row: self.delete_model(r))
            self.model_table.setCellWidget(row, 2, delete_btn)

    def get_huggingface_models(self):
        """从 huggingface 缓存目录获取模型列表"""
        models = []

        # huggingface 缓存目录路径
        cache_dir = Path(AppConstants.AUDIO_EXTRACT_CACHE_DIR).expanduser()

        if not cache_dir.exists():
            return models

        try:
            # 遍历缓存目录中的所有文件夹
            for item in cache_dir.iterdir():
                if item.is_dir() and not item.name.startswith("."):
                    # 获取模型名称（去掉前缀）
                    model_name = item.name
                    if model_name.startswith("models--"):
                        model_name = model_name.replace("models--", "").replace(
                            "--", "/"
                        )

                    # 计算文件夹大小
                    size = self.get_folder_size(item)
                    size_str = self.format_size(size)

                    models.append(
                        {"name": model_name, "size": size_str, "path": str(item)}
                    )
        except Exception as e:
            print(f"读取模型缓存时出错: {e}")

        return models

    def get_folder_size(self, folder_path: Path) -> int:
        """计算文件夹大小（字节）"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
        except Exception as e:
            print(f"计算文件夹大小时出错: {e}")
        return total_size

    def format_size(self, size_bytes: int) -> str:
        """格式化文件大小显示"""
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(size_bytes)

        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1

        return f"{size:.1f} {size_names[i]}"

    def delete_model(self, row: int):
        """删除模型"""
        if row >= self.model_table.rowCount():
            return

        model_name = self.model_table.item(row, 0).text()

        # 获取模型路径
        models = self.get_huggingface_models()
        if row >= len(models):
            return

        model_path = models[row]["path"]

        # 显示确认对话框
        msg_box = MessageBox(
            "确认删除",
            f"确定要删除模型 {model_name} 吗？\n\n这将永久删除模型文件，无法恢复。",
            self,
        )

        if msg_box.exec():
            try:
                # 删除模型文件夹
                if os.path.exists(model_path):
                    shutil.rmtree(model_path)
                    print(f"已删除模型: {model_name}")

                    # 显示成功消息
                    success_msg = MessageBox(
                        "删除成功", f"模型 {model_name} 已成功删除。", self
                    )
                    success_msg.exec()
                else:
                    # 显示错误消息
                    error_msg = MessageBox(
                        "删除失败", f"模型路径不存在: {model_path}", self
                    )
                    error_msg.exec()

            except Exception as e:
                # 显示错误消息
                error_msg = MessageBox("删除失败", f"删除模型时出错: {str(e)}", self)
                error_msg.exec()

            # 重新加载数据以更新列表
            self.load_model_data()
