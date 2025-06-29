"""提取音频页面模块"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from qfluentwidgets import (
    InfoBar,
    InfoBarPosition,
    BodyLabel,
)
from config.core import AppConstants
from config.theme import ThemeConfig
from pages.components.file_drop_area import FileDropArea
from pages.components.extract_text_area import ExtractTextArea
from pages.components.refine_area import RefineArea
from core import get_state_manager


class ExtractAudioPage(QWidget):
    """提取音频页面"""

    def __init__(self):
        super().__init__()
        self.state_manager = get_state_manager()
        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            AppConstants.EXTRACT_AUDIO_LAYOUT_MARGIN,
            AppConstants.EXTRACT_AUDIO_LAYOUT_MARGIN,
            AppConstants.EXTRACT_AUDIO_LAYOUT_MARGIN,
            AppConstants.EXTRACT_AUDIO_LAYOUT_MARGIN,
        )
        layout.setSpacing(AppConstants.EXTRACT_AUDIO_LAYOUT_SPACING)

        # 页面标题
        title_label = BodyLabel(AppConstants.PAGE_TITLE_EXTRACT_AUDIO)
        title_label.setFont(
            QFont(
                "Microsoft YaHei",
                16,
                QFont.Weight.Bold,
            )
        )
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 文件拖拽区域
        self.drop_area = FileDropArea()
        self.drop_area.file_dropped.connect(self.on_file_selected)

        # 文件路径显示
        # self.file_path_label = BodyLabel(AppConstants.EXTRACT_AUDIO_NO_FILE_SELECTED)
        # self.file_path_label.setStyleSheet(AppConstants.EXTRACT_AUDIO_NO_FILE_STYLE)

        # 文本提取区域
        self.extract_text_area = ExtractTextArea()
        self.extract_text_area.text_extracted.connect(self.on_text_extracted)
        self.extract_text_area.navigate_to_analysis.connect(self.on_navigate_to_analysis)

        # 添加到布局
        layout.addWidget(title_label)
        layout.addWidget(self.drop_area)
        # layout.addWidget(self.file_path_label)
        layout.addWidget(self.extract_text_area)

        # 文案修复区域
        self.refine_area = RefineArea()
        layout.addWidget(self.refine_area)

        layout.addStretch()

    def on_file_selected(self, file_path: str):
        """文件选择事件"""
        self.current_file_path = file_path
        file_name = Path(file_path).name
        # self.file_path_label.setText(
        #     f"{AppConstants.EXTRACT_AUDIO_FILE_SELECTED_PREFIX}{file_name}"
        # )
        # self.file_path_label.setStyleSheet(
        #     AppConstants.EXTRACT_AUDIO_FILE_SELECTED_STYLE
        # )
        # 设置提取区域的文件路径
        self.extract_text_area.set_file_path(file_path)

        InfoBar.success(
            title=AppConstants.EXTRACT_AUDIO_SUCCESS_TITLE,
            content=f"{AppConstants.EXTRACT_AUDIO_SUCCESS_CONTENT_PREFIX}{file_name}",
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=AppConstants.EXTRACT_AUDIO_SUCCESS_DURATION,
            parent=self,
        )

    def on_text_extracted(self, text: str):
        """处理提取的文本"""
        # 更新修复区域的原始文案
        if hasattr(self, "refine_area"):
            self.refine_area.set_original_text(text)

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

    def on_navigate_to_analysis(self, project_id: str):
        """导航到音频分析页面"""
        # 获取主窗口实例
        main_window = self.window()
        if hasattr(main_window, 'navigation_manager'):
            # 先切换到音频分析页面
            main_window.navigation_manager.set_current_item(AppConstants.ROUTE_AUDIO_ANALYSIS)
            main_window.show_page(AppConstants.ROUTE_AUDIO_ANALYSIS)
            
            # 获取音频分析页面实例并加载项目
            if AppConstants.ROUTE_AUDIO_ANALYSIS in main_window.pages_cache:
                analysis_page = main_window.pages_cache[AppConstants.ROUTE_AUDIO_ANALYSIS]
                if hasattr(analysis_page, 'loadProject'):
                    analysis_page.loadProject(project_id)
