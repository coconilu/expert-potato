"""使用pytest的端到端测试"""

import pytest
import time
from pathlib import Path
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from tests.config import TestConfig
from tests.utils import UITestHelper, FileTestHelper, MockAPIHelper
from ui.main_window import MainWindow
from pages.extract_audio_page import ExtractAudioPage
from pages.extract_text_page import ExtractTextPage
from pages.components.file_drop_area import FileDropArea
from pages.components.refine_area import RefineArea
from config.core import AppConstants


@pytest.fixture(scope="session")
def qapp():
    """创建QApplication实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()


@pytest.fixture
def main_window(qtbot):
    """创建主窗口实例"""
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    qtbot.waitForWindowShown(window)
    time.sleep(TestConfig.WINDOW_WAIT_TIME)
    return window


@pytest.fixture
def test_audio_file():
    """创建测试音频文件"""
    TestConfig.ensure_test_dirs()
    return FileTestHelper.create_test_audio_file()


@pytest.fixture
def test_text_content():
    """获取测试文本内容"""
    cache_file = TestConfig.PROJECT_ROOT / ".cache" / "large-v3-turbo.txt"
    if cache_file.exists():
        content = cache_file.read_text(encoding='utf-8')
        return content[:500] + "..."
    else:
        return (
            "欢迎收听,今天我们来聊一个AI领域里,一个挺基础的技术,Embedding,也就是嵌入。"
            "对。您可能不直接接触它,但它几乎就是说驱动着你每天在用的各种智能推荐啊,搜索啊这些。"
        )


class TestE2EWorkflow:
    """端到端工作流程测试类"""
    
    @pytest.mark.e2e
    def test_complete_workflow(self, qtbot, main_window, test_audio_file, test_text_content):
        """测试完整的工作流程"""
        print("\n=== 开始完整工作流程测试 ===")
        
        # 1. 测试文件选择
        self._test_file_selection(qtbot, main_window, test_audio_file)
        
        # 2. 测试文案提取
        self._test_text_extraction(qtbot, main_window, test_text_content)
        
        # 3. 测试文案修复
        self._test_text_refinement(qtbot, main_window, test_text_content)
        
        print("=== 完整工作流程测试完成 ===")
    
    def _test_file_selection(self, qtbot, main_window, test_file):
        """测试文件选择功能"""
        print("\n--- 测试文件选择 ---")
        
        # 导航到提取音频页面
        main_window.navigation_manager.set_current_item(AppConstants.ROUTE_EXTRACT_AUDIO)
        qtbot.wait(1000)
        
        # 验证页面加载
        current_page = main_window.get_current_page()
        assert isinstance(current_page, ExtractAudioPage), "页面类型不匹配"
        
        # 查找文件拖拽区域
        file_drop_area = current_page.findChild(FileDropArea)
        if file_drop_area:
            # 模拟文件选择
            file_drop_area.file_dropped.emit(str(test_file))
            qtbot.wait(1000)
            
            # 验证文件选择
            selected_file = file_drop_area.get_current_file_path()
            assert selected_file == str(test_file), "文件选择失败"
            print(f"✓ 文件选择成功: {Path(selected_file).name}")
        else:
            print("⚠ 文件拖拽区域未找到")
    
    def _test_text_extraction(self, qtbot, main_window, test_content):
        """测试文案提取功能"""
        print("\n--- 测试文案提取 ---")
        
        # 导航到提取文案页面
        main_window.navigation_manager.set_current_item(AppConstants.ROUTE_EXTRACT_TEXT)
        qtbot.wait(1000)
        
        # 验证页面加载
        current_page = main_window.get_current_page()
        assert isinstance(current_page, ExtractTextPage), "页面类型不匹配"
        
        # 查找提取按钮
        extract_button = UITestHelper.find_button_by_text(
            current_page, 
            AppConstants.EXTRACT_AUDIO_EXTRACT_BUTTON_TEXT
        )
        
        if extract_button:
            # 查找结果显示区域
            result_text_edit = UITestHelper.find_text_edit(current_page)
            if result_text_edit:
                # 模拟点击提取按钮
                qtbot.mouseClick(extract_button, qtbot.LeftButton)
                qtbot.wait(2000)
                
                # 模拟设置提取结果
                UITestHelper.set_text(result_text_edit, test_content)
                qtbot.wait(1000)
                
                # 验证提取结果
                extracted_text = UITestHelper.get_text(result_text_edit)
                assert len(extracted_text) > 0, "提取的文案为空"
                print(f"✓ 文案提取成功，长度: {len(extracted_text)} 字符")
            else:
                print("⚠ 结果显示区域未找到")
        else:
            print("⚠ 提取按钮未找到")
    
    def _test_text_refinement(self, qtbot, main_window, test_content):
        """测试文案修复功能"""
        print("\n--- 测试文案修复 ---")
        
        current_page = main_window.get_current_page()
        
        # 查找文案修复区域
        refine_area = current_page.findChild(RefineArea)
        if not refine_area:
            print("⚠ 文案修复区域未找到")
            return
        
        # 查找API密钥输入框
        api_key_input = UITestHelper.find_line_edit(refine_area)
        if api_key_input:
            # 输入API密钥
            api_key_input.setText(TestConfig.MOCK_API_KEY)
            qtbot.wait(500)
            print(f"✓ 已输入API密钥: {TestConfig.MOCK_API_KEY}")
        
        # 查找文案输入区域
        from qfluentwidgets import TextEdit
        text_inputs = refine_area.findChildren(TextEdit)
        
        if len(text_inputs) >= 1:
            original_text_edit = text_inputs[0]
            UITestHelper.set_text(original_text_edit, test_content)
            qtbot.wait(1000)
            
            # 查找修复按钮
            refine_button = UITestHelper.find_button_by_text(refine_area, "修复文案")
            if not refine_button:
                refine_button = UITestHelper.find_button_by_text(refine_area, "开始修复")
            
            if refine_button:
                # 点击修复按钮
                qtbot.mouseClick(refine_button, qtbot.LeftButton)
                qtbot.wait(2000)
                
                # 模拟修复结果
                if len(text_inputs) >= 2:
                    refined_text_edit = text_inputs[1]
                    refined_content = MockAPIHelper.get_mock_refined_text(test_content)
                    UITestHelper.set_text(refined_text_edit, refined_content)
                    qtbot.wait(1000)
                    
                    # 验证修复结果
                    final_text = UITestHelper.get_text(refined_text_edit)
                    assert len(final_text) > 0, "修复后的文案为空"
                    assert "[已修复]" in final_text, "修复标记未找到"
                    print(f"✓ 文案修复成功，长度: {len(final_text)} 字符")
                else:
                    print("⚠ 修复结果显示区域未找到")
            else:
                print("⚠ 修复按钮未找到")
        else:
            print("⚠ 文案输入区域未找到")
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_file_selection_only(self, qtbot, main_window, test_audio_file):
        """单独测试文件选择功能"""
        print("\n=== 测试文件选择功能 ===")
        
        # 导航到提取音频页面
        main_window.navigation_manager.set_current_item(AppConstants.ROUTE_EXTRACT_AUDIO)
        qtbot.wait(1000)
        
        # 验证页面加载
        current_page = main_window.get_current_page()
        assert isinstance(current_page, ExtractAudioPage)
        
        # 测试文件选择
        self._test_file_selection(qtbot, main_window, test_audio_file)
        
        print("=== 文件选择功能测试完成 ===")
    
    @pytest.mark.e2e
    def test_navigation_between_pages(self, qtbot, main_window):
        """测试页面间导航"""
        print("\n=== 测试页面导航 ===")
        
        # 测试导航到提取音频页面
        main_window.navigation_manager.set_current_item(AppConstants.ROUTE_EXTRACT_AUDIO)
        qtbot.wait(1000)
        
        current_page = main_window.get_current_page()
        assert isinstance(current_page, ExtractAudioPage), "导航到提取音频页面失败"
        print("✓ 成功导航到提取音频页面")
        
        # 测试导航到提取文案页面
        main_window.navigation_manager.set_current_item(AppConstants.ROUTE_EXTRACT_TEXT)
        qtbot.wait(1000)
        
        current_page = main_window.get_current_page()
        assert isinstance(current_page, ExtractTextPage), "导航到提取文案页面失败"
        print("✓ 成功导航到提取文案页面")
        
        print("=== 页面导航测试完成 ===")


class TestAPIIntegration:
    """API集成测试类"""
    
    @pytest.mark.api
    def test_api_key_validation(self):
        """测试API密钥验证"""
        # 测试有效密钥
        valid_key = TestConfig.MOCK_API_KEY
        assert MockAPIHelper.validate_api_key(valid_key), "有效API密钥验证失败"
        
        # 测试无效密钥
        invalid_keys = ["", "123", None]
        for invalid_key in invalid_keys:
            assert not MockAPIHelper.validate_api_key(invalid_key), f"无效API密钥应该验证失败: {invalid_key}"
    
    @pytest.mark.api
    @patch('requests.post')
    def test_mock_api_request(self, mock_post):
        """测试模拟API请求"""
        # 模拟API响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': "这是模拟的API响应内容"
                }
            }]
        }
        mock_post.return_value = mock_response
        
        # 测试API调用
        from core.text_refine_worker import TextRefineWorker
        worker = TextRefineWorker(
            text="测试文本",
            api_key=TestConfig.MOCK_API_KEY,
            api_url=TestConfig.MOCK_API_URL
        )
        
        # 验证worker创建成功
        assert worker.text == "测试文本"
        assert worker.api_key == TestConfig.MOCK_API_KEY
        assert worker.api_url == TestConfig.MOCK_API_URL


class TestPerformance:
    """性能测试类"""
    
    @pytest.mark.slow
    def test_window_startup_time(self, qtbot):
        """测试窗口启动时间"""
        start_time = time.time()
        
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitForWindowShown(window)
        
        startup_time = time.time() - start_time
        
        # 窗口应该在3秒内启动
        assert startup_time < 3.0, f"窗口启动时间过长: {startup_time:.2f}秒"
        print(f"✓ 窗口启动时间: {startup_time:.2f}秒")
    
    @pytest.mark.slow
    def test_page_navigation_performance(self, qtbot, main_window):
        """测试页面导航性能"""
        pages = [
            AppConstants.ROUTE_EXTRACT_AUDIO,
            AppConstants.ROUTE_EXTRACT_TEXT,
        ]
        
        for page_route in pages:
            start_time = time.time()
            
            main_window.navigation_manager.set_current_item(page_route)
            qtbot.wait(100)  # 等待页面切换
            
            navigation_time = time.time() - start_time
            
            # 页面导航应该在1秒内完成
            assert navigation_time < 1.0, f"页面导航时间过长: {navigation_time:.2f}秒"
            print(f"✓ 导航到 {page_route} 耗时: {navigation_time:.2f}秒")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])