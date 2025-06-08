# Expert Potato 测试完整指南

## 📖 目录

1. [测试架构概览](#测试架构概览)
2. [环境配置](#环境配置)
3. [测试分类](#测试分类)
4. [运行策略](#运行策略)
5. [Mock和模拟](#mock和模拟)
6. [CI/CD集成](#cicd集成)
7. [性能测试](#性能测试)
8. [故障排除](#故障排除)
9. [最佳实践](#最佳实践)

## 🏗️ 测试架构概览

### 测试金字塔

```
    🔺 E2E Tests (端到端测试)
   ────────────────────────
  🔺🔺 Integration Tests (集成测试)
 ──────────────────────────────────
🔺🔺🔺 Unit Tests (单元测试)
```

### 项目测试结构

```
tests/
├── 📁 utils/                    # 测试工具
│   ├── test_helpers.py         # 测试辅助类
│   └── __init__.py
├── 📁 data/                     # 测试数据（自动生成）
├── 📁 output/                   # 测试输出（自动清理）
├── 📄 config.py                # 测试配置
├── 📄 base_test.py             # 基础测试类
├── 📄 run_tests.py             # 自定义运行器
├── 📄 test_components.py       # 组件单元测试
├── 📄 test_e2e_core_flow.py   # E2E测试（unittest）
├── 📄 test_e2e_pytest.py      # E2E测试（pytest）
├── 📄 README.md                # 详细文档
├── 📄 E2E_QUICK_START.md       # 快速入门
└── 📄 TESTING_GUIDE.md         # 本文档
```

## ⚙️ 环境配置

### 1. Python环境要求

```toml
# pyproject.toml 中的配置
[project]
requires-python = ">=3.11"

[project.optional-dependencies]
test = [
    "pytest>=7.0.0",
    "pytest-qt>=4.2.0",
    "pytest-mock>=3.10.0",
    "pytest-cov>=4.0.0",
    "pytest-xvfb>=3.0.0",  # Linux GUI测试支持
]
```

### 2. 测试环境变量

```bash
# 可选的环境变量配置
set EXPERT_POTATO_TEST_MODE=1
set EXPERT_POTATO_LOG_LEVEL=DEBUG
set EXPERT_POTATO_TEST_TIMEOUT=60
```

### 3. pytest配置详解

```ini
# pytest.ini
[pytest]
# 测试发现
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

# 输出配置
addopts = 
    -v                    # 详细输出
    --tb=short           # 简短的错误回溯
    --strict-markers     # 严格标记模式
    --disable-warnings   # 禁用警告
    --color=yes          # 彩色输出
    --durations=10       # 显示最慢的10个测试

# 测试标记
markers =
    e2e: 端到端测试
    unit: 单元测试
    integration: 集成测试
    slow: 慢速测试（>5秒）
    gui: GUI相关测试
    api: API相关测试
    mock: 使用Mock的测试
    windows: Windows特定测试
    linux: Linux特定测试
```

## 🏷️ 测试分类

### 1. 单元测试 (Unit Tests)

**目标**：测试单个组件或函数

```python
@pytest.mark.unit
class TestFileDropArea:
    def test_component_creation(self):
        """测试组件创建"""
        pass
    
    def test_drag_drop_enabled(self):
        """测试拖拽功能启用"""
        pass
```

**运行命令**：
```bash
uv run pytest tests/ -m "unit" -v
```

### 2. 集成测试 (Integration Tests)

**目标**：测试组件间的交互

```python
@pytest.mark.integration
class TestStateManagerIntegration:
    def test_file_state_update_integration(self):
        """测试文件状态更新集成"""
        pass
```

**运行命令**：
```bash
uv run pytest tests/ -m "integration" -v
```

### 3. 端到端测试 (E2E Tests)

**目标**：测试完整的用户工作流程

```python
@pytest.mark.e2e
@pytest.mark.gui
class TestE2EWorkflow:
    def test_complete_workflow(self, qtbot, main_window):
        """测试完整工作流程"""
        pass
```

**运行命令**：
```bash
uv run pytest tests/ -m "e2e" -v
```

## 🎯 运行策略

### 1. 开发阶段运行策略

```bash
# 快速反馈循环（只运行单元测试）
uv run pytest tests/ -m "unit and not slow" -x

# 功能验证（运行相关的集成测试）
uv run pytest tests/ -m "integration" -k "file_selection"

# 完整验证（运行所有测试）
uv run pytest tests/ -v
```

### 2. 提交前运行策略

```bash
# 1. 运行快速测试
uv run pytest tests/ -m "not slow" --maxfail=3

# 2. 如果通过，运行完整测试套件
uv run pytest tests/ -v --cov=src --cov-report=term-missing
```

### 3. CI/CD运行策略

```bash
# 并行运行（如果支持）
uv run pytest tests/ -n auto --dist=worksteal

# 生成多种报告
uv run pytest tests/ --junitxml=junit.xml --cov=src --cov-report=xml --cov-report=html
```

## 🎭 Mock和模拟

### 1. API Mock策略

```python
# tests/utils/test_helpers.py
class MockAPIHelper:
    @staticmethod
    def mock_deepseek_api_success():
        """模拟成功的API响应"""
        return {
            "choices": [{
                "message": {
                    "content": "修复后的文案内容"
                }
            }]
        }
    
    @staticmethod
    def mock_deepseek_api_error():
        """模拟API错误响应"""
        raise requests.exceptions.RequestException("API调用失败")
```

### 2. 文件系统Mock

```python
# 使用pytest-mock
def test_file_operations(mocker):
    # Mock文件读取
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="测试内容"))
    
    # Mock文件存在检查
    mocker.patch('os.path.exists', return_value=True)
    
    # 执行测试
    result = your_function()
    assert result == "期望结果"
```

### 3. UI组件Mock

```python
def test_ui_interaction(qtbot, mocker):
    # Mock QFileDialog
    mock_dialog = mocker.patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName')
    mock_dialog.return_value = ('/path/to/test/file.wav', 'Audio Files (*.wav)')
    
    # 执行UI操作
    button.click()
    
    # 验证Mock被调用
    mock_dialog.assert_called_once()
```

## 🔄 CI/CD集成

### 1. GitHub Actions完整配置

```yaml
# .github/workflows/tests.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    strategy:
      matrix:
        os: [windows-latest, ubuntu-latest]
        python-version: ['3.11', '3.12']
    
    runs-on: ${{ matrix.os }}
    
    steps:
    - name: Checkout
      uses: actions/checkout@v4
      
    - name: Install uv
      uses: astral-sh/setup-uv@v1
      
    - name: Set up Python ${{ matrix.python-version }}
      run: uv python install ${{ matrix.python-version }}
      
    - name: Install dependencies
      run: uv sync
      
    - name: Run unit tests
      run: |
        uv run pytest tests/ -m "unit" --junitxml=unit-results.xml
        
    - name: Run integration tests
      run: |
        uv run pytest tests/ -m "integration" --junitxml=integration-results.xml
        
    - name: Run E2E tests (Ubuntu with xvfb)
      if: matrix.os == 'ubuntu-latest'
      run: |
        xvfb-run -a uv run pytest tests/ -m "e2e" --junitxml=e2e-results.xml
        
    - name: Run E2E tests (Windows)
      if: matrix.os == 'windows-latest'
      run: |
        uv run pytest tests/ -m "e2e" --junitxml=e2e-results.xml
        
    - name: Generate coverage report
      run: |
        uv run pytest tests/ --cov=src --cov-report=xml --cov-report=html
        
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        
    - name: Upload test results
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: test-results-${{ matrix.os }}-${{ matrix.python-version }}
        path: '*-results.xml'
        
    - name: Upload coverage report
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: coverage-report-${{ matrix.os }}-${{ matrix.python-version }}
        path: htmlcov/
```

### 2. 预提交钩子

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest-unit
        name: Run unit tests
        entry: uv run pytest tests/ -m "unit and not slow" --maxfail=3
        language: system
        pass_filenames: false
        always_run: true
```

## 📊 性能测试

### 1. 性能基准测试

```python
@pytest.mark.slow
@pytest.mark.performance
class TestPerformance:
    def test_window_startup_time(self, qtbot):
        """测试窗口启动时间"""
        import time
        start_time = time.time()
        
        # 创建主窗口
        main_window = MainWindow()
        main_window.show()
        qtbot.waitForWindowShown(main_window)
        
        startup_time = time.time() - start_time
        
        # 断言启动时间小于3秒
        assert startup_time < 3.0, f"窗口启动时间过长: {startup_time:.2f}秒"
    
    def test_large_file_processing(self, qtbot, main_window):
        """测试大文件处理性能"""
        # 创建大文件（模拟）
        large_file_size = 100 * 1024 * 1024  # 100MB
        
        start_time = time.time()
        # 执行文件处理
        process_time = time.time() - start_time
        
        # 断言处理时间合理
        assert process_time < 30.0, f"大文件处理时间过长: {process_time:.2f}秒"
```

### 2. 内存使用监控

```python
import psutil
import os

def test_memory_usage(qtbot, main_window):
    """测试内存使用情况"""
    process = psutil.Process(os.getpid())
    
    # 记录初始内存
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # 执行操作
    for i in range(100):
        # 模拟重复操作
        pass
    
    # 记录最终内存
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory
    
    # 断言内存增长合理
    assert memory_increase < 50, f"内存增长过多: {memory_increase:.2f}MB"
```

## 🔧 故障排除

### 1. 常见错误和解决方案

#### 错误1：QApplication实例冲突
```
RuntimeError: QApplication instance already exists
```

**解决方案**：
```python
# 在测试开始前清理
def setup_method(self):
    app = QApplication.instance()
    if app is not None:
        app.quit()
        app = None
```

#### 错误2：组件未找到
```
AssertionError: Widget not found: button_name
```

**解决方案**：
```python
# 增加等待时间和调试信息
def find_widget_with_debug(self, parent, name):
    print(f"查找组件: {name}")
    print(f"父组件子组件列表: {[child.objectName() for child in parent.findChildren(QWidget)]}")
    
    widget = self.find_widget(parent, name)
    if widget is None:
        # 截图调试
        qtbot.screenshot(parent, f"debug_{name}.png")
    return widget
```

#### 错误3：测试超时
```
TimeoutError: Condition not met within timeout
```

**解决方案**：
```python
# 调整超时时间和检查条件
def wait_for_condition_with_debug(self, condition, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            if condition():
                return True
        except Exception as e:
            print(f"条件检查异常: {e}")
        time.sleep(0.1)
    
    print(f"超时后的状态信息...")
    return False
```

### 2. 调试工具和技巧

#### 使用pytest的调试功能
```bash
# 进入调试模式
uv run pytest tests/test_e2e_pytest.py::test_method --pdb

# 在失败时进入调试
uv run pytest tests/test_e2e_pytest.py --pdb-trace

# 显示局部变量
uv run pytest tests/test_e2e_pytest.py -vvv --tb=long
```

#### 使用日志调试
```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_with_logging(qtbot, main_window):
    logger.debug("开始测试")
    logger.info(f"主窗口状态: {main_window.isVisible()}")
    # 测试逻辑
    logger.debug("测试完成")
```

## 🎯 最佳实践

### 1. 测试设计原则

#### FIRST原则
- **Fast**: 测试应该快速运行
- **Independent**: 测试应该相互独立
- **Repeatable**: 测试应该可重复
- **Self-Validating**: 测试应该有明确的通过/失败结果
- **Timely**: 测试应该及时编写

#### AAA模式
```python
def test_example():
    # Arrange - 准备
    test_data = "测试数据"
    expected_result = "期望结果"
    
    # Act - 执行
    actual_result = function_under_test(test_data)
    
    # Assert - 断言
    assert actual_result == expected_result
```

### 2. 测试命名约定

```python
# 好的测试名称
def test_file_selection_updates_state_when_valid_audio_file_selected():
    pass

def test_api_key_validation_rejects_invalid_format():
    pass

def test_text_refine_worker_handles_network_timeout_gracefully():
    pass

# 避免的测试名称
def test_1():
    pass

def test_file():
    pass

def test_api():
    pass
```

### 3. 断言最佳实践

```python
# 使用描述性的断言消息
assert result == expected, f"期望 {expected}，但得到 {result}"

# 使用专门的断言方法
assert widget.isVisible(), "组件应该是可见的"
assert not widget.isEnabled(), "组件应该是禁用的"

# 对于浮点数比较
import math
assert math.isclose(actual, expected, rel_tol=1e-9)

# 对于集合比较
assert set(actual) == set(expected)
```

### 4. 测试数据管理

```python
# 使用fixture管理测试数据
@pytest.fixture
def sample_audio_file():
    """创建示例音频文件"""
    file_path = "tests/data/sample.wav"
    # 创建文件逻辑
    yield file_path
    # 清理逻辑
    if os.path.exists(file_path):
        os.remove(file_path)

# 使用参数化测试
@pytest.mark.parametrize("input_value,expected", [
    ("valid_key_123", True),
    ("invalid", False),
    ("", False),
    (None, False),
])
def test_api_key_validation(input_value, expected):
    assert validate_api_key(input_value) == expected
```

### 5. 错误处理测试

```python
# 测试异常情况
def test_file_not_found_raises_exception():
    with pytest.raises(FileNotFoundError, match="文件不存在"):
        load_file("nonexistent.wav")

# 测试警告
def test_deprecated_function_warns():
    with pytest.warns(DeprecationWarning):
        deprecated_function()
```

---

## 📚 参考资源

### 官方文档
- [pytest官方文档](https://docs.pytest.org/)
- [pytest-qt文档](https://pytest-qt.readthedocs.io/)
- [PyQt6测试指南](https://doc.qt.io/qtforpython/)

### 推荐阅读
- 《测试驱动开发》- Kent Beck
- 《单元测试的艺术》- Roy Osherove
- 《Google软件测试之道》- James Whittaker

### 在线资源
- [Python测试最佳实践](https://docs.python-guide.org/writing/tests/)
- [pytest插件列表](https://plugincompat.herokuapp.com/)
- [GUI测试策略](https://martinfowler.com/articles/practical-test-pyramid.html)

---

**记住**：好的测试不仅能发现bug，更能提高代码质量和开发效率！🚀