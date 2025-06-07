"""全局状态管理模块 - 类似Vue Pinia的状态管理方案"""

from typing import Any, Dict, Callable, Optional, List
from PyQt6.QtCore import QObject, pyqtSignal
from enum import Enum
from dataclasses import dataclass, field
from config.core import AppConstants


class FileState(Enum):
    """文件状态枚举"""

    NONE = "none"  # 无文件
    LOADED = "loaded"  # 文件已加载
    ERROR = "error"  # 文件错误


class ExtractState(Enum):
    """提取状态枚举"""

    IDLE = "idle"  # 空闲状态
    PROCESSING = "processing"  # 正在提取
    COMPLETED = "completed"  # 提取完成
    ERROR = "error"  # 提取错误


class RefineState(Enum):
    """修复状态枚举"""

    IDLE = "idle"  # 空闲状态
    PROCESSING = "processing"  # 正在修复
    COMPLETED = "completed"  # 修复完成
    ERROR = "error"  # 修复错误


@dataclass
class FileStateData:
    """文件状态数据类"""

    path: str = ""
    name: str = ""
    state: FileState = FileState.NONE


@dataclass
class ExtractTextState:
    """文本提取状态数据类"""

    state: ExtractState = ExtractState.IDLE
    progress: int = 0
    selected_model: str = AppConstants.AUDIO_EXTRACT_DEFAULT_MODEL
    extracted_text: str = ""
    error_message: str = ""


@dataclass
class RefineTextState:
    """文本修复状态数据类"""

    state: RefineState = RefineState.IDLE
    progress: int = 0
    api_key: str = ""
    refined_text: str = ""
    detected_domain: str = ""
    error_message: str = ""
    refine_time: int = 0  # 修复耗时（秒）


@dataclass
class AppState:
    """应用程序全局状态"""

    file: FileStateData = field(default_factory=FileStateData)
    extract: ExtractTextState = field(default_factory=ExtractTextState)
    refine: RefineTextState = field(default_factory=RefineTextState)


class StateManager(QObject):
    """全局状态管理器 - 类似Vue Pinia的Store"""

    # 状态变化信号
    file_state_changed = pyqtSignal(FileState)
    extract_state_changed = pyqtSignal(ExtractState)
    refine_state_changed = pyqtSignal(RefineState)

    # 文本变化信号
    extract_text_changed = pyqtSignal(str)
    refine_text_changed = pyqtSignal(str)

    # 具体状态变化信号
    file_selected = pyqtSignal(str, str)  # file_path, file_name
    extract_started = pyqtSignal(str)  # model_name
    extract_progress_updated = pyqtSignal(int)  # progress
    extract_completed = pyqtSignal(str)  # extracted_text
    extract_failed = pyqtSignal(str)  # error_message

    refine_started = pyqtSignal(str)  # original_text
    refine_progress_updated = pyqtSignal(int)  # progress
    refine_completed = pyqtSignal(str, str)  # refined_text, domain
    refine_failed = pyqtSignal(str)  # error_message

    def __init__(self):
        super().__init__()
        self._state = AppState()
        self._subscribers: Dict[str, List[Callable]] = {
            "file": [],
            "extract": [],
            "refine": [],
        }

    @property
    def state(self) -> AppState:
        """获取当前状态"""
        return self._state

    # ==================== 文件状态管理 ====================

    def set_file(self, file_path: str) -> None:
        """设置选中的文件"""
        import os

        self._state.file.path = file_path
        self._state.file.name = os.path.basename(file_path) if file_path else ""
        self._state.file.state = FileState.LOADED if file_path else FileState.NONE

        # 发射信号
        self.file_state_changed.emit(self._state.file.state)
        self.file_selected.emit(file_path, self._state.file.name)

        # 通知订阅者
        self._notify_subscribers("file")

    def reset_file(self) -> None:
        """重置文件状态"""
        self._state.file = FileStateData()
        self.file_state_changed.emit(self._state.file.state)
        self._notify_subscribers("file")

    # ==================== 文本提取状态管理 ====================

    def start_extract(self, model_name: str = None) -> None:
        """开始文本提取"""
        if model_name:
            self._state.extract.selected_model = model_name
        self._state.extract.state = ExtractState.PROCESSING
        self._state.extract.progress = 0
        self._state.extract.extracted_text = ""
        self._state.extract.error_message = ""

        # 发射信号
        self.extract_state_changed.emit(self._state.extract.state)
        self.extract_started.emit(self._state.extract.selected_model)

        # 通知订阅者
        self._notify_subscribers("extract")

    def update_extract_progress(self, progress: int) -> None:
        """更新提取进度"""
        self._state.extract.progress = progress

        # 发射信号
        self.extract_progress_updated.emit(progress)

        # 通知订阅者
        self._notify_subscribers("extract")

    def complete_extract(self, extracted_text: str) -> None:
        """完成文本提取"""
        self._state.extract.state = ExtractState.COMPLETED
        self._state.extract.extracted_text = extracted_text
        self._state.extract.progress = 100

        # 发射信号
        self.extract_state_changed.emit(self._state.extract.state)
        self.extract_completed.emit(extracted_text)
        self.extract_text_changed.emit(extracted_text)

        # 通知订阅者
        self._notify_subscribers("extract")
        self._notify_subscribers("refine")  # 修复区域也需要更新

    def fail_extract(self, error_message: str) -> None:
        """提取失败"""
        self._state.extract.state = ExtractState.ERROR
        self._state.extract.error_message = error_message

        # 发射信号
        self.extract_state_changed.emit(self._state.extract.state)
        self.extract_failed.emit(error_message)

        # 通知订阅者
        self._notify_subscribers("extract")

    def reset_extract(self) -> None:
        """重置提取状态"""
        self._state.extract = ExtractTextState()
        self.extract_state_changed.emit(self._state.extract.state)
        self.extract_text_changed.emit("")
        self._notify_subscribers("extract")

    # ==================== 文本修复状态管理 ====================

    def set_api_key(self, api_key: str) -> None:
        """设置API密钥"""
        self._state.refine.api_key = api_key
        self._notify_subscribers("refine")

    def start_refine(self) -> None:
        """开始文本修复"""
        original_text = self._state.extract.extracted_text
        self._state.refine.state = RefineState.PROCESSING
        self._state.refine.progress = 0
        self._state.refine.refined_text = ""
        self._state.refine.detected_domain = ""
        self._state.refine.error_message = ""
        self._state.refine.refine_time = 0

        # 发射信号
        self.refine_state_changed.emit(self._state.refine.state)
        self.refine_started.emit(original_text)

        # 通知订阅者
        self._notify_subscribers("refine")

    def update_refine_progress(self, progress: int) -> None:
        """更新修复进度"""
        self._state.refine.progress = progress

        # 发射信号
        self.refine_progress_updated.emit(progress)

        # 通知订阅者
        self._notify_subscribers("refine")

    def complete_refine(self, refined_text: str, detected_domain: str = "") -> None:
        """完成文本修复"""
        self._state.refine.state = RefineState.COMPLETED
        self._state.refine.refined_text = refined_text
        self._state.refine.detected_domain = detected_domain
        self._state.refine.progress = 100

        # 发射信号
        self.refine_state_changed.emit(self._state.refine.state)
        self.refine_completed.emit(refined_text, detected_domain)
        self.refine_text_changed.emit(refined_text)

        # 通知订阅者
        self._notify_subscribers("refine")

    def fail_refine(self, error_message: str) -> None:
        """修复失败"""
        self._state.refine.state = RefineState.ERROR
        self._state.refine.error_message = error_message

        # 发射信号
        self.refine_state_changed.emit(self._state.refine.state)
        self.refine_failed.emit(error_message)

        # 通知订阅者
        self._notify_subscribers("refine")

    def update_refine_time(self, refine_time: int) -> None:
        """更新修复耗时"""
        self._state.refine.refine_time = refine_time
        self._notify_subscribers("refine")

    def reset_refine(self) -> None:
        """重置修复状态"""
        api_key = self._state.refine.api_key  # 保留API密钥
        self._state.refine = RefineTextState()
        self._state.refine.api_key = api_key
        self.refine_state_changed.emit(self._state.refine.state)
        self.refine_text_changed.emit("")
        self._notify_subscribers("refine")

    # ==================== 订阅机制 ====================

    def subscribe(self, state_type: str, callback: Callable) -> None:
        """订阅状态变化

        Args:
            state_type: 状态类型 ('file', 'extract', 'refine')
            callback: 回调函数
        """
        if state_type in self._subscribers:
            self._subscribers[state_type].append(callback)

    def unsubscribe(self, state_type: str, callback: Callable) -> None:
        """取消订阅状态变化

        Args:
            state_type: 状态类型 ('file', 'extract', 'refine')
            callback: 回调函数
        """
        if (
            state_type in self._subscribers
            and callback in self._subscribers[state_type]
        ):
            self._subscribers[state_type].remove(callback)

    def _notify_subscribers(self, state_type: str) -> None:
        """通知订阅者状态变化"""
        if state_type in self._subscribers:
            for callback in self._subscribers[state_type]:
                try:
                    callback()
                except Exception as e:
                    print(f"状态订阅回调执行失败: {e}")

    # ==================== 便捷方法 ====================

    def can_extract(self) -> bool:
        """是否可以开始提取"""
        return (
            self._state.file.state == FileState.LOADED
            and self._state.extract.state != ExtractState.PROCESSING
        )

    def can_refine(self) -> bool:
        """是否可以开始修复"""
        return (
            bool(self._state.refine.api_key)
            and bool(self._state.extract.extracted_text)
            and self._state.refine.state != RefineState.PROCESSING
        )

    def get_file_info(self) -> tuple[str, str]:
        """获取文件信息"""
        return self._state.file.path, self._state.file.name

    def get_extracted_text(self) -> str:
        """获取提取的文本"""
        return self._state.extract.extracted_text

    def get_refined_text(self) -> str:
        """获取修复的文本"""
        return self._state.refine.refined_text

    def set_extracted_text(self, text: str) -> None:
        """设置提取的文本"""
        self._state.extract.extracted_text = text
        self.extract_text_changed.emit(text)
        self._notify_subscribers("extract")
        self._notify_subscribers("refine")  # 修复区域也需要更新

    def set_refined_text(self, text: str) -> None:
        """设置修复的文本"""
        self._state.refine.refined_text = text
        self.refine_text_changed.emit(text)
        self._notify_subscribers("refine")


# 全局状态管理器实例
_state_manager: Optional[StateManager] = None


def get_state_manager() -> StateManager:
    """获取全局状态管理器实例（单例模式）"""
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager()
    return _state_manager


def reset_state_manager() -> None:
    """重置状态管理器（主要用于测试）"""
    global _state_manager
    _state_manager = None