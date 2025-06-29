#!/usr/bin/env python3
"""
快速测试GUI程序能否正常显示
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def quick_test():
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
        from gui_main import MainWindow
        
        app = QApplication(sys.argv)
        
        # 创建主窗口但不显示
        window = MainWindow()
        print("✅ 主窗口创建成功")
        
        # 不启动事件循环，直接退出
        app.quit()
        return True
        
    except Exception as e:
        print(f"❌ GUI测试失败: {e}")
        return False

if __name__ == "__main__":
    print("快速GUI测试...")
    if quick_test():
        print("✅ GUI程序可以正常运行")
        print("请运行: python gui_main.py 启动完整程序")
    else:
        print("❌ GUI程序有问题，请检查依赖")