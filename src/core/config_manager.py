"""配置管理器模块 - 处理应用程序配置的持久化存储"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """配置管理器类 - 负责配置的保存和加载"""

    def __init__(self, config_file: str = "app_config.json"):
        """初始化配置管理器

        Args:
            config_file: 配置文件名，默认为 app_config.json
        """
        # 配置文件保存在用户目录下的应用程序文件夹中
        self.config_dir = Path.home() / ".expert-potato"
        self.config_file = self.config_dir / config_file
        self._ensure_config_dir()
        self._config_data = self._load_config()

    def _ensure_config_dir(self) -> None:
        """确保配置目录存在"""
        self.config_dir.mkdir(exist_ok=True)

    def _load_config(self) -> Dict[str, Any]:
        """从文件加载配置

        Returns:
            配置数据字典
        """
        if not self.config_file.exists():
            return {}

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"加载配置文件失败: {e}")
            return {}

    def _save_config(self) -> bool:
        """保存配置到文件

        Returns:
            保存是否成功
        """
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self._config_data, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            print(f"保存配置文件失败: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值

        Args:
            key: 配置键名
            default: 默认值

        Returns:
            配置值
        """
        return self._config_data.get(key, default)

    def set(self, key: str, value: Any) -> bool:
        """设置配置值

        Args:
            key: 配置键名
            value: 配置值

        Returns:
            设置是否成功
        """
        self._config_data[key] = value
        return self._save_config()

    def remove(self, key: str) -> bool:
        """删除配置项

        Args:
            key: 配置键名

        Returns:
            删除是否成功
        """
        if key in self._config_data:
            del self._config_data[key]
            return self._save_config()
        return True

    def get_api_key(self) -> Optional[str]:
        """获取API密钥

        Returns:
            API密钥，如果不存在则返回None
        """
        return self.get("deepseek_api_key")

    def set_api_key(self, api_key: str) -> bool:
        """设置API密钥

        Args:
            api_key: API密钥

        Returns:
            设置是否成功
        """
        return self.set("deepseek_api_key", api_key)

    def clear_api_key(self) -> bool:
        """清除API密钥

        Returns:
            清除是否成功
        """
        return self.remove("deepseek_api_key")
