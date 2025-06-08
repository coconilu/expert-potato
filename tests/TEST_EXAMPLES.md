# Expert Potato 测试示例和模板

## 📋 目录

1. [基础测试模板](#基础测试模板)
2. [E2E测试示例](#e2e测试示例)
3. [组件测试示例](#组件测试示例)
4. [Mock测试示例](#mock测试示例)
5. [性能测试示例](#性能测试示例)
6. [错误处理测试](#错误处理测试)
7. [参数化测试](#参数化测试)
8. [异步测试](#异步测试)

## 🏗️ 基础测试模板

### 1. 基础E2E测试模板

```python
# tests/test_my_feature_e2e.py
import pytest
from PyQt6.QtCore import Qt
from tests.base_test import BaseTestCase
from tests.utils import UITestHelper, FileTestHelper

class TestMyFeatureE2E(BaseTestCase):
    """我的功能端到端测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        super().setup_method()
        self.ui_helper = UITestHelper()
        self.file_helper = FileTestHelper()
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        self.file_helper.cleanup_test_files()
        super().teardown_method()
    
    @pytest.mark.e2e
    @pytest.mark.gui
    def test_my_feature_complete_workflow(self, qtbot, main_window):
        """测试我的功能完整工作流程
        
        测试步骤：
        1. 准备测试数据
        2. 执行用户操作
        3. 验证结果
        """
        # 1. Arrange - 准备
        test_file = self.file_helper.create_test_audio_file()
        expected_result = "期望的结果"
        
        # 2. Act - 执行
        # 导航到目标页面
        self.navigate_to_page(main_window, "目标页面")
        
        # 模拟用户操作
        button = self.find_widget(main_window, "操作按钮")
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
        
        # 等待操作完成
        self.wait_and_process_events(2)
        
        # 3. Assert - 验证
        result_widget = self.find_widget(main_window, "结果显示")
        assert result_widget.text() == expected_result
        
        # 验证状态更新
        assert self.wait_for_condition(
            lambda: self.check_expected_state(),
            timeout=10,
            error_msg="状态未按预期更新"
        )
    
    def check_expected_state(self):
        """检查期望的状态"""
        # 实现状态检查逻辑
        return True
```

### 2. 基础组件测试模板

```python
# tests/test_my_component.py
import pytest
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QWidget
from src.pages.components.my_component import MyComponent

class TestMyComponent:
    """我的组件单元测试"""
    
    @pytest.fixture
    def component(self, qtbot):
        """创建组件实例"""
        widget = MyComponent()
        qtbot.addWidget(widget)
        return widget
    
    @pytest.mark.unit
    def test_component_initialization(self, component):
        """测试组件初始化"""
        assert component is not None
        assert isinstance(component, QWidget)
        assert component.objectName() == "MyComponent"
    
    @pytest.mark.unit
    def test_component_default_state(self, component):
        """测试组件默认状态"""
        assert component.isEnabled()
        assert not component.isVisible()  # 根据实际情况调整
    
    @pytest.mark.unit
    def test_component_method(self, component):
        """测试组件方法"""
        # 准备测试数据
        test_input = "测试输入"
        expected_output = "期望输出"
        
        # 执行方法
        result = component.my_method(test_input)
        
        # 验证结果
        assert result == expected_output
```

## 🎯 E2E测试示例

### 1. 文件选择流程测试

```python
@pytest.mark.e2e
@pytest.mark.gui
def test_file_selection_workflow(self, qtbot, main_window):
    """测试文件选择完整流程"""
    # 创建测试文件
    test_file = self.file_helper.create_test_audio_file(
        filename="test_audio.wav",
        duration=10  # 10秒音频
    )
    
    # 导航到文件选择页面
    self.navigate_to_page(main_window, "ExtractAudioPage")
    
    # 查找文件拖拽区域
    drop_area = self.find_widget(main_window, "file_drop_area")
    assert drop_area is not None, "文件拖拽区域未找到"
    
    # 模拟文件拖拽
    self.ui_helper.simulate_file_drop(drop_area, test_file)
    
    # 等待文件处理
    self.wait_and_process_events(1)
    
    # 验证文件选择状态
    state_manager = StateManager()
    assert state_manager.current_file_path == test_file
    
    # 验证UI更新
    file_info = self.find_widget(main_window, "file_info_label")
    assert "test_audio.wav" in file_info.text()
```

### 2. 模型选择测试

```python
@pytest.mark.e2e
@pytest.mark.gui
def test_model_selection(self, qtbot, main_window):
    """测试模型选择功能"""
    # 导航到文本提取页面
    self.navigate_to_page(main_window, "ExtractTextPage")
    
    # 查找模型选择组件
    model_selector = self.find_widget(main_window, "model_selector")
    assert model_selector is not None
    
    # 获取可用模型列表
    available_models = ["large-v3-turbo", "large-v3", "medium"]
    
    for model in available_models:
        # 选择模型
        self.ui_helper.select_combobox_item(model_selector, model)
        
        # 验证选择
        assert model_selector.currentText() == model
        
        # 验证状态更新
        state_manager = StateManager()
        assert state_manager.selected_model == model
```

### 3. API密钥验证测试

```python
@pytest.mark.e2e
@pytest.mark.api
def test_api_key_validation_workflow(self, qtbot, main_window):
    """测试API密钥验证流程"""
    # 导航到文案修复页面
    self.navigate_to_page(main_window, "ExtractTextPage")
    
    # 查找API密钥输入框
    api_key_input = self.find_widget(main_window, "api_key_input")
    assert api_key_input is not None
    
    # 测试无效密钥
    invalid_keys = ["", "short", "invalid_format_key"]
    
    for invalid_key in invalid_keys:
        # 输入无效密钥
        api_key_input.clear()
        qtbot.keyClicks(api_key_input, invalid_key)
        
        # 触发验证
        validate_button = self.find_widget(main_window, "validate_api_key_button")
        qtbot.mouseClick(validate_button, Qt.MouseButton.LeftButton)
        
        # 验证错误提示
        error_label = self.find_widget(main_window, "api_error_label")
        assert error_label.isVisible()
        assert "无效" in error_label.text() or "错误" in error_label.text()
    
    # 测试有效密钥
    valid_key = "sk-1234567890abcdef1234567890abcdef"
    api_key_input.clear()
    qtbot.keyClicks(api_key_input, valid_key)
    
    # 模拟API验证成功
    with patch('src.core.text_refine_worker.requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"valid": True}
        
        qtbot.mouseClick(validate_button, Qt.MouseButton.LeftButton)
        
        # 验证成功状态
        success_label = self.find_widget(main_window, "api_success_label")
        assert success_label.isVisible()
        assert "有效" in success_label.text()
```

## 🧩 组件测试示例

### 1. FileDropArea组件测试

```python
class TestFileDropArea:
    """文件拖拽区域组件测试"""
    
    @pytest.fixture
    def drop_area(self, qtbot):
        """创建FileDropArea实例"""
        from src.pages.components.file_drop_area import FileDropArea
        area = FileDropArea()
        qtbot.addWidget(area)
        return area
    
    @pytest.mark.unit
    def test_drag_drop_enabled(self, drop_area):
        """测试拖拽功能启用"""
        assert drop_area.acceptDrops()
    
    @pytest.mark.unit
    def test_file_selected_signal(self, drop_area, qtbot):
        """测试文件选择信号"""
        # 使用信号监听器
        with qtbot.waitSignal(drop_area.file_selected, timeout=1000) as blocker:
            # 模拟文件选择
            drop_area.select_file_programmatically("test.wav")
        
        # 验证信号参数
        assert blocker.args[0] == "test.wav"
    
    @pytest.mark.unit
    def test_clear_selection(self, drop_area):
        """测试清除选择"""
        # 先选择文件
        drop_area.select_file_programmatically("test.wav")
        assert drop_area.current_file == "test.wav"
        
        # 清除选择
        drop_area.clear_selection()
        assert drop_area.current_file is None
    
    @pytest.mark.unit
    def test_supported_formats(self, drop_area):
        """测试支持的文件格式"""
        supported_formats = drop_area.get_supported_formats()
        expected_formats = [".wav", ".mp3", ".mp4", ".avi"]
        
        for fmt in expected_formats:
            assert fmt in supported_formats
```

### 2. RefineArea组件测试

```python
class TestRefineArea:
    """文案修复区域组件测试"""
    
    @pytest.fixture
    def refine_area(self, qtbot):
        """创建RefineArea实例"""
        from src.pages.components.refine_area import RefineArea
        area = RefineArea()
        qtbot.addWidget(area)
        return area
    
    @pytest.mark.unit
    def test_api_key_input_validation(self, refine_area):
        """测试API密钥输入验证"""
        # 测试空密钥
        assert not refine_area.validate_api_key("")
        
        # 测试短密钥
        assert not refine_area.validate_api_key("short")
        
        # 测试有效密钥
        valid_key = "sk-1234567890abcdef1234567890abcdef"
        assert refine_area.validate_api_key(valid_key)
    
    @pytest.mark.unit
    @patch('src.core.text_refine_worker.TextRefineWorker')
    def test_start_refine_process(self, mock_worker_class, refine_area, qtbot):
        """测试启动修复过程"""
        # 设置mock
        mock_worker = Mock()
        mock_worker_class.return_value = mock_worker
        
        # 设置测试数据
        test_text = "需要修复的文案"
        test_api_key = "test_api_key"
        
        # 启动修复
        refine_area.start_refine(test_text, test_api_key)
        
        # 验证worker创建和启动
        mock_worker_class.assert_called_once_with(test_text, test_api_key)
        mock_worker.start.assert_called_once()
    
    @pytest.mark.unit
    def test_refine_progress_update(self, refine_area, qtbot):
        """测试修复进度更新"""
        # 监听进度更新信号
        with qtbot.waitSignal(refine_area.progress_updated, timeout=1000) as blocker:
            # 模拟进度更新
            refine_area.update_progress(50)
        
        # 验证进度值
        assert blocker.args[0] == 50
        
        # 验证UI更新
        progress_bar = refine_area.findChild(QProgressBar)
        assert progress_bar.value() == 50
```

## 🎭 Mock测试示例

### 1. API调用Mock

```python
@pytest.mark.api
@pytest.mark.mock
class TestAPIIntegration:
    """API集成测试（使用Mock）"""
    
    @patch('requests.post')
    def test_successful_api_call(self, mock_post):
        """测试成功的API调用"""
        # 设置mock响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "修复后的文案内容"
                }
            }]
        }
        mock_post.return_value = mock_response
        
        # 执行API调用
        from src.core.text_refine_worker import TextRefineWorker
        worker = TextRefineWorker("原始文案", "test_api_key")
        result = worker.call_api()
        
        # 验证调用参数
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "test_api_key" in str(call_args)
        
        # 验证结果
        assert result == "修复后的文案内容"
    
    @patch('requests.post')
    def test_api_error_handling(self, mock_post):
        """测试API错误处理"""
        # 模拟网络错误
        mock_post.side_effect = requests.exceptions.RequestException("网络错误")
        
        # 执行API调用
        from src.core.text_refine_worker import TextRefineWorker
        worker = TextRefineWorker("原始文案", "test_api_key")
        
        # 验证异常处理
        with pytest.raises(requests.exceptions.RequestException):
            worker.call_api()
    
    @patch('requests.post')
    def test_api_timeout_handling(self, mock_post):
        """测试API超时处理"""
        # 模拟超时
        mock_post.side_effect = requests.exceptions.Timeout("请求超时")
        
        from src.core.text_refine_worker import TextRefineWorker
        worker = TextRefineWorker("原始文案", "test_api_key")
        
        with pytest.raises(requests.exceptions.Timeout):
            worker.call_api()
```

### 2. 文件系统Mock

```python
@pytest.mark.unit
@pytest.mark.mock
class TestFileOperations:
    """文件操作测试（使用Mock）"""
    
    @patch('builtins.open', new_callable=mock_open, read_data="测试文件内容")
    @patch('os.path.exists')
    def test_file_reading(self, mock_exists, mock_file):
        """测试文件读取"""
        # 设置文件存在
        mock_exists.return_value = True
        
        # 执行文件读取
        from src.utils.file_utils import read_file
        content = read_file("test.txt")
        
        # 验证调用
        mock_exists.assert_called_once_with("test.txt")
        mock_file.assert_called_once_with("test.txt", 'r', encoding='utf-8')
        
        # 验证结果
        assert content == "测试文件内容"
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    def test_file_writing(self, mock_makedirs, mock_file):
        """测试文件写入"""
        # 执行文件写入
        from src.utils.file_utils import write_file
        write_file("output/test.txt", "写入内容")
        
        # 验证目录创建
        mock_makedirs.assert_called_once_with("output", exist_ok=True)
        
        # 验证文件写入
        mock_file.assert_called_once_with("output/test.txt", 'w', encoding='utf-8')
        mock_file().write.assert_called_once_with("写入内容")
```

## ⚡ 性能测试示例

### 1. 响应时间测试

```python
@pytest.mark.slow
@pytest.mark.performance
class TestPerformance:
    """性能测试"""
    
    def test_window_startup_performance(self, qtbot):
        """测试窗口启动性能"""
        import time
        
        # 记录启动时间
        start_time = time.perf_counter()
        
        # 创建主窗口
        from src.ui.main_window import MainWindow
        main_window = MainWindow()
        main_window.show()
        qtbot.waitForWindowShown(main_window)
        
        end_time = time.perf_counter()
        startup_time = end_time - start_time
        
        # 性能断言
        assert startup_time < 3.0, f"窗口启动时间过长: {startup_time:.2f}秒"
        
        # 记录性能数据
        print(f"窗口启动时间: {startup_time:.2f}秒")
    
    def test_file_processing_performance(self, qtbot, main_window):
        """测试文件处理性能"""
        import time
        from tests.utils import FileTestHelper
        
        # 创建大文件
        file_helper = FileTestHelper()
        large_file = file_helper.create_test_audio_file(
            filename="large_test.wav",
            duration=300  # 5分钟音频
        )
        
        # 记录处理时间
        start_time = time.perf_counter()
        
        # 模拟文件处理
        self.simulate_file_processing(main_window, large_file)
        
        end_time = time.perf_counter()
        processing_time = end_time - start_time
        
        # 性能断言
        assert processing_time < 60.0, f"文件处理时间过长: {processing_time:.2f}秒"
        
        # 清理
        file_helper.cleanup_test_files()
    
    def simulate_file_processing(self, main_window, file_path):
        """模拟文件处理过程"""
        # 实现文件处理模拟逻辑
        pass
```

### 2. 内存使用测试

```python
@pytest.mark.performance
def test_memory_usage(qtbot, main_window):
    """测试内存使用情况"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    
    # 记录初始内存
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # 执行内存密集操作
    for i in range(100):
        # 模拟创建大量对象
        large_data = [f"数据{j}" for j in range(1000)]
        # 模拟UI操作
        qtbot.wait(10)
    
    # 强制垃圾回收
    import gc
    gc.collect()
    
    # 记录最终内存
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory
    
    # 内存使用断言
    assert memory_increase < 100, f"内存增长过多: {memory_increase:.2f}MB"
    
    print(f"内存使用: 初始 {initial_memory:.2f}MB, 最终 {final_memory:.2f}MB, 增长 {memory_increase:.2f}MB")
```

## 🚨 错误处理测试

### 1. 异常测试

```python
@pytest.mark.unit
class TestErrorHandling:
    """错误处理测试"""
    
    def test_file_not_found_exception(self):
        """测试文件不存在异常"""
        from src.utils.file_utils import load_audio_file
        
        with pytest.raises(FileNotFoundError, match="文件不存在"):
            load_audio_file("nonexistent.wav")
    
    def test_invalid_api_key_exception(self):
        """测试无效API密钥异常"""
        from src.core.text_refine_worker import TextRefineWorker
        
        with pytest.raises(ValueError, match="API密钥无效"):
            worker = TextRefineWorker("文案", "")
            worker.validate_api_key()
    
    def test_network_error_handling(self):
        """测试网络错误处理"""
        with patch('requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError("连接失败")
            
            from src.core.text_refine_worker import TextRefineWorker
            worker = TextRefineWorker("文案", "valid_key")
            
            with pytest.raises(requests.exceptions.ConnectionError):
                worker.call_api()
```

### 2. 警告测试

```python
@pytest.mark.unit
def test_deprecation_warning():
    """测试弃用警告"""
    with pytest.warns(DeprecationWarning, match="此功能已弃用"):
        from src.utils.deprecated_utils import old_function
        old_function()

@pytest.mark.unit
def test_user_warning():
    """测试用户警告"""
    with pytest.warns(UserWarning, match="建议使用新版本"):
        from src.utils.version_utils import check_version
        check_version("1.0.0")
```

## 📊 参数化测试

### 1. 基础参数化

```python
@pytest.mark.parametrize("input_value,expected", [
    ("sk-1234567890abcdef1234567890abcdef", True),
    ("invalid_key", False),
    ("", False),
    (None, False),
    ("sk-short", False),
])
def test_api_key_validation(input_value, expected):
    """参数化测试API密钥验证"""
    from src.utils.validation import validate_api_key
    assert validate_api_key(input_value) == expected
```

### 2. 复杂参数化

```python
@pytest.mark.parametrize("file_format,file_size,expected_result", [
    ("wav", 1024, True),
    ("mp3", 2048, True),
    ("mp4", 4096, True),
    ("txt", 512, False),
    ("wav", 0, False),
    ("mp3", 1024*1024*100, False),  # 100MB文件
])
def test_file_validation(file_format, file_size, expected_result):
    """参数化测试文件验证"""
    from src.utils.file_utils import validate_file
    
    # 创建模拟文件信息
    file_info = {
        "format": file_format,
        "size": file_size
    }
    
    result = validate_file(file_info)
    assert result == expected_result
```

### 3. 使用pytest.param

```python
@pytest.mark.parametrize("test_case", [
    pytest.param(
        {"input": "正常文案", "expected": "修复后文案"},
        id="normal_text"
    ),
    pytest.param(
        {"input": "包含错误的文案", "expected": "修复后的文案"},
        id="error_text"
    ),
    pytest.param(
        {"input": "", "expected": ""},
        id="empty_text",
        marks=pytest.mark.skip(reason="空文案暂不支持")
    ),
])
def test_text_refine_cases(test_case):
    """使用pytest.param的参数化测试"""
    from src.core.text_processor import refine_text
    
    result = refine_text(test_case["input"])
    assert result == test_case["expected"]
```

## ⏱️ 异步测试

### 1. QThread测试

```python
@pytest.mark.unit
class TestAsyncOperations:
    """异步操作测试"""
    
    def test_text_refine_worker_async(self, qtbot):
        """测试文本修复工作线程"""
        from src.core.text_refine_worker import TextRefineWorker
        
        # 创建工作线程
        worker = TextRefineWorker("测试文案", "test_api_key")
        
        # 监听完成信号
        with qtbot.waitSignal(worker.finished, timeout=5000) as blocker:
            worker.start()
        
        # 验证结果
        assert blocker.signal_triggered
        assert worker.result is not None
    
    def test_worker_error_signal(self, qtbot):
        """测试工作线程错误信号"""
        from src.core.text_refine_worker import TextRefineWorker
        
        # 创建会失败的工作线程
        worker = TextRefineWorker("测试文案", "invalid_key")
        
        # 监听错误信号
        with qtbot.waitSignal(worker.error_occurred, timeout=5000) as blocker:
            worker.start()
        
        # 验证错误信息
        assert blocker.signal_triggered
        error_message = blocker.args[0]
        assert "API密钥" in error_message
```

### 2. 定时器测试

```python
@pytest.mark.unit
def test_timer_functionality(qtbot):
    """测试定时器功能"""
    from PyQt6.QtCore import QTimer
    
    # 创建定时器
    timer = QTimer()
    timer.setSingleShot(True)
    timer.setInterval(1000)  # 1秒
    
    # 监听超时信号
    with qtbot.waitSignal(timer.timeout, timeout=2000) as blocker:
        timer.start()
    
    # 验证定时器触发
    assert blocker.signal_triggered
```

## 📝 测试文档模板

### 1. 测试用例文档模板

```python
def test_feature_name(self):
    """测试功能名称
    
    测试目标：
        描述这个测试要验证什么功能
    
    前置条件：
        - 条件1
        - 条件2
    
    测试步骤：
        1. 步骤1描述
        2. 步骤2描述
        3. 步骤3描述
    
    预期结果：
        - 结果1
        - 结果2
    
    测试数据：
        - 输入数据：xxx
        - 期望输出：yyy
    
    注意事项：
        - 特殊说明1
        - 特殊说明2
    """
    # 测试实现
    pass
```

### 2. 测试类文档模板

```python
class TestFeatureName:
    """功能名称测试套件
    
    测试范围：
        描述这个测试类覆盖的功能范围
    
    测试策略：
        - 单元测试：测试单个方法
        - 集成测试：测试组件交互
        - E2E测试：测试完整流程
    
    依赖项：
        - 外部依赖1
        - 外部依赖2
    
    Mock策略：
        - Mock的组件和原因
    
    性能要求：
        - 响应时间要求
        - 内存使用要求
    """
    
    def setup_class(cls):
        """类级别的设置"""
        pass
    
    def teardown_class(cls):
        """类级别的清理"""
        pass
    
    def setup_method(self):
        """方法级别的设置"""
        pass
    
    def teardown_method(self):
        """方法级别的清理"""
        pass
```

---

## 🎯 使用建议

1. **选择合适的模板**：根据测试类型选择对应的模板
2. **遵循命名约定**：使用描述性的测试名称
3. **添加详细文档**：为复杂测试添加详细的文档字符串
4. **合理使用标记**：使用pytest标记对测试进行分类
5. **适当的Mock**：对外部依赖进行合理的Mock
6. **性能考虑**：为耗时操作添加性能测试
7. **错误处理**：确保测试覆盖异常情况
8. **数据清理**：测试后及时清理临时数据

记住：好的测试代码和好的产品代码一样重要！🚀