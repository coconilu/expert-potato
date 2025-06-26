"""
音频分析页面
用于分析音频中的不同说话人，并展示分析结果
"""

import os
from typing import Optional, List, Dict, Any
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QProgressBar,
    QGridLayout, QFrame, QScrollArea
)
from PyQt6.QtGui import QShowEvent
from qfluentwidgets import (
    FluentIcon as FIF, PrimaryPushButton, PushButton,
    ProgressBar, InfoBar, InfoBarPosition,
    CardWidget, BodyLabel, SubtitleLabel,
    TitleLabel, CaptionLabel, IconWidget,
    FlowLayout, MessageBox
)

from config.core import Messages
from core.project_manager import AudioProjectManager
from pages.components.file_drop_area import FileDropArea
from core import get_state_manager


class SpeakerCard(CardWidget):
    """说话人卡片组件"""
    
    clicked = pyqtSignal(str)  # 点击信号，传递说话人ID
    
    def __init__(self, speaker_id: str, speaker_info: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.speaker_id = speaker_id
        self.speaker_info = speaker_info
        self._setupUi()
        
    def _setupUi(self):
        """设置UI"""
        self.setFixedHeight(150)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # 顶部信息
        top_layout = QHBoxLayout()
        top_layout.setSpacing(12)
        
        # 说话人图标
        icon_widget = IconWidget(FIF.PEOPLE, self)
        icon_widget.setFixedSize(48, 48)
        top_layout.addWidget(icon_widget)
        
        # 说话人信息
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        # 标签
        self.label_text = SubtitleLabel(self.speaker_info.get('label', f'Speaker {self.speaker_id}'))
        info_layout.addWidget(self.label_text)
        
        # 性别
        gender = self.speaker_info.get('gender', 'unknown')
        gender_text = '男性' if gender == 'male' else '女性' if gender == 'female' else '未知'
        self.gender_label = CaptionLabel(f'性别: {gender_text}')
        info_layout.addWidget(self.gender_label)
        
        top_layout.addLayout(info_layout)
        top_layout.addStretch()
        
        layout.addLayout(top_layout)
        
        # 统计信息
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        # 时长
        duration = self.speaker_info.get('total_duration', 0)
        duration_text = f"{int(duration // 60)}:{int(duration % 60):02d}"
        self.duration_label = BodyLabel(f'总时长: {duration_text}')
        stats_layout.addWidget(self.duration_label)
        
        # 片段数
        segments = self.speaker_info.get('segments_count', 0)
        self.segments_label = BodyLabel(f'片段数: {segments}')
        stats_layout.addWidget(self.segments_label)
        
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        self.play_button = PushButton("试听", self, FIF.PLAY)
        self.play_button.clicked.connect(self._onPlayClicked)
        button_layout.addWidget(self.play_button)
        
        self.train_button = PrimaryPushButton("训练模型", self, FIF.DEVELOPER_TOOLS)
        self.train_button.clicked.connect(self._onTrainClicked)
        button_layout.addWidget(self.train_button)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
    def _onPlayClicked(self):
        """试听按钮点击"""
        # TODO: 实现试听功能
        InfoBar.info(
            title="功能开发中",
            content="试听功能即将推出",
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self.parent()
        )
        
    def _onTrainClicked(self):
        """训练模型按钮点击"""
        self.clicked.emit(self.speaker_id)
        
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.speaker_id)


class AudioAnalysisPage(QWidget):
    """音频分析页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AudioAnalysisPage")
        self.project_manager = AudioProjectManager()
        self.state_manager = get_state_manager()
        self.current_project_id = None
        self.current_file_path = None
        self.speakers = {}
        self._setupUi()
        
    def _setupUi(self):
        """设置UI"""
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 20, 36, 20)
        layout.setSpacing(20)
        
        # 标题
        self.title_label = TitleLabel("音频角色分析")
        layout.addWidget(self.title_label)
        
        # 文件选择区域
        self.file_drop_area = FileDropArea()
        self.file_drop_area.file_dropped.connect(self.on_file_selected)
        layout.addWidget(self.file_drop_area)
        
        # 项目信息卡片
        self.info_card = CardWidget()
        info_layout = QVBoxLayout(self.info_card)
        info_layout.setContentsMargins(20, 20, 20, 20)
        info_layout.setSpacing(12)
        
        # 项目名称
        self.project_name_label = SubtitleLabel("项目名称: -")
        info_layout.addWidget(self.project_name_label)
        
        # 音频信息
        audio_info_layout = QHBoxLayout()
        audio_info_layout.setSpacing(30)
        
        self.duration_label = BodyLabel("时长: -")
        audio_info_layout.addWidget(self.duration_label)
        
        self.sample_rate_label = BodyLabel("采样率: -")
        audio_info_layout.addWidget(self.sample_rate_label)
        
        self.speakers_count_label = BodyLabel("说话人数: -")
        audio_info_layout.addWidget(self.speakers_count_label)
        
        audio_info_layout.addStretch()
        
        info_layout.addLayout(audio_info_layout)
        
        layout.addWidget(self.info_card)
        
        # 分析进度区域
        self.progress_widget = QWidget()
        progress_layout = QVBoxLayout(self.progress_widget)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(8)
        
        self.progress_label = BodyLabel("准备分析...")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = ProgressBar()
        self.progress_bar.setRange(0, 100)
        progress_layout.addWidget(self.progress_bar)
        
        layout.addWidget(self.progress_widget)
        
        # 分析结果区域
        self.result_widget = QWidget()
        self.result_widget.setVisible(False)
        result_layout = QVBoxLayout(self.result_widget)
        result_layout.setContentsMargins(0, 0, 0, 0)
        result_layout.setSpacing(16)
        
        # 结果标题
        result_title_layout = QHBoxLayout()
        result_title_layout.setSpacing(12)
        
        self.result_title = SubtitleLabel("识别到的说话人")
        result_title_layout.addWidget(self.result_title)
        
        result_title_layout.addStretch()
        
        # 刷新按钮
        self.refresh_button = PushButton("重新分析", self, FIF.SYNC)
        self.refresh_button.clicked.connect(self._onRefreshClicked)
        result_title_layout.addWidget(self.refresh_button)
        
        result_layout.addLayout(result_title_layout)
        
        # 说话人卡片容器
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        self.speakers_container = QWidget()
        self.speakers_layout = FlowLayout(self.speakers_container)
        self.speakers_layout.setSpacing(16)
        
        scroll_area.setWidget(self.speakers_container)
        result_layout.addWidget(scroll_area)
        
        layout.addWidget(self.result_widget)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        self.analyze_button = PrimaryPushButton("开始分析", self, FIF.PLAY)
        self.analyze_button.clicked.connect(self._onAnalyzeClicked)
        button_layout.addWidget(self.analyze_button)
        
        self.next_button = PrimaryPushButton("下一步：声音克隆", self, FIF.MICROPHONE)
        self.next_button.clicked.connect(self._onNextClicked)
        self.next_button.setEnabled(False)
        button_layout.addWidget(self.next_button)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        layout.addStretch()
        
    def on_file_selected(self, file_path: str):
        """文件选择事件处理"""
        self.current_file_path = file_path
        
        # 创建一个临时项目来管理这个音频文件
        import os
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        project_name = f"Audio_Analysis_{file_name}"
        
        # 这里可以创建项目或直接使用文件路径
        # 暂时直接更新UI显示
        self.project_name_label.setText(f"音频文件: {os.path.basename(file_path)}")
        
        # 获取音频文件信息并更新UI
        try:
            # 优先使用 soundfile，避免 librosa 的警告
            import soundfile as sf
            import os
            
            # 使用 soundfile 获取基本信息
            info = sf.info(file_path)
            duration = info.frames / info.samplerate
            sr = info.samplerate
            
            duration_text = f"{int(duration // 60)}:{int(duration % 60):02d}"
            self.duration_label.setText(f"时长: {duration_text}")
            self.sample_rate_label.setText(f"采样率: {sr} Hz")
            self.speakers_count_label.setText("说话人数: 待分析")
            
        except ImportError:
            # 如果没有soundfile，回退到基本文件信息
            try:
                import os
                file_size = os.path.getsize(file_path)
                size_mb = file_size / (1024 * 1024)
                self.duration_label.setText(f"文件大小: {size_mb:.1f} MB")
                self.sample_rate_label.setText("采样率: 未知") 
                self.speakers_count_label.setText("说话人数: 待分析")
            except Exception:
                self.duration_label.setText("时长: 未知")
                self.sample_rate_label.setText("采样率: 未知") 
                self.speakers_count_label.setText("说话人数: 待分析")
        except Exception as e:
            # 如果soundfile也失败，尝试使用librosa（但会有警告）
            try:
                import librosa
                import warnings
                # 临时抑制 librosa 的警告
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", FutureWarning)
                    warnings.simplefilter("ignore", UserWarning)
                    duration = librosa.get_duration(path=file_path)
                    y, sr = librosa.load(file_path, sr=None)
                
                duration_text = f"{int(duration // 60)}:{int(duration % 60):02d}"
                self.duration_label.setText(f"时长: {duration_text}")
                self.sample_rate_label.setText(f"采样率: {sr} Hz")
                self.speakers_count_label.setText("说话人数: 待分析")
            except Exception:
                self.duration_label.setText("时长: 获取失败")
                self.sample_rate_label.setText("采样率: 获取失败")
                self.speakers_count_label.setText("说话人数: 待分析")
            
        # 重置UI状态
        self.result_widget.setVisible(False)
        self.progress_widget.setVisible(True)
        self.analyze_button.setEnabled(True)
        self.next_button.setEnabled(False)
        
        InfoBar.success(
            title="文件加载成功",
            content=f"已加载音频文件: {os.path.basename(file_path)}",
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )
        
    def set_file_path(self, file_path: str):
        """设置文件路径（用于从其他页面跳转）"""
        if file_path and os.path.exists(file_path):
            self.on_file_selected(file_path)
            
    def showEvent(self, event: QShowEvent):
        """页面显示事件处理"""
        super().showEvent(event)
        
        # 检查状态管理器中是否有文件路径，且当前页面没有设置文件
        current_state_file_path, _ = self.state_manager.get_file_info()
        
        # 如果状态管理器中有文件路径，且当前页面没有设置文件，则自动设置
        if (current_state_file_path and 
            os.path.exists(current_state_file_path) and 
            not self.current_file_path):
            self.set_file_path(current_state_file_path)
        
    def loadProject(self, project_id: str):
        """
        加载项目
        
        Args:
            project_id: 项目ID
        """
        self.current_project_id = project_id
        metadata = self.project_manager.get_project(project_id)
        
        if metadata:
            # 更新项目信息
            self.project_name_label.setText(f"项目名称: {metadata.name}")
            
            # 更新音频信息
            duration = metadata.audio_duration
            if duration > 0:
                duration_text = f"{int(duration // 60)}:{int(duration % 60):02d}"
                self.duration_label.setText(f"时长: {duration_text}")
            
            if metadata.sample_rate > 0:
                self.sample_rate_label.setText(f"采样率: {metadata.sample_rate} Hz")
                
            if metadata.speakers_count > 0:
                self.speakers_count_label.setText(f"说话人数: {metadata.speakers_count}")
                
            # 检查是否已经分析过
            if metadata.status == "analyzed" and metadata.speakers_count > 0:
                self._loadSpeakers()
                self.progress_widget.setVisible(False)
                self.result_widget.setVisible(True)
                self.analyze_button.setEnabled(False)
                self.next_button.setEnabled(True)
                
    def _loadSpeakers(self):
        """加载说话人信息"""
        # 清空现有卡片
        for i in reversed(range(self.speakers_layout.count())):
            widget = self.speakers_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
                
        # 如果有项目ID，从项目管理器加载数据
        if self.current_project_id:
            try:
                speakers_dir = self.project_manager.get_speakers_dir(self.current_project_id)
                
                for speaker_dir in speakers_dir.iterdir():
                    if speaker_dir.is_dir():
                        speaker_id = speaker_dir.name
                        metadata = self.project_manager.get_speaker_metadata(
                            self.current_project_id, 
                            speaker_id
                        )
                        
                        if metadata:
                            # 创建说话人卡片
                            card = SpeakerCard(speaker_id, metadata)
                            card.clicked.connect(self._onSpeakerClicked)
                            self.speakers_layout.addWidget(card)
                            
                            self.speakers[speaker_id] = metadata
            except Exception as e:
                print(f"从项目加载说话人数据失败: {e}")
                
        # 如果没有项目ID或从项目加载失败，使用内存中的数据
        if hasattr(self, 'speakers') and self.speakers:
            for speaker_id, speaker_info in self.speakers.items():
                # 创建说话人卡片
                card = SpeakerCard(speaker_id, speaker_info)
                card.clicked.connect(self._onSpeakerClicked)
                self.speakers_layout.addWidget(card)
                    
    def _onAnalyzeClicked(self):
        """开始分析按钮点击"""
        if not self.current_project_id and not self.current_file_path:
            InfoBar.warning(
                title="无音频文件",
                content="请先选择音频文件或加载项目",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return
            
        # 如果没有项目ID，创建一个新项目
        if not self.current_project_id and self.current_file_path:
            try:
                import os
                file_name = os.path.splitext(os.path.basename(self.current_file_path))[0]
                project_name = f"音频分析_{file_name}"
                
                # 创建项目
                self.current_project_id = self.project_manager.create_project(
                    project_name, 
                    self.current_file_path
                )
                
                # 更新项目名称显示
                self.project_name_label.setText(f"项目名称: {project_name}")
                
                InfoBar.success(
                    title="项目创建成功",
                    content=f"已创建项目: {project_name}",
                    orient=Qt.Orientation.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
                
            except Exception as e:
                InfoBar.error(
                    title="项目创建失败",
                    content=f"无法创建项目: {str(e)}",
                    orient=Qt.Orientation.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                return
            
        # 显示进度
        self.progress_widget.setVisible(True)
        self.result_widget.setVisible(False)
        self.analyze_button.setEnabled(False)
        
        # TODO: 启动分析线程
        self._startAnalysis()
        
    def _startAnalysis(self):
        """启动分析"""
        # 模拟分析过程
        self.progress_label.setText("正在分析音频...")
        self.progress_bar.setValue(0)
        
        # 使用定时器模拟进度
        self.timer = QTimer()
        self.timer.timeout.connect(self._updateProgress)
        self.timer.start(100)
        
    def _updateProgress(self):
        """更新进度"""
        value = self.progress_bar.value()
        if value < 100:
            self.progress_bar.setValue(value + 2)
        else:
            self.timer.stop()
            self._onAnalysisComplete()
            
    def _onAnalysisComplete(self):
        """分析完成"""
        # 模拟分析结果
        mock_speakers = {
            "speaker_1": {
                "label": "Man1",
                "gender": "male",
                "total_duration": 125.5,
                "segments_count": 15
            },
            "speaker_2": {
                "label": "Woman1", 
                "gender": "female",
                "total_duration": 198.3,
                "segments_count": 23
            }
        }
        
        # 保存说话人数据（只有当项目ID存在时）
        if self.current_project_id:
            try:
                for speaker_id, speaker_info in mock_speakers.items():
                    self.project_manager.create_speaker_dir(self.current_project_id, speaker_id)
                    self.project_manager.save_speaker_metadata(
                        self.current_project_id,
                        speaker_id,
                        speaker_info
                    )
                    
                # 更新项目状态
                self.project_manager.update_project(
                    self.current_project_id,
                    status="analyzed",
                    speakers_count=len(mock_speakers)
                )
                
                # 更新说话人计数显示
                self.speakers_count_label.setText(f"说话人数: {len(mock_speakers)}")
                
            except Exception as e:
                InfoBar.error(
                    title="保存失败",
                    content=f"无法保存分析结果: {str(e)}",
                    orient=Qt.Orientation.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                # 即使保存失败，也继续显示结果
        
        # 保存到实例变量以供显示使用
        self.speakers = mock_speakers
        
        # 显示结果
        self._loadSpeakers()
        self.progress_widget.setVisible(False)
        self.result_widget.setVisible(True)
        self.analyze_button.setEnabled(False)
        self.next_button.setEnabled(True)
        
        InfoBar.success(
            title="分析完成",
            content=f"成功识别到 {len(mock_speakers)} 个说话人",
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )
        
    def _onRefreshClicked(self):
        """重新分析"""
        reply = MessageBox.question(
            self,
            "重新分析",
            "确定要重新分析吗？这将覆盖现有的分析结果。",
            MessageBox.Yes | MessageBox.No
        )
        
        if reply == MessageBox.Yes:
            self.analyze_button.setEnabled(True)
            self._onAnalyzeClicked()
            
    def _onSpeakerClicked(self, speaker_id: str):
        """说话人卡片点击"""
        speaker_info = self.speakers.get(speaker_id)
        if speaker_info:
                    InfoBar.info(
            title=f"{speaker_info.get('label', speaker_id)}",
            content="即将进入声音克隆页面",
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )
            
    def _onNextClicked(self):
        """下一步按钮点击"""
        # TODO: 跳转到声音克隆页面
        InfoBar.info(
            title="功能开发中",
            content="声音克隆功能即将推出",
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        ) 