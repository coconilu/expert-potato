"""测试配置文件"""

import os
from pathlib import Path


class TestConfig:
    """测试配置类"""
    
    # 测试项目根目录
    PROJECT_ROOT = Path(__file__).parent.parent
    
    # 测试数据目录
    TEST_DATA_DIR = PROJECT_ROOT / "tests" / "data"
    
    # 测试输出目录
    TEST_OUTPUT_DIR = PROJECT_ROOT / "tests" / "output"
    
    # 测试超时时间（秒）
    DEFAULT_TIMEOUT = 30
    LONG_TIMEOUT = 120
    
    # 测试文件路径
    TEST_AUDIO_FILE = TEST_DATA_DIR / "test_audio.wav"
    TEST_VIDEO_FILE = TEST_DATA_DIR / "test_video.mp4"
    
    # 模拟API配置
    MOCK_API_KEY = "test_api_key_12345"
    MOCK_API_URL = "http://localhost:8080/mock/api"
    
    # 应用窗口配置
    WINDOW_WAIT_TIME = 2  # 窗口显示等待时间
    OPERATION_WAIT_TIME = 1  # 操作间隔等待时间
    
    # 测试模型配置
    TEST_MODEL_NAME = "large-v3-turbo"
    
    # 预期文案内容（用于验证）
    EXPECTED_TEXT_KEYWORDS = ["欢迎", "AI", "Embedding"]
    
    @classmethod
    def ensure_test_dirs(cls):
        """确保测试目录存在"""
        cls.TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_test_file_path(cls, filename: str) -> Path:
        """获取测试文件路径"""
        return cls.TEST_DATA_DIR / filename
    
    @classmethod
    def get_output_file_path(cls, filename: str) -> Path:
        """获取输出文件路径"""
        return cls.TEST_OUTPUT_DIR / filename