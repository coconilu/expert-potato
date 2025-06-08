"""视频音频提取工具模块"""

import os
import tempfile
from pathlib import Path
from typing import Optional
from PyQt6.QtCore import QThread, pyqtSignal
from config.core import AppConstants


class VideoAudioExtractor(QThread):
    """视频音频提取器"""
    
    progress_updated = pyqtSignal(int)
    extraction_completed = pyqtSignal(str)  # 提取完成，返回音频文件路径
    error_occurred = pyqtSignal(str)
    
    def __init__(self, video_file_path: str, temp_dir: Optional[str] = None):
        super().__init__()
        self.video_file_path = video_file_path
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.output_audio_path = None
        
    def get_supported_video_extensions(self) -> list:
        """获取支持的视频文件扩展名"""
        return AppConstants.SUPPORTED_VIDEO_EXTENSIONS
        
    def is_video_file(self, file_path: str) -> bool:
        """检查是否为支持的视频文件"""
        file_ext = Path(file_path).suffix.lower()
        return file_ext in self.get_supported_video_extensions()
        
    def generate_output_path(self) -> str:
        """生成输出音频文件路径"""
        video_name = Path(self.video_file_path).stem
        output_filename = f"{video_name}_extracted_audio.wav"
        return os.path.join(self.temp_dir, output_filename)
        
    def extract_with_ffmpeg(self) -> bool:
        """使用 FFmpeg 提取音频"""
        try:
            import subprocess
            
            self.output_audio_path = self.generate_output_path()
            
            # FFmpeg 命令
            cmd = [
                'ffmpeg',
                '-i', self.video_file_path,
                '-vn',  # 不包含视频
                '-acodec', 'pcm_s16le',  # 音频编码
                '-ar', '16000',  # 采样率
                '-ac', '1',  # 单声道
                '-y',  # 覆盖输出文件
                self.output_audio_path
            ]
            
            self.progress_updated.emit(30)
            
            # 执行 FFmpeg 命令
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=AppConstants.VIDEO_EXTRACT_TIMEOUT
            )
            
            self.progress_updated.emit(80)
            
            if result.returncode == 0:
                return True
            else:
                self.error_occurred.emit(f"FFmpeg 错误: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.error_occurred.emit("视频处理超时")
            return False
        except FileNotFoundError:
            self.error_occurred.emit("未找到 FFmpeg，请确保已安装 FFmpeg")
            return False
        except Exception as e:
            self.error_occurred.emit(f"音频提取失败: {str(e)}")
            return False
            
    def extract_with_moviepy(self) -> bool:
        """使用 MoviePy 提取音频（备用方案）"""
        try:
            from moviepy.editor import VideoFileClip
            
            self.output_audio_path = self.generate_output_path()
            
            self.progress_updated.emit(20)
            
            # 加载视频文件
            video = VideoFileClip(self.video_file_path)
            
            self.progress_updated.emit(50)
            
            # 提取音频
            audio = video.audio
            if audio is None:
                self.error_occurred.emit("视频文件中没有音频轨道")
                return False
                
            self.progress_updated.emit(70)
            
            # 保存音频文件
            audio.write_audiofile(
                self.output_audio_path,
                verbose=False,
                logger=None
            )
            
            # 清理资源
            audio.close()
            video.close()
            
            self.progress_updated.emit(90)
            return True
            
        except ImportError:
            self.error_occurred.emit("未安装 MoviePy 库，请安装: pip install moviepy")
            return False
        except Exception as e:
            self.error_occurred.emit(f"MoviePy 音频提取失败: {str(e)}")
            return False
            
    def run(self):
        """执行音频提取任务"""
        try:
            self.progress_updated.emit(10)
            
            # 检查输入文件是否存在
            if not os.path.exists(self.video_file_path):
                self.error_occurred.emit(f"视频文件不存在: {self.video_file_path}")
                return
                
            # 检查是否为支持的视频文件
            if not self.is_video_file(self.video_file_path):
                self.error_occurred.emit("不支持的视频文件格式")
                return
                
            # 确保临时目录存在
            os.makedirs(self.temp_dir, exist_ok=True)
            
            # 优先尝试使用 FFmpeg
            success = self.extract_with_ffmpeg()
            
            # 如果 FFmpeg 失败，尝试使用 MoviePy
            if not success:
                success = self.extract_with_moviepy()
                
            if success and self.output_audio_path and os.path.exists(self.output_audio_path):
                self.progress_updated.emit(100)
                self.extraction_completed.emit(self.output_audio_path)
            else:
                self.error_occurred.emit("音频提取失败")
                
        except Exception as e:
            self.error_occurred.emit(f"视频处理过程中发生错误: {str(e)}")
            
    def cleanup(self):
        """清理临时文件"""
        if self.output_audio_path and os.path.exists(self.output_audio_path):
            try:
                os.remove(self.output_audio_path)
            except Exception:
                pass  # 忽略清理错误