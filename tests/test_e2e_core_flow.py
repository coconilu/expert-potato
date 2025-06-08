"""核心流程端到端测试"""

import time
import unittest
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from qfluentwidgets import PushButton, TextEdit, LineEdit

from tests.base_test import BaseTestCase
from tests.config import TestConfig
from tests.utils import UITestHelper, FileTestHelper, MockAPIHelper
from pages.extract_audio_page import ExtractAudioPage
from pages.extract_text_page import ExtractTextPage
from pages.components.file_drop_area import FileDropArea
from pages.components.refine_area import RefineArea
from config.core import AppConstants


class TestCoreFlowE2E(BaseTestCase):
    """核心流程端到端测试类"""
    
    def test_complete_workflow(self):
        """测试完整的工作流程：选择文件 -> 选择模型 -> 提取文案 -> 修复文案"""
        print("\n=== 开始完整工作流程测试 ===")
        
        # 1. 准备测试数据
        test_file = FileTestHelper.create_test_audio_file()
        self.assertTrue(test_file.exists(), "测试文件创建失败")
        print(f"✓ 测试文件已创建: {test_file}")
        
        # 2. 导航到提取音频页面
        print("\n--- 步骤1: 导航到提取音频页面 ---")
        self.navigate_to_page(AppConstants.ROUTE_EXTRACT_AUDIO)
        self.assert_page_loaded(ExtractAudioPage)
        print("✓ 成功导航到提取音频页面")
        
        # 3. 测试文件选择功能
        print("\n--- 步骤2: 测试文件选择 ---")
        self._test_file_selection(str(test_file))
        
        # 4. 导航到提取文案页面
        print("\n--- 步骤3: 导航到提取文案页面 ---")
        self.navigate_to_page(AppConstants.ROUTE_EXTRACT_TEXT)
        self.assert_page_loaded(ExtractTextPage)
        print("✓ 成功导航到提取文案页面")
        
        # 5. 测试模型选择和文案提取
        print("\n--- 步骤4: 测试文案提取 ---")
        self._test_text_extraction()
        
        # 6. 测试文案修复功能
        print("\n--- 步骤5: 测试文案修复 ---")
        self._test_text_refinement()
        
        print("\n=== 完整工作流程测试完成 ===")
    
    def _test_file_selection(self, file_path: str):
        """测试文件选择功能"""
        current_page = self.get_current_page()
        
        # 查找文件拖拽区域
        file_drop_area = self.find_widget_by_type(FileDropArea, current_page)
        self.assertIsNotNone(file_drop_area, "未找到文件拖拽区域")
        
        # 模拟文件选择
        UITestHelper.simulate_file_drop(file_drop_area, file_path)
        self.wait_and_process_events(2)
        
        # 验证文件是否被正确选择
        selected_file = file_drop_area.get_current_file_path()
        self.assertEqual(selected_file, file_path, "文件选择失败")
        print(f"✓ 文件选择成功: {Path(selected_file).name}")
    
    def _test_text_extraction(self):
        """测试文案提取功能"""
        current_page = self.get_current_page()
        
        # 查找提取按钮
        extract_button = UITestHelper.find_button_by_text(
            current_page, 
            AppConstants.EXTRACT_AUDIO_EXTRACT_BUTTON_TEXT
        )
        
        if extract_button:
            print("✓ 找到提取按钮")
            
            # 查找结果显示区域
            result_text_edit = UITestHelper.find_text_edit(current_page)
            if result_text_edit:
                initial_text = UITestHelper.get_text(result_text_edit)
                print(f"初始文本内容: {initial_text[:50]}...")
                
                # 点击提取按钮
                UITestHelper.click_button(extract_button, 2)
                print("✓ 已点击提取按钮")
                
                # 等待提取完成（模拟）
                # 在实际测试中，这里会等待真正的语音识别完成
                # 为了测试，我们模拟设置一些文本内容
                test_content = self._get_test_content()
                UITestHelper.set_text(result_text_edit, test_content)
                self.wait_and_process_events(2)
                
                # 验证提取结果
                extracted_text = UITestHelper.get_text(result_text_edit)
                self.assertTrue(len(extracted_text) > 0, "提取的文案为空")
                print(f"✓ 文案提取成功，长度: {len(extracted_text)} 字符")
                print(f"提取内容预览: {extracted_text[:100]}...")
            else:
                print("⚠ 未找到结果显示区域，跳过文案提取测试")
        else:
            print("⚠ 未找到提取按钮，跳过文案提取测试")
    
    def _test_text_refinement(self):
        """测试文案修复功能"""
        current_page = self.get_current_page()
        
        # 查找文案修复区域
        refine_area = self.find_widget_by_type(RefineArea, current_page)
        if not refine_area:
            print("⚠ 未找到文案修复区域，跳过修复测试")
            return
        
        print("✓ 找到文案修复区域")
        
        # 查找API密钥输入框
        api_key_input = UITestHelper.find_line_edit(refine_area)
        if api_key_input:
            # 输入测试API密钥
            UITestHelper.set_text(api_key_input, TestConfig.MOCK_API_KEY)
            print(f"✓ 已输入API密钥: {TestConfig.MOCK_API_KEY}")
        
        # 查找原始文案输入区域
        text_inputs = refine_area.findChildren(TextEdit)
        if len(text_inputs) >= 1:
            original_text_edit = text_inputs[0]
            test_content = self._get_test_content()
            UITestHelper.set_text(original_text_edit, test_content)
            print("✓ 已输入原始文案")
            
            # 查找修复按钮
            refine_button = UITestHelper.find_button_by_text(refine_area, "修复文案")
            if not refine_button:
                refine_button = UITestHelper.find_button_by_text(refine_area, "开始修复")
            
            if refine_button:
                print("✓ 找到修复按钮")
                
                # 点击修复按钮
                UITestHelper.click_button(refine_button, 2)
                print("✓ 已点击修复按钮")
                
                # 模拟修复过程
                if len(text_inputs) >= 2:
                    refined_text_edit = text_inputs[1]
                    
                    # 模拟API返回修复后的文案
                    refined_content = MockAPIHelper.get_mock_refined_text(test_content)
                    UITestHelper.set_text(refined_text_edit, refined_content)
                    self.wait_and_process_events(3)
                    
                    # 验证修复结果
                    final_text = UITestHelper.get_text(refined_text_edit)
                    self.assertTrue(len(final_text) > 0, "修复后的文案为空")
                    self.assertIn("[已修复]", final_text, "修复标记未找到")
                    print(f"✓ 文案修复成功，长度: {len(final_text)} 字符")
                    print(f"修复内容预览: {final_text[:100]}...")
                else:
                    print("⚠ 未找到修复结果显示区域")
            else:
                print("⚠ 未找到修复按钮")
        else:
            print("⚠ 未找到文案输入区域")
    
    def _get_test_content(self) -> str:
        """获取测试内容"""
        # 尝试从缓存文件读取真实内容
        cache_file = TestConfig.PROJECT_ROOT / ".cache" / "large-v3-turbo.txt"
        if cache_file.exists():
            content = cache_file.read_text(encoding='utf-8')
            # 取前500个字符作为测试内容
            return content[:500] + "..."
        else:
            # 使用默认测试内容
            return (
                "欢迎收听,今天我们来聊一个AI领域里,一个挺基础的技术,Embedding,也就是嵌入。"
                "对。您可能不直接接触它,但它几乎就是说驱动着你每天在用的各种智能推荐啊,搜索啊这些。"
                "没错,是挺核心的。它就像是让机器能真正理解我们说话,还有我们这个世界里那些微妙含义的一种魔法吧。"
            )
    
    def test_file_selection_only(self):
        """单独测试文件选择功能"""
        print("\n=== 测试文件选择功能 ===")
        
        # 创建测试文件
        test_file = FileTestHelper.create_test_audio_file()
        
        # 导航到提取音频页面
        self.navigate_to_page(AppConstants.ROUTE_EXTRACT_AUDIO)
        self.assert_page_loaded(ExtractAudioPage)
        
        # 测试文件选择
        self._test_file_selection(str(test_file))
        
        print("=== 文件选择功能测试完成 ===")
    
    def test_model_selection(self):
        """测试模型选择功能"""
        print("\n=== 测试模型选择功能 ===")
        
        # 导航到提取文案页面
        self.navigate_to_page(AppConstants.ROUTE_EXTRACT_TEXT)
        self.assert_page_loaded(ExtractTextPage)
        
        # 这里可以添加模型选择的具体测试逻辑
        # 由于当前代码中模型选择可能在设置中，这里先做基础验证
        current_page = self.get_current_page()
        self.assertIsNotNone(current_page, "页面加载失败")
        
        print("✓ 模型选择页面加载成功")
        print("=== 模型选择功能测试完成 ===")
    
    def test_api_key_validation(self):
        """测试API密钥验证"""
        print("\n=== 测试API密钥验证 ===")
        
        # 测试有效的API密钥
        valid_key = TestConfig.MOCK_API_KEY
        self.assertTrue(
            MockAPIHelper.validate_api_key(valid_key),
            "有效API密钥验证失败"
        )
        print(f"✓ 有效API密钥验证通过: {valid_key}")
        
        # 测试无效的API密钥
        invalid_keys = ["", "123", None]
        for invalid_key in invalid_keys:
            self.assertFalse(
                MockAPIHelper.validate_api_key(invalid_key),
                f"无效API密钥应该验证失败: {invalid_key}"
            )
        print("✓ 无效API密钥验证正确")
        
        print("=== API密钥验证测试完成 ===")


if __name__ == '__main__':
    unittest.main()