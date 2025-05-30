"""提取文案页面模块"""

from ui.base_page import BasePage
from config.core import AppConstants, Messages


class ExtractTextPage(BasePage):
    """提取文案页面"""

    def __init__(self):
        super().__init__(
            title=AppConstants.PAGE_TITLE_EXTRACT_TEXT,
            content=AppConstants.PAGE_CONTENT_EXTRACT_TEXT,
        )

    def setup_ui(self):
        """设置用户界面"""
        super().setup_ui()
        # 可以在这里添加特定于提取文案页面的UI组件
        # 例如：音频文件选择器、语言选择、识别精度设置等

    def extract_text_from_audio(self, audio_path: str) -> str:
        """从音频提取文本的核心功能"""
        # TODO: 实现语音识别逻辑
        pass

    def generate_subtitles(self, audio_path: str, output_path: str):
        """生成字幕文件"""
        # TODO: 实现字幕生成逻辑
        pass

    def batch_extract_text(self, audio_paths: list, output_dir: str):
        """批量提取文案"""
        # TODO: 实现批量文案提取逻辑
        pass
