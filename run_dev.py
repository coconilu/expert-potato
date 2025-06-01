#!/usr/bin/env python3
"""开发环境启动脚本 - 支持热更新"""

import os
import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# 设置热更新环境变量
os.environ["ENABLE_HOT_RELOAD"] = "true"

# 导入并运行主程序
from main import main

if __name__ == "__main__":
    print("🚀 启动开发模式 (热更新已启用)")
    print("💡 修改代码后会自动重启应用")
    print("🛑 按 Ctrl+C 退出")
    print("-" * 50)
    main()
