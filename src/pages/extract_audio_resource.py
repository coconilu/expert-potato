import os
import tempfile
import threading
from urllib.parse import urlparse
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from qfluentwidgets import (
    InfoBar,
    InfoBarPosition,
    BodyLabel,
    LineEdit,
    PrimaryPushButton,
    ProgressBar,
    MessageBox,
)
from config.core import AppConstants
from config.theme import ThemeConfig
from core import get_state_manager


class AudioExtractWorker(QThread):
    """音频提取工作线程"""

    progress_updated = pyqtSignal(str)  # 进度更新信号
    extraction_completed = pyqtSignal(str)  # 提取完成信号
    extraction_failed = pyqtSignal(str)  # 提取失败信号

    def __init__(self, url: str, output_dir: str):
        super().__init__()
        self.url = url
        self.output_dir = output_dir

    def run(self):
        """执行音频提取"""
        try:
            import yt_dlp

            # 配置yt-dlp选项
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": os.path.join(self.output_dir, "%(title)s.%(ext)s"),
                "extractaudio": True,
                "audioformat": "mp3",
                "audioquality": "192",
                "noplaylist": True,
            }

            self.progress_updated.emit(AppConstants.ONLINE_AUDIO_MSG_PROCESSING)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 获取视频信息
                info = ydl.extract_info(self.url, download=False)
                title = info.get("title", "unknown")

                # 下载并提取音频
                ydl.download([self.url])

                # 查找生成的音频文件
                for file in os.listdir(self.output_dir):
                    if file.endswith((".mp3", ".m4a", ".webm", ".ogg")):
                        file_path = os.path.join(self.output_dir, file)
                        self.extraction_completed.emit(file_path)
                        return

                self.extraction_failed.emit("未找到提取的音频文件")

        except ImportError:
            self.extraction_failed.emit("缺少yt-dlp依赖，请运行: uv sync --extra video")
        except Exception as e:
            self.extraction_failed.emit(f"提取失败: {str(e)}")


class ExtractAudioResourcePage(QWidget):
    """在线音频提取页面"""

    def __init__(self):
        super().__init__()
        self.state_manager = get_state_manager()
        self.temp_audio_dir = None
        self.worker = None
        self.setup_ui()
        self.setup_temp_dir()

    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        # 页面标题
        title_label = QLabel(AppConstants.PAGE_TITLE_EXTRACT_AUDIO_RESOURCE)
        title_label.setFont(
            QFont(
                ThemeConfig.DEFAULT_FONT_FAMILY,
                ThemeConfig.TITLE_FONT_SIZE,
                QFont.Weight.Bold,
            )
        )
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 说明文本
        desc_label = BodyLabel("支持YouTube和Bilibili视频链接，自动提取音频文件")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)

        # 输入区域
        input_layout = QVBoxLayout()
        input_layout.setSpacing(15)

        # URL输入框
        self.url_input = LineEdit()
        self.url_input.setPlaceholderText(AppConstants.ONLINE_AUDIO_INPUT_PLACEHOLDER)
        self.url_input.setFixedHeight(40)
        input_layout.addWidget(self.url_input)

        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.extract_button = PrimaryPushButton(
            AppConstants.ONLINE_AUDIO_EXTRACT_BUTTON
        )
        self.extract_button.setFixedSize(120, 40)
        self.extract_button.clicked.connect(self.start_extraction)
        button_layout.addWidget(self.extract_button)

        button_layout.addStretch()
        input_layout.addLayout(button_layout)

        layout.addLayout(input_layout)

        # 进度条
        self.progress_bar = ProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 状态标签
        self.status_label = BodyLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # 进一步处理按钮（初始隐藏）
        self.process_button = PrimaryPushButton(AppConstants.ONLINE_AUDIO_PROCESS_BUTTON)
        self.process_button.clicked.connect(self.on_process_button_clicked)
        self.process_button.setVisible(False)
        layout.addWidget(self.process_button)

        layout.addStretch()
        self.setLayout(layout)

    def setup_temp_dir(self):
        """设置临时目录"""
        if not self.temp_audio_dir:
            self.temp_audio_dir = os.path.join(
                tempfile.gettempdir(), AppConstants.VIDEO_EXTRACT_TEMP_DIR
            )
            os.makedirs(self.temp_audio_dir, exist_ok=True)

    def validate_url(self, url: str) -> bool:
        """验证URL是否有效"""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False

            # 检查是否为支持的平台
            for platform in AppConstants.ONLINE_AUDIO_SUPPORTED_PLATFORMS:
                if platform in parsed.netloc.lower():
                    return True

            return False
        except Exception:
            return False

    def start_extraction(self):
        """开始提取音频"""
        url = self.url_input.text().strip()

        if not url:
            self.show_error_message("请输入视频链接")
            return

        if not self.validate_url(url):
            self.show_error_message(AppConstants.ONLINE_AUDIO_MSG_INVALID_URL)
            return

        # 禁用按钮和输入框
        self.extract_button.setEnabled(False)
        self.url_input.setEnabled(False)

        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 无限进度条
        self.process_button.setVisible(False)

        # 启动工作线程
        self.worker = AudioExtractWorker(url, self.temp_audio_dir)
        self.worker.progress_updated.connect(self.update_status)
        self.worker.extraction_completed.connect(self.on_extraction_completed)
        self.worker.extraction_failed.connect(self.on_extraction_failed)
        self.worker.start()

    def update_status(self, message: str):
        """更新状态信息"""
        self.status_label.setText(message)

    def on_extraction_completed(self, file_path: str):
        """提取完成处理"""
        self.progress_bar.setVisible(False)
        self.extract_button.setEnabled(True)
        self.url_input.setEnabled(True)

        # 更新状态管理器
        self.state_manager.set_file(file_path)

        # 显示成功信息
        self.status_label.setText(
            f"{AppConstants.ONLINE_AUDIO_MSG_COMPLETE}\n文件保存至: {file_path}"
        )

        # 保存文件路径并显示进一步处理按钮
        self.extracted_file_path = file_path
        self.process_button.setVisible(True)

    def on_process_button_clicked(self):
        """处理按钮点击事件"""
        if hasattr(self, 'extracted_file_path') and self.extracted_file_path:
            self.navigate_to_extract_audio_page(self.extracted_file_path)
        else:
            self.show_error_message("没有可处理的音频文件")

    def navigate_to_extract_audio_page(self, file_path: str):
        """跳转到音频处理页面"""
        main_window = self.window()
        if main_window and hasattr(main_window, 'navigation_manager'):
            # 跳转到extract_audio页面
            main_window.navigation_manager.set_current_item(AppConstants.ROUTE_EXTRACT_AUDIO)
            main_window.show_page(AppConstants.ROUTE_EXTRACT_AUDIO)
            
            # 使用QTimer延迟设置文件路径，确保页面已经加载
            QTimer.singleShot(100, lambda: self.set_file_to_extract_page(file_path))

    def set_file_to_extract_page(self, file_path: str):
        """设置文件路径到音频处理页面"""
        try:
            main_window = self.window()
            if main_window and hasattr(main_window, 'pages_cache'):
                # 获取extract_audio页面实例
                extract_audio_page = main_window.pages_cache.get('extract_audio')
                if extract_audio_page and hasattr(extract_audio_page, 'on_file_selected'):
                    extract_audio_page.on_file_selected(file_path)
                else:
                    self.show_error_message("目标页面不支持文件设置")
            else:
                self.show_error_message("无法找到页面缓存")
        except Exception as e:
            self.show_error_message(f"文件路径设置失败: {str(e)}")

    def on_extraction_failed(self, error_message: str):
        """提取失败处理"""
        self.progress_bar.setVisible(False)
        self.extract_button.setEnabled(True)
        self.url_input.setEnabled(True)

        # 隐藏进一步处理按钮
        self.process_button.setVisible(False)

        self.show_error_message(
            f"{AppConstants.ONLINE_AUDIO_MSG_FAILED}\n{error_message}"
        )
        self.status_label.setText(AppConstants.ONLINE_AUDIO_MSG_FAILED)

    def show_success_message(self, message: str):
        """显示成功消息"""
        InfoBar.success(
            title="成功",
            content=message,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self,
        )

    def show_error_message(self, message: str):
        """显示错误消息"""
        InfoBar.error(
            title="错误",
            content=message,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self,
        )

    def closeEvent(self, event):
        """关闭事件处理"""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        event.accept()
