import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from qfluentwidgets import (
    NavigationInterface, NavigationItemPosition, FluentIcon,
    setTheme, Theme, setThemeColor, qconfig
)


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("音视频处理工具")
        self.setGeometry(100, 100, 1200, 800)
        
        # 设置主题
        setTheme(Theme.DARK)
        setThemeColor('#009faa')
        
        # 创建主布局
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局（水平布局）
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建侧边栏导航
        self.navigation = NavigationInterface(self, showMenuButton=True)
        self.navigation.setExpandWidth(200)
        
        # 添加导航项
        self.add_navigation_items()
        
        # 创建右侧内容区域
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        
        # 初始显示提取音频页面
        self.show_extract_audio_page()
        
        # 添加到主布局
        main_layout.addWidget(self.navigation)
        main_layout.addWidget(self.content_widget, 1)
        
        # 设置默认选中项
        self.navigation.setCurrentItem('extract_audio')
        
    def add_navigation_items(self):
        """添加导航项"""
        # 添加提取音频项
        self.navigation.addItem(
            routeKey='extract_audio',
            icon=FluentIcon.MUSIC,
            text='提取音频',
            onClick=self.show_extract_audio_page,
            position=NavigationItemPosition.TOP
        )
        
        # 添加提取文案项
        self.navigation.addItem(
            routeKey='extract_text',
            icon=FluentIcon.DOCUMENT,
            text='提取文案',
            onClick=self.show_extract_text_page,
            position=NavigationItemPosition.TOP
        )
        

            
    def clear_content(self):
        """清空内容区域"""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
    def show_extract_audio_page(self):
        """显示提取音频页面"""
        self.clear_content()
        
        # 创建页面标题
        title_label = QLabel("提取音频")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Microsoft YaHei", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                padding: 50px;
                background-color: transparent;
            }
        """)
        
        # 创建内容标签
        content_label = QLabel("这里是提取音频功能的内容区域")
        content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_label.setFont(QFont("Microsoft YaHei", 14))
        content_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                padding: 20px;
                background-color: transparent;
            }
        """)
        
        # 添加到布局
        self.content_layout.addStretch()
        self.content_layout.addWidget(title_label)
        self.content_layout.addWidget(content_label)
        self.content_layout.addStretch()
        
    def show_extract_text_page(self):
        """显示提取文案页面"""
        self.clear_content()
        
        # 创建页面标题
        title_label = QLabel("提取文案")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Microsoft YaHei", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                padding: 50px;
                background-color: transparent;
            }
        """)
        
        # 创建内容标签
        content_label = QLabel("这里是提取文案功能的内容区域")
        content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_label.setFont(QFont("Microsoft YaHei", 14))
        content_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                padding: 20px;
                background-color: transparent;
            }
        """)
        
        # 添加到布局
        self.content_layout.addStretch()
        self.content_layout.addWidget(title_label)
        self.content_layout.addWidget(content_label)
        self.content_layout.addStretch()


def main():
    """主函数"""
    # 创建应用程序
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == '__main__':
    main()