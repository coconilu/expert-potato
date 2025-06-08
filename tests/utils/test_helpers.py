"""测试辅助工具类"""

import time
import shutil
from pathlib import Path
from typing import Optional, List
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QTextEdit, QLabel
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtTest import QTest
from qfluentwidgets import PushButton, TextEdit, LineEdit

from tests.config import TestConfig


class UITestHelper:
    """UI测试辅助类"""
    
    @staticmethod
    def wait_for_window(window, timeout: int = TestConfig.DEFAULT_TIMEOUT) -> bool:
        """等待窗口显示"""
        start_time = time.time()
        while not window.isVisible() and (time.time() - start_time) < timeout:
            QApplication.processEvents()
            time.sleep(0.1)
        return window.isVisible()
    
    @staticmethod
    def wait_for_widget(parent: QWidget, widget_type: type, timeout: int = TestConfig.DEFAULT_TIMEOUT) -> Optional[QWidget]:
        """等待特定类型的控件出现"""
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            widget = parent.findChild(widget_type)
            if widget and widget.isVisible():
                return widget
            QApplication.processEvents()
            time.sleep(0.1)
        return None
    
    @staticmethod
    def find_button_by_text(parent: QWidget, text: str) -> Optional[QPushButton]:
        """根据文本查找按钮"""
        buttons = parent.findChildren(QPushButton)
        for button in buttons:
            if button.text() == text:
                return button
        
        # 也查找 FluentUI 的按钮
        fluent_buttons = parent.findChildren(PushButton)
        for button in fluent_buttons:
            if button.text() == text:
                return button
        
        return None
    
    @staticmethod
    def find_text_edit(parent: QWidget) -> Optional[QTextEdit]:
        """查找文本编辑控件"""
        # 查找标准 QTextEdit
        text_edit = parent.findChild(QTextEdit)
        if text_edit:
            return text_edit
        
        # 查找 FluentUI 的 TextEdit
        fluent_text_edit = parent.findChild(TextEdit)
        return fluent_text_edit
    
    @staticmethod
    def find_line_edit(parent: QWidget) -> Optional[LineEdit]:
        """查找单行文本输入控件"""
        return parent.findChild(LineEdit)
    
    @staticmethod
    def click_button(button: QPushButton, wait_time: float = TestConfig.OPERATION_WAIT_TIME):
        """点击按钮并等待"""
        if button and button.isEnabled():
            QTest.mouseClick(button, Qt.MouseButton.LeftButton)
            time.sleep(wait_time)
            QApplication.processEvents()
    
    @staticmethod
    def set_text(text_widget, text: str, wait_time: float = TestConfig.OPERATION_WAIT_TIME):
        """设置文本内容"""
        if hasattr(text_widget, 'setPlainText'):
            text_widget.setPlainText(text)
        elif hasattr(text_widget, 'setText'):
            text_widget.setText(text)
        time.sleep(wait_time)
        QApplication.processEvents()
    
    @staticmethod
    def get_text(text_widget) -> str:
        """获取文本内容"""
        if hasattr(text_widget, 'toPlainText'):
            return text_widget.toPlainText()
        elif hasattr(text_widget, 'text'):
            return text_widget.text()
        return ""
    
    @staticmethod
    def wait_for_text_change(text_widget, initial_text: str, timeout: int = TestConfig.LONG_TIMEOUT) -> bool:
        """等待文本内容变化"""
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            current_text = UITestHelper.get_text(text_widget)
            if current_text != initial_text and current_text.strip():
                return True
            QApplication.processEvents()
            time.sleep(0.5)
        return False
    
    @staticmethod
    def simulate_file_drop(widget: QWidget, file_path: str):
        """模拟文件拖拽"""
        # 这里可以通过直接调用组件的方法来模拟文件选择
        # 因为真正的拖拽事件在自动化测试中比较复杂
        if hasattr(widget, 'file_dropped'):
            widget.file_dropped.emit(file_path)
        elif hasattr(widget, 'set_file_path'):
            widget.set_file_path(file_path)


class FileTestHelper:
    """文件测试辅助类"""
    
    @staticmethod
    def create_test_audio_file() -> Path:
        """创建测试音频文件"""
        TestConfig.ensure_test_dirs()
        test_file = TestConfig.get_test_file_path("test_audio.wav")
        
        # 如果测试文件不存在，复制现有的音频文件或创建一个空文件
        if not test_file.exists():
            # 尝试从 .cache 目录复制现有文件
            cache_file = TestConfig.PROJECT_ROOT / ".cache" / "large-v3-turbo.txt"
            if cache_file.exists():
                # 创建一个简单的文本文件作为测试文件
                test_file.write_text("测试音频文件内容", encoding='utf-8')
            else:
                # 创建空的测试文件
                test_file.touch()
        
        return test_file
    
    @staticmethod
    def create_test_text_file(content: str = None) -> Path:
        """创建测试文本文件"""
        TestConfig.ensure_test_dirs()
        test_file = TestConfig.get_test_file_path("test_text.txt")
        
        if content is None:
            # 使用项目中现有的文本内容
            cache_file = TestConfig.PROJECT_ROOT / ".cache" / "large-v3-turbo.txt"
            if cache_file.exists():
                content = cache_file.read_text(encoding='utf-8')
            else:
                content = "这是测试文本内容，用于验证文案修复功能。包含一些需要修复的内容。"
        
        test_file.write_text(content, encoding='utf-8')
        return test_file
    
    @staticmethod
    def cleanup_test_files():
        """清理测试文件"""
        if TestConfig.TEST_OUTPUT_DIR.exists():
            shutil.rmtree(TestConfig.TEST_OUTPUT_DIR)
        TestConfig.ensure_test_dirs()


class MockAPIHelper:
    """模拟API辅助类"""
    
    @staticmethod
    def get_mock_refined_text(original_text: str) -> str:
        """获取模拟的修复后文本"""
        # 简单的文本修复模拟
        refined_text = original_text.replace("，", ", ")
        refined_text = refined_text.replace("。", ". ")
        refined_text = f"[已修复] {refined_text}"
        return refined_text
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """验证API密钥格式"""
        return api_key and len(api_key) >= 10