#!/usr/bin/env python3
"""
Discord Bot GUI 打包脚本
使用PyInstaller将应用程序打包成exe文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build():
    """清理之前的构建文件"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"清理目录: {dir_name}")
            shutil.rmtree(dir_name, ignore_errors=True)
    
    # 清理.pyc文件
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))

def create_spec_file():
    """创建PyInstaller配置文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 分析主脚本
a = Analysis(
    ['gui_main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),
        ('*.json', '.'),
        ('.env', '.'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'requests',
        'json',
        'threading',
        'logging',
        'datetime',
        'pathlib',
        'dotenv',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 创建PYZ文件
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 创建可执行文件
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DiscordBotManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 设置为False隐藏控制台窗口
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None
)

# 创建COLLECT来生成目录结构
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DiscordBotManager'
)
'''
    
    with open('discord_bot.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("创建配置文件: discord_bot.spec")

def install_requirements():
    """安装依赖包"""
    print("安装依赖包...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements_gui.txt'])
        print("依赖包安装完成")
    except subprocess.CalledProcessError as e:
        print(f"依赖包安装失败: {e}")
        return False
    return True

def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    # 使用spec文件构建
    cmd = [
        'pyinstaller',
        '--clean',
        '--noconfirm',
        'discord_bot.spec'
    ]
    
    try:
        subprocess.check_call(cmd)
        print("构建完成！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        return False

def copy_resources():
    """复制必要的资源文件到dist目录"""
    dist_dir = Path('dist')
    if not dist_dir.exists():
        print("dist目录不存在，构建可能失败了")
        return False
    
    # 寻找可执行文件目录
    exe_dir = dist_dir / 'DiscordBotManager'
    if not exe_dir.exists():
        print(f"找不到可执行文件目录: {exe_dir}")
        return False
    
    # 复制配置文件（如果不存在则创建默认）
    config_files = {
        'accounts.json': '[]',
        '.env': '''# Discord Bot 配置文件
AI_API_KEY=your_api_key_here
AI_API_URL=https://api.openai.com/v1/chat/completions
AI_MODEL=gpt-4o-mini
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
  "description": "关键词自动回复词库配置",
  "rules": {
    "exact_match": {
      "description": "精确匹配",
      "responses": {
        "你好": ["你好！", "嗨！", "哈喽"],
        "再见": ["再见！", "拜拜", "下次见"]
      }
    },
    "contains_match": {
      "description": "包含匹配",
      "responses": {
        "工作": ["上班族", "搬砖去", "工作辛苦"],
        "富婆": ["想得美", "梦想挺好", "醒醒吧兄弟"]
      }
    },
    "regex_match": {
      "description": "正则匹配",
      "responses": {
        "价格|价位|多少钱": ["不清楚", "看行情", "自己dyor"],
        "买|卖|交易": ["dyor", "自己判断", "风险自负"]
      }
    }
  },
  "settings": {
    "enable_keyword_responses": true,
    "random_response": true,
    "fallback_to_ai": true,
    "match_priority": ["exact_match", "contains_match", "regex_match"]
  }
}'''
    }
    
    for file_name, default_content in config_files.items():
        dest_path = exe_dir / file_name
        if os.path.exists(file_name):
            # 复制现有文件
            shutil.copy2(file_name, dest_path)
            print(f"复制现有文件: {file_name} -> {dest_path}")
        else:
            # 创建默认文件
            with open(dest_path, 'w', encoding='utf-8') as f:
                f.write(default_content)
            print(f"创建默认文件: {dest_path}")
    
    # 创建必要的目录并添加说明文件
    dirs_to_create = {
        'data': '聊天记录存储目录',
        'logs': '运行日志存储目录', 
        'config_backups': '配置文件备份目录'
    }
    
    for dir_name, description in dirs_to_create.items():
        dir_path = exe_dir / dir_name
        dir_path.mkdir(exist_ok=True)
        
        # 创建目录说明文件
        readme_path = dir_path / 'README.txt'
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"{description}\n")
            f.write(f"此目录由Discord Bot Manager自动创建\n")
            f.write(f"请勿手动删除此目录\n")
        
        print(f"创建目录: {dir_path} - {description}")
    
    # 复制其他资源文件
    other_files = [
        'GUI_使用说明.md',
        '关键词配置功能说明.md',
        '日志滚动改进说明.md'
    ]
    
    for file_name in other_files:
        if os.path.exists(file_name):
            dest_path = exe_dir / file_name
            shutil.copy2(file_name, dest_path)
            print(f"复制说明文件: {file_name} -> {dest_path}")
    
    return True

def create_readme():
    """创建README文件"""
    readme_content = """# Discord Bot Manager

## 使用说明

### 1. 首次运行
- 双击 `DiscordBotManager.exe` 启动程序
- 程序会自动创建必要的配置文件夹

### 2. 配置Discord账户
1. 切换到"账户配置"标签页
2. 点击"添加账户"按钮
3. 填写以下信息：
   - 名称：给账户起个名字，用于识别
   - Token：Discord Bot的Token
   - 频道ID：要监控的Discord频道ID
   - 白名单用户：用逗号分隔的用户ID列表

### 3. 配置AI设置
1. 切换到"通用配置"标签页
2. 填写AI API相关信息：
   - API Key：你的AI服务API密钥
   - API URL：AI服务的API地址
   - 模型：使用的AI模型名称

### 4. 启动Bot
1. 确保所有配置填写完整
2. 点击顶部的"启动Bot"按钮
3. 观察右侧日志区域的运行状态

### 5. 停止和重启
- 点击"停止Bot"按钮停止所有机器人
- 点击"重启Bot"按钮重新启动

## 注意事项

1. **Token安全**：请妥善保管你的Discord Bot Token
2. **网络连接**：确保网络连接正常，程序需要访问Discord API和AI API
3. **日志监控**：通过右侧日志窗口监控程序运行状态
4. **配置备份**：程序会自动备份配置文件到 `config_backups` 目录

## 故障排除

### 常见问题
1. **程序无法启动**：检查是否有杀毒软件阻止
2. **Bot无法连接**：检查Token和网络连接
3. **AI回复异常**：检查AI API配置和余额

### 日志文件
- 运行日志保存在 `logs` 目录下
- 配置备份保存在 `config_backups` 目录下

## 联系支持
如有问题，请查看日志文件并联系技术支持。
"""
    
    with open('dist/README.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("创建说明文件: dist/README.txt")

def main():
    """主函数"""
    print("Discord Bot Manager 构建脚本")
    print("=" * 50)
    
    # 清理之前的构建
    clean_build()
    
    # 安装依赖
    if not install_requirements():
        print("依赖安装失败，退出构建")
        return False
    
    # 创建spec文件
    create_spec_file()
    
    # 构建可执行文件
    if not build_executable():
        print("构建失败")
        return False
    
    # 复制资源文件
    if not copy_resources():
        print("资源文件复制失败")
        return False
    
    # 创建说明文件
    create_readme()
    
    print("\n" + "=" * 50)
    print("构建完成！")
    print("可执行文件位置: dist/DiscordBotManager/")
    print("请将整个文件夹分发给用户")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    main()