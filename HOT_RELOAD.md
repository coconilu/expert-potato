# 热更新功能说明

本项目已集成 `hupper` 热更新功能，可以在开发过程中自动检测代码变化并重启应用程序。

## 功能特性

- 🔥 **自动重启**: 检测到代码变化时自动重启应用
- 📁 **智能监控**: 监控 `src/` 目录下的所有 Python 文件
- ⚡ **快速响应**: 文件保存后立即触发重启
- 🛡️ **安全隔离**: 仅在开发环境启用，生产环境不受影响

## 使用方法

### 方法一：使用批处理文件（推荐）

双击运行 `run_dev.bat` 文件：

```bash
# Windows 用户直接双击
run_dev.bat
```

### 方法二：使用 Python 脚本

```bash
# 运行开发脚本
python run_dev.py
```

### 方法三：手动设置环境变量

```bash
# 设置环境变量
set ENABLE_HOT_RELOAD=true

# 运行应用
python src/main.py
```

### 方法四：使用 uv 运行

```bash
# 安装依赖
uv pip install -e .

# 启用热更新运行
ENABLE_HOT_RELOAD=true uv run python src/main.py
```

## 工作原理

1. **环境检测**: 检查 `ENABLE_HOT_RELOAD` 环境变量
2. **启动监控**: 使用 `hupper` 启动文件监控器
3. **文件监控**: 监控 `src/**/*.py` 模式的所有文件
4. **自动重启**: 检测到变化时自动重启应用进程

## 配置说明

热更新相关配置在 `src/config/core.py` 中的 `Messages` 类：

```python
# 热更新相关常量
HOT_RELOAD_ENV_VAR = "ENABLE_HOT_RELOAD"           # 环境变量名
HOT_RELOAD_TRUE_VALUES = ('true', '1', 'yes')      # 启用值
HOT_RELOAD_WATCH_PATTERN = "src/**/*.py"           # 监控模式
HOT_RELOAD_MODULE_PATH = "src.main.run_app"        # 重启入口
```

## 注意事项

1. **开发专用**: 热更新功能仅用于开发环境，生产环境请勿启用
2. **性能影响**: 启用热更新会增加少量系统资源消耗
3. **文件保存**: 确保代码保存后才会触发重启
4. **依赖安装**: 首次使用需要安装 `hupper` 依赖

## 故障排除

### 热更新不工作

1. 检查环境变量是否正确设置
2. 确认 `hupper` 依赖已安装
3. 检查文件路径是否正确

### 重启过于频繁

1. 检查是否有临时文件被监控
2. 调整监控模式排除不必要的文件

### 应用无法启动

1. 检查代码语法错误
2. 确认所有依赖已正确安装
3. 查看控制台错误信息

## 依赖信息

- **hupper**: >= 1.12.1
- **PyQt6**: >= 6.5.0
- **Python**: >= 3.11.12
