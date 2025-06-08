# Expert Potato E2E 测试文档

## 📚 文档导航

- **[快速入门指南](./E2E_QUICK_START.md)** - 5分钟快速上手E2E测试
- **[完整测试指南](./TESTING_GUIDE.md)** - 详细的测试架构和最佳实践
- **[测试示例和模板](./TEST_EXAMPLES.md)** - 各种测试用例的示例代码
- **[本文档](./README.md)** - 完整的测试文档和参考

## 概述

本测试套件为 Expert Potato 应用提供了完整的端到端（E2E）测试，涵盖了核心功能流程：

1. **文件选择** - 测试音频/视频文件的选择和拖拽功能
2. **模型选择** - 测试 large-v3-turbo 等模型的选择
3. **文案提取** - 测试从音频中提取文字的功能
4. **文案修复** - 测试使用 API 密钥修复文案的功能

## 测试架构

### 测试文件结构

```
tests/
├── __init__.py                 # 测试模块初始化
├── README.md                   # 测试文档（本文件）
├── config.py                   # 测试配置
├── base_test.py               # 基础测试类
├── run_tests.py               # 测试运行器
├── test_components.py         # 组件单元测试
├── test_e2e_core_flow.py     # 核心流程E2E测试（unittest版本）
├── test_e2e_pytest.py       # 核心流程E2E测试（pytest版本）
├── utils/
│   ├── __init__.py
│   └── test_helpers.py       # 测试辅助工具
├── data/                     # 测试数据目录（自动创建）
└── output/                   # 测试输出目录（自动创建）
```

### 核心组件

#### 1. 测试配置 (`config.py`)
- 定义测试相关的常量和路径
- 配置超时时间和等待时间
- 管理测试文件和输出目录

#### 2. 测试辅助工具 (`utils/test_helpers.py`)
- `UITestHelper`: UI自动化测试辅助类
- `FileTestHelper`: 文件操作测试辅助类
- `MockAPIHelper`: 模拟API测试辅助类

#### 3. 基础测试类 (`base_test.py`)
- 提供测试的基础设施
- 管理QApplication生命周期
- 提供通用的测试方法

## 运行测试

### 环境准备

1. 安装测试依赖：
```bash
uv add --group test pytest pytest-qt pytest-mock pytest-cov pytest-xvfb
```

2. 确保应用依赖已安装：
```bash
uv sync
```

### 运行方式

#### 方式1：使用自定义测试运行器

```bash
# 运行所有测试
uv run python tests/run_tests.py

# 只运行E2E测试
uv run python tests/run_tests.py e2e

# 只运行组件测试
uv run python tests/run_tests.py component
```

#### 方式2：使用unittest

```bash
# 运行所有测试
uv run python -m unittest discover tests

# 运行特定测试文件
uv run python -m unittest tests.test_e2e_core_flow
uv run python -m unittest tests.test_components

# 运行特定测试方法
uv run python -m unittest tests.test_e2e_core_flow.TestCoreFlowE2E.test_complete_workflow
```

#### 方式3：使用pytest

```bash
# 运行所有pytest测试
uv run pytest tests/test_e2e_pytest.py -v

# 运行特定标记的测试
uv run pytest tests/test_e2e_pytest.py -m "e2e" -v
uv run pytest tests/test_e2e_pytest.py -m "api" -v
uv run pytest tests/test_e2e_pytest.py -m "slow" -v

# 运行特定测试方法
uv run pytest tests/test_e2e_pytest.py::TestE2EWorkflow::test_complete_workflow -v

# 生成覆盖率报告
uv run pytest tests/test_e2e_pytest.py --cov=src --cov-report=html
```

## 测试用例说明

### 核心流程测试

#### `test_complete_workflow`
完整的端到端工作流程测试，包括：
1. 文件选择和验证
2. 页面导航
3. 文案提取模拟
4. API密钥输入
5. 文案修复模拟

#### `test_file_selection_only`
专门测试文件选择功能：
- 文件拖拽模拟
- 文件路径验证
- 状态更新检查

#### `test_model_selection`
测试模型选择功能：
- 模型列表显示
- 模型切换
- 默认模型验证

#### `test_api_key_validation`
测试API密钥验证：
- 有效密钥格式检查
- 无效密钥拒绝
- 密钥长度验证

### 组件单元测试

#### `TestFileDropArea`
- 组件创建和初始化
- 拖拽功能启用检查
- 文件选择信号测试
- 文件清除功能测试

#### `TestRefineArea`
- 修复区域组件创建
- API密钥输入测试
- 修复按钮功能测试

#### `TestTextRefineWorker`
- 工作线程创建
- 模拟API请求
- 错误处理测试

#### `TestStateManager`
- 单例模式验证
- 文件状态管理
- 状态重置功能

## 测试数据管理

### 测试文件
- 测试音频文件：`tests/data/test_audio.wav`
- 测试文本文件：`tests/data/test_text.txt`
- 自动从 `.cache/large-v3-turbo.txt` 复制真实内容

### 输出文件
- 测试输出目录：`tests/output/`
- 自动清理机制

## 模拟和Mock

### API模拟
- 使用 `MockAPIHelper` 模拟API响应
- 模拟文案修复结果
- 模拟网络请求（使用 `unittest.mock.patch`）

### UI操作模拟
- 文件拖拽模拟
- 按钮点击模拟
- 文本输入模拟
- 页面导航模拟

## 配置选项

### 超时设置
```python
DEFAULT_TIMEOUT = 30      # 默认超时时间（秒）
LONG_TIMEOUT = 120        # 长时间操作超时（秒）
WINDOW_WAIT_TIME = 2      # 窗口显示等待时间（秒）
OPERATION_WAIT_TIME = 1   # 操作间隔等待时间（秒）
```

### 测试模型
```python
TEST_MODEL_NAME = "large-v3-turbo"  # 测试使用的模型名称
```

### 模拟API配置
```python
MOCK_API_KEY = "test_api_key_12345"     # 模拟API密钥
MOCK_API_URL = "http://localhost:8080/mock/api"  # 模拟API地址
```

## 故障排除

### 常见问题

1. **窗口未显示**
   - 检查是否有其他QApplication实例运行
   - 确保测试环境支持GUI显示
   - 在Linux上可能需要安装 `pytest-xvfb`

2. **组件未找到**
   - 检查页面是否正确加载
   - 确认组件类型和查找方法
   - 增加等待时间

3. **文件操作失败**
   - 检查文件权限
   - 确认测试目录存在
   - 检查磁盘空间

4. **API测试失败**
   - 检查mock配置
   - 确认网络模拟设置
   - 验证API密钥格式

### 调试技巧

1. **增加日志输出**
```python
print(f"当前页面类型: {type(current_page)}")
print(f"找到的组件: {component}")
```

2. **增加等待时间**
```python
self.wait_and_process_events(5)  # 等待5秒
```

3. **使用断点调试**
```python
import pdb; pdb.set_trace()
```

4. **截图调试**（pytest-qt支持）
```python
qtbot.screenshot(window, "debug_screenshot.png")
```

## 持续集成

### GitHub Actions 示例

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Install uv
      uses: astral-sh/setup-uv@v1
    - name: Set up Python
      run: uv python install 3.11
    - name: Install dependencies
      run: |
        uv sync
        uv add --group test pytest pytest-qt pytest-xvfb
    - name: Run tests
      run: |
        xvfb-run -a uv run pytest tests/test_e2e_pytest.py -v
```

## 扩展测试

### 添加新测试用例

1. 在相应的测试文件中添加新的测试方法
2. 使用适当的测试标记（`@pytest.mark.e2e`等）
3. 遵循现有的命名约定
4. 添加适当的文档字符串

### 添加新的测试辅助方法

1. 在 `utils/test_helpers.py` 中添加新的辅助方法
2. 确保方法具有良好的错误处理
3. 添加类型提示和文档字符串
4. 在 `utils/__init__.py` 中导出新方法

### 性能测试

可以添加性能相关的测试：
```python
@pytest.mark.slow
def test_large_file_processing(self, qtbot, main_window):
    """测试大文件处理性能"""
    # 测试逻辑
```

## 最佳实践

1. **测试隔离**：每个测试应该独立运行，不依赖其他测试的状态
2. **清理资源**：测试结束后清理创建的文件和资源
3. **模拟外部依赖**：使用mock模拟API调用和文件操作
4. **合理的等待时间**：给UI操作足够的时间完成
5. **详细的断言消息**：提供清晰的错误信息
6. **测试文档**：为复杂的测试用例添加详细说明

## 贡献指南

1. 添加新功能时，同时添加相应的测试
2. 确保所有测试通过后再提交代码
3. 遵循现有的代码风格和命名约定
4. 更新相关文档
5. 考虑测试的可维护性和可读性