"""文件拖拽区域组件模块"""

from PyQt6.QtWidgets import QVBoxLayout, QLabel, QFileDialog
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from qfluentwidgets import (
    CardWidget,
    BodyLabel,
    InfoBar,
    InfoBarPosition,
)


class FileDropArea(CardWidget):
    """文件拖拽区域"""

    file_dropped = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 图标和提示文字
        icon_label = QLabel("🎵")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px; margin: 20px;")

        tip_label = BodyLabel("拖拽音频文件到此处\n或点击选择文件")
        tip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(icon_label)
        layout.addWidget(tip_label)

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
                self.file_dropped.emit(file_path)
