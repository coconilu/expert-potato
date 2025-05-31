# 剪辑工具

一个基于 PyQt6 和 PyQt6-Fluent-Widgets 构建的现代化剪辑工具应用。

## 功能特性

### 提取音频页面

- **文件选择**: 支持拖拽和点击选择音频文件
- **音频转文字**: 使用 OpenAI Whisper 模型进行高精度语音识别
- **支持格式**: MP3, WAV, M4A, FLAC, AAC, OGG, WMA
- **实时进度**: 显示转换进度条
- **文案复制**: 一键复制提取的文案到剪贴板
- **现代 UI**: 基于 Fluent Design 的美观界面

### 提取文案页面

- 占位页面，待后续开发

## 安装依赖

### 1. 安装 FFmpeg

在安装 Python 依赖之前，需要先安装 FFmpeg（Whisper 音频处理必需）：

**Windows:**

```bash
# 使用 Chocolatey
choco install ffmpeg

# 或使用 Scoop
scoop install ffmpeg

# 或手动下载安装
# 从 https://ffmpeg.org/download.html 下载并添加到 PATH
```

**macOS:**

```bash
# 使用 Homebrew
brew install ffmpeg
```

**Linux:**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg
```

### 2. 安装 Python 依赖

使用 uv 包管理器安装依赖：

```bash
# 创建虚拟环境
uv venv

# 同步依赖
uv sync
```

或者使用 pip：

```bash
pip install PyQt6 PyQt6-Fluent-Widgets openai-whisper torch torchaudio
```

## 运行应用

```bash
python src/main.py
```

## 使用说明

### 提取音频文案

1. 启动应用后，默认进入"提取音频"页面
2. 将音频文件拖拽到指定区域，或点击区域选择文件
3. 选择文件后，点击"提取文案"按钮
4. 等待 Whisper 模型处理（首次使用会下载模型）
5. 提取完成后，文案会显示在文本区域
6. 点击"复制文案"按钮将结果复制到剪贴板

## 技术栈

- **UI 框架**: PyQt6
- **UI 组件库**: PyQt6-Fluent-Widgets
- **语音识别**: OpenAI Whisper
- **深度学习**: PyTorch
- **包管理**: uv

## 项目结构

```
src/
├── assets/          # 资源文件
├── config/          # 配置文件
│   ├── core.py      # 核心常量配置
│   └── theme.py     # 主题配置
├── pages/           # 页面组件
│   ├── extract_audio_page.py  # 提取音频页面
│   └── extract_text_page.py   # 提取文案页面
├── ui/              # UI组件
│   ├── base_page.py     # 页面基类
│   ├── main_window.py   # 主窗口
│   ├── navigation.py    # 导航组件
│   └── title_bar.py     # 标题栏
└── main.py          # 应用入口
```

## 注意事项

- 首次使用 Whisper 时会自动下载模型文件（约 140MB）
- 音频文件越大，处理时间越长
- 建议使用清晰的音频文件以获得更好的识别效果
- 支持中文、英文等多种语言的语音识别

## 开发说明

- 代码遵循 PEP 8 规范
- 使用类型注解提高代码可读性
- 常量统一在 `config/core.py` 中管理
- UI 样式在 `config/theme.py` 中配置
- 采用模块化设计，便于扩展新功能
