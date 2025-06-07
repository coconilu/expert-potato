"""文件拖拽区域组件模块"""

import os
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QFileDialog
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from qfluentwidgets import (
    CardWidget,
    BodyLabel,
    InfoBar,
    InfoBarPosition,
)
from core import get_state_manager, FileState


class FileDropArea(CardWidget):
    """文件拖拽区域"""

    file_dropped = pyqtSignal(str)

    def get_current_file_path(self) -> str:
        """获取当前选择的文件路径"""
        return self.state_manager.state.file.path or ""

    def clear_file(self):
        """清空文件选择"""
        self.state_manager.reset_file()

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.state_manager = get_state_manager()
        self.setup_ui()
        self.connect_state_signals()

        # 初始状态更新
        self.update_ui_state()

    def connect_state_signals(self):
        """连接状态管理器的信号"""
        self.state_manager.file_state_changed.connect(self.on_file_state_changed)

    def on_file_state_changed(self, file_state: FileState):
        """响应文件状态变化"""
        self.update_ui_state()

    def update_ui_state(self):
        """更新UI状态"""
        file_path = self.state_manager.state.file.path
        file_state = self.state_manager.state.file.state

        if file_path and file_state == FileState.LOADED:
            file_name = os.path.basename(file_path)
            self.tip_label.setText(f"已选择文件: {file_name}")
            self.tip_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.tip_label.setText("拖拽音频文件到此处\n或点击选择文件")
            self.tip_label.setStyleSheet("color: #666; font-style: italic;")

    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 图标和提示文字
        icon_label = QLabel("🎵")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px; margin: 20px;")

        self.tip_label = BodyLabel("拖拽音频文件到此处\n或点击选择文件")
        self.tip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(icon_label)
        layout.addWidget(self.tip_label)

        self.setMinimumHeight(150)
        self.setStyleSheet(
            """
            FileDropArea {
                border: 2px dashed #666;
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.05);
            }
            FileDropArea:hover {
                border-color: #009faa;
                background-color: rgba(0, 159, 170, 0.1);
            }
        """
        )

    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """拖拽放下事件"""
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        if files:
            file_path = files[0]
            # 检查是否为音频文件
            audio_extensions = [".mp3", ".wav", ".m4a", ".flac", ".aac", ".ogg", ".wma"]
            if any(file_path.lower().endswith(ext) for ext in audio_extensions):
                # 通过状态管理器设置文件
                self.state_manager.set_file(file_path)
                # 发射信号保持向后兼容
                self.file_dropped.emit(file_path)
            else:
                InfoBar.error(
                    title="文件格式错误",
                    content="请选择音频文件",
                    orient=Qt.Orientation.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self,
                )

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "选择音频文件",
                "",
                "音频文件 (*.mp3 *.wav *.m4a *.flac *.aac *.ogg *.wma)",
            )
            if file_path:
                # 通过状态管理器设置文件
                self.state_manager.set_file(file_path)
                # 发射信号保持向后兼容
                self.file_dropped.emit(file_path)
