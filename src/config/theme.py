"""主题配置模块"""

from qfluentwidgets import setTheme, Theme, setThemeColor
from PyQt6.QtGui import QIcon


class ThemeConfig:
    """主题配置类"""

    # 主题设置
    DEFAULT_THEME = Theme.DARK
    DEFAULT_COLOR = "#009faa"

    # 应用图标设置
    APP_ICON = QIcon("src/assets/movie_icon.svg")  # 电影图标

    # 字体设置
    DEFAULT_FONT_FAMILY = "Microsoft YaHei"
    TITLE_FONT_SIZE = 24
    CONTENT_FONT_SIZE = 14

    # 窗口设置
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    NAVIGATION_WIDTH = 200

    @classmethod
    def apply_theme(cls):
        """应用主题设置"""
        setTheme(cls.DEFAULT_THEME)
        setThemeColor(cls.DEFAULT_COLOR)

    @classmethod
    def get_title_style(cls):
        """获取标题样式"""
        return """
            QLabel {
                color: #ffffff;
                padding: 50px;
                background-color: transparent;
            }
        """

    @classmethod
    def get_content_style(cls):
        """获取内容样式"""
        return """
            QLabel {
                color: #cccccc;
                padding: 20px;
                background-color: transparent;
            }
        """
