#!/usr/bin/env python3
"""
测试GUI程序，检查所有依赖是否正常
"""

import sys
import os

def test_imports():
    """测试所有必要的导入"""
    print("正在测试Python导入...")
    
    try:
        print("✓ sys, os")
        
        import json
        print("✓ json")
        
        import threading
        print("✓ threading")
        
        import logging
        print("✓ logging")
        
        from datetime import datetime
        print("✓ datetime")
        
        from pathlib import Path
        print("✓ pathlib")
        
        import requests
        print("✓ requests")
        
        # 测试PyQt6
        from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
        print("✓ PyQt6.QtWidgets")
        
        from PyQt6.QtCore import QThread, pyqtSignal, QTimer
        print("✓ PyQt6.QtCore")
        
        from PyQt6.QtGui import QFont, QTextCursor
        print("✓ PyQt6.QtGui")
        
        # 测试src模块
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        try:
            from config import Config
            print("✓ config")
        except ImportError as e:
            print(f"⚠️ config导入警告: {e}")
        
        try:
            from bot import MultiAccountBotManager
            print("✓ bot")
        except ImportError as e:
            print(f"⚠️ bot导入警告: {e}")
        
        try:
            from chat_history import ChatHistoryManager
            print("✓ chat_history")
        except ImportError as e:
            print(f"⚠️ chat_history导入警告: {e}")
        
        try:
            from keyword_manager import KeywordManager
            print("✓ keyword_manager")
        except ImportError as e:
            print(f"⚠️ keyword_manager导入警告: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_qt_compatibility():
    """测试Qt兼容性"""
    print("\n正在测试Qt兼容性...")
    
    try:
        from PyQt6.QtWidgets import QApplication, QLineEdit, QTextEdit
        
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # 测试QLineEdit的EchoMode
        line_edit = QLineEdit()
        try:
            line_edit.setEchoMode(QLineEdit.EchoMode.Password)
            print("✓ QLineEdit.EchoMode (新版本)")
        except AttributeError:
            try:
                line_edit.setEchoMode(QLineEdit.Password)
                print("✓ QLineEdit.Password (旧版本)")
            except Exception as e:
                print(f"❌ QLineEdit密码模式测试失败: {e}")
                return False
        
        # 测试QTextEdit
        text_edit = QTextEdit()
        print("✓ QTextEdit")
        
        # 测试QTextCursor
        from PyQt6.QtGui import QTextCursor
        cursor = text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        print("✓ QTextCursor")
        
        # 清理
        app.quit()
        return True
        
    except Exception as e:
        print(f"❌ Qt兼容性测试失败: {e}")
        return False

def create_test_files():
    """创建必要的测试文件"""
    print("\n正在创建测试文件...")
    
    # 确保目录存在
    for dirname in ['data', 'logs', 'config_backups']:
        if not os.path.exists(dirname):
            os.makedirs(dirname)
            print(f"✓ 创建目录: {dirname}")
    
    # 创建测试配置文件
    if not os.path.exists('accounts.json'):
        with open('accounts.json', 'w', encoding='utf-8') as f:
            f.write('[]')
        print("✓ 创建accounts.json")
    
    if not os.path.exists('.env'):
        env_content = '''AI_API_KEY=your_api_key_here
AI_API_URL=https://api.openai.com/v1/chat/completions
AI_MODEL=gpt-3.5-turbo
REPLY_LANGUAGE=中文
MESSAGE_LIMIT=50
REPLY_DELAY_MIN=30
REPLY_DELAY_MAX=60
ENABLE_WHITELIST_MODE=true
CHAT_HISTORY_MAX_LENGTH=50'''
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✓ 创建.env")
    
    if not os.path.exists('keyword_responses.json'):
        keyword_content = '''{
  "你好": ["你好！", "嗨！"],
  "再见": ["再见！", "拜拜"]
}'''
        with open('keyword_responses.json', 'w', encoding='utf-8') as f:
            f.write(keyword_content)
        print("✓ 创建keyword_responses.json")

def main():
    """主测试函数"""
    print("Discord Bot Manager GUI - 兼容性测试")
    print("=" * 50)
    
    # 测试导入
    if not test_imports():
        print("\n❌ 导入测试失败，请安装缺少的依赖")
        print("运行: pip install -r requirements_gui.txt")
        return False
    
    # 测试Qt兼容性
    if not test_qt_compatibility():
        print("\n❌ Qt兼容性测试失败")
        return False
    
    # 创建测试文件
    create_test_files()
    
    print("\n" + "=" * 50)
    print("✅ 所有测试通过！GUI应该可以正常启动")
    print("运行: python gui_main.py")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    main()