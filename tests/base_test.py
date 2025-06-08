"""基础测试类"""

import sys
import unittest
import time
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ui.main_window import MainWindow
from tests.config import TestConfig
from tests.utils import UITestHelper, FileTestHelper


class BaseTestCase(unittest.TestCase):
    """基础测试用例类"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        # 确保测试目录存在
        TestConfig.ensure_test_dirs()
        
        # 创建QApplication实例（如果不存在）
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """每个测试方法执行前的初始化"""
        # 创建主窗口
        self.main_window = MainWindow()
        
        # 等待窗口显示
        self.main_window.show()
        self.assertTrue(
            UITestHelper.wait_for_window(self.main_window, TestConfig.DEFAULT_TIMEOUT),
            "主窗口未能在指定时间内显示"
        )
        
        # 等待UI完全加载
        time.sleep(TestConfig.WINDOW_WAIT_TIME)
        QApplication.processEvents()
    
    def tearDown(self):
        """每个测试方法执行后的清理"""
        if hasattr(self, 'main_window') and self.main_window:
            self.main_window.close()
            self.main_window = None
        
        # 处理所有待处理的事件
        QApplication.processEvents()
        time.sleep(0.5)
    
    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        # 清理测试文件
        FileTestHelper.cleanup_test_files()
        
        # 退出应用程序
        if hasattr(cls, 'app') and cls.app:
            cls.app.quit()
    
    def wait_and_process_events(self, seconds: float = 1.0):
        """等待并处理事件"""
        time.sleep(seconds)
        QApplication.processEvents()
    
    def navigate_to_page(self, route_key: str):
        """导航到指定页面"""
        # 通过导航管理器切换页面
        if hasattr(self.main_window, 'navigation_manager'):
            self.main_window.navigation_manager.set_current_item(route_key)
            self.wait_and_process_events()
    
    def get_current_page(self):
        """获取当前页面"""
        return self.main_window.get_current_page()
    
    def assert_page_loaded(self, expected_page_type):
        """断言页面已加载"""
        current_page = self.get_current_page()
        self.assertIsNotNone(current_page, "当前页面为空")
        self.assertIsInstance(current_page, expected_page_type, 
                            f"当前页面类型不匹配，期望: {expected_page_type}, 实际: {type(current_page)}")
    
    def find_widget_by_type(self, widget_type, parent=None):
        """根据类型查找控件"""
        if parent is None:
            parent = self.main_window
        return parent.findChild(widget_type)
    
    def find_widgets_by_type(self, widget_type, parent=None):
        """根据类型查找所有控件"""
        if parent is None:
            parent = self.main_window
        return parent.findChildren(widget_type)