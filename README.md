# 多功能工具箱

这是一个基于 PyQt6 和 PyQt6-Fluent-Widgets 构建的现代化桌面应用程序，采用模块化设计，提供音视频处理功能。

## 功能特性

### 提取音频

- 从视频文件中提取音频
- 支持多种音频格式输出
- 批量处理功能

### 提取文案

- 从音频文件中提取文字
- 语音识别转文本
- 支持多种语言识别
- 字幕生成功能

## 项目结构

```
src/
├── main.py                 # 应用程序入口文件
├── config/                  # 配置模块
│   ├── __init__.py
│   └── theme.py            # 主题配置（颜色、字体、窗口大小等）
├── ui/                     # UI组件模块
│   ├── __init__.py
│   ├── base_page.py        # 页面基类
│   ├── navigation.py       # 导航栏组件
│   └── main_window.py      # 主窗口
└── pages/                  # 页面模块
    ├── __init__.py
    ├── extract_audio_page.py  # 提取音频页面
    └── extract_text_page.py   # 提取文案页面
```

### 模块说明

- **config/theme.py**: 统一管理应用主题、颜色、字体等配置
- **ui/base_page.py**: 提供页面基类，统一页面布局和样式
- **ui/navigation.py**: 导航栏组件，管理页面切换逻辑
- **ui/main_window.py**: 主窗口，负责整体布局和页面管理
- **pages/**: 各功能页面的具体实现

## 技术栈

- **PyQt6**: 现代化的 Python GUI 框架
- **PyQt6-Fluent-Widgets**: 提供 Fluent Design 风格的 UI 组件
- **模块化架构**: 清晰的代码结构，便于维护和扩展

## 安装说明

1. 确保已安装 Python 3.11.12 或更高版本
2. 安装 uv 包管理器：

```bash
pip install uv
```

3. 同步项目依赖：

```bash
uv sync
```

## 运行应用

在项目根目录下运行：

```bash
uv run python src/main.py
```

## 开发指南

### 添加新页面

1. 在 `pages/` 目录下创建新的页面文件
2. 继承 `BasePage` 类
3. 在 `main_window.py` 中注册新页面
4. 在导航栏中添加对应的导航项

### 自定义主题

修改 `config/theme.py` 文件中的配置项：

- `DEFAULT_THEME`: 主题模式（亮色/暗色）
- `DEFAULT_COLOR`: 主题色彩
- `WINDOW_WIDTH/HEIGHT`: 窗口尺寸
- 样式相关的方法

## 注意事项

- 应用采用暗色主题，适合长时间使用
- 页面切换使用缓存机制，提高性能
- 所有 UI 组件都遵循 Fluent Design 设计规范
