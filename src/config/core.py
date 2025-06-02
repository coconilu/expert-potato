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

    # 提取音频页面UI常量
    EXTRACT_AUDIO_LAYOUT_MARGIN = 30
    EXTRACT_AUDIO_LAYOUT_SPACING = 20
    EXTRACT_AUDIO_RESULT_TEXT_MIN_HEIGHT = 200

    # 提取音频页面文本常量
    EXTRACT_AUDIO_NO_FILE_SELECTED = "未选择文件"
    EXTRACT_AUDIO_FILE_SELECTED_PREFIX = "已选择文件："
    EXTRACT_AUDIO_EXTRACT_BUTTON_TEXT = "提取文案"
    EXTRACT_AUDIO_RESULT_LABEL_TEXT = "提取结果："
    EXTRACT_AUDIO_RESULT_PLACEHOLDER = "提取的文案将显示在这里..."
    EXTRACT_AUDIO_COPY_BUTTON_TEXT = "复制文案"

    # 提取音频页面样式常量
    EXTRACT_AUDIO_NO_FILE_STYLE = "color: #888; padding: 10px;"
    EXTRACT_AUDIO_FILE_SELECTED_STYLE = "color: #009faa; padding: 10px;"

    # 提取音频页面InfoBar常量
    EXTRACT_AUDIO_SUCCESS_TITLE = "文件选择成功"
    EXTRACT_AUDIO_SUCCESS_CONTENT_PREFIX = "已选择："
    EXTRACT_AUDIO_START_TITLE = "开始提取"
    EXTRACT_AUDIO_START_CONTENT = "正在使用 Faster-Whisper 【{model}】 提取音频文案..."
    EXTRACT_AUDIO_COMPLETE_TITLE = "提取完成"
    EXTRACT_AUDIO_COMPLETE_CONTENT = "音频文案提取成功！"
    EXTRACT_AUDIO_ERROR_TITLE = "提取失败"
    EXTRACT_AUDIO_COPY_SUCCESS_TITLE = "复制成功"
    EXTRACT_AUDIO_COPY_SUCCESS_CONTENT = "文案已复制到剪贴板"

    # 提取音频页面持续时间常量
    EXTRACT_AUDIO_SUCCESS_DURATION = 2000
    EXTRACT_AUDIO_START_DURATION = 3000
    EXTRACT_AUDIO_COMPLETE_DURATION = 3000
    EXTRACT_AUDIO_ERROR_DURATION = 5000
    EXTRACT_AUDIO_COPY_DURATION = 2000

    # 提取音频页面UI常量
    EXTRACT_AUDIO_MODEL_COMBO_MIN_WIDTH = 150
    EXTRACT_AUDIO_MODEL_STATUS_COLOR = "#666666"
    EXTRACT_AUDIO_PROGRESS_INITIAL_VALUE = 0

    # 音频提取进度常量
    AUDIO_EXTRACT_PROGRESS_MODEL_LOADED = 20
    AUDIO_EXTRACT_PROGRESS_FILE_CHECKED = 50
    AUDIO_EXTRACT_PROGRESS_TRANSCRIPTION_DONE = 90
    AUDIO_EXTRACT_PROGRESS_COMPLETE = 100

    # 音频提取错误消息常量
    AUDIO_EXTRACT_ERROR_MODEL_LOAD_FAILED = "模型加载失败"
    AUDIO_EXTRACT_ERROR_MODEL_NOT_FOUND = "模型 {model_name} 加载失败"
    AUDIO_EXTRACT_ERROR_FILE_NOT_FOUND = "音频文件不存在：{file_path}"
    AUDIO_EXTRACT_ERROR_TRANSCRIPTION_FAILED = "音频转写失败: {error}"
    AUDIO_EXTRACT_ERROR_INSTALL_LIBRARY = (
        "请先安装 faster-whisper 库：pip install faster-whisper"
    )
    AUDIO_EXTRACT_ERROR_GENERAL = "音频转文字失败：{error}"
    AUDIO_EXTRACT_ERROR_MODEL_STATUS_CHECK = "检查模型状态失败"

    # 音频提取状态文本常量
    AUDIO_EXTRACT_STATUS_MODEL_CACHED = "已缓存"
    AUDIO_EXTRACT_STATUS_MODEL_DOWNLOAD_NEEDED = "下载模型需要占用一些时间"
    AUDIO_EXTRACT_LOG_START_TRANSCRIPTION = "开始转录文件:"
    AUDIO_EXTRACT_LOG_EXCEPTION = "Exception"

    # 音频提取样式颜色常量
    AUDIO_EXTRACT_COLOR_MODEL_CACHED = "#28a745"
    AUDIO_EXTRACT_COLOR_MODEL_DOWNLOAD = "#ffc107"

    # 音频提取默认值常量
    AUDIO_EXTRACT_DEFAULT_MODEL = "base"
    AUDIO_EXTRACT_CACHE_DIR = "~/.cache/huggingface/hub"
    AUDIO_EXTRACT_MODEL_PREFIX = "whisper-"
    AUDIO_EXTRACT_DEVICE_CUDA = "cuda"
    AUDIO_EXTRACT_DEVICE_CPU = "cpu"
    AUDIO_EXTRACT_COMPUTE_TYPE_CUDA = "float16"
    AUDIO_EXTRACT_COMPUTE_TYPE_CPU = "int8"
    AUDIO_EXTRACT_TEXT_JOIN_SEPARATOR = ""

    # DeepSeek API 常量
    DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
    DEEPSEEK_DEFAULT_MODEL = "deepseek-chat"
    DEEPSEEK_DEFAULT_TEMPERATURE = 0.3
    DEEPSEEK_DEFAULT_MAX_TOKENS = 2000
    DEEPSEEK_REQUEST_TIMEOUT = 200
    DEEPSEEK_SUCCESS_STATUS_CODE = 200
    DEEPSEEK_DEFAULT_DOMAIN = "通用"

    # DeepSeek API 请求头常量
    DEEPSEEK_HEADER_CONTENT_TYPE = "Content-Type"
    DEEPSEEK_HEADER_AUTHORIZATION = "Authorization"
    DEEPSEEK_CONTENT_TYPE_JSON = "application/json"
    DEEPSEEK_AUTH_PREFIX = "Bearer "

    # DeepSeek API 参数常量
    DEEPSEEK_PARAM_MODEL = "model"
    DEEPSEEK_PARAM_MESSAGES = "messages"
    DEEPSEEK_PARAM_TEMPERATURE = "temperature"
    DEEPSEEK_PARAM_MAX_TOKENS = "max_tokens"
    DEEPSEEK_MESSAGE_ROLE = "role"
    DEEPSEEK_MESSAGE_CONTENT = "content"
    DEEPSEEK_ROLE_USER = "user"

    # DeepSeek API 响应常量
    DEEPSEEK_RESPONSE_CHOICES = "choices"
    DEEPSEEK_RESPONSE_MESSAGE = "message"
    DEEPSEEK_RESPONSE_CONTENT = "content"
    DEEPSEEK_RESULT_DOMAIN = "domain"
    DEEPSEEK_RESULT_REFINED_TEXT = "refined_text"

    # DeepSeek 进度常量
    DEEPSEEK_PROGRESS_START = 10
    DEEPSEEK_PROGRESS_VALIDATING = 30
    DEEPSEEK_PROGRESS_PROCESSING = 70
    DEEPSEEK_PROGRESS_COMPLETE = 100

    # DeepSeek 错误消息常量
    DEEPSEEK_ERROR_EMPTY_TEXT = "输入文案不能为空"
    DEEPSEEK_ERROR_EMPTY_API_KEY = "API密钥不能为空"
    DEEPSEEK_ERROR_API_REQUEST = "API请求失败，状态码: {status_code}，错误信息: {error}"
    DEEPSEEK_ERROR_TIMEOUT = "API请求超时，请检查网络连接"
    DEEPSEEK_ERROR_CONNECTION = "网络连接失败，请检查网络设置"
    DEEPSEEK_ERROR_GENERAL = "文案修复失败：{error}"

    # DeepSeek 日志消息常量
    DEEPSEEK_LOG_START_REFINING = "开始修复文案:"
    DEEPSEEK_LOG_TEXT_TRUNCATE = "..."
    DEEPSEEK_LOG_REFINING_SUCCESS = "文案修复完成"
    DEEPSEEK_LOG_VALIDATION_ERROR = "验证错误:"
    DEEPSEEK_LOG_EXCEPTION = "Exception:"

    # DeepSeek 提示词模板
    DEEPSEEK_PROMPT_TEMPLATE = """请分析以下文案的专业领域，并在该领域的上下文中修复文案中的错别字、语法错误和专业术语。

文案内容：
{text}

请按照以下JSON格式返回结果：
{{
    "domain": "识别出的专业领域（如：科技、医疗、教育、金融等）",
    "refined_text": "修复后的文案内容"
}}

修复要求：
1. 保持原文的语义和风格
2. 修正错别字和语法错误
3. 统一专业术语的表达
4. 确保术语在该领域内的准确性
5. 保持文案的流畅性和可读性"""


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

    # 热更新相关
    HOT_RELOAD_ENV_VAR = "ENABLE_HOT_RELOAD"
    HOT_RELOAD_TRUE_VALUES = ("true", "1", "yes")
    HOT_RELOAD_WATCH_PATTERN = "src/**/*.py"
    HOT_RELOAD_MODULE_PATH = "src.main.run_app"
