"""
音频项目管理系统
用于管理声音克隆项目的文件结构、数据存储和项目生命周期
"""

import os
import json
import uuid
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict

@dataclass
class ProjectMetadata:
    """项目元数据"""
    id: str
    name: str
    created_at: str
    updated_at: str
    original_audio: str
    audio_duration: float = 0.0
    sample_rate: int = 0
    speakers_count: int = 0
    status: str = "created"  # created, analyzing, analyzed, processing, completed
    target_language: str = "zh"

class AudioProjectManager:
    """音频项目管理器"""
    
    def __init__(self, workspace_dir: Optional[str] = None):
        """
        初始化项目管理器
        
        Args:
            workspace_dir: 工作空间目录，默认为用户目录下的.expert-potato/projects
        """
        if workspace_dir is None:
            workspace_dir = os.path.join(
                os.path.expanduser("~"), 
                ".expert-potato", 
                "projects"
            )
        
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
    def create_project(self, name: str, audio_file: str) -> str:
        """
        创建新项目
        
        Args:
            name: 项目名称
            audio_file: 原始音频文件路径
            
        Returns:
            项目ID
        """
        project_id = str(uuid.uuid4())
        project_dir = self.workspace_dir / project_id
        
        # 创建项目目录结构
        project_dir.mkdir(exist_ok=True)
        (project_dir / "speakers").mkdir(exist_ok=True)
        (project_dir / "transcripts").mkdir(exist_ok=True)
        (project_dir / "outputs").mkdir(exist_ok=True)
        
        # 复制原始音频
        audio_path = Path(audio_file)
        if audio_path.exists():
            dest_audio = project_dir / f"original_audio{audio_path.suffix}"
            shutil.copy2(audio_file, dest_audio)
            
            # 创建项目元数据
            metadata = ProjectMetadata(
                id=project_id,
                name=name,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                original_audio=dest_audio.name
            )
            
            # 保存元数据
            self._save_metadata(project_id, metadata)
            
            return project_id
        else:
            raise FileNotFoundError(f"音频文件不存在: {audio_file}")
            
    def get_project(self, project_id: str) -> Optional[ProjectMetadata]:
        """
        获取项目信息
        
        Args:
            project_id: 项目ID
            
        Returns:
            项目元数据，如果不存在返回None
        """
        metadata_file = self.workspace_dir / project_id / "metadata.json"
        
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return ProjectMetadata(**data)
        
        return None
        
    def update_project(self, project_id: str, **kwargs) -> bool:
        """
        更新项目信息
        
        Args:
            project_id: 项目ID
            **kwargs: 要更新的字段
            
        Returns:
            是否更新成功
        """
        metadata = self.get_project(project_id)
        if metadata:
            # 更新字段
            for key, value in kwargs.items():
                if hasattr(metadata, key):
                    setattr(metadata, key, value)
                    
            metadata.updated_at = datetime.now().isoformat()
            
            # 保存更新
            self._save_metadata(project_id, metadata)
            return True
            
        return False
        
    def list_projects(self) -> List[ProjectMetadata]:
        """
        列出所有项目
        
        Returns:
            项目列表
        """
        projects = []
        
        for project_dir in self.workspace_dir.iterdir():
            if project_dir.is_dir():
                metadata = self.get_project(project_dir.name)
                if metadata:
                    projects.append(metadata)
                    
        # 按更新时间排序
        projects.sort(key=lambda x: x.updated_at, reverse=True)
        
        return projects
        
    def delete_project(self, project_id: str) -> bool:
        """
        删除项目
        
        Args:
            project_id: 项目ID
            
        Returns:
            是否删除成功
        """
        project_dir = self.workspace_dir / project_id
        
        if project_dir.exists():
            shutil.rmtree(project_dir)
            return True
            
        return False
        
    def get_project_dir(self, project_id: str) -> Path:
        """
        获取项目目录路径
        
        Args:
            project_id: 项目ID
            
        Returns:
            项目目录路径
        """
        return self.workspace_dir / project_id
        
    def get_audio_path(self, project_id: str) -> Optional[Path]:
        """
        获取原始音频文件路径
        
        Args:
            project_id: 项目ID
            
        Returns:
            音频文件路径，如果不存在返回None
        """
        metadata = self.get_project(project_id)
        if metadata:
            audio_path = self.get_project_dir(project_id) / metadata.original_audio
            if audio_path.exists():
                return audio_path
                
        return None
        
    def get_speakers_dir(self, project_id: str) -> Path:
        """
        获取说话人目录路径
        
        Args:
            project_id: 项目ID
            
        Returns:
            说话人目录路径
        """
        return self.get_project_dir(project_id) / "speakers"
        
    def create_speaker_dir(self, project_id: str, speaker_id: str) -> Path:
        """
        创建说话人目录
        
        Args:
            project_id: 项目ID
            speaker_id: 说话人ID
            
        Returns:
            说话人目录路径
        """
        speaker_dir = self.get_speakers_dir(project_id) / speaker_id
        speaker_dir.mkdir(exist_ok=True)
        (speaker_dir / "samples").mkdir(exist_ok=True)
        (speaker_dir / "model").mkdir(exist_ok=True)
        
        return speaker_dir
        
    def save_speaker_metadata(self, project_id: str, speaker_id: str, metadata: Dict[str, Any]):
        """
        保存说话人元数据
        
        Args:
            project_id: 项目ID
            speaker_id: 说话人ID
            metadata: 元数据字典
        """
        speaker_dir = self.get_speakers_dir(project_id) / speaker_id
        metadata_file = speaker_dir / "metadata.json"
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
            
    def get_speaker_metadata(self, project_id: str, speaker_id: str) -> Optional[Dict[str, Any]]:
        """
        获取说话人元数据
        
        Args:
            project_id: 项目ID
            speaker_id: 说话人ID
            
        Returns:
            元数据字典，如果不存在返回None
        """
        metadata_file = self.get_speakers_dir(project_id) / speaker_id / "metadata.json"
        
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        return None
        
    def _save_metadata(self, project_id: str, metadata: ProjectMetadata):
        """
        保存项目元数据
        
        Args:
            project_id: 项目ID
            metadata: 项目元数据
        """
        metadata_file = self.workspace_dir / project_id / "metadata.json"
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(metadata), f, ensure_ascii=False, indent=2)
            
    def export_project(self, project_id: str, export_path: str) -> bool:
        """
        导出项目为压缩包
        
        Args:
            project_id: 项目ID
            export_path: 导出路径
            
        Returns:
            是否导出成功
        """
        project_dir = self.get_project_dir(project_id)
        
        if project_dir.exists():
            # 创建压缩包
            shutil.make_archive(
                export_path.replace('.zip', ''), 
                'zip', 
                project_dir
            )
            return True
            
        return False
        
    def import_project(self, archive_path: str) -> Optional[str]:
        """
        从压缩包导入项目
        
        Args:
            archive_path: 压缩包路径
            
        Returns:
            导入的项目ID，失败返回None
        """
        if not os.path.exists(archive_path):
            return None
            
        # 生成新的项目ID
        new_project_id = str(uuid.uuid4())
        project_dir = self.workspace_dir / new_project_id
        
        try:
            # 解压到新项目目录
            shutil.unpack_archive(archive_path, project_dir)
            
            # 更新项目ID
            metadata = self.get_project(new_project_id)
            if metadata:
                metadata.id = new_project_id
                metadata.updated_at = datetime.now().isoformat()
                self._save_metadata(new_project_id, metadata)
                
                return new_project_id
                
        except Exception as e:
            # 清理失败的导入
            if project_dir.exists():
                shutil.rmtree(project_dir)
            raise e
            
        return None 