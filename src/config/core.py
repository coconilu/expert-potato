"""核心配置模块 - 统一管理项目中的常量"""

from enum import Enum


class AppConstants:
    """应用程序常量"""

    # 应用程序基本信息
    APP_TITLE = "剪辑工具"

    # 窗口设置
    WINDOW_X = 100
    WINDOW_Y = 100

    # 布局设置
    LAYOUT_MARGIN = 0
    LAYOUT_SPACING = 0
    CONTENT_STRETCH_FACTOR = 1

    # 默认页面
    DEFAULT_PAGE = "extract_audio"

    # 页面路由键
    ROUTE_EXTRACT_AUDIO = "extract_audio"
    ROUTE_EXTRACT_TEXT = "extract_text"

    # 导航文本
    NAV_TEXT_EXTRACT_AUDIO = "提取音频"
    NAV_TEXT_EXTRACT_TEXT = "提取文案"

    # 页面标题
    PAGE_TITLE_EXTRACT_AUDIO = "提取音频"
    PAGE_TITLE_EXTRACT_TEXT = "提取文案"

    # 页面内容
    PAGE_CONTENT_EXTRACT_AUDIO = (
        "这里是提取音频功能的内容区域\n\n"
        "功能包括：\n"
        "• 从视频文件中提取音频\n"
        "• 支持多种音频格式输出\n"
        "• 批量处理功能"
    )

    PAGE_CONTENT_EXTRACT_TEXT = (
        "这里是提取文案功能的内容区域\n\n"
        "功能包括：\n"
        "• 从音频文件中提取文字\n"
        "• 语音识别转文本\n"
        "• 支持多种语言识别\n"
        "• 字幕生成功能"
    )

    # 默认内容模板
    DEFAULT_CONTENT_TEMPLATE = "这里是{title}功能的内容区域"

    # 字典键名
    DICT_KEY_ICON = "icon"
    DICT_KEY_TEXT = "text"
    DICT_KEY_PAGE_FACTORY = "page_factory"
    DICT_KEY_POSITION = "position"

    # 布局索引
    LAYOUT_FIRST_ITEM = 0


class TitleBarConstants:
    """标题栏常量"""

    # 标题栏尺寸
    HEIGHT = 40
    ICON_SIZE = 20
    BUTTON_SIZE = 32

    # 标题栏边距和间距
    MARGIN_LEFT = 10
    MARGIN_TOP = 0
    MARGIN_RIGHT = 0
    MARGIN_BOTTOM = 0
    SPACING = 8

    # 标题样式
    TITLE_COLOR = "#ffffff"
    TITLE_FONT_SIZE = 14
    TITLE_FONT_WEIGHT = "bold"

    # 按钮样式
    BUTTON_COLOR = "#f0f0f0"
    BUTTON_HOVER_COLOR = "rgba(255, 255, 255, 0.1)"
    BUTTON_HOVER_TEXT_COLOR = "#ffffff"
    CLOSE_BUTTON_HOVER_COLOR = "rgba(255, 0, 0, 0.8)"


class Messages:
    """消息和文档字符串常量"""

    # 模块文档字符串
    DOC_MAIN_WINDOW_MODULE = "主窗口模块"
    DOC_NAVIGATION_MODULE = "导航栏组件模块"
    DOC_BASE_PAGE_MODULE = "页面基类模块"
    DOC_EXTRACT_AUDIO_MODULE = "提取音频页面模块"
    DOC_EXTRACT_TEXT_MODULE = "提取文案页面模块"
    DOC_MAIN_APP_MODULE = "应用程序入口文件"
    DOC_THEME_CONFIG_MODULE = "主题配置模块"
    DOC_CORE_CONFIG_MODULE = "核心配置模块 - 统一管理项目中的常量"

    # 类文档字符串
    DOC_MAIN_WINDOW_CLASS = "主窗口类"
    DOC_NAVIGATION_MANAGER_CLASS = "导航管理器"
    DOC_BASE_PAGE_CLASS = "页面基类"
    DOC_EXTRACT_AUDIO_CLASS = "提取音频页面"
    DOC_EXTRACT_TEXT_CLASS = "提取文案页面"
    DOC_THEME_CONFIG_CLASS = "主题配置类"
    DOC_APP_CONSTANTS_CLASS = "应用程序常量"
    DOC_MESSAGES_CLASS = "消息和文档字符串常量"

    # 方法文档字符串
    DOC_SETUP_WINDOW = "设置窗口属性"
    DOC_SETUP_UI = "设置用户界面"
    DOC_SETUP_NAVIGATION = "设置导航"
    DOC_SHOW_PAGE = "显示指定页面"
    DOC_CLEAR_CONTENT = "清空内容区域"
    DOC_GET_CURRENT_PAGE = "获取当前页面"
    DOC_ADD_NAVIGATION_ITEM = "添加导航项"
    DOC_ON_NAVIGATION_CLICKED = "导航项点击事件"
    DOC_SET_CURRENT_ITEM = "设置当前选中项"
    DOC_GET_NAVIGATION_WIDGET = "获取导航组件"
    DOC_GET_PAGE_INFO = "获取页面信息"
    DOC_GET_TITLE = "获取页面标题"
    DOC_SET_CONTENT = "设置页面内容"
    DOC_EXTRACT_AUDIO = "提取音频的核心功能"
    DOC_BATCH_EXTRACT_AUDIO = "批量提取音频"
    DOC_EXTRACT_TEXT_FROM_AUDIO = "从音频提取文本的核心功能"
    DOC_GENERATE_SUBTITLES = "生成字幕文件"
    DOC_BATCH_EXTRACT_TEXT = "批量提取文案"
    DOC_MAIN_FUNCTION = "主函数"
    DOC_APPLY_THEME = "应用主题设置"
    DOC_GET_TITLE_STYLE = "获取标题样式"
    DOC_GET_CONTENT_STYLE = "获取内容样式"

    # 条件语句
    CONDITION_MAIN_MODULE = "__main__"
