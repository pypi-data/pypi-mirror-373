"""
rbpop UI测试演示
提供完整的交互式测试界面
"""

import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget, QPushButton, QLabel, QLineEdit, QTextEdit, 
    QSpinBox, QGroupBox, QComboBox, QColorDialog
)
from PyQt6.QtCore import Qt, QTimer

from rbpop.win import WinManager, QPop
from rbpop.prefab.message import QPMsg

class TestControlPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("rbpop 弹窗测试控制面板")
        self.setGeometry(200, 200, 500, 400)
        
        # 创建主部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 标题区域
        title = QLabel("rbpop 弹窗管理系统测试")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
        # 创建输入区域
        self._create_input_group(layout)
        
        # 控制按钮区域
        self._create_control_group(layout)
        
        # 状态显示
        self._create_status_group(layout)
        
        # 定时更新状态
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(500)  # 每500ms更新一次
        
    def _create_input_group(self, parent_layout):
        """创建输入区域"""
        group = QGroupBox("弹窗创建")
        layout = QVBoxLayout(group)
        
        # 标题输入
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("标题:"))
        self.title_input = QLineEdit("测试弹窗")
        title_layout.addWidget(self.title_input)
        layout.addLayout(title_layout)
        
        # 内容输入
        content_layout = QHBoxLayout()
        content_layout.addWidget(QLabel("内容:"))
        self.content_input = QTextEdit("这是测试内容\n可以输入多行文本")
        self.content_input.setMaximumHeight(60)
        content_layout.addWidget(self.content_input)
        layout.addLayout(content_layout)
        
        # 显示时长
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("显示时长(秒):"))
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 30)
        self.duration_spin.setValue(5)
        duration_layout.addWidget(self.duration_spin)
        layout.addLayout(duration_layout)
        
        # 颜色选择
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("背景颜色:"))
        self.color_combo = QComboBox()
        self.color_combo.addItems([
            "天蓝色 (#3498db)",
            "翡翠绿 (#2ecc71)", 
            "紫罗兰 (#9b59b6)",
            "胡萝卜橙 (#e67e22)",
            "石榴红 (#e74c3c)",
            "向日葵黄 (#f1c40f)",
            "薄荷绿 (#1abc9c)",
            "蓝灰色 (#34495e)",
            "粉色 (#ff9ff3)",
            "自定义..."
        ])
        self.color_combo.setCurrentIndex(0)
        color_layout.addWidget(self.color_combo)
        
        # 自定义颜色按钮
        self.custom_color_btn = QPushButton("选择颜色")
        self.custom_color_btn.clicked.connect(self.choose_custom_color)
        self.custom_color_btn.setEnabled(False)
        color_layout.addWidget(self.custom_color_btn)
        layout.addLayout(color_layout)
        
        # 连接颜色选择变化事件
        self.color_combo.currentTextChanged.connect(self.on_color_changed)
        
        # 创建按钮
        create_btn = QPushButton("创建弹窗")
        create_btn.clicked.connect(self.create_popup)
        create_btn.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
        layout.addWidget(create_btn)
        
        parent_layout.addWidget(group)
        
    def _create_control_group(self, parent_layout):
        """创建控制按钮区域"""
        group = QGroupBox("批量控制")
        layout = QHBoxLayout(group)
        
        buttons = [
            ("创建随机弹窗", self.create_random, "#2ecc71"),
            ("隐藏全部", self.hide_all, "#f39c12"),
            ("显示全部", self.show_all, "#9b59b6"),
            ("清空全部", self.clear_all, "#e74c3c"),
        ]
        
        for text, callback, color in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            btn.setStyleSheet(f"background-color: {color}; color: white; font-weight: bold;")
            layout.addWidget(btn)
        
        parent_layout.addWidget(group)
        
    def _create_status_group(self, parent_layout):
        """创建状态显示区域"""
        group = QGroupBox("实时状态")
        layout = QVBoxLayout(group)
        
        self.status_label = QLabel("就绪")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; padding: 10px;")
        layout.addWidget(self.status_label)
        
        # 创建多个随机弹窗的快捷按钮
        batch_layout = QHBoxLayout()
        for i in range(1, 6):
            btn = QPushButton(f"创建{i}个")
            btn.clicked.connect(lambda checked, count=i: self.create_batch(count))
            btn.setStyleSheet("background-color: #34495e; color: white;")
            batch_layout.addWidget(btn)
        layout.addLayout(batch_layout)
        
        # 平滑下降测试按钮
        smooth_btn = QPushButton("测试平滑下降效果")
        smooth_btn.clicked.connect(self.test_smooth_fall)
        smooth_btn.setStyleSheet("background-color: #16a085; color: white; font-weight: bold;")
        layout.addWidget(smooth_btn)
        
        # 滑入动画测试按钮（现在是默认效果）
        slide_btn = QPushButton("测试滑入动画效果")
        slide_btn.clicked.connect(self.test_slide_in)
        slide_btn.setStyleSheet("background-color: #e67e22; color: white; font-weight: bold;")
        layout.addWidget(slide_btn)
        
        parent_layout.addWidget(group)
        
    def on_color_changed(self, text):
        """颜色选择变化时启用/禁用自定义颜色按钮"""
        self.custom_color_btn.setEnabled(text == "自定义...")
        
    def choose_custom_color(self):
        """选择自定义颜色"""
        color = QColorDialog.getColor()
        if color.isValid():
            # 存储自定义颜色
            self.custom_color = color.name()
            self.custom_color_btn.setStyleSheet(f"background-color: {self.custom_color}; color: white;")
            
    def get_selected_color(self):
        """获取当前选择的颜色"""
        color_text = self.color_combo.currentText()
        if color_text == "自定义...":
            return getattr(self, 'custom_color', '#3498db')
        else:
            # 从文本中提取颜色代码
            import re
            match = re.search(r'#([0-9a-fA-F]{6})', color_text)
            return match.group(0) if match else '#3498db'
            
    def create_popup(self):
        """创建单个弹窗"""
        title = self.title_input.text() or f"弹窗-{random.randint(1000, 9999)}"
        content = self.content_input.toPlainText() or "这是自定义测试内容"
        duration = self.duration_spin.value() * 1000
        color = self.get_selected_color()
        
        popup = QPMsg(content, title, duration)
        popup.setStyleSheet(f"background-color: {color}; color: white;")
        QPop(popup)
            
    def create_random(self):
        """创建随机弹窗"""
        colors = ["#ff6b6b", "#4ecdc4", "#45b7d1", "#96ceb4", "#feca57", "#ff9ff3"]
        color = random.choice(colors)
        duration_seconds = random.randint(2, 8)
        
        popup = QPMsg(
            f"这是随机生成的弹窗内容\n颜色: {color}\n时间: {duration_seconds}秒",
            f"随机弹窗-{random.randint(1000, 9999)}",
            duration_seconds * 1000
        )
        popup.setStyleSheet(f"background-color: {color}; color: white;")
        QPop(popup)
        
    def create_batch(self, count):
        """批量创建弹窗"""
        for i in range(count):
            title = f"批量-{i+1}"
            content = f"这是第{i+1}个批量创建的弹窗\n共{count}个"
            popup = QPMsg(content, title, 5000)
            QPop(popup)
            
    def test_smooth_fall(self):
        """测试平滑下降效果"""
        colors = ["#ff6b6b", "#4ecdc4", "#45b7d1", "#96ceb4"]
        for i, color in enumerate(colors):
            title = f"下降测试-{i+1}"
            content = f"这是第{i+1}个弹窗\n观察关闭后的平滑下降效果\n颜色: {color}"
            popup = QPMsg(content, title, 6000)
            popup.setStyleSheet(f"background-color: {color}; color: white;")
            QPop(popup)
            
    def test_slide_in(self):
        """测试滑入动画效果"""
        colors = ["#3498db", "#2ecc71", "#9b59b6", "#e67e22", "#1abc9c"]
        durations = [600, 800, 1000, 1200, 1500]  # 不同的滑入持续时间
        
        for i, (color, duration) in enumerate(zip(colors, durations)):
            title = f"滑入测试-{i+1}"
            content = f"这是第{i+1}个弹窗\n滑入动画持续时间: {duration}ms\n颜色: {color}"
            
            # 创建启用滑入动画的弹窗
            popup = QPMsg(
                content, 
                title, 
                5000,  # 总显示时间
                slide_in=True,
                slide_duration=duration
            )
            popup.setStyleSheet(f"background-color: {color}; color: white;")
            QPop(popup)
            
    def hide_all(self):
        """隐藏所有窗口"""
        manager = WinManager.get_instance()
        manager.hide_all_windows()
        
    def show_all(self):
        """显示所有窗口"""
        manager = WinManager.get_instance()
        manager.show_all_windows()
        
    def clear_all(self):
        """清空所有窗口"""
        manager = WinManager.get_instance()
        # 关闭所有窗口
        for win in manager._win_list[:]:
            win.close()
        for win in manager._pending_queue[:]:
            win.close()
        manager._win_list.clear()
        manager._pending_queue.clear()
        
    def update_status(self):
        """更新状态显示"""
        manager = WinManager.get_instance()
        active_count = manager.get_window_count()
        pending_count = len(manager._pending_queue)
        
        status_text = f"活跃窗口: {active_count} | 待显示: {pending_count}"
        if active_count == 0 and pending_count == 0:
            status_text += "\n系统空闲"
        elif pending_count > 0:
            status_text += f"\n队列处理中... ({pending_count}个等待)"
        
        self.status_label.setText(status_text)

def launch_ui_demo():
    """启动UI测试界面"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    window = TestControlPanel()
    window.show()
    return app, window

if __name__ == "__main__":
    print("启动 rbpop UI测试界面...")
    app, window = launch_ui_demo()
    sys.exit(app.exec())
