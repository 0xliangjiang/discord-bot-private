#!/usr/bin/env python3
"""
只测试导入，不创建界面
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """测试所有导入"""
    try:
        print("测试基础导入...")
        from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
        print("✅ PyQt6基础组件")
        
        print("测试GUI主模块...")
        import gui_main
        print("✅ gui_main模块")
        
        print("测试关键词配置类...")
        from gui_main import KeywordConfigWidget
        print("✅ KeywordConfigWidget类")
        
        print("测试JSON处理...")
        import json
        test_data = {"test": "data"}
        json.dumps(test_data)
        print("✅ JSON处理")
        
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("导入测试")
    print("=" * 15)
    if test_imports():
        print("\n🎉 所有导入成功！")
        print("关键词配置功能已添加到GUI中")
    else:
        print("导入失败，请检查代码")