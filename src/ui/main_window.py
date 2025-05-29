"""主窗口模块"""

import sys
from PyQt6.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import FluentIcon, NavigationItemPosition

from config.theme import ThemeConfig
from ui.navigation import NavigationManager
from pages.extract_audio_page import ExtractAudioPage
from pages.extract_text_page import ExtractTextPage


class MainWindow(QMainWindow):
    """主窗口类"""

    def __init__(self):
        super().__init__()
        self.current_page = None
        self.pages_cache = {}  # 页面缓存

        self.setup_window()
        self.setup_ui()
        self.setup_navigation()

        # 显示默认页面
        self.show_page("extract_audio")

    def setup_window(self):
        """设置窗口属性"""
        self.setWindowTitle("音视频处理工具")
        self.setGeometry(100, 100, ThemeConfig.WINDOW_WIDTH, ThemeConfig.WINDOW_HEIGHT)

        # 应用主题
        ThemeConfig.apply_theme()

    def setup_ui(self):
        """设置用户界面"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局（水平布局）
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 创建导航管理器
        self.navigation_manager = NavigationManager(self)

        # 创建右侧内容区域
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        # 添加到主布局
        self.main_layout.addWidget(self.navigation_manager.get_navigation_widget())
        self.main_layout.addWidget(self.content_widget, 1)

    def setup_navigation(self):
        """设置导航"""
        # 连接页面切换信号
        self.navigation_manager.page_changed.connect(self.show_page)

        # 添加导航项
        self.navigation_manager.add_navigation_item(
            route_key="extract_audio",
            icon=FluentIcon.MUSIC,
            text="提取音频",
            page_factory=ExtractAudioPage,
            position=NavigationItemPosition.TOP,
        )

        self.navigation_manager.add_navigation_item(
            route_key="extract_text",
            icon=FluentIcon.DOCUMENT,
            text="提取文案",
            page_factory=ExtractTextPage,
            position=NavigationItemPosition.TOP,
        )

        # 设置默认选中项
        self.navigation_manager.set_current_item("extract_audio")

    def show_page(self, route_key: str):
        """显示指定页面"""
        # 清空当前内容
        self.clear_content()

        # 从缓存获取或创建新页面
        if route_key not in self.pages_cache:
            page_info = self.navigation_manager.get_page_info(route_key)
            if page_info and "page_factory" in page_info:
                self.pages_cache[route_key] = page_info["page_factory"]()

        # 显示页面
        if route_key in self.pages_cache:
            page = self.pages_cache[route_key]
            self.content_layout.addWidget(page)
            self.current_page = page

    def clear_content(self):
        """清空内容区域"""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)  # 不删除，只是移除父级关系

    def get_current_page(self):
        """获取当前页面"""
        return self.current_page
