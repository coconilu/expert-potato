import os
import tempfile
import threading
import re
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

    def sanitize_filename(self, filename: str) -> str:
        """清理文件名，移除特殊字符"""
        # 移除或替换Windows文件名中的非法字符
        illegal_chars = r'[<>:"/\\|?*]'
        filename = re.sub(illegal_chars, '_', filename)
        
        # 移除前后空格并限制长度
        filename = filename.strip()
        if len(filename) > 200:
            filename = filename[:200]
            
        return filename

    def run(self):
        """执行音频提取"""
        try:
            import yt_dlp

            # 记录下载前的文件列表
            files_before = set(os.listdir(self.output_dir)) if os.path.exists(self.output_dir) else set()

            self.progress_updated.emit(AppConstants.ONLINE_AUDIO_MSG_PROCESSING)

            # 先获取视频信息以生成清理后的文件名
            with yt_dlp.YoutubeDL({"quiet": True}) as ydl_info:
                info = ydl_info.extract_info(self.url, download=False)
                title = info.get("title", "unknown")
                sanitized_title = self.sanitize_filename(title)

            # 生成唯一的文件名（如果文件已存在，添加时间戳）
            import time
            timestamp = int(time.time())
            final_filename = sanitized_title
            expected_mp3_path = os.path.join(self.output_dir, f"{final_filename}.mp3")
            
            # 如果文件已存在，添加时间戳
            if os.path.exists(expected_mp3_path):
                final_filename = f"{sanitized_title}_{timestamp}"
                expected_mp3_path = os.path.join(self.output_dir, f"{final_filename}.mp3")

            # 配置yt-dlp选项，使用清理后的文件名
            output_template = os.path.join(self.output_dir, f"{final_filename}.%(ext)s")
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": output_template,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
                "noplaylist": True,
                "restrictfilenames": True,  # 限制文件名为ASCII字符
                "windowsfilenames": True,   # 确保Windows兼容性
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 下载并提取音频
                ydl.download([self.url])

                # 查找新生成的音频文件
                files_after = set(os.listdir(self.output_dir))
                new_files = files_after - files_before
                
                print(f"下载前文件: {files_before}")
                print(f"下载后文件: {files_after}")
                print(f"新增文件: {new_files}")
                print(f"输出目录: {self.output_dir}")
                print(f"预期文件名: {final_filename}")
                print(f"预期MP3文件: {expected_mp3_path}")
                
                # 首先检查预期的MP3文件是否存在
                if os.path.exists(expected_mp3_path):
                    print(f"找到预期的MP3文件: {expected_mp3_path}")
                    file_path = os.path.normpath(expected_mp3_path)
                    self.extraction_completed.emit(file_path)
                    return
                
                # 查找新增的音频文件
                audio_extensions = [".mp3", ".m4a", ".webm", ".ogg", ".wav"]
                audio_files = []
                
                for ext in audio_extensions:
                    matching_files = [f for f in new_files if f.lower().endswith(ext.lower())]
                    if matching_files:
                        audio_files.extend(matching_files)
                        break  # 找到匹配的扩展名就停止
                
                if audio_files:
                    # 如果有多个文件，选择最大的（通常是主音频文件）
                    largest_file = max(audio_files, key=lambda f: os.path.getsize(os.path.join(self.output_dir, f)))
                    file_path = os.path.join(self.output_dir, largest_file)
                    
                    # 规范化路径
                    file_path = os.path.normpath(file_path)
                    print(f"从新增文件中找到: {file_path}")
                    self.extraction_completed.emit(file_path)
                    return
                
                # 最后尝试查找所有匹配预期文件名前缀的音频文件
                matching_audio_files = []
                for f in files_after:
                    if f.startswith(final_filename) and any(f.lower().endswith(ext.lower()) for ext in audio_extensions):
                        matching_audio_files.append(f)
                
                if matching_audio_files:
                    # 优先选择mp3文件
                    mp3_files = [f for f in matching_audio_files if f.lower().endswith('.mp3')]
                    if mp3_files:
                        file_path = os.path.normpath(os.path.join(self.output_dir, mp3_files[0]))
                        print(f"从匹配前缀的文件中找到MP3: {file_path}")
                        self.extraction_completed.emit(file_path)
                        return
                    else:
                        # 选择第一个匹配的文件
                        file_path = os.path.normpath(os.path.join(self.output_dir, matching_audio_files[0]))
                        print(f"从匹配前缀的文件中找到: {file_path}")
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

        # 处理按钮区域（初始隐藏）
        self.button_widget = QWidget()
        button_layout = QHBoxLayout(self.button_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(15)
        
        button_layout.addStretch()
        
        # 提取文案按钮
        self.extract_text_button = PrimaryPushButton(AppConstants.ONLINE_AUDIO_EXTRACT_TEXT_BUTTON)
        self.extract_text_button.clicked.connect(self.on_extract_text_button_clicked)
        self.extract_text_button.setFixedSize(120, 40)
        button_layout.addWidget(self.extract_text_button)
        
        # 分析音频按钮
        self.analyze_button = PrimaryPushButton(AppConstants.ONLINE_AUDIO_ANALYZE_BUTTON)
        self.analyze_button.clicked.connect(self.on_analyze_button_clicked)
        self.analyze_button.setFixedSize(120, 40)
        button_layout.addWidget(self.analyze_button)
        
        button_layout.addStretch()
        
        self.button_widget.setVisible(False)
        layout.addWidget(self.button_widget)

        layout.addStretch()
        self.setLayout(layout)

    def setup_temp_dir(self):
        """设置临时目录"""
        if not self.temp_audio_dir:
            self.temp_audio_dir = os.path.normpath(os.path.join(
                tempfile.gettempdir(), AppConstants.VIDEO_EXTRACT_TEMP_DIR
            ))
            os.makedirs(self.temp_audio_dir, exist_ok=True)
            print(f"音频临时目录: {self.temp_audio_dir}")

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
        self.button_widget.setVisible(False)

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

        # 规范化路径显示
        normalized_path = os.path.normpath(file_path)
        file_name = os.path.basename(normalized_path)
        
        # 更新状态管理器
        self.state_manager.set_file(normalized_path)

        # 显示成功信息，显示文件名和简化的路径
        display_path = normalized_path
        # 如果路径太长，只显示文件名和父目录
        if len(display_path) > 80:
            parent_dir = os.path.basename(os.path.dirname(normalized_path))
            display_path = f"...{os.sep}{parent_dir}{os.sep}{file_name}"
        
        self.status_label.setText(
            f"{AppConstants.ONLINE_AUDIO_MSG_COMPLETE}\n文件: {file_name}\n路径: {display_path}"
        )

        # 保存文件路径并显示处理按钮
        self.extracted_file_path = normalized_path
        self.button_widget.setVisible(True)

    def on_extract_text_button_clicked(self):
        """提取文案按钮点击事件"""
        if hasattr(self, 'extracted_file_path') and self.extracted_file_path:
            self.navigate_to_extract_audio_page(self.extracted_file_path)
        else:
            self.show_error_message("没有可处理的音频文件")

    def on_analyze_button_clicked(self):
        """分析音频按钮点击事件"""
        if hasattr(self, 'extracted_file_path') and self.extracted_file_path:
            self.navigate_to_audio_analysis_page(self.extracted_file_path)
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

    def navigate_to_audio_analysis_page(self, file_path: str):
        """跳转到音频分析页面"""
        main_window = self.window()
        if main_window and hasattr(main_window, 'navigation_manager'):
            # 跳转到audio_analysis页面
            main_window.navigation_manager.set_current_item(AppConstants.ROUTE_AUDIO_ANALYSIS)
            main_window.show_page(AppConstants.ROUTE_AUDIO_ANALYSIS)
            
            # 使用QTimer延迟设置文件路径，确保页面已经加载
            QTimer.singleShot(100, lambda: self.set_file_to_analysis_page(file_path))

    def set_file_to_extract_page(self, file_path: str):
        """设置文件路径到音频处理页面"""
        try:
            main_window = self.window()
            if main_window and hasattr(main_window, 'pages_cache'):
                # 获取extract_audio页面实例
                extract_audio_page = main_window.pages_cache.get(AppConstants.ROUTE_EXTRACT_AUDIO)
                if extract_audio_page and hasattr(extract_audio_page, 'on_file_selected'):
                    extract_audio_page.on_file_selected(file_path)
                else:
                    self.show_error_message("目标页面不支持文件设置")
            else:
                print("无法找到页面缓存1")
        except Exception as e:
            self.show_error_message(f"文件路径设置失败: {str(e)}")

    def set_file_to_analysis_page(self, file_path: str):
        """设置文件路径到音频分析页面"""
        try:
            main_window = self.window()
            if main_window and hasattr(main_window, 'pages_cache'):
                # 获取audio_analysis页面实例
                analysis_page = main_window.pages_cache.get(AppConstants.ROUTE_AUDIO_ANALYSIS)
                if analysis_page and hasattr(analysis_page, 'set_file_path'):
                    analysis_page.set_file_path(file_path)
                else:
                    self.show_error_message("目标页面不支持文件设置")
            else:
                print("无法找到页面缓存2")
        except Exception as e:
            self.show_error_message(f"文件路径设置失败: {str(e)}")

    def on_extraction_failed(self, error_message: str):
        """提取失败处理"""
        self.progress_bar.setVisible(False)
        self.extract_button.setEnabled(True)
        self.url_input.setEnabled(True)

        # 隐藏处理按钮
        self.button_widget.setVisible(False)

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
