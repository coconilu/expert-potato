# Expert Potato E2E 测试快速入门指南

## 🚀 快速开始

### 1. 环境准备（5分钟）

```bash
# 1. 确保项目依赖已安装
uv sync

# 2. 安装测试依赖（如果还没有安装）
# 测试依赖已在 pyproject.toml 中配置，sync 时会自动安装
```

### 2. 运行你的第一个E2E测试（1分钟）

```bash
# 运行完整的核心流程测试
uv run pytest tests/test_e2e_pytest.py::TestE2EWorkflow::test_complete_workflow -v
```

如果看到 `PASSED` 绿色输出，恭喜！你的E2E测试环境已经准备就绪。

## 📋 核心测试场景

### 场景1：完整工作流程测试
```bash
# 测试：文件选择 → 模型选择 → 文案提取 → API修复
uv run pytest tests/test_e2e_pytest.py::TestE2EWorkflow::test_complete_workflow -v
```

### 场景2：文件选择功能测试
```bash
# 测试：拖拽文件、文件验证、状态更新
uv run pytest tests/test_e2e_pytest.py::TestE2EWorkflow::test_file_selection_only -v
```

### 场景3：API密钥验证测试
```bash
# 测试：API密钥格式验证、错误处理
uv run pytest tests/test_e2e_pytest.py::TestE2EWorkflow::test_api_key_validation -v
```

### 场景4：页面导航测试
```bash
# 测试：页面切换、导航功能
uv run pytest tests/test_e2e_pytest.py::TestE2EWorkflow::test_page_navigation -v
```

## 🎯 按标记运行测试

```bash
# 只运行E2E测试
uv run pytest tests/ -m "e2e" -v

# 只运行API相关测试
uv run pytest tests/ -m "api" -v

# 只运行GUI测试
uv run pytest tests/ -m "gui" -v

# 跳过慢速测试
uv run pytest tests/ -m "not slow" -v

# 运行单元测试
uv run pytest tests/ -m "unit" -v
```

## 📊 测试报告和覆盖率

### 生成HTML覆盖率报告
```bash
uv run pytest tests/test_e2e_pytest.py --cov=src --cov-report=html --cov-report=term
```

报告将生成在 `htmlcov/index.html`，用浏览器打开查看详细覆盖率。

### 生成JUnit XML报告（CI/CD友好）
```bash
uv run pytest tests/test_e2e_pytest.py --junitxml=test-results.xml
```

## 🔧 常用调试命令

### 详细输出模式
```bash
# 显示详细的测试输出和print语句
uv run pytest tests/test_e2e_pytest.py -v -s
```

### 失败时立即停止
```bash
# 遇到第一个失败就停止
uv run pytest tests/test_e2e_pytest.py -x
```

### 重新运行失败的测试
```bash
# 只重新运行上次失败的测试
uv run pytest tests/test_e2e_pytest.py --lf
```

### 显示最慢的10个测试
```bash
uv run pytest tests/test_e2e_pytest.py --durations=10
```

## 🐛 常见问题快速解决

### 问题1：窗口未显示或测试卡住
```bash
# Windows: 确保没有其他应用实例运行
taskkill /f /im "Expert Potato.exe" 2>nul

# 然后重新运行测试
uv run pytest tests/test_e2e_pytest.py::TestE2EWorkflow::test_window_startup -v
```

### 问题2：找不到组件或控件
```bash
# 运行带调试信息的测试
uv run pytest tests/test_e2e_pytest.py -v -s --tb=long
```

### 问题3：API测试失败
```bash
# 检查mock配置，运行API相关测试
uv run pytest tests/test_e2e_pytest.py -m "api" -v -s
```

### 问题4：文件权限错误
```bash
# 清理测试文件并重新运行
rmdir /s /q tests\data tests\output 2>nul
uv run pytest tests/test_e2e_pytest.py::TestE2EWorkflow::test_file_selection_only -v
```

## 📝 编写新的E2E测试

### 基本测试模板
```python
import pytest
from tests.base_test import BaseTestCase

class TestMyFeature(BaseTestCase):
    
    @pytest.mark.e2e
    def test_my_new_feature(self, qtbot, main_window):
        """测试我的新功能"""
        # 1. 准备测试数据
        test_data = "测试数据"
        
        # 2. 执行操作
        # 导航到目标页面
        self.navigate_to_page(main_window, "目标页面")
        
        # 查找并操作控件
        button = self.find_widget(main_window, "按钮名称")
        qtbot.mouseClick(button, Qt.LeftButton)
        
        # 3. 验证结果
        assert self.wait_for_condition(
            lambda: self.check_expected_result(),
            timeout=10
        )
```

### 添加测试到现有文件
1. 打开 `tests/test_e2e_pytest.py`
2. 在 `TestE2EWorkflow` 类中添加新方法
3. 使用适当的 pytest 标记
4. 运行测试验证

## 🔄 持续集成设置

### GitHub Actions 配置示例
创建 `.github/workflows/e2e-tests.yml`：

```yaml
name: E2E Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  e2e-tests:
    runs-on: windows-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Install uv
      uses: astral-sh/setup-uv@v1
      
    - name: Set up Python
      run: uv python install 3.11
      
    - name: Install dependencies
      run: uv sync
      
    - name: Run E2E tests
      run: |
        uv run pytest tests/test_e2e_pytest.py -v --junitxml=test-results.xml
        
    - name: Upload test results
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: test-results
        path: test-results.xml
```

## 📈 性能监控

### 监控测试执行时间
```bash
# 显示每个测试的执行时间
uv run pytest tests/test_e2e_pytest.py --durations=0
```

### 性能基准测试
```bash
# 运行性能相关的测试
uv run pytest tests/test_e2e_pytest.py -m "slow" --durations=10
```

## 🎨 测试数据管理

### 测试文件位置
- 测试音频：`tests/data/test_audio.wav`（自动生成）
- 测试文本：`tests/data/test_text.txt`（自动生成）
- 输出目录：`tests/output/`（自动清理）

### 手动清理测试数据
```bash
# Windows
rmdir /s /q tests\data tests\output 2>nul

# 或使用Python脚本
uv run python -c "from tests.utils.test_helpers import FileTestHelper; FileTestHelper.cleanup_test_files()"
```

## 🔍 高级调试技巧

### 1. 截图调试
```python
# 在测试中添加截图
qtbot.screenshot(main_window, "debug_screenshot.png")
```

### 2. 断点调试
```python
# 在测试代码中添加断点
import pdb; pdb.set_trace()
```

### 3. 日志调试
```python
# 添加详细日志
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug(f"当前状态: {current_state}")
```

### 4. 组件查找调试
```bash
# 运行组件查找测试
uv run pytest tests/test_components.py::TestUITestHelper::test_find_widget -v -s
```

## 📚 进阶学习资源

### 相关文档
- [pytest-qt 官方文档](https://pytest-qt.readthedocs.io/)
- [PyQt6 测试指南](https://doc.qt.io/qtforpython/tutorials/index.html)
- [unittest.mock 文档](https://docs.python.org/3/library/unittest.mock.html)

### 测试最佳实践
1. **测试命名**：使用描述性的测试名称
2. **测试隔离**：每个测试独立运行
3. **数据清理**：测试后清理临时数据
4. **等待策略**：合理设置等待时间
5. **错误处理**：提供清晰的错误信息

## 🤝 贡献测试

### 提交测试的步骤
1. 创建功能分支：`git checkout -b feature/new-test`
2. 编写测试代码
3. 运行所有测试：`uv run pytest tests/ -v`
4. 确保测试通过
5. 提交代码：`git commit -m "添加新的E2E测试"`
6. 推送分支：`git push origin feature/new-test`
7. 创建Pull Request

### 测试代码审查清单
- [ ] 测试名称清晰描述功能
- [ ] 使用适当的pytest标记
- [ ] 包含必要的文档字符串
- [ ] 遵循现有代码风格
- [ ] 测试独立且可重复运行
- [ ] 包含适当的断言和错误信息
- [ ] 清理测试产生的临时文件

---

## 🆘 获取帮助

如果遇到问题：
1. 查看 [完整测试文档](./README.md)
2. 检查 [常见问题](#常见问题快速解决)
3. 运行诊断命令：`uv run pytest tests/test_e2e_pytest.py --collect-only`
4. 在项目仓库创建Issue

**记住**：好的E2E测试是确保应用质量的关键！🎯