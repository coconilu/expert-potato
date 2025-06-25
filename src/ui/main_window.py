"""主窗口模块"""

import sys
from PyQt6.QtWidgets import (
    QMainWindow,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QEvent
from qfluentwidgets import FluentIcon, NavigationItemPosition

from config.theme import ThemeConfig
from config.core import AppConstants, Messages
from ui.navigation import NavigationManager
from ui.title_bar import CustomTitleBar
from pages import ExtractAudioPage
from pages.audio_analysis_page import AudioAnalysisPage
from pages import ExtractAudioResourcePage


class MainWindow(QMainWindow):
    """主窗口类"""

    def __init__(self):
        super().__init__()
        self.current_page = None
        self.drag_position = None
        self.title_bar = None
        self.pages_cache = {}  # 页面缓存

        self.setup_window()
        self.setup_ui()
        self.setup_navigation()

        # 显示默认页面
        self.show_page(AppConstants.DEFAULT_PAGE)

    def setup_window(self):
        """设置窗口属性"""
        self.setWindowTitle(AppConstants.APP_TITLE)
        self.setWindowIcon(ThemeConfig.APP_ICON)  # 设置窗口图标
        self.setGeometry(
            AppConstants.WINDOW_X,
            AppConstants.WINDOW_Y,
            ThemeConfig.WINDOW_WIDTH,
            ThemeConfig.WINDOW_HEIGHT,
        )

        # 隐藏默认标题栏，但保留任务栏交互
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
        )

        # 应用主题
        ThemeConfig.apply_theme()

    def setup_ui(self):
        """设置用户界面"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主垂直布局
        main_vertical_layout = QVBoxLayout(central_widget)
        main_vertical_layout.setContentsMargins(0, 0, 0, 0)
        main_vertical_layout.setSpacing(0)

        # 创建自定义标题栏
        self.title_bar = CustomTitleBar(self)
        self.setup_title_bar_signals()
        main_vertical_layout.addWidget(self.title_bar)

        # 创建内容区域容器
        content_container = QWidget()
        main_vertical_layout.addWidget(content_container)

        # 创建主布局（水平布局）
        self.main_layout = QHBoxLayout(content_container)
        self.main_layout.setContentsMargins(
            AppConstants.LAYOUT_MARGIN,
            AppConstants.LAYOUT_MARGIN,
            AppConstants.LAYOUT_MARGIN,
            AppConstants.LAYOUT_MARGIN,
        )
        self.main_layout.setSpacing(AppConstants.LAYOUT_SPACING)

        # 创建导航管理器
        self.navigation_manager = NavigationManager(self)

        # 创建右侧内容区域
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(
            AppConstants.LAYOUT_MARGIN,
            AppConstants.LAYOUT_MARGIN,
            AppConstants.LAYOUT_MARGIN,
            AppConstants.LAYOUT_MARGIN,
        )

        # 添加到主布局
        self.main_layout.addWidget(self.navigation_manager.get_navigation_widget())
        self.main_layout.addWidget(
            self.content_widget, AppConstants.CONTENT_STRETCH_FACTOR
        )

    def setup_navigation(self):
        """设置导航"""
        # 连接页面切换信号
        self.navigation_manager.page_changed.connect(self.show_page)

        # 添加导航项
        self.navigation_manager.add_navigation_item(
            route_key=AppConstants.ROUTE_EXTRACT_AUDIO,
            icon=FluentIcon.MUSIC,
            text=AppConstants.NAV_TEXT_EXTRACT_AUDIO,
            page_factory=ExtractAudioPage,
            position=NavigationItemPosition.TOP,
        )

        self.navigation_manager.add_navigation_item(
            route_key=AppConstants.ROUTE_AUDIO_ANALYSIS,
            icon=FluentIcon.PEOPLE,
            text=AppConstants.NAV_TEXT_AUDIO_ANALYSIS,
            page_factory=AudioAnalysisPage,
            position=NavigationItemPosition.TOP,
        )

        self.navigation_manager.add_navigation_item(
            route_key=AppConstants.ROUTE_EXTRACT_AUDIO_RESOURCE,
            icon=FluentIcon.DOWNLOAD,
            text=AppConstants.NAV_TEXT_EXTRACT_AUDIO_RESOURCE,
            page_factory=ExtractAudioResourcePage,
            position=NavigationItemPosition.TOP,
        )

        # 设置默认选中项
        self.navigation_manager.set_current_item(AppConstants.ROUTE_EXTRACT_AUDIO)

    def show_page(self, route_key: str):
        """显示指定页面"""
        # 清空当前内容
        self.clear_content()

        # 从缓存获取或创建新页面
        if route_key not in self.pages_cache:
            page_info = self.navigation_manager.get_page_info(route_key)
            if page_info and AppConstants.DICT_KEY_PAGE_FACTORY in page_info:
                self.pages_cache[route_key] = page_info[
                    AppConstants.DICT_KEY_PAGE_FACTORY
                ]()

        # 显示页面
        if route_key in self.pages_cache:
            page = self.pages_cache[route_key]
            self.content_layout.addWidget(page)
            self.current_page = page

    def clear_content(self):
        """清空内容区域"""
        while self.content_layout.count():
            child = self.content_layout.takeAt(AppConstants.LAYOUT_FIRST_ITEM)
            if child.widget():
                child.widget().setParent(None)  # 不删除，只是移除父级关系

    def setup_title_bar_signals(self):
        """设置标题栏信号连接"""
        self.title_bar.minimize_clicked.connect(self.showMinimized)
        self.title_bar.maximize_clicked.connect(self.toggle_maximize)
        self.title_bar.close_clicked.connect(self.close)
        self.title_bar.title_bar_pressed.connect(self.on_title_bar_pressed)
        self.title_bar.title_bar_moved.connect(self.on_title_bar_moved)

    def toggle_maximize(self):
        """切换最大化状态"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
        self.title_bar.update_maximize_button(self.isMaximized())

    def on_title_bar_pressed(self, event):
        """标题栏鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            event.accept()

    def on_title_bar_moved(self, event):
        """标题栏鼠标移动事件"""
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(
            self, "drag_position"
        ):
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def get_current_page(self):
        """获取当前页面"""
        return self.current_page

    def changeEvent(self, event):
        """处理窗口状态变化事件"""
        if event.type() == QEvent.Type.WindowStateChange:
            # 处理任务栏点击事件
            if self.windowState() & Qt.WindowState.WindowMinimized:
                # 窗口被最小化
                pass
            elif event.oldState() & Qt.WindowState.WindowMinimized:
                # 窗口从最小化状态恢复
                self.show()
                self.raise_()
                self.activateWindow()
        super().changeEvent(event)

    def event(self, event):
        """重写事件处理以支持任务栏交互"""
        # 处理任务栏点击事件
        if event.type() == QEvent.Type.WindowActivate:
            # 窗口被激活时确保显示
            if self.isMinimized():
                self.showNormal()
            self.raise_()
            self.activateWindow()
        elif event.type() == QEvent.Type.ApplicationActivate:
            # 应用程序被激活时的处理
            if self.isMinimized():
                self.showNormal()
                self.raise_()
                self.activateWindow()
        return super().event(event)

    def showEvent(self, event):
        """窗口显示事件"""
        super().showEvent(event)
        # 确保窗口在任务栏中正确显示
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event):
        """窗口关闭事件"""
        # 可以在这里添加关闭前的清理工作
        event.accept()
        super().closeEvent(event)
