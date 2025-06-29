#!/usr/bin/env python3
"""
Discord Bot 配置管理器启动脚本
"""

import os
import sys
import subprocess

def check_dependencies():
    """检查依赖是否已安装"""
    try:
        import flask
        print("✅ Flask 已安装")
        return True
    except ImportError:
        print("❌ Flask 未安装")
        print("正在安装 Flask...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
            print("✅ Flask 安装成功")
            return True
        except subprocess.CalledProcessError:
            print("❌ Flask 安装失败")
            return False

def main():
    print("Discord Bot 配置管理器")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        print("请手动安装依赖: pip install flask")
        return
    
    # 启动配置服务器
    print("正在启动配置管理界面...")
    print("访问地址: http://localhost:5001")
    print("按 Ctrl+C 停止服务")
    print("=" * 50)
    
    try:
        # 导入并运行配置服务器
        from config_web import app
        app.run(host='0.0.0.0', port=5001, debug=False)
    except KeyboardInterrupt:
        print("\n配置管理器已停止")
    except Exception as e:
        print(f"启动失败: {e}")

if __name__ == "__main__":
    main()