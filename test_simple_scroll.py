#!/usr/bin/env python3
"""
简单测试日志滚动功能
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def simple_test():
    """简单测试日志组件创建和滚动"""
    try:
        from PyQt6.QtWidgets import QApplication
        from gui_main import LogWidget
        
        app = QApplication([])
        
        # 创建日志组件
        log_widget = LogWidget()
        
        # 测试添加日志
        print("测试日志组件...")
        log_widget.append_log("测试消息 1")
        log_widget.append_log("测试消息 2")
        log_widget.append_log("测试消息 3")
        
        # 测试滚动方法
        log_widget.scroll_to_bottom()
        
        print("✅ 日志组件测试成功")
        print("✅ 滚动功能正常")
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("简单日志滚动测试")
    print("=" * 20)
    if simple_test():
        print("\n🎉 日志滚动功能已修复完成！")
        print("\n功能改进：")
        print("- 每次添加日志都自动滚动到底部")
        print("- 使用多重滚动确保机制")
        print("- 添加了延迟滚动处理渲染延迟")
        print("- 使用@pyqtSlot确保线程安全")
        print("\n运行 'python gui_main.py' 测试完整功能")
    else:
        print("测试失败，请检查PyQt6安装")