@echo off
chcp 65001 >nul
echo 🚀 启动开发模式 (热更新已启用)
echo 💡 修改代码后会自动重启应用
echo 🛑 按 Ctrl+C 退出
echo --------------------------------------------------
uv run python run_dev.py
pause