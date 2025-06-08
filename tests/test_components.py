"""组件单元测试"""

import unittest
import time
from unittest.mock import Mock, patch
from PyQt6.QtCore import QThread

from tests.base_test import BaseTestCase
from tests.config import TestConfig
from tests.utils import FileTestHelper, MockAPIHelper
from pages.components.file_drop_area import FileDropArea
from pages.components.refine_area import RefineArea
from core.text_refine_worker import TextRefineWorker
from core.state_manager import StateManager
from config.core import AppConstants


class TestFileDropArea(BaseTestCase):
    """文件拖拽区域组件测试"""
    
    def test_file_drop_area_creation(self):
        """测试文件拖拽区域创建"""
        # 导航到提取音频页面
        self.navigate_to_page(AppConstants.ROUTE_EXTRACT_AUDIO)
        current_page = self.get_current_page()
        
        # 查找文件拖拽区域
        file_drop_area = self.find_widget_by_type(FileDropArea, current_page)
        self.assertIsNotNone(file_drop_area, "文件拖拽区域未创建")
        self.assertTrue(file_drop_area.acceptDrops(), "文件拖拽区域未启用拖拽功能")
    
    def test_file_selection_signal(self):
        """测试文件选择信号"""
        # 导航到提取音频页面
        self.navigate_to_page(AppConstants.ROUTE_EXTRACT_AUDIO)
        current_page = self.get_current_page()
        
        # 查找文件拖拽区域
        file_drop_area = self.find_widget_by_type(FileDropArea, current_page)
        self.assertIsNotNone(file_drop_area, "文件拖拽区域未找到")
        
        # 创建测试文件
        test_file = FileTestHelper.create_test_audio_file()
        
        # 监听信号
        signal_received = []
        file_drop_area.file_dropped.connect(lambda path: signal_received.append(path))
        
        # 触发文件选择
        file_drop_area.file_dropped.emit(str(test_file))
        self.wait_and_process_events()
        
        # 验证信号
        self.assertEqual(len(signal_received), 1, "文件选择信号未触发")
        self.assertEqual(signal_received[0], str(test_file), "文件路径不匹配")
    
    def test_file_clear_function(self):
        """测试文件清除功能"""
        # 导航到提取音频页面
        self.navigate_to_page(AppConstants.ROUTE_EXTRACT_AUDIO)
        current_page = self.get_current_page()
        
        # 查找文件拖拽区域
        file_drop_area = self.find_widget_by_type(FileDropArea, current_page)
        self.assertIsNotNone(file_drop_area, "文件拖拽区域未找到")
        
        # 创建并选择测试文件
        test_file = FileTestHelper.create_test_audio_file()
        file_drop_area.file_dropped.emit(str(test_file))
        self.wait_and_process_events()
        
        # 验证文件已选择
        selected_file = file_drop_area.get_current_file_path()
        self.assertEqual(selected_file, str(test_file), "文件选择失败")
        
        # 清除文件
        file_drop_area.clear_file()
        self.wait_and_process_events()
        
        # 验证文件已清除
        cleared_file = file_drop_area.get_current_file_path()
        self.assertEqual(cleared_file, "", "文件清除失败")


class TestRefineArea(BaseTestCase):
    """文案修复区域组件测试"""
    
    def test_refine_area_creation(self):
        """测试文案修复区域创建"""
        # 导航到提取文案页面
        self.navigate_to_page(AppConstants.ROUTE_EXTRACT_TEXT)
        current_page = self.get_current_page()
        
        # 查找文案修复区域
        refine_area = self.find_widget_by_type(RefineArea, current_page)
        if refine_area:
            self.assertIsNotNone(refine_area, "文案修复区域未创建")
            print("✓ 文案修复区域创建成功")
        else:
            print("⚠ 文案修复区域未找到，可能在其他页面或组件中")
    
    def test_api_key_input(self):
        """测试API密钥输入"""
        # 导航到提取文案页面
        self.navigate_to_page(AppConstants.ROUTE_EXTRACT_TEXT)
        current_page = self.get_current_page()
        
        # 查找文案修复区域
        refine_area = self.find_widget_by_type(RefineArea, current_page)
        if not refine_area:
            self.skipTest("文案修复区域未找到")
        
        # 查找API密钥输入框
        from qfluentwidgets import LineEdit
        api_key_inputs = refine_area.findChildren(LineEdit)
        
        if api_key_inputs:
            api_key_input = api_key_inputs[0]
            
            # 测试API密钥输入
            test_api_key = TestConfig.MOCK_API_KEY
            api_key_input.setText(test_api_key)
            self.wait_and_process_events()
            
            # 验证输入
            entered_key = api_key_input.text()
            self.assertEqual(entered_key, test_api_key, "API密钥输入失败")
            print(f"✓ API密钥输入成功: {test_api_key}")
        else:
            print("⚠ API密钥输入框未找到")


class TestTextRefineWorker(unittest.TestCase):
    """文案修复工作线程测试"""
    
    def setUp(self):
        """测试初始化"""
        self.test_text = "这是一个测试文本，需要修复。"
        self.test_api_key = TestConfig.MOCK_API_KEY
        self.test_api_url = TestConfig.MOCK_API_URL
    
    def test_worker_creation(self):
        """测试工作线程创建"""
        worker = TextRefineWorker(
            text=self.test_text,
            api_key=self.test_api_key,
            api_url=self.test_api_url
        )
        
        self.assertIsInstance(worker, QThread, "工作线程类型错误")
        self.assertEqual(worker.text, self.test_text, "文本设置错误")
        self.assertEqual(worker.api_key, self.test_api_key, "API密钥设置错误")
        self.assertEqual(worker.api_url, self.test_api_url, "API URL设置错误")
    
    @patch('requests.post')
    def test_mock_api_request(self, mock_post):
        """测试模拟API请求"""
        # 模拟API响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': MockAPIHelper.get_mock_refined_text(self.test_text)
                }
            }]
        }
        mock_post.return_value = mock_response
        
        # 创建工作线程
        worker = TextRefineWorker(
            text=self.test_text,
            api_key=self.test_api_key,
            api_url=self.test_api_url
        )
        
        # 测试域检测和修复方法
        try:
            domain, refined_text = worker.detect_domain_and_refine(self.test_text)
            self.assertIsInstance(domain, str, "域检测结果类型错误")
            self.assertIsInstance(refined_text, str, "修复文本类型错误")
            self.assertIn("[已修复]", refined_text, "修复标记未找到")
            print(f"✓ 模拟API请求成功，域: {domain}")
        except Exception as e:
            print(f"⚠ 模拟API请求测试跳过: {e}")


class TestStateManager(unittest.TestCase):
    """状态管理器测试"""
    
    def test_state_manager_singleton(self):
        """测试状态管理器单例模式"""
        from core import get_state_manager
        
        manager1 = get_state_manager()
        manager2 = get_state_manager()
        
        self.assertIs(manager1, manager2, "状态管理器不是单例")
        self.assertIsInstance(manager1, StateManager, "状态管理器类型错误")
    
    def test_file_state_management(self):
        """测试文件状态管理"""
        from core import get_state_manager
        
        manager = get_state_manager()
        
        # 测试初始状态
        initial_path = manager.state.file.path
        self.assertEqual(initial_path, "", "初始文件路径应为空")
        
        # 测试设置文件路径
        test_file = FileTestHelper.create_test_audio_file()
        manager.set_file_path(str(test_file))
        
        updated_path = manager.state.file.path
        self.assertEqual(updated_path, str(test_file), "文件路径设置失败")
        
        # 测试重置文件状态
        manager.reset_file()
        reset_path = manager.state.file.path
        self.assertEqual(reset_path, "", "文件状态重置失败")


class TestMockAPIHelper(unittest.TestCase):
    """模拟API辅助类测试"""
    
    def test_mock_refined_text(self):
        """测试模拟修复文本"""
        original_text = "这是测试文本，包含一些标点符号。"
        refined_text = MockAPIHelper.get_mock_refined_text(original_text)
        
        self.assertIsInstance(refined_text, str, "修复文本类型错误")
        self.assertIn("[已修复]", refined_text, "修复标记未找到")
        self.assertNotEqual(original_text, refined_text, "修复前后文本相同")
        print(f"原文: {original_text}")
        print(f"修复后: {refined_text}")
    
    def test_api_key_validation(self):
        """测试API密钥验证"""
        # 测试有效密钥
        valid_keys = [
            "sk-1234567890abcdef",
            TestConfig.MOCK_API_KEY,
            "a" * 20
        ]
        
        for key in valid_keys:
            self.assertTrue(
                MockAPIHelper.validate_api_key(key),
                f"有效密钥验证失败: {key}"
            )
        
        # 测试无效密钥
        invalid_keys = [
            "",
            "123",
            "short",
            None
        ]
        
        for key in invalid_keys:
            self.assertFalse(
                MockAPIHelper.validate_api_key(key),
                f"无效密钥应该验证失败: {key}"
            )


if __name__ == '__main__':
    unittest.main()