"""文本提取区域组件模块"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
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
    CardWidget,
)
from config.core import AppConstants
from core import AudioExtractWorker


class ExtractTextArea(CardWidget):
    """文本提取区域组件"""

    # 信号定义
    text_extracted = pyqtSignal(str)  # 文本提取完成信号

    def __init__(self):
        super().__init__()
        self.current_file_path = ""
        self.worker = None
        self.selected_model = "base"
        self.model_download_progress = {}
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 模型选择区域
        model_layout = QHBoxLayout()
        model_label = BodyLabel("选择模型：")
        self.model_combo = ComboBox()
        self.model_combo.setMinimumWidth(
            AppConstants.EXTRACT_AUDIO_MODEL_COMBO_MIN_WIDTH
        )
        self.model_combo.currentTextChanged.connect(self.on_model_changed)

        # 模型状态标签
        self.model_status_label = CaptionLabel("")
        self.model_status_label.setStyleSheet(
            f"color: {AppConstants.EXTRACT_AUDIO_MODEL_STATUS_COLOR};"
        )

        # 提取按钮
        self.extract_button = PushButton(AppConstants.EXTRACT_AUDIO_EXTRACT_BUTTON_TEXT)
        self.extract_button.setIcon(FIF.MICROPHONE)
        self.extract_button.clicked.connect(self.extract_text)
        self.extract_button.setEnabled(False)

        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        model_layout.addWidget(self.model_status_label)
        model_layout.addWidget(self.extract_button)
        model_layout.addStretch()
        layout.addLayout(model_layout)

        # 初始化模型列表
        self.init_model_list()

        # 进度条
        self.progress_bar = ProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 结果文本区域
        result_label = BodyLabel(AppConstants.EXTRACT_AUDIO_RESULT_LABEL_TEXT)
        self.result_text = TextEdit()
        self.result_text.setPlaceholderText(
            AppConstants.EXTRACT_AUDIO_RESULT_PLACEHOLDER
        )
        self.result_text.setMinimumHeight(
            AppConstants.EXTRACT_AUDIO_RESULT_TEXT_MIN_HEIGHT
        )
        # 监听文本变化事件，动态更新复制按钮状态
        self.result_text.textChanged.connect(self.update_copy_button_state)
        layout.addWidget(result_label)
        layout.addWidget(self.result_text)

        # 复制按钮
        copy_layout = QHBoxLayout()
        self.copy_button = PushButton(AppConstants.EXTRACT_AUDIO_COPY_BUTTON_TEXT)
        self.copy_button.setIcon(FIF.COPY)
        self.copy_button.clicked.connect(self.copy_text)
        self.copy_button.setEnabled(False)
        copy_layout.addStretch()
        copy_layout.addWidget(self.copy_button)
        layout.addLayout(copy_layout)

    def set_file_path(self, file_path: str):
        """设置文件路径"""
        self.current_file_path = file_path
        self.extract_button.setEnabled(bool(file_path))

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
            model_cache_dir = os.path.expanduser(AppConstants.AUDIO_EXTRACT_CACHE_DIR)
            model_exists = False

            if os.path.exists(model_cache_dir):
                # 检查是否存在对应的模型文件夹
                for item in os.listdir(model_cache_dir):
                    if (
                        f"{AppConstants.AUDIO_EXTRACT_MODEL_PREFIX}{model_name}"
                        in item.lower()
                    ):
                        model_exists = True
                        break

            if model_exists:
                self.model_status_label.setText(
                    AppConstants.AUDIO_EXTRACT_STATUS_MODEL_CACHED
                )
                self.model_status_label.setStyleSheet(
                    f"color: {AppConstants.AUDIO_EXTRACT_COLOR_MODEL_CACHED};"
                )
            else:
                self.model_status_label.setText(
                    AppConstants.AUDIO_EXTRACT_STATUS_MODEL_DOWNLOAD_NEEDED
                )
                self.model_status_label.setStyleSheet(
                    f"color: {AppConstants.AUDIO_EXTRACT_COLOR_MODEL_DOWNLOAD};"
                )

        except Exception as e:
            print(f"{AppConstants.AUDIO_EXTRACT_ERROR_MODEL_STATUS_CHECK}: {e}")
            # 默认显示需要下载
            self.model_status_label.setText(
                AppConstants.AUDIO_EXTRACT_STATUS_MODEL_DOWNLOAD_NEEDED
            )
            self.model_status_label.setStyleSheet(
                f"color: {AppConstants.AUDIO_EXTRACT_COLOR_MODEL_DOWNLOAD};"
            )

    def extract_text(self):
        """提取文案"""
        if not self.current_file_path:
            return

        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(AppConstants.EXTRACT_AUDIO_PROGRESS_INITIAL_VALUE)
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
        """处理提取的文本"""
        self.result_text.setPlainText(text)
        # 发射信号通知外部
        self.text_extracted.emit(text)

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

    def update_copy_button_state(self):
        """根据文本区域内容更新复制按钮状态"""
        text = self.result_text.toPlainText().strip()
        self.copy_button.setEnabled(bool(text))

    def get_extracted_text(self) -> str:
        """获取提取的文本"""
        return self.result_text.toPlainText()

    def clear_text(self):
        """清空文本"""
        self.result_text.clear()
        self.copy_button.setEnabled(False)
