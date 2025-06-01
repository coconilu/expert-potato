"""提取音频页面模块"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QClipboard
from qfluentwidgets import (
    PushButton,
    TextEdit,
    ProgressBar,
    InfoBar,
    InfoBarPosition,
    FluentIcon as FIF,
    BodyLabel,
    CaptionLabel,
)
from config.core import AppConstants, Messages
from config.theme import ThemeConfig
from core import AudioExtractWorker
from pages.components import FileDropArea


class ExtractAudioPage(QWidget):
    """提取音频页面"""

    def __init__(self):
        super().__init__()
        self.current_file_path = ""
        self.worker = None
        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            AppConstants.EXTRACT_AUDIO_LAYOUT_MARGIN,
            AppConstants.EXTRACT_AUDIO_LAYOUT_MARGIN,
            AppConstants.EXTRACT_AUDIO_LAYOUT_MARGIN,
            AppConstants.EXTRACT_AUDIO_LAYOUT_MARGIN,
        )
        layout.setSpacing(AppConstants.EXTRACT_AUDIO_LAYOUT_SPACING)

        # 页面标题
        title_label = BodyLabel(AppConstants.PAGE_TITLE_EXTRACT_AUDIO)
        title_label.setFont(
            QFont(
                ThemeConfig.DEFAULT_FONT_FAMILY,
                ThemeConfig.TITLE_FONT_SIZE,
                QFont.Weight.Bold,
            )
        )
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 文件拖拽区域
        self.drop_area = FileDropArea()
        self.drop_area.file_dropped.connect(self.on_file_selected)

        # 文件路径显示
        self.file_path_label = CaptionLabel(AppConstants.EXTRACT_AUDIO_NO_FILE_SELECTED)
        self.file_path_label.setStyleSheet(AppConstants.EXTRACT_AUDIO_NO_FILE_STYLE)

        # 提取按钮
        self.extract_button = PushButton(AppConstants.EXTRACT_AUDIO_EXTRACT_BUTTON_TEXT)
        self.extract_button.setIcon(FIF.MICROPHONE)
        self.extract_button.clicked.connect(self.extract_text)
        self.extract_button.setEnabled(False)

        # 进度条
        self.progress_bar = ProgressBar()
        self.progress_bar.setVisible(False)

        # 结果文本区域
        result_label = BodyLabel(AppConstants.EXTRACT_AUDIO_RESULT_LABEL_TEXT)
        self.result_text = TextEdit()
        self.result_text.setPlaceholderText(
            AppConstants.EXTRACT_AUDIO_RESULT_PLACEHOLDER
        )
        self.result_text.setMinimumHeight(
            AppConstants.EXTRACT_AUDIO_RESULT_TEXT_MIN_HEIGHT
        )

        # 复制按钮
        self.copy_button = PushButton(AppConstants.EXTRACT_AUDIO_COPY_BUTTON_TEXT)
        self.copy_button.setIcon(FIF.COPY)
        self.copy_button.clicked.connect(self.copy_text)
        self.copy_button.setEnabled(False)

        # 添加到布局
        layout.addWidget(title_label)
        layout.addWidget(self.drop_area)
        layout.addWidget(self.file_path_label)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.extract_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        layout.addWidget(self.progress_bar)
        layout.addWidget(result_label)
        layout.addWidget(self.result_text)

        copy_layout = QHBoxLayout()
        copy_layout.addStretch()
        copy_layout.addWidget(self.copy_button)
        layout.addLayout(copy_layout)

        layout.addStretch()

    def on_file_selected(self, file_path: str):
        """文件选择事件"""
        self.current_file_path = file_path
        file_name = Path(file_path).name
        self.file_path_label.setText(
            f"{AppConstants.EXTRACT_AUDIO_FILE_SELECTED_PREFIX}{file_name}"
        )
        self.file_path_label.setStyleSheet(
            AppConstants.EXTRACT_AUDIO_FILE_SELECTED_STYLE
        )
        self.extract_button.setEnabled(True)

        InfoBar.success(
            title=AppConstants.EXTRACT_AUDIO_SUCCESS_TITLE,
            content=f"{AppConstants.EXTRACT_AUDIO_SUCCESS_CONTENT_PREFIX}{file_name}",
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=AppConstants.EXTRACT_AUDIO_SUCCESS_DURATION,
            parent=self,
        )

    def extract_text(self):
        """提取文案"""
        if not self.current_file_path:
            return

        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.extract_button.setEnabled(False)
        self.result_text.clear()

        # 创建工作线程
        self.worker = AudioExtractWorker(self.current_file_path)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.text_extracted.connect(self.on_text_extracted)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.finished.connect(self.on_extraction_finished)
        self.worker.start()

        InfoBar.info(
            title=AppConstants.EXTRACT_AUDIO_START_TITLE,
            content=AppConstants.EXTRACT_AUDIO_START_CONTENT,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=AppConstants.EXTRACT_AUDIO_START_DURATION,
            parent=self,
        )

    def update_progress(self, value: int):
        """更新进度条"""
        self.progress_bar.setValue(value)

    def on_text_extracted(self, text: str):
        """文案提取完成"""
        self.result_text.setPlainText(text)
        self.copy_button.setEnabled(True)

        InfoBar.success(
            title=AppConstants.EXTRACT_AUDIO_COMPLETE_TITLE,
            content=AppConstants.EXTRACT_AUDIO_COMPLETE_CONTENT,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=AppConstants.EXTRACT_AUDIO_COMPLETE_DURATION,
            parent=self,
        )

    def on_error(self, error_message: str):
        """处理错误"""
        InfoBar.error(
            title=AppConstants.EXTRACT_AUDIO_ERROR_TITLE,
            content=error_message,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=AppConstants.EXTRACT_AUDIO_ERROR_DURATION,
            parent=self,
        )

    def on_extraction_finished(self):
        """提取任务完成"""
        self.progress_bar.setVisible(False)
        self.extract_button.setEnabled(True)
        if self.worker:
            self.worker.deleteLater()
            self.worker = None

    def copy_text(self):
        """复制文案到剪贴板"""
        text = self.result_text.toPlainText()
        if text:
            clipboard = QClipboard()
            clipboard.setText(text)

            InfoBar.success(
                title=AppConstants.EXTRACT_AUDIO_COPY_SUCCESS_TITLE,
                content=AppConstants.EXTRACT_AUDIO_COPY_SUCCESS_CONTENT,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=AppConstants.EXTRACT_AUDIO_COPY_DURATION,
                parent=self,
            )
