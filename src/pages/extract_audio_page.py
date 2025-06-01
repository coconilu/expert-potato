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
    ComboBox,
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
        self.selected_model = "base"
        self.model_download_progress = {}
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

        # 模型选择区域
        model_layout = QHBoxLayout()
        model_label = BodyLabel("选择模型：")
        self.model_combo = ComboBox()
        self.model_combo.setMinimumWidth(150)
        self.model_combo.currentTextChanged.connect(self.on_model_changed)

        # 模型状态标签
        self.model_status_label = CaptionLabel("")
        self.model_status_label.setStyleSheet("color: #666666;")

        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        model_layout.addWidget(self.model_status_label)
        model_layout.addStretch()

        # 初始化模型列表
        self.init_model_list()

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
        self.result_text.setReadOnly(True)
        self.result_text.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # 复制按钮
        self.copy_button = PushButton(AppConstants.EXTRACT_AUDIO_COPY_BUTTON_TEXT)
        self.copy_button.setIcon(FIF.COPY)
        self.copy_button.clicked.connect(self.copy_text)
        self.copy_button.setEnabled(False)

        # 添加到布局
        layout.addWidget(title_label)
        layout.addWidget(self.drop_area)
        layout.addWidget(self.file_path_label)
        layout.addLayout(model_layout)

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

    def init_model_list(self):
        """初始化模型列表"""
        try:
            # 获取支持的模型列表
            worker = AudioExtractWorker("")
            models = worker.supportModel()

            if models:
                for model in models:
                    self.model_combo.addItem(model)
                # 设置默认选择base模型
                if "base" in models:
                    self.model_combo.setCurrentText("base")
                    self.selected_model = "base"
            else:
                # 如果无法获取模型列表，添加默认模型
                default_models = ["tiny", "base", "small", "medium", "large"]
                for model in default_models:
                    self.model_combo.addItem(model)
                self.model_combo.setCurrentText("base")
                self.selected_model = "base"

        except Exception as e:
            print(f"初始化模型列表失败: {e}")
            # 添加默认模型作为备选
            default_models = ["tiny", "base", "small", "medium", "large"]
            for model in default_models:
                self.model_combo.addItem(model)
            self.model_combo.setCurrentText("base")
            self.selected_model = "base"
            self.check_model_status(self.selected_model)

    def on_model_changed(self, model_name: str):
        """模型选择改变事件"""
        self.selected_model = model_name
        self.check_model_status(model_name)

    def check_model_status(self, model_name: str):
        """检查模型状态"""
        try:
            import os

            # 检查模型缓存目录
            model_cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
            model_exists = False

            if os.path.exists(model_cache_dir):
                # 检查是否存在对应的模型文件夹
                for item in os.listdir(model_cache_dir):
                    if f"whisper-{model_name}" in item.lower():
                        model_exists = True
                        break

            if model_exists:
                self.model_status_label.setText("已缓存")
                self.model_status_label.setStyleSheet("color: #28a745;")
            else:
                self.model_status_label.setText("下载模型需要占用一些时间")
                self.model_status_label.setStyleSheet("color: #ffc107;")

        except Exception as e:
            print(f"检查模型状态失败: {e}")
            # 默认显示需要下载
            self.model_status_label.setText("下载模型需要占用一些时间")
            self.model_status_label.setStyleSheet("color: #ffc107;")

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

        # 创建工作线程，传入选择的模型
        self.worker = AudioExtractWorker(self.current_file_path, self.selected_model)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.text_extracted.connect(self.on_text_extracted)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.finished.connect(self.on_extraction_finished)
        self.worker.start()

        InfoBar.info(
            title=AppConstants.EXTRACT_AUDIO_START_TITLE,
            content=AppConstants.EXTRACT_AUDIO_START_CONTENT.format(
                model=self.selected_model
            ),
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

        # 检查模型状态
        self.check_model_status(self.selected_model)

    def copy_text(self):
        """复制文案到剪贴板"""
        text = self.result_text.toPlainText()
        if text:
            from PyQt6.QtWidgets import QApplication

            clipboard = QApplication.clipboard()
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
