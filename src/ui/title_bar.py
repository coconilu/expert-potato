"""自定义标题栏组件模块"""

from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QToolButton,
    QStyle,
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QPalette

from config.theme import ThemeConfig
from config.core import AppConstants, TitleBarConstants


class CustomTitleBar(QWidget):
    """自定义标题栏组件"""

    # 定义信号
    minimize_clicked = pyqtSignal()
    maximize_clicked = pyqtSignal()
    close_clicked = pyqtSignal()
    title_bar_pressed = pyqtSignal(object)  # 传递事件对象
    title_bar_moved = pyqtSignal(object)  # 传递事件对象

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.maximize_btn = None
        self.setup_ui()
        self.setup_events()

    def setup_ui(self):
        """设置UI"""
        self.setAutoFillBackground(True)
        self.setFixedHeight(TitleBarConstants.HEIGHT)

        # 设置标题栏背景色与主题一致
        palette = self.palette()
        palette.setColor(
            QPalette.ColorRole.Window, palette.color(QPalette.ColorRole.Base)
        )
        self.setPalette(palette)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(
            TitleBarConstants.MARGIN_LEFT,
            TitleBarConstants.MARGIN_TOP,
            TitleBarConstants.MARGIN_RIGHT,
            TitleBarConstants.MARGIN_BOTTOM,
        )
        layout.setSpacing(TitleBarConstants.SPACING)

        # 应用图标
        self.create_app_icon(layout)

        # 应用标题
        self.create_app_title(layout)

        # 添加弹性空间
        layout.addStretch()

        # 窗口控制按钮
        self.create_window_buttons(layout)

    def create_app_icon(self, layout):
        """创建应用图标"""
        icon_label = QLabel()
        icon_label.setPixmap(
            ThemeConfig.APP_ICON.pixmap(
                QSize(TitleBarConstants.ICON_SIZE, TitleBarConstants.ICON_SIZE)
            )
        )
        icon_label.setFixedSize(
            QSize(TitleBarConstants.ICON_SIZE, TitleBarConstants.ICON_SIZE)
        )
        layout.addWidget(icon_label)

    def create_app_title(self, layout):
        """创建应用标题"""
        title_label = QLabel(AppConstants.APP_TITLE)
        title_label.setStyleSheet(
            f"""
            QLabel {{
                color: {TitleBarConstants.TITLE_COLOR};
                font-size: {TitleBarConstants.TITLE_FONT_SIZE}px;
                font-weight: {TitleBarConstants.TITLE_FONT_WEIGHT};
                background-color: transparent;
            }}
        """
        )
        layout.addWidget(title_label)

    def create_window_buttons(self, layout):
        """创建窗口控制按钮"""
        # 最小化按钮
        minimize_btn = self.create_button(
            QStyle.StandardPixmap.SP_TitleBarMinButton,
            self.minimize_clicked.emit,
            TitleBarConstants.BUTTON_HOVER_COLOR,
        )

        # 最大化/还原按钮
        self.maximize_btn = self.create_button(
            QStyle.StandardPixmap.SP_TitleBarMaxButton,
            self.maximize_clicked.emit,
            TitleBarConstants.BUTTON_HOVER_COLOR,
        )

        # 关闭按钮
        close_btn = self.create_button(
            QStyle.StandardPixmap.SP_TitleBarCloseButton,
            self.close_clicked.emit,
            TitleBarConstants.CLOSE_BUTTON_HOVER_COLOR,
        )

        layout.addWidget(minimize_btn)
        layout.addWidget(self.maximize_btn)
        layout.addWidget(close_btn)

    def create_button(self, icon_type, click_handler, hover_color):
        """创建按钮"""
        button = QToolButton()
        button.setIcon(self.style().standardIcon(icon_type))
        button.setFixedSize(
            QSize(TitleBarConstants.BUTTON_SIZE, TitleBarConstants.BUTTON_SIZE)
        )
        button.clicked.connect(click_handler)
        button.setStyleSheet(
            f"""
            QToolButton {{
                border: none;
                background-color: transparent;
                color: {TitleBarConstants.BUTTON_COLOR};
            }}
            QToolButton:hover {{
                background-color: {hover_color};
                color: {TitleBarConstants.BUTTON_HOVER_TEXT_COLOR};
            }}
        """
        )
        return button

    def setup_events(self):
        """设置事件"""
        self.mousePressEvent = self.on_mouse_press
        self.mouseMoveEvent = self.on_mouse_move

    def update_maximize_button(self, is_maximized):
        """更新最大化按钮图标"""
        if is_maximized:
            self.maximize_btn.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarNormalButton)
            )
        else:
            self.maximize_btn.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMaxButton)
            )

    def on_mouse_press(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.title_bar_pressed.emit(event)
            event.accept()

    def on_mouse_move(self, event):
        """鼠标移动事件"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.title_bar_moved.emit(event)
            event.accept()
