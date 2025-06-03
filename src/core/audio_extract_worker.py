"""音频提取工作线程模块"""

import os
from PyQt6.QtCore import QThread, pyqtSignal
from config.core import AppConstants


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

    def ensure_model_downloaded(
        self, model_name=AppConstants.AUDIO_EXTRACT_DEFAULT_MODEL
    ):
        """确保模型已下载，如果没有则进行下载"""
        try:
            from faster_whisper import WhisperModel
            import os
            from pathlib import Path

            # 检查模型是否已缓存
            cache_dir = Path(os.path.expanduser(AppConstants.AUDIO_EXTRACT_CACHE_DIR))
            model_pattern = f"*{AppConstants.AUDIO_EXTRACT_MODEL_PREFIX}{model_name}*"

            # 查找已缓存的模型
            cached_models = list(cache_dir.glob(f"**/{model_pattern}"))

            if not cached_models:
                # 模型未缓存，需要下载
                self.text_extracted.emit(
                    f"📥 {AppConstants.AUDIO_EXTRACT_MSG_FIRST_RUN}"
                )
                self.text_extracted.emit(
                    f"🔄 {AppConstants.AUDIO_EXTRACT_MSG_DOWNLOADING}"
                )
                self.progress_updated.emit(10)

            device = (
                AppConstants.AUDIO_EXTRACT_DEVICE_CUDA
                if self.is_cuda_available()
                else AppConstants.AUDIO_EXTRACT_DEVICE_CPU
            )
            compute_type = (
                AppConstants.AUDIO_EXTRACT_COMPUTE_TYPE_CUDA
                if device == AppConstants.AUDIO_EXTRACT_DEVICE_CUDA
                else AppConstants.AUDIO_EXTRACT_COMPUTE_TYPE_CPU
            )

            # 创建模型实例（如果需要会自动下载）
            model = WhisperModel(
                model_name,
                device=device,
                compute_type=compute_type,
                download_root=os.path.expanduser(AppConstants.AUDIO_EXTRACT_CACHE_DIR),
            )

            if not cached_models:
                self.text_extracted.emit(
                    f"✅ {AppConstants.AUDIO_EXTRACT_MSG_DOWNLOAD_COMPLETE}"
                )
                self.progress_updated.emit(20)

            return model
        except Exception as e:
            print(f"{AppConstants.AUDIO_EXTRACT_ERROR_MODEL_LOAD_FAILED}: {e}")
            # 可以尝试重新下载或使用其他模型
            return None

    def run(self):
        """执行音频转文字任务"""
        try:

            # 更新进度
            self.progress_updated.emit(AppConstants.AUDIO_EXTRACT_PROGRESS_MODEL_LOADED)

            # 加载模型
            model = self.ensure_model_downloaded(self.model_name)
            if not model:
                raise Exception(
                    AppConstants.AUDIO_EXTRACT_ERROR_MODEL_NOT_FOUND.format(
                        model_name=self.model_name
                    )
                )
            # 更新进度
            self.progress_updated.emit(AppConstants.AUDIO_EXTRACT_PROGRESS_FILE_CHECKED)

            # 检查音频文件是否存在
            if not os.path.exists(self.audio_file_path):
                raise FileNotFoundError(
                    AppConstants.AUDIO_EXTRACT_ERROR_FILE_NOT_FOUND.format(
                        file_path=self.audio_file_path
                    )
                )

            print(
                AppConstants.AUDIO_EXTRACT_LOG_START_TRANSCRIPTION, self.audio_file_path
            )

            # 转录音频
            try:
                segments, info = model.transcribe(self.audio_file_path)
                # 将所有段落的文本合并
                text_segments = []
                for segment in segments:
                    text_segments.append(segment.text)
                text = AppConstants.AUDIO_EXTRACT_TEXT_JOIN_SEPARATOR.join(
                    text_segments
                )
            except Exception as e:
                print(
                    AppConstants.AUDIO_EXTRACT_ERROR_TRANSCRIPTION_FAILED.format(
                        error=str(e)
                    )
                )
                raise Exception(
                    AppConstants.AUDIO_EXTRACT_ERROR_TRANSCRIPTION_FAILED.format(
                        error=str(e)
                    )
                )
            self.progress_updated.emit(
                AppConstants.AUDIO_EXTRACT_PROGRESS_TRANSCRIPTION_DONE
            )

            self.progress_updated.emit(AppConstants.AUDIO_EXTRACT_PROGRESS_COMPLETE)

            # 发送结果
            self.text_extracted.emit(text)

        except ImportError:
            self.error_occurred.emit(AppConstants.AUDIO_EXTRACT_ERROR_INSTALL_LIBRARY)
        except Exception as e:
            print(AppConstants.AUDIO_EXTRACT_LOG_EXCEPTION, e)
            self.error_occurred.emit(
                AppConstants.AUDIO_EXTRACT_ERROR_GENERAL.format(error=str(e))
            )
