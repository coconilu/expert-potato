"""导航栏组件模块"""

from typing import Callable, Dict, Any
from PyQt6.QtCore import pyqtSignal, QObject
from qfluentwidgets import NavigationInterface, NavigationItemPosition, FluentIcon
from config.theme import ThemeConfig
from config.core import AppConstants, Messages
from ui.settings_dialog import SettingsDialog


class NavigationManager(QObject):
    """导航管理器"""

    # 定义信号
    page_changed = pyqtSignal(str)  # 页面切换信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.navigation = NavigationInterface(parent, showMenuButton=True)
        self.navigation.setExpandWidth(ThemeConfig.NAVIGATION_WIDTH)
        self.pages: Dict[str, Dict[str, Any]] = {}
        self.parent_window = parent
        self.setup_settings_button()

    def add_navigation_item(
        self,
        route_key: str,
        icon: FluentIcon,
        text: str,
        page_factory: Callable,
        position: NavigationItemPosition = NavigationItemPosition.TOP,
    ):
        """添加导航项"""
        # 存储页面信息
        self.pages[route_key] = {
            AppConstants.DICT_KEY_ICON: icon,
            AppConstants.DICT_KEY_TEXT: text,
            AppConstants.DICT_KEY_PAGE_FACTORY: page_factory,
            AppConstants.DICT_KEY_POSITION: position,
        }

        # 添加到导航栏
        self.navigation.addItem(
            routeKey=route_key,
            icon=icon,
            text=text,
            onClick=lambda: self.on_navigation_clicked(route_key),
            position=position,
        )

    def on_navigation_clicked(self, route_key: str):
        """导航项点击事件"""
        self.page_changed.emit(route_key)

    def set_current_item(self, route_key: str):
        """设置当前选中项"""
        self.navigation.setCurrentItem(route_key)

    def get_navigation_widget(self):
        """获取导航组件"""
        return self.navigation

    def get_page_info(self, route_key: str) -> Dict[str, Any]:
        """获取页面信息"""
        return self.pages.get(route_key, {})

    def setup_settings_button(self):
        """设置配置按钮"""
        self.navigation.addItem(
            routeKey="settings",
            icon=FluentIcon.SETTING,
            text=AppConstants.NAV_TEXT_SETTINGS,
            onClick=self.show_settings_dialog,
            position=NavigationItemPosition.BOTTOM,
        )

    def show_settings_dialog(self):
        """显示配置弹窗"""
        dialog = SettingsDialog(self.parent_window)
        dialog.exec()
