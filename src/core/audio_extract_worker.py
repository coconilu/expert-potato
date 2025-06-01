"""音频提取工作线程模块"""

import os
from PyQt6.QtCore import QThread, pyqtSignal


class AudioExtractWorker(QThread):
    """音频提取工作线程"""

    progress_updated = pyqtSignal(int)
    text_extracted = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, audio_file_path: str, model_name: str = "base"):
        super().__init__()
        self.audio_file_path = audio_file_path
        self.model_name = model_name

    def is_cuda_available(self):
        """检查 CUDA 是否可用"""
        try:
            import torch

            return torch.cuda.is_available()
        except ImportError:
            return False

    def supportModel(self):
        """获取支持的模型列表"""
        return [
            "tiny",
            "base",
            "small",
            "large",
            "large-v1",
            "large-v2",
            "large-v3",
            "large-v3-turbo",
        ]

    def ensure_model_downloaded(self, model_name="base"):
        try:
            from faster_whisper import WhisperModel

            device = "cuda" if self.is_cuda_available() else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"

            model = WhisperModel(model_name, device=device, compute_type=compute_type)
            return model
        except Exception as e:
            print(f"模型加载失败: {e}")
            # 可以尝试重新下载或使用其他模型
            return None

    def run(self):
        """执行音频转文字任务"""
        try:

            # 更新进度
            self.progress_updated.emit(20)

            # 加载模型
            model = self.ensure_model_downloaded(self.model_name)
            if not model:
                raise Exception(f"模型 {self.model_name} 加载失败")
            # 更新进度
            self.progress_updated.emit(50)

            # 检查音频文件是否存在
            if not os.path.exists(self.audio_file_path):
                raise FileNotFoundError(f"音频文件不存在：{self.audio_file_path}")

            print("开始转录文件:", self.audio_file_path)

            # 转录音频
            try:
                segments, info = model.transcribe(self.audio_file_path)
                # 将所有段落的文本合并
                text_segments = []
                for segment in segments:
                    text_segments.append(segment.text)
                text = "".join(text_segments)
            except Exception as e:
                print(f"音频转写失败: {str(e)}")
                raise Exception(f"音频转写失败: {str(e)}")
            self.progress_updated.emit(90)

            self.progress_updated.emit(100)

            # 发送结果
            self.text_extracted.emit(text)

        except ImportError:
            self.error_occurred.emit(
                "请先安装 faster-whisper 库：pip install faster-whisper"
            )
        except Exception as e:
            print("Exception", e)
            self.error_occurred.emit(f"音频转文字失败：{str(e)}")
