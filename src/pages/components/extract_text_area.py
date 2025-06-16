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
from core import AudioExtractWorker, get_state_manager, ExtractState


class ExtractTextArea(CardWidget):
    """文本提取区域组件"""

    # 信号定义（保留用于向后兼容）
    text_extracted = pyqtSignal(str)  # 文本提取完成信号

    def __init__(self):
        super().__init__()
        self.worker = None
        self.state_manager = get_state_manager()
        self.selected_output_format = AppConstants.OUTPUT_FORMAT_DEFAULT
        self.setup_ui()
        self.connect_state_signals()

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

        # 设置默认选择的模型
        if "base" in [
            self.model_combo.itemText(i) for i in range(self.model_combo.count())
        ]:
            self.model_combo.setCurrentText("base")
            self.state_manager.state.extract.selected_model = "base"

        # 模型状态标签
        self.model_status_label = CaptionLabel("")
        self.model_status_label.setStyleSheet(
            f"color: {AppConstants.EXTRACT_AUDIO_MODEL_STATUS_COLOR};"
        )

        # 输出格式选择
        output_format_label = BodyLabel(AppConstants.OUTPUT_FORMAT_LABEL_TEXT)
        self.output_format_combo = ComboBox()
        self.output_format_combo.setMinimumWidth(
            AppConstants.OUTPUT_FORMAT_COMBO_MIN_WIDTH
        )
        self.output_format_combo.addItems([
            AppConstants.OUTPUT_FORMAT_TXT,
            AppConstants.OUTPUT_FORMAT_SRT,
            AppConstants.OUTPUT_FORMAT_VTT
        ])
        self.output_format_combo.setCurrentText(AppConstants.OUTPUT_FORMAT_DEFAULT)
        self.output_format_combo.currentTextChanged.connect(self.on_output_format_changed)

        # 提取按钮
        self.extract_button = PushButton(AppConstants.EXTRACT_AUDIO_EXTRACT_BUTTON_TEXT)
        self.extract_button.setIcon(FIF.MICROPHONE)
        self.extract_button.clicked.connect(self.extract_text)

        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        model_layout.addWidget(self.model_status_label)
        model_layout.addWidget(output_format_label)
        model_layout.addWidget(self.output_format_combo)
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
        # 监听文本变化事件，动态更新复制按钮状态和字符数
        self.result_text.textChanged.connect(self.update_copy_button_state)
        self.result_text.textChanged.connect(self.update_char_count)
        layout.addWidget(result_label)
        layout.addWidget(self.result_text)
        
        # 字符数显示标签
        self.char_count_label = CaptionLabel(AppConstants.EXTRACT_AUDIO_CHAR_COUNT_TEXT.format(count=0))
        self.char_count_label.setStyleSheet("color: #888; margin-top: 5px;")
        layout.addWidget(self.char_count_label)

        # 复制按钮
        copy_layout = QHBoxLayout()
        self.copy_button = PushButton(AppConstants.EXTRACT_AUDIO_COPY_BUTTON_TEXT)
        self.copy_button.setIcon(FIF.COPY)
        self.copy_button.clicked.connect(self.copy_text)
        self.copy_button.setEnabled(False)
        copy_layout.addStretch()
        copy_layout.addWidget(self.copy_button)
        layout.addLayout(copy_layout)

    def connect_state_signals(self):
        """连接状态管理器信号"""
        # 连接文件状态变化信号
        self.state_manager.file_state_changed.connect(self.on_file_state_changed)

        # 连接提取状态变化信号
        self.state_manager.extract_state_changed.connect(self.on_extract_state_changed)
        self.state_manager.extract_progress_updated.connect(self.update_progress)
        self.state_manager.extract_completed.connect(self.on_text_extracted)
        self.state_manager.extract_failed.connect(self.on_error)

        # 初始状态更新
        self.update_ui_state()
        self.sync_text_display()

    def on_file_state_changed(self, file_state):
        """文件状态变化处理"""
        self.update_ui_state()

    def on_extract_state_changed(self, extract_state):
        """提取状态变化处理"""
        self.update_ui_state()

        # 更新进度条显示
        if extract_state == ExtractState.PROCESSING:
            self.progress_bar.setVisible(True)
            # 获取进度值
            progress = self.state_manager.state.extract.progress
            self.progress_bar.setValue(progress)
        elif extract_state in [
            ExtractState.COMPLETED,
            ExtractState.ERROR,
            ExtractState.IDLE,
        ]:
            self.progress_bar.setVisible(False)

    def update_ui_state(self):
        """更新UI状态"""
        # 更新提取按钮状态
        can_extract = self.state_manager.can_extract()
        self.extract_button.setEnabled(can_extract)

        # 更新复制按钮状态
        has_text = bool(self.state_manager.get_extracted_text())
        self.copy_button.setEnabled(has_text)
        
        # 同步文本显示
        self.sync_text_display()
    
    def sync_text_display(self):
        """同步状态管理器中的文本到UI显示"""
        extracted_text = self.state_manager.get_extracted_text()
        current_text = self.result_text.toPlainText()
        if extracted_text != current_text:
            self.result_text.setPlainText(extracted_text)

    def set_file_path(self, file_path: str):
        """设置文件路径（保留用于向后兼容）"""
        self.state_manager.set_file(file_path)

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
                    self.state_manager.state.extract.selected_model = "base"
            else:
                # 如果无法获取模型列表，添加默认模型
                default_models = ["tiny", "base", "small", "medium", "large"]
                for model in default_models:
                    self.model_combo.addItem(model)
                self.model_combo.setCurrentText("base")
                self.state_manager.state.extract.selected_model = "base"

        except Exception as e:
            print(f"初始化模型列表失败: {e}")
            # 添加默认模型作为备选
            default_models = ["tiny", "base", "small", "medium", "large"]
            for model in default_models:
                self.model_combo.addItem(model)
            self.model_combo.setCurrentText("base")
            self.state_manager.state.extract.selected_model = "base"
            self.check_model_status("base")

    def on_model_changed(self, model_name: str):
        """模型选择改变事件"""
        self.state_manager.state.extract.selected_model = model_name
        self.check_model_status(model_name)

    def on_output_format_changed(self, format_name: str):
        """输出格式选择改变事件"""
        # 这里可以将选择的格式保存到状态管理器中
        # 暂时只是记录选择的格式，后续可以在提取时使用
        self.selected_output_format = format_name

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
        file_path, _ = self.state_manager.get_file_info()
        if not file_path:
            return

        selected_model = self.state_manager.state.extract.selected_model

        # 通过状态管理器开始提取
        self.state_manager.start_extract(selected_model)

        # 清空结果文本
        self.result_text.clear()

        # 创建工作线程，传入选择的模型和输出格式
        self.worker = AudioExtractWorker(file_path, selected_model, self.selected_output_format)
        self.worker.progress_updated.connect(self.state_manager.update_extract_progress)
        self.worker.text_extracted.connect(self.state_manager.complete_extract)
        self.worker.error_occurred.connect(self.state_manager.fail_extract)
        self.worker.finished.connect(self.on_extraction_finished)
        self.worker.start()

        InfoBar.info(
            title=AppConstants.EXTRACT_AUDIO_START_TITLE,
            content=AppConstants.EXTRACT_AUDIO_START_CONTENT.format(
                model=selected_model
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
        # 发射信号通知外部（保留向后兼容）
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
        if self.worker:
            self.worker.deleteLater()
            self.worker = None

        # 检查模型状态
        selected_model = self.state_manager.state.extract.selected_model
        self.check_model_status(selected_model)

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
        # 发射信号通知外部（保留向后兼容）
        self.text_extracted.emit(text)
    
    def update_char_count(self):
        """更新字符数显示"""
        text = self.result_text.toPlainText()
        char_count = len(text)
        self.char_count_label.setText(AppConstants.EXTRACT_AUDIO_CHAR_COUNT_TEXT.format(count=char_count))

    def get_extracted_text(self) -> str:
        """获取提取的文本"""
        return self.state_manager.get_extracted_text()

    def clear_text(self):
        """清空文本"""
        self.result_text.clear()
        self.state_manager.reset_extract()
