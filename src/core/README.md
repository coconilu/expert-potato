# Core 模块

核心功能模块，包含各种工作线程和核心业务逻辑。

## 模块列表

### AudioExtractWorker

音频提取工作线程，用于从音频文件中提取文字内容。

**功能特性：**

- 支持多种音频格式
- 使用 Faster-Whisper 模型进行语音识别
- 支持 CUDA 和 CPU 运行模式
- 提供进度更新和错误处理

### TextRefineWorker

文案修复工作线程，用于调用 DeepSeek API 识别文案领域并修复文案内容。

**功能特性：**

- 自动识别文案所属专业领域
- 修复错别字和语法错误
- 统一专业术语表达
- 保持原文语义和风格
- 提供进度更新和错误处理

## 使用方法

### TextRefineWorker 使用示例

```python
from PyQt6.QtWidgets import QApplication
from core import TextRefineWorker

# 创建工作线程
worker = TextRefineWorker(
    text="需要修复的文案内容",
    api_key="your_deepseek_api_key"
)

# 连接信号
worker.progress_updated.connect(lambda progress: print(f"进度: {progress}%"))
worker.domain_detected.connect(lambda domain: print(f"检测到领域: {domain}"))
worker.text_refined.connect(lambda text: print(f"修复后文案: {text}"))
worker.error_occurred.connect(lambda error: print(f"错误: {error}"))

# 启动任务
worker.start()
```

### 信号说明

**TextRefineWorker 信号：**

- `progress_updated(int)`: 进度更新信号，参数为进度百分比
- `domain_detected(str)`: 领域检测信号，参数为检测到的专业领域
- `text_refined(str)`: 文案修复完成信号，参数为修复后的文案
- `error_occurred(str)`: 错误发生信号，参数为错误信息

## 配置说明

所有常量配置都在 `src/config/core.py` 的 `AppConstants` 类中定义：

### DeepSeek API 配置

- `DEEPSEEK_API_URL`: API 端点地址
- `DEEPSEEK_DEFAULT_MODEL`: 默认使用的模型
- `DEEPSEEK_DEFAULT_TEMPERATURE`: 生成温度参数
- `DEEPSEEK_DEFAULT_MAX_TOKENS`: 最大生成令牌数
- `DEEPSEEK_REQUEST_TIMEOUT`: 请求超时时间

### 提示词模板

`DEEPSEEK_PROMPT_TEMPLATE` 定义了发送给 API 的提示词模板，包含：

- 任务描述
- 输出格式要求
- 修复要求和标准

## 依赖要求

- `PyQt6`: GUI 框架
- `requests`: HTTP 请求库
- `faster-whisper`: 语音识别库（AudioExtractWorker）
- `torch`: 深度学习框架（AudioExtractWorker）

## 注意事项

1. **API 密钥安全**：请妥善保管 DeepSeek API 密钥，不要在代码中硬编码
2. **网络连接**：TextRefineWorker 需要稳定的网络连接来访问 DeepSeek API
3. **错误处理**：建议在使用时连接 `error_occurred` 信号来处理可能的错误
4. **线程安全**：所有 Worker 都继承自 QThread，请在主线程中创建和管理

## 示例程序

运行 `text_refine_example.py` 可以查看 TextRefineWorker 的完整使用示例：

```bash
uv run python src/core/text_refine_example.py
```
