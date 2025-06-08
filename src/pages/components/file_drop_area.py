"""文件拖拽区域组件模块"""

import os
import tempfile
from pathlib import Path
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
from config.core import AppConstants
from utils.video_audio_extractor import VideoAudioExtractor


class FileDropArea(CardWidget):
    """文件拖拽区域"""

    file_dropped = pyqtSignal(str)

    def get_current_file_path(self) -> str:
        """获取当前选择的文件路径"""
        return self.state_manager.state.file.path or ""

    def clear_file(self):
        """清空文件选择"""
        self.state_manager.reset_file()
        self.cleanup_temp_files()
        
    def cleanup_temp_files(self):
        """清理临时文件"""
        if self.video_extractor:
            self.video_extractor.cleanup()
            self.video_extractor = None
            
    def is_video_file(self, file_path: str) -> bool:
        """检查是否为视频文件"""
        file_ext = Path(file_path).suffix.lower()
        return file_ext in AppConstants.SUPPORTED_VIDEO_EXTENSIONS
        
    def is_audio_file(self, file_path: str) -> bool:
        """检查是否为音频文件"""
        file_ext = Path(file_path).suffix.lower()
        return file_ext in AppConstants.SUPPORTED_AUDIO_EXTENSIONS
        
    def setup_temp_directory(self):
        """设置临时目录"""
        if not self.temp_audio_dir:
            self.temp_audio_dir = os.path.join(
                tempfile.gettempdir(), 
                AppConstants.VIDEO_EXTRACT_TEMP_DIR
            )
            os.makedirs(self.temp_audio_dir, exist_ok=True)
        return self.temp_audio_dir

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.state_manager = get_state_manager()
        self.video_extractor = None
        self.temp_audio_dir = None
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
            self.tip_label.setText(AppConstants.FILE_DROP_HINT_TEXT)
            self.tip_label.setStyleSheet("color: #666; font-style: italic;")

    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 图标和提示文字
        icon_label = QLabel("🎬")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px; margin: 20px;")

        self.tip_label = BodyLabel(AppConstants.FILE_DROP_HINT_TEXT)
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
            self.process_file(file_path)

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                AppConstants.FILE_DROP_DIALOG_TITLE,
                "",
                AppConstants.FILE_DROP_DIALOG_FILTER,
            )
            if file_path:
                self.process_file(file_path)
                
    def process_file(self, file_path: str):
        """处理选择的文件"""
        if self.is_audio_file(file_path):
            # 直接处理音频文件
            self.handle_audio_file(file_path)
        elif self.is_video_file(file_path):
            # 处理视频文件，提取音频
            self.handle_video_file(file_path)
        else:
            InfoBar.error(
                title="文件格式错误",
                content="请选择音频或视频文件",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self,
            )
            
    def handle_audio_file(self, file_path: str):
        """处理音频文件"""
        # 通过状态管理器设置文件
        self.state_manager.set_file(file_path)
        # 发射信号保持向后兼容
        self.file_dropped.emit(file_path)
        
    def handle_video_file(self, file_path: str):
        """处理视频文件，提取音频"""
        # 显示处理提示
        InfoBar.info(
            title="视频处理",
            content=AppConstants.VIDEO_EXTRACT_MSG_PROCESSING,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self,
        )
        
        # 设置临时目录
        temp_dir = self.setup_temp_directory()
        
        # 创建视频音频提取器
        self.video_extractor = VideoAudioExtractor(file_path, temp_dir)
        self.video_extractor.extraction_completed.connect(self.on_audio_extracted)
        self.video_extractor.error_occurred.connect(self.on_extraction_error)
        
        # 开始提取
        self.video_extractor.start()
        
    def on_audio_extracted(self, audio_file_path: str):
        """音频提取完成"""
        InfoBar.success(
            title="提取成功",
            content=AppConstants.VIDEO_EXTRACT_MSG_COMPLETE,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self,
        )
        
        # 处理提取的音频文件
        self.handle_audio_file(audio_file_path)
        
    def on_extraction_error(self, error_message: str):
        """音频提取失败"""
        InfoBar.error(
            title=AppConstants.VIDEO_EXTRACT_MSG_FAILED,
            content=error_message,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=self,
        )
