"""文案修复区域组件模块"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from qfluentwidgets import (
    PushButton,
    TextEdit,
    ProgressBar,
    InfoBar,
    InfoBarPosition,
    FluentIcon as FIF,
    BodyLabel,
    LineEdit,
    CardWidget,
)
from config.theme import ThemeConfig
from config.core import AppConstants
from core import (
    TextRefineWorker,
    ConnectivityChecker,
    ConfigManager,
    get_state_manager,
    RefineState,
)


class RefineArea(CardWidget):
    """文案修复区域组件"""

    # 信号定义
    refined_text_changed = pyqtSignal(str)  # 修复后文案变化信号

    def __init__(self):
        super().__init__()
        self.refine_worker = None
        self.connectivity_checker = None
        self.refine_start_time = 0
        self.refine_timer = QTimer()
        self.refine_timer.timeout.connect(self.update_timer_display)
        self.config_manager = ConfigManager()
        self.state_manager = get_state_manager()
        self.setup_ui()
        self.load_saved_api_key()
        self.connect_state_signals()

        # 初始状态更新
        self.update_ui_state()
        self.sync_text_display()

    def connect_state_signals(self):
        """连接状态管理器的信号"""
        self.state_manager.extract_text_changed.connect(self.on_extract_text_changed)
        self.state_manager.refine_state_changed.connect(self.on_refine_state_changed)
        self.state_manager.refine_text_changed.connect(self.on_refine_text_changed)

    def on_extract_text_changed(self, text: str):
        """响应提取文本变化"""
        self.sync_text_display()
        self.update_ui_state()

    def on_refine_state_changed(self, state: RefineState):
        """响应修复状态变化"""
        self.update_ui_state()

    def on_refine_text_changed(self, text: str):
        """响应修复文本变化"""
        self.sync_text_display()

    def update_ui_state(self):
        """更新UI状态"""
        # 检查是否可以进行修复
        can_refine = self.state_manager.can_refine()
        refine_state = self.state_manager.state.refine.state

        # 更新按钮状态
        self.refine_button.setEnabled(
            can_refine and refine_state != RefineState.PROCESSING
        )

        # 更新进度条显示
        if refine_state == RefineState.PROCESSING:
            self.refine_progress_bar.setVisible(True)
            self.refine_progress_bar.setRange(0, 0)  # 无限进度条
        else:
            self.refine_progress_bar.setVisible(False)

    def sync_text_display(self):
        """同步状态管理器中的文本到UI显示"""
        # 同步修复后文本
        refined_text = self.state_manager.get_refined_text()
        current_refined = self.refined_text.toPlainText()
        if refined_text != current_refined:
            self.refined_text.setPlainText(refined_text)

    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # DeepSeek 文案修复区域标题
        refine_label = BodyLabel("文案修复 (DeepSeek AI)")
        refine_label.setFont(
            QFont(
                ThemeConfig.DEFAULT_FONT_FAMILY,
                ThemeConfig.CONTENT_FONT_SIZE,
                QFont.Weight.Bold,
            )
        )
        layout.addWidget(refine_label)

        # API密钥输入
        api_key_layout = QHBoxLayout()
        api_key_label = BodyLabel("API密钥：")
        self.api_key_input = LineEdit()
        self.api_key_input.setPlaceholderText("请输入DeepSeek API密钥")
        self.api_key_input.setEchoMode(LineEdit.EchoMode.Password)
        self.api_key_input.setMinimumWidth(300)
        # 监听API密钥输入变化，动态更新修复按钮状态和保存API密钥
        self.api_key_input.textChanged.connect(self.update_refine_button_state)
        self.api_key_input.textChanged.connect(self.save_api_key)

        # 连通性检查按钮
        self.connectivity_button = PushButton("检查连通性")
        self.connectivity_button.setIcon(FIF.WIFI)
        self.connectivity_button.clicked.connect(self.check_api_connectivity)
        self.connectivity_button.setEnabled(False)

        # 修复按钮
        self.refine_button = PushButton("修复文案")
        self.refine_button.setIcon(FIF.EDIT)
        self.refine_button.clicked.connect(self.start_refine_text)
        self.refine_button.setEnabled(False)

        # 计时器标签
        self.timer_label = BodyLabel(AppConstants.REFINE_TIMER_INITIAL_TEXT)
        self.timer_label.setVisible(False)

        api_key_layout.addWidget(api_key_label)
        api_key_layout.addWidget(self.api_key_input)
        api_key_layout.addWidget(self.connectivity_button)
        api_key_layout.addWidget(self.refine_button)
        api_key_layout.addWidget(self.timer_label)
        api_key_layout.addStretch()
        layout.addLayout(api_key_layout)

        # 修复进度条
        self.refine_progress_bar = ProgressBar()
        self.refine_progress_bar.setVisible(False)
        layout.addWidget(self.refine_progress_bar)

        # 修复后的文案
        refined_label = BodyLabel("修复后的文案：")
        self.refined_text = TextEdit()
        self.refined_text.setPlaceholderText("修复后的文案将显示在这里...")
        self.refined_text.setMinimumHeight(150)
        self.refined_text.setReadOnly(True)
        # 监听修复后文案变化
        self.refined_text.textChanged.connect(self.on_refined_text_changed)
        layout.addWidget(refined_label)
        layout.addWidget(self.refined_text)

        # 复制修复后文案按钮
        copy_refined_layout = QHBoxLayout()
        self.copy_refined_button = PushButton("复制修复后文案")
        self.copy_refined_button.setIcon(FIF.COPY)
        self.copy_refined_button.clicked.connect(self.copy_refined_text)
        self.copy_refined_button.setEnabled(False)
        copy_refined_layout.addStretch()
        copy_refined_layout.addWidget(self.copy_refined_button)
        layout.addLayout(copy_refined_layout)

    def set_original_text(self, text: str):
        """设置原始文案"""
        # 通过状态管理器设置提取的文本
        self.state_manager.set_extracted_text(text)

    def check_api_connectivity(self):
        """检查DeepSeek API连通性"""
        api_key = self.api_key_input.text().strip()
        if not api_key:
            InfoBar.error(
                title="检查失败",
                content="请先输入API密钥",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self,
            )
            return

        # 禁用按钮，显示检查中状态
        self.connectivity_button.setEnabled(False)
        self.connectivity_button.setText("检查中...")

        # 创建连通性检查工作线程
        self.connectivity_checker = ConnectivityChecker(api_key)
        self.connectivity_checker.check_completed.connect(
            self.on_connectivity_check_completed
        )
        self.connectivity_checker.check_failed.connect(
            self.on_connectivity_check_failed
        )
        self.connectivity_checker.start()

    def on_connectivity_check_completed(self):
        """连通性检查成功"""
        self.connectivity_button.setText("检查连通性")
        self.connectivity_button.setEnabled(True)
        InfoBar.success(
            title="连通性检查成功",
            content="API密钥有效，可以正常使用DeepSeek服务",
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self,
        )
        if self.connectivity_checker:
            self.connectivity_checker.deleteLater()
            self.connectivity_checker = None

    def on_connectivity_check_failed(self, error_message: str):
        """连通性检查失败"""
        self.connectivity_button.setText("检查连通性")
        self.connectivity_button.setEnabled(True)
        InfoBar.error(
            title="连通性检查失败",
            content=f"API连接失败: {error_message}",
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=self,
        )
        if self.connectivity_checker:
            self.connectivity_checker.deleteLater()
            self.connectivity_checker = None

    def update_refine_button_state(self):
        """根据文本区域内容和API密钥更新修复按钮状态"""
        api_key = self.api_key_input.text().strip()
        original_text = self.state_manager.get_extracted_text()
        # 只有当原始文案有内容且API密钥已填写时才启用修复按钮
        self.refine_button.setEnabled(bool(original_text) and bool(api_key))
        # 同时更新连通性检查按钮状态
        self.connectivity_button.setEnabled(bool(api_key))

    def start_refine_text(self):
        """开始文案修复"""
        api_key = self.api_key_input.text().strip()

        if not api_key:
            InfoBar.error(
                title="错误",
                content="请输入DeepSeek API密钥",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self,
            )
            return

        original_text = self.state_manager.get_extracted_text()
        if not original_text:
            InfoBar.error(
                title="错误",
                content="请先提取文案",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self,
            )
            return

        # 重置界面
        self.refine_button.setEnabled(False)
        self.refine_progress_bar.setVisible(True)
        self.refine_progress_bar.setValue(0)

        self.refined_text.clear()
        self.copy_refined_button.setEnabled(False)

        # 启动计时器
        self.start_timer()

        # 直接开始文案修复
        self.start_text_refinement()

    def start_text_refinement(self):
        """开始文案修复处理"""
        api_key = self.api_key_input.text().strip()

        # 构建文案修复的提示词
        original_text = self.state_manager.get_extracted_text()
        refine_prompt = f"""请修复文案中的错别字、语法错误、专业术语和断句分段等问题。

原始文案：
{original_text}

请按照以下要求修复文案：
1. 修正错别字和语法错误，但是不要变更原文（插入或删除）
2. 统一专业术语表达
3. 优化断句和分段，提高可读性
4. 保持原文的语义和风格
5. 确保术语的准确性

请直接返回修复后的文案内容，不需要JSON格式。"""

        # 清理之前的worker
        if self.refine_worker:
            self.refine_worker.deleteLater()

        # 创建并启动工作线程
        self.refine_worker = TextRefineWorker(refine_prompt, api_key)
        self.refine_worker.progress_updated.connect(self.update_refine_progress)
        self.refine_worker.text_refined.connect(self.on_text_refined)
        self.refine_worker.error_occurred.connect(self.on_refine_error)
        self.refine_worker.finished.connect(self.on_refine_finished)
        self.refine_worker.start()

        InfoBar.info(
            title="开始修复",
            content="正在修复文案...",
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self,
        )

    def update_refine_progress(self, value: int):
        """更新修复进度条"""
        self.refine_progress_bar.setValue(value)

    def on_text_refined(self, refined_text: str):
        """文案修复完成"""
        # 通过状态管理器完成修复并设置文本
        self.state_manager.complete_refine(refined_text)

        InfoBar.success(
            title="修复完成",
            content="文案修复已完成！",
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self,
        )

    def on_refine_error(self, error_message: str):
        """处理修复错误"""
        # 通过状态管理器标记修复失败
        self.state_manager.fail_refine(error_message)

        InfoBar.error(
            title="修复失败",
            content=error_message,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=self,
        )

    def on_refine_finished(self):
        """修复任务完成"""
        self.refine_progress_bar.setVisible(False)
        # 停止计时器但保持显示
        self.stop_timer()
        if self.refine_worker:
            self.refine_worker.deleteLater()
            self.refine_worker = None

    def on_refined_text_changed(self):
        """修复后文案变化事件"""
        text = self.refined_text.toPlainText().strip()
        self.copy_refined_button.setEnabled(bool(text))
        # 发射信号通知外部
        self.refined_text_changed.emit(text)

    def copy_refined_text(self):
        """复制修复后的文案到剪贴板"""
        text = self.state_manager.get_refined_text()
        if text:
            from PyQt6.QtWidgets import QApplication

            clipboard = QApplication.clipboard()
            clipboard.setText(text)

            InfoBar.success(
                title="复制成功",
                content="修复后的文案已复制到剪贴板",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self,
            )

    def get_refined_text(self) -> str:
        """获取修复后的文案"""
        return self.state_manager.get_refined_text()

    def start_timer(self):
        """启动计时器"""
        import time

        self.refine_start_time = time.time()
        self.timer_label.setText(AppConstants.REFINE_TIMER_INITIAL_TEXT)
        self.timer_label.setVisible(True)
        self.refine_timer.start(AppConstants.REFINE_TIMER_INTERVAL_MS)

    def stop_timer(self):
        """停止计时器"""
        self.refine_timer.stop()

    def update_timer_display(self):
        """更新计时器显示"""
        import time

        elapsed_time = int(time.time() - self.refine_start_time)
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        timer_text = AppConstants.REFINE_TIMER_TEXT_TEMPLATE.format(
            minutes=minutes, seconds=seconds
        )
        self.timer_label.setText(timer_text)

    def clear_refined_text(self):
        """清空修复后的文案"""
        self.state_manager.reset_refine()

    def save_api_key(self):
        """保存API密钥到本地配置"""
        api_key = self.api_key_input.text().strip()
        if api_key:
            success = self.config_manager.set_api_key(api_key)
            if not success:
                print("保存API密钥失败")
            # 同时更新状态管理器中的API密钥
            self.state_manager.set_api_key(api_key)
        else:
            # 如果API密钥为空，则清除保存的密钥
            self.config_manager.clear_api_key()
            # 同时清除状态管理器中的API密钥
            self.state_manager.set_api_key("")

    def load_saved_api_key(self):
        """加载保存的API密钥"""
        saved_api_key = self.config_manager.get_api_key()
        if saved_api_key:
            self.api_key_input.setText(saved_api_key)
            # 同时更新状态管理器中的API密钥
            self.state_manager.set_api_key(saved_api_key)
            # 手动触发一次状态更新，因为setText不会触发textChanged信号
            self.update_refine_button_state()
