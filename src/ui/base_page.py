"""页面基类模块"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from config.theme import ThemeConfig


class BasePage(QWidget):
    """页面基类"""

    def __init__(self, title: str, content: str = ""):
        super().__init__()
        self.title = title
        self.content = content
        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)

        # 创建页面标题
        title_label = QLabel(self.title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(
            QFont(
                ThemeConfig.DEFAULT_FONT_FAMILY,
                ThemeConfig.TITLE_FONT_SIZE,
                QFont.Weight.Bold,
            )
        )
        title_label.setStyleSheet(ThemeConfig.get_title_style())

        # 创建内容标签
        content_label = QLabel(self.content or f"这里是{self.title}功能的内容区域")
        content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_label.setFont(
            QFont(ThemeConfig.DEFAULT_FONT_FAMILY, ThemeConfig.CONTENT_FONT_SIZE)
        )
        content_label.setStyleSheet(ThemeConfig.get_content_style())

        # 添加到布局
        layout.addStretch()
        layout.addWidget(title_label)
        layout.addWidget(content_label)
        layout.addStretch()

    def get_title(self) -> str:
        """获取页面标题"""
        return self.title

    def set_content(self, content: str):
        """设置页面内容"""
        self.content = content
        # 可以在这里更新UI
