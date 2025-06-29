#!/usr/bin/env python3
"""
Discord Bot 配置管理 Web 界面
运行此脚本启动配置管理服务器：python config_web.py
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import os
import logging
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'discord-bot-config-secret-key'

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ACCOUNTS_FILE = 'accounts.json'
ENV_FILE = '.env'
BACKUP_DIR = 'config_backups'

def ensure_backup_dir():
    """确保备份目录存在"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

def load_accounts():
    """加载账户配置"""
    try:
        if os.path.exists(ACCOUNTS_FILE):
            with open(ACCOUNTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"加载配置失败: {e}")
        return []

def save_accounts(accounts):
    """保存账户配置"""
    try:
        # 创建备份
        ensure_backup_dir()
        if os.path.exists(ACCOUNTS_FILE):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(BACKUP_DIR, f'accounts_backup_{timestamp}.json')
            with open(ACCOUNTS_FILE, 'r', encoding='utf-8') as f:
                backup_data = f.read()
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(backup_data)
            logger.info(f"配置备份已保存: {backup_file}")
        
        # 保存新配置
        with open(ACCOUNTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(accounts, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"保存配置失败: {e}")
        return False

def load_env():
    """加载.env文件，包含注释"""
    try:
        env_vars = {}
        if os.path.exists(ENV_FILE):
            with open(ENV_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                current_comment = ""
                
                for line in lines:
                    line = line.rstrip()
                    
                    # 处理注释行
                    if line.startswith('#'):
                        comment_text = line[1:].strip()
                        if comment_text:  # 非空注释
                            current_comment = comment_text
                        continue
                    
                    # 处理空行
                    if not line.strip():
                        current_comment = ""
                        continue
                    
                    # 处理键值对
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        env_vars[key] = {
                            'value': value,
                            'comment': current_comment
                        }
                        current_comment = ""  # 清空当前注释
        
        return env_vars
    except Exception as e:
        logger.error(f"加载.env失败: {e}")
        return {}

def save_env(env_vars):
    """保存.env文件，包含注释"""
    try:
        # 创建备份
        ensure_backup_dir()
        if os.path.exists(ENV_FILE):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(BACKUP_DIR, f'env_backup_{timestamp}.env')
            with open(ENV_FILE, 'r', encoding='utf-8') as f:
                backup_data = f.read()
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(backup_data)
            logger.info(f".env备份已保存: {backup_file}")
        
        # 保存新配置
        with open(ENV_FILE, 'w', encoding='utf-8') as f:
            for key, data in env_vars.items():
                # 处理新格式和旧格式的兼容性
                if isinstance(data, dict):
                    value = data.get('value', '')
                    comment = data.get('comment', '')
                else:
                    # 兼容旧格式
                    value = data
                    comment = ''
                
                # 写入注释
                if comment:
                    f.write(f"# {comment}\n")
                
                # 写入键值对
                f.write(f"{key}={value}\n")
                
                # 添加空行分隔（除了最后一个）
                f.write("\n")
        
        return True
    except Exception as e:
        logger.error(f"保存.env失败: {e}")
        return False

@app.route('/')
def index():
    """主页"""
    return send_from_directory('.', 'config_web.html')

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    """获取所有账户配置"""
    accounts = load_accounts()
    return jsonify(accounts)

@app.route('/api/accounts', methods=['POST'])
def save_accounts_api():
    """保存账户配置"""
    try:
        accounts = request.json
        if not isinstance(accounts, list):
            return jsonify({'error': '配置格式错误'}), 400
        
        # 验证每个账户配置
        for i, account in enumerate(accounts):
            if not account.get('token'):
                return jsonify({'error': f'账户 {i+1} 缺少token'}), 400
            if not account.get('channel_id'):
                return jsonify({'error': f'账户 {i+1} 缺少channel_id'}), 400
            if not account.get('name'):
                return jsonify({'error': f'账户 {i+1} 缺少name'}), 400
            if 'whitelist_users' not in account:
                account['whitelist_users'] = []
        
        if save_accounts(accounts):
            return jsonify({'success': True, 'message': '配置保存成功'})
        else:
            return jsonify({'error': '配置保存失败'}), 500
    except Exception as e:
        logger.error(f"API保存配置失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/backups', methods=['GET'])
def get_backups():
    """获取备份文件列表"""
    try:
        ensure_backup_dir()
        backups = []
        for filename in os.listdir(BACKUP_DIR):
            if filename.startswith('accounts_backup_') and filename.endswith('.json'):
                filepath = os.path.join(BACKUP_DIR, filename)
                stat = os.stat(filepath)
                backups.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
        # 按修改时间排序
        backups.sort(key=lambda x: x['modified'], reverse=True)
        return jsonify(backups)
    except Exception as e:
        logger.error(f"获取备份列表失败: {e}")
        return jsonify([])

@app.route('/api/restore/<filename>', methods=['POST'])
def restore_backup(filename):
    """恢复备份"""
    try:
        backup_path = os.path.join(BACKUP_DIR, filename)
        if not os.path.exists(backup_path):
            return jsonify({'error': '备份文件不存在'}), 404
        
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        if save_accounts(backup_data):
            return jsonify({'success': True, 'message': f'已恢复备份: {filename}'})
        else:
            return jsonify({'error': '恢复备份失败'}), 500
    except Exception as e:
        logger.error(f"恢复备份失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/env', methods=['GET'])
def get_env():
    """获取环境变量配置"""
    env_vars = load_env()
    return jsonify(env_vars)

@app.route('/api/env', methods=['POST'])
def save_env_api():
    """保存环境变量配置"""
    try:
        env_vars = request.json
        if not isinstance(env_vars, dict):
            return jsonify({'error': '环境变量格式错误'}), 400
        
        if save_env(env_vars):
            return jsonify({'success': True, 'message': '环境变量保存成功'})
        else:
            return jsonify({'error': '环境变量保存失败'}), 500
    except Exception as e:
        logger.error(f"API保存环境变量失败: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Discord Bot 配置管理界面")
    print("访问地址: http://localhost:5001")
    print("按 Ctrl+C 停止服务")
    app.run(host='0.0.0.0', port=5001, debug=True)