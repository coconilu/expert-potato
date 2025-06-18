"""音频提取工作线程模块"""

import os
import tempfile
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal
from config.core import AppConstants


class AudioExtractWorker(QThread):
    """音频提取工作线程"""

    progress_updated = pyqtSignal(int)
    text_extracted = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(
        self, audio_file_path: str, model_name: str = "base", output_format: str = "txt"
    ):
        super().__init__()
        self.audio_file_path = audio_file_path
        self.model_name = model_name
        self.output_format = output_format
        self.temp_txt_dir = None
        self.output_file_path = None

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

                # 根据输出格式生成不同的内容
                if self.output_format == AppConstants.OUTPUT_FORMAT_TXT:
                    # 纯文本格式
                    text_segments = []
                    for segment in segments:
                        print("txt format: ", segment.text)
                        text_segments.append(segment.text)
                    text = AppConstants.AUDIO_EXTRACT_TEXT_JOIN_SEPARATOR.join(
                        text_segments
                    )
                elif self.output_format == AppConstants.OUTPUT_FORMAT_SRT:
                    # SRT字幕格式
                    text = self._generate_srt_format(segments)
                elif self.output_format == AppConstants.OUTPUT_FORMAT_VTT:
                    # VTT字幕格式
                    text = self._generate_vtt_format(segments)
                else:
                    # 默认使用纯文本格式
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

            print("txt result len: ", len(text))

            # 保存文本到临时文件
            self._save_text_to_file(text)

            # 发送结果
            self.text_extracted.emit(text)

        except ImportError:
            self.error_occurred.emit(AppConstants.AUDIO_EXTRACT_ERROR_INSTALL_LIBRARY)
        except Exception as e:
            print(AppConstants.AUDIO_EXTRACT_LOG_EXCEPTION, e)
            self.error_occurred.emit(
                AppConstants.AUDIO_EXTRACT_ERROR_GENERAL.format(error=str(e))
            )

    def _generate_srt_format(self, segments):
        """生成SRT格式的字幕"""
        srt_content = []
        for i, segment in enumerate(segments, 1):
            start_time = self._format_timestamp_srt(segment.start)
            end_time = self._format_timestamp_srt(segment.end)
            srt_content.append(f"{i}")
            srt_content.append(f"{start_time} --> {end_time}")
            srt_content.append(segment.text.strip())
            srt_content.append("")  # 空行分隔
        return "\n".join(srt_content)

    def _generate_vtt_format(self, segments):
        """生成VTT格式的字幕"""
        vtt_content = ["WEBVTT", ""]  # VTT文件头
        for segment in segments:
            start_time = self._format_timestamp_vtt(segment.start)
            end_time = self._format_timestamp_vtt(segment.end)
            vtt_content.append(f"{start_time} --> {end_time}")
            vtt_content.append(segment.text.strip())
            vtt_content.append("")  # 空行分隔
        return "\n".join(vtt_content)

    def _ensure_temp_txt_dir(self):
        """确保TXT输出临时文件夹存在"""
        if not self.temp_txt_dir:
            self.temp_txt_dir = os.path.join(
                tempfile.gettempdir(), AppConstants.TXT_OUTPUT_TEMP_DIR
            )
            os.makedirs(self.temp_txt_dir, exist_ok=True)

    def _save_text_to_file(self, text: str):
        """将文本保存到临时文件"""
        try:
            self._ensure_temp_txt_dir()

            # 获取音频文件名（不含扩展名）
            audio_filename = Path(self.audio_file_path).stem

            # 根据输出格式确定文件扩展名
            if self.output_format == AppConstants.OUTPUT_FORMAT_SRT:
                file_extension = ".srt"
            elif self.output_format == AppConstants.OUTPUT_FORMAT_VTT:
                file_extension = ".vtt"
            else:
                file_extension = ".txt"

            # 构建输出文件路径
            output_filename = f"{audio_filename}{file_extension}"
            self.output_file_path = os.path.join(self.temp_txt_dir, output_filename)

            # 保存文件
            with open(self.output_file_path, "w", encoding="utf-8") as f:
                f.write(text)

            print(f"文本已保存到: {self.output_file_path}")

        except Exception as e:
            print(f"保存文本文件失败: {str(e)}")
            self.output_file_path = None

    def _format_timestamp_srt(self, seconds):
        """格式化时间戳为SRT格式 (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

    def _format_timestamp_vtt(self, seconds):
        """格式化时间戳为VTT格式 (HH:MM:SS.mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"
