#!/usr/bin/env python3
"""
启动Discord Bot GUI的便捷脚本
"""

import sys
import os
import subprocess

def check_requirements():
    """检查必要的依赖包"""
    required_packages = [
        'PyQt6',
        'requests',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_').lower())
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("缺少以下依赖包:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\n请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def setup_environment():
    """设置运行环境"""
    # 确保必要的目录存在
    dirs_to_create = ['data', 'logs', 'config_backups']
    for dir_name in dirs_to_create:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"创建目录: {dir_name}")
    
    # 检查配置文件
    config_files = {
        'accounts.json': '[]',
        '.env': '''# Discord Bot 配置文件
AI_API_KEY=your_api_key_here
AI_API_URL=https://api.openai.com/v1/chat/completions
AI_MODEL=gpt-3.5-turbo
REPLY_LANGUAGE=中文
MESSAGE_LIMIT=50
REPLY_DELAY_MIN=30
REPLY_DELAY_MAX=60
ENABLE_WHITELIST_MODE=true
CHAT_HISTORY_MAX_LENGTH=50
ENABLE_ACTIVITY_MONITOR=true
ACTIVITY_CHECK_MINUTES=30
MIN_ACTIVE_USERS=2
CLEAR_DATA_ON_RESTART=false
USE_CUSTOM_TEMPLATE_FOR_WHITELIST=false
MAX_WORKERS=4
''',
        'keyword_responses.json': '''{
  "你好": ["你好！", "嗨！", "哈喽"],
  "再见": ["再见！", "拜拜", "下次见"],
  "谢谢": ["不客气", "不用谢", "😊"],
  "帮助": ["有什么可以帮您的吗？", "需要什么帮助？"],
  "早上好": ["早上好！", "早安！", "新的一天开始了"],
  "晚安": ["晚安！", "好梦！", "早点休息"],
  "怎么样": ["还不错", "挺好的", "一般般"],
  "在吗": ["在的", "我在", "有什么事吗"],
  "忙吗": ["不忙", "还好", "有什么事"],
  "好的": ["👍", "收到", "明白了"]
}'''
    }
    
    for filename, default_content in config_files.items():
        if not os.path.exists(filename):
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(default_content)
            print(f"创建配置文件: {filename}")

def main():
    """主函数"""
    print("Discord Bot Manager 启动器")
    print("=" * 40)
    
    # 检查依赖
    if not check_requirements():
        print("\n请安装必要的依赖包后重试")
        input("按Enter键退出...")
        return False
    
    # 设置环境
    setup_environment()
    
    print("\n环境检查完成，启动GUI...")
    
    try:
        # 启动主程序
        from gui_main import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"导入GUI模块失败: {e}")
        print("请确保gui_main.py文件存在")
        return False
    except Exception as e:
        print(f"启动失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()