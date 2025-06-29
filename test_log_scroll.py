#!/usr/bin/env python3
"""
测试日志滚动功能
"""

import sys
import os
import time
import threading

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_log_scroll():
    """测试日志自动滚动功能"""
    try:
        from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
        from PyQt6.QtCore import QTimer
        from gui_main import LogWidget
        
        app = QApplication(sys.argv)
        
        # 创建测试窗口
        window = QMainWindow()
        window.setWindowTitle("日志滚动测试")
        window.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        # 创建日志组件
        log_widget = LogWidget()
        layout.addWidget(log_widget)
        
        # 添加测试按钮
        def add_test_logs():
            """添加测试日志"""
            for i in range(10):
                log_widget.append_log(f"测试日志消息 #{i+1}")
                time.sleep(0.1)  # 短暂延迟模拟实际日志
        
        def add_many_logs():
            """添加大量日志测试滚动"""
            for i in range(50):
                log_widget.append_log(f"大量日志测试 #{i+1} - 这是一条比较长的日志消息，用于测试滚动功能是否正常工作")
        
        def add_continuous_logs():
            """持续添加日志"""
            def add_log():
                import datetime
                timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
                log_widget.append_log(f"持续日志 {timestamp} - Bot正在运行中...")
            
            # 创建定时器持续添加日志
            timer = QTimer()
            timer.timeout.connect(add_log)
            timer.start(500)  # 每500ms添加一条日志
            return timer
        
        # 创建按钮
        btn1 = QPushButton("添加10条测试日志")
        btn1.clicked.connect(add_test_logs)
        layout.addWidget(btn1)
        
        btn2 = QPushButton("添加50条长日志")
        btn2.clicked.connect(add_many_logs)
        layout.addWidget(btn2)
        
        btn3 = QPushButton("开始持续日志")
        timer_ref = [None]
        def start_continuous():
            if timer_ref[0] is None:
                timer_ref[0] = add_continuous_logs()
                btn3.setText("停止持续日志")
            else:
                timer_ref[0].stop()
                timer_ref[0] = None
                btn3.setText("开始持续日志")
        
        btn3.clicked.connect(start_continuous)
        layout.addWidget(btn3)
        
        central_widget.setLayout(layout)
        window.setCentralWidget(central_widget)
        
        # 添加初始日志
        log_widget.append_log("日志滚动测试开始")
        log_widget.append_log("点击按钮测试不同的日志滚动场景")
        log_widget.append_log("注意观察日志是否自动滚动到底部")
        
        window.show()
        
        print("✅ 日志滚动测试窗口已打开")
        print("请在窗口中测试各种日志滚动功能")
        print("按Ctrl+C退出测试")
        
        # 运行应用
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("日志滚动功能测试")
    print("=" * 30)
    test_log_scroll()