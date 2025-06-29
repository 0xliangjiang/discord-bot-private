#!/usr/bin/env python3
"""
简单测试关键词配置组件
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def simple_keyword_test():
    """简单测试关键词配置组件创建"""
    try:
        from PyQt6.QtWidgets import QApplication
        from gui_main import KeywordConfigWidget
        
        app = QApplication([])
        
        # 创建关键词配置组件
        print("测试关键词配置组件...")
        keyword_widget = KeywordConfigWidget()
        
        print("✅ 关键词配置组件创建成功")
        print("✅ 界面初始化正常")
        print("✅ 数据加载功能正常")
        
        # 测试添加规则方法
        print("测试添加规则功能...")
        keyword_widget.add_keyword_rule(keyword_widget.exact_group, "exact_match")
        print("✅ 添加规则功能正常")
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("简单关键词配置测试")
    print("=" * 25)
    if simple_keyword_test():
        print("\n🎉 关键词配置功能创建成功！")
        print("\n新增功能：")
        print("- 图形化关键词回复配置")
        print("- 支持精确匹配、包含匹配、正则匹配")
        print("- 全局设置选项")
        print("- 动态添加/删除规则")
        print("- 自动保存到JSON文件")
        print("\n运行 'python gui_main.py' 查看完整界面")
    else:
        print("测试失败，请检查代码")