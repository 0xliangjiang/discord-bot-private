#!/usr/bin/env python3
"""
测试关键词回复配置功能
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_keyword_config():
    """测试关键词配置界面"""
    try:
        from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
        from gui_main import KeywordConfigWidget
        
        app = QApplication(sys.argv)
        
        # 创建测试窗口
        window = QMainWindow()
        window.setWindowTitle("关键词配置测试")
        window.setGeometry(100, 100, 900, 700)
        
        # 创建关键词配置组件
        keyword_widget = KeywordConfigWidget()
        window.setCentralWidget(keyword_widget)
        
        # 添加一些测试数据
        print("✅ 关键词配置界面创建成功")
        print("界面功能：")
        print("- 全局设置：启用关键词回复、随机选择回复、AI回复后备")
        print("- 精确匹配：完全匹配关键词")
        print("- 包含匹配：消息包含关键词")
        print("- 正则匹配：支持正则表达式")
        print("- 动态添加/删除规则")
        print("- 保存到keyword_responses.json")
        
        window.show()
        
        print("\n请在窗口中测试关键词配置功能：")
        print("1. 点击'添加XXX规则'按钮添加规则")
        print("2. 填写关键词和回复内容")
        print("3. 点击'保存配置'保存")
        print("4. 点击'重新加载'测试加载")
        print("按Ctrl+C退出测试")
        
        # 运行应用
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("关键词回复配置功能测试")
    print("=" * 40)
    test_keyword_config()