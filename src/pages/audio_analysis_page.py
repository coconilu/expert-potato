"""
音频分析页面
用于分析音频中的不同说话人，并展示分析结果
"""

from typing import Optional, List, Dict, Any
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QProgressBar,
    QGridLayout, QFrame, QScrollArea
)
from qfluentwidgets import (
    FluentIcon as FIF, PrimaryPushButton, PushButton,
    ProgressBar, InfoBar, InfoBarPosition,
    CardWidget, BodyLabel, SubtitleLabel,
    TitleLabel, CaptionLabel, IconWidget,
    FlowLayout, MessageBox
)

from config.core import Messages
from core.project_manager import AudioProjectManager


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
        self.setCursor(Qt.PointingHandCursor)
        
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
            orient=Qt.Horizontal,
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
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.speaker_id)


class AudioAnalysisPage(QWidget):
    """音频分析页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AudioAnalysisPage")
        self.project_manager = AudioProjectManager()
        self.current_project_id = None
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
        if not self.current_project_id:
            return
            
        # 清空现有卡片
        for i in reversed(range(self.speakers_layout.count())):
            widget = self.speakers_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
                
        # 加载说话人数据
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
                    
    def _onAnalyzeClicked(self):
        """开始分析按钮点击"""
        if not self.current_project_id:
            InfoBar.warning(
                title="无项目",
                content="请先创建或加载项目",
                orient=Qt.Horizontal,
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
        
        # 保存说话人数据
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
        
        # 显示结果
        self._loadSpeakers()
        self.progress_widget.setVisible(False)
        self.result_widget.setVisible(True)
        self.analyze_button.setEnabled(False)
        self.next_button.setEnabled(True)
        
        InfoBar.success(
            title="分析完成",
            content=f"成功识别到 {len(mock_speakers)} 个说话人",
            orient=Qt.Horizontal,
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
                orient=Qt.Horizontal,
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
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        ) 