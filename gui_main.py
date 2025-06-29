#!/usr/bin/env python3
"""
Discord Bot GUI - PyQt6主界面
"""

import sys
import os
import json
import threading
import logging
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTextEdit, QPushButton, QLabel, QLineEdit, QSpinBox,
    QCheckBox, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QGroupBox, QFormLayout, QMessageBox, QSplitter, QFrame, QScrollArea,
    QFileDialog, QProgressBar, QStatusBar
)
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap, QTextCursor
import requests

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from config import Config
    from bot import MultiAccountBotManager
    from chat_history import ChatHistoryManager
    from keyword_manager import KeywordManager
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保src目录中的模块存在")

class LogHandler(logging.Handler):
    """自定义日志处理器，将日志发送到GUI"""
    
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        
    def emit(self, record):
        try:
            msg = self.format(record)
            # 使用信号安全地更新GUI
            if hasattr(self.text_widget, 'append_log'):
                self.text_widget.append_log(msg)
        except Exception:
            pass

class BotWorker(QThread):
    """Bot运行工作线程"""
    log_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.manager = None
        self.running = False
        
    def run(self):
        """在后台线程运行bot"""
        try:
            self.status_signal.emit("正在启动Discord Bot...")
            self.manager = MultiAccountBotManager()
            self.running = True
            
            # 重定向日志到GUI
            self.setup_logging()
            
            self.status_signal.emit("Bot正在运行中...")
            self.manager.start_all()
            
        except Exception as e:
            self.error_signal.emit(f"Bot运行失败: {str(e)}")
        finally:
            self.status_signal.emit("Bot已停止")
            self.running = False
    
    def setup_logging(self):
        """设置日志重定向"""
        # 这里可以添加更多日志配置
        pass
    
    def stop_bot(self):
        """停止bot"""
        if self.manager and self.running:
            self.manager.stop_all()
            self.running = False

class LogWidget(QTextEdit):
    """日志显示组件"""
    
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setMaximumBlockCount(1000)  # 限制最大行数
        
        # 设置字体
        font = QFont("Consolas", 9)
        font.setFamily("Monaco")  # macOS
        self.setFont(font)
        
        # 设置样式
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
            }
        """)
        
    def append_log(self, message):
        """线程安全地添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {message}"
        
        # 移动到末尾并添加文本
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(formatted_msg + "\n")
        
        # 自动滚动到底部
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

class AccountConfigWidget(QWidget):
    """账户配置界面"""
    
    def __init__(self):
        super().__init__()
        self.accounts = []
        self.init_ui()
        self.load_accounts()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 顶部按钮
        button_layout = QHBoxLayout()
        self.add_account_btn = QPushButton("添加账户")
        self.save_btn = QPushButton("保存配置")
        self.load_btn = QPushButton("重新加载")
        
        self.add_account_btn.clicked.connect(self.add_account)
        self.save_btn.clicked.connect(self.save_accounts)
        self.load_btn.clicked.connect(self.load_accounts)
        
        button_layout.addWidget(self.add_account_btn)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.load_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # 账户表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["名称", "Token", "频道ID", "白名单用户", "操作"])
        
        # 设置列宽
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        
        self.table.setColumnWidth(0, 120)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(4, 80)
        
        layout.addWidget(self.table)
        self.setLayout(layout)
        
    def load_accounts(self):
        """加载账户配置"""
        try:
            accounts_file = "accounts.json"
            if os.path.exists(accounts_file):
                with open(accounts_file, 'r', encoding='utf-8') as f:
                    self.accounts = json.load(f)
            else:
                self.accounts = []
            self.refresh_table()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载配置失败: {str(e)}")
            
    def save_accounts(self):
        """保存账户配置"""
        try:
            # 从表格收集数据
            accounts = []
            for row in range(self.table.rowCount()):
                name_item = self.table.item(row, 0)
                token_item = self.table.item(row, 1)
                channel_item = self.table.item(row, 2)
                whitelist_item = self.table.item(row, 3)
                
                if name_item and token_item and channel_item:
                    whitelist_text = whitelist_item.text() if whitelist_item else ""
                    whitelist_users = [uid.strip() for uid in whitelist_text.split(',') if uid.strip()]
                    
                    account = {
                        "name": name_item.text(),
                        "token": token_item.text(),
                        "channel_id": channel_item.text(),
                        "whitelist_users": whitelist_users
                    }
                    accounts.append(account)
            
            # 保存到文件
            with open("accounts.json", 'w', encoding='utf-8') as f:
                json.dump(accounts, f, ensure_ascii=False, indent=2)
                
            self.accounts = accounts
            QMessageBox.information(self, "成功", "账户配置已保存")
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存配置失败: {str(e)}")
    
    def add_account(self):
        """添加新账户"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # 添加默认值
        self.table.setItem(row, 0, QTableWidgetItem(f"账户_{row+1}"))
        self.table.setItem(row, 1, QTableWidgetItem(""))
        self.table.setItem(row, 2, QTableWidgetItem(""))
        self.table.setItem(row, 3, QTableWidgetItem(""))
        
        # 删除按钮
        delete_btn = QPushButton("删除")
        delete_btn.clicked.connect(lambda: self.delete_account(row))
        self.table.setCellWidget(row, 4, delete_btn)
        
    def delete_account(self, row):
        """删除账户"""
        reply = QMessageBox.question(self, "确认", "确定要删除这个账户吗？")
        if reply == QMessageBox.StandardButton.Yes:
            self.table.removeRow(row)
            self.refresh_table()
    
    def refresh_table(self):
        """刷新表格"""
        self.table.setRowCount(len(self.accounts))
        
        for row, account in enumerate(self.accounts):
            self.table.setItem(row, 0, QTableWidgetItem(account.get("name", "")))
            self.table.setItem(row, 1, QTableWidgetItem(account.get("token", "")))
            self.table.setItem(row, 2, QTableWidgetItem(account.get("channel_id", "")))
            
            whitelist_text = ",".join(account.get("whitelist_users", []))
            self.table.setItem(row, 3, QTableWidgetItem(whitelist_text))
            
            delete_btn = QPushButton("删除")
            delete_btn.clicked.connect(lambda checked, r=row: self.delete_account(r))
            self.table.setCellWidget(row, 4, delete_btn)

class ConfigWidget(QWidget):
    """配置界面"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_config()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 创建滚动区域
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        
        # AI配置组
        ai_group = QGroupBox("AI配置")
        ai_layout = QFormLayout()
        
        self.ai_api_key = QLineEdit()
        self.ai_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.ai_api_url = QLineEdit()
        self.ai_model = QLineEdit()
        
        ai_layout.addRow("API Key:", self.ai_api_key)
        ai_layout.addRow("API URL:", self.ai_api_url)
        ai_layout.addRow("模型:", self.ai_model)
        ai_group.setLayout(ai_layout)
        
        # Bot配置组
        bot_group = QGroupBox("Bot配置")
        bot_layout = QFormLayout()
        
        self.reply_language = QComboBox()
        self.reply_language.addItems(["中文", "English", "日本語"])
        
        self.message_limit = QSpinBox()
        self.message_limit.setRange(1, 100)
        self.message_limit.setValue(50)
        
        self.reply_delay_min = QSpinBox()
        self.reply_delay_min.setRange(1, 300)
        self.reply_delay_min.setValue(30)
        
        self.reply_delay_max = QSpinBox()
        self.reply_delay_max.setRange(1, 300)
        self.reply_delay_max.setValue(60)
        
        bot_layout.addRow("回复语言:", self.reply_language)
        bot_layout.addRow("消息限制:", self.message_limit)
        bot_layout.addRow("最小延迟(秒):", self.reply_delay_min)
        bot_layout.addRow("最大延迟(秒):", self.reply_delay_max)
        bot_group.setLayout(bot_layout)
        
        # 白名单配置组
        whitelist_group = QGroupBox("白名单配置")
        whitelist_layout = QFormLayout()
        
        self.enable_whitelist = QCheckBox("启用白名单模式")
        self.chat_history_max_length = QSpinBox()
        self.chat_history_max_length.setRange(10, 1000)
        self.chat_history_max_length.setValue(50)
        
        whitelist_layout.addRow("", self.enable_whitelist)
        whitelist_layout.addRow("聊天历史长度:", self.chat_history_max_length)
        whitelist_group.setLayout(whitelist_layout)
        
        # 保存按钮
        save_btn = QPushButton("保存配置")
        save_btn.clicked.connect(self.save_config)
        
        # 添加到滚动布局
        scroll_layout.addWidget(ai_group)
        scroll_layout.addWidget(bot_group)
        scroll_layout.addWidget(whitelist_group)
        scroll_layout.addWidget(save_btn)
        scroll_layout.addStretch()
        
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        
        layout.addWidget(scroll)
        self.setLayout(layout)
    
    def load_config(self):
        """加载配置"""
        try:
            # 这里可以从config.py或环境变量加载配置
            # 暂时使用默认值
            self.ai_api_url.setText("https://api.openai.com/v1/chat/completions")
            self.ai_model.setText("gpt-3.5-turbo")
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载配置失败: {str(e)}")
    
    def save_config(self):
        """保存配置"""
        try:
            # 这里可以保存配置到.env文件或其他地方
            config_data = {
                "AI_API_KEY": self.ai_api_key.text(),
                "AI_API_URL": self.ai_api_url.text(),
                "AI_MODEL": self.ai_model.text(),
                "REPLY_LANGUAGE": self.reply_language.currentText(),
                "MESSAGE_LIMIT": self.message_limit.value(),
                "REPLY_DELAY_MIN": self.reply_delay_min.value(),
                "REPLY_DELAY_MAX": self.reply_delay_max.value(),
                "ENABLE_WHITELIST_MODE": self.enable_whitelist.isChecked(),
                "CHAT_HISTORY_MAX_LENGTH": self.chat_history_max_length.value()
            }
            
            # 保存到.env文件
            env_content = ""
            for key, value in config_data.items():
                env_content += f"{key}={value}\n"
            
            with open(".env", "w", encoding="utf-8") as f:
                f.write(env_content)
            
            QMessageBox.information(self, "成功", "配置已保存到.env文件")
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存配置失败: {str(e)}")

class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.bot_worker = None
        self.init_ui()
        self.setup_logging()
        
    def init_ui(self):
        self.setWindowTitle("Discord Bot 管理器 v1.0")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout()
        
        # 顶部控制面板
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)
        
        # 创建分割器
        splitter = QSplitter()
        
        # 左侧标签页
        tab_widget = QTabWidget()
        
        # 账户配置页
        self.account_config = AccountConfigWidget()
        tab_widget.addTab(self.account_config, "账户配置")
        
        # 通用配置页
        self.config_widget = ConfigWidget()
        tab_widget.addTab(self.config_widget, "通用配置")
        
        # 右侧日志区域
        log_frame = QFrame()
        log_layout = QVBoxLayout()
        log_layout.addWidget(QLabel("运行日志:"))
        
        self.log_widget = LogWidget()
        log_layout.addWidget(self.log_widget)
        
        log_frame.setLayout(log_layout)
        
        # 添加到分割器
        splitter.addWidget(tab_widget)
        splitter.addWidget(log_frame)
        splitter.setSizes([600, 600])
        
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
        
        # 状态栏
        self.statusBar().showMessage("就绪")
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin: 10px 0;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
    
    def create_control_panel(self):
        """创建控制面板"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout()
        
        # 状态指示器
        self.status_label = QLabel("状态: 未运行")
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 5px 10px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
        """)
        
        # 控制按钮
        self.start_btn = QPushButton("启动Bot")
        self.stop_btn = QPushButton("停止Bot")
        self.restart_btn = QPushButton("重启Bot")
        
        self.start_btn.clicked.connect(self.start_bot)
        self.stop_btn.clicked.connect(self.stop_bot)
        self.restart_btn.clicked.connect(self.restart_bot)
        
        # 初始状态
        self.stop_btn.setEnabled(False)
        self.restart_btn.setEnabled(False)
        
        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(self.restart_btn)
        
        panel.setLayout(layout)
        return panel
    
    def setup_logging(self):
        """设置日志系统"""
        # 创建自定义日志处理器
        log_handler = LogHandler(self.log_widget)
        log_handler.setLevel(logging.INFO)
        
        # 设置格式
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        log_handler.setFormatter(formatter)
        
        # 添加到根日志记录器
        root_logger = logging.getLogger()
        root_logger.addHandler(log_handler)
        root_logger.setLevel(logging.INFO)
        
        # 初始日志
        self.log_widget.append_log("Discord Bot 管理器已启动")
    
    def start_bot(self):
        """启动Bot"""
        try:
            if self.bot_worker and self.bot_worker.isRunning():
                QMessageBox.warning(self, "警告", "Bot已在运行中")
                return
            
            # 检查配置
            if not os.path.exists("accounts.json"):
                QMessageBox.warning(self, "错误", "请先配置账户信息")
                return
            
            # 创建工作线程
            self.bot_worker = BotWorker()
            self.bot_worker.status_signal.connect(self.update_status)
            self.bot_worker.error_signal.connect(self.show_error)
            self.bot_worker.log_signal.connect(self.log_widget.append_log)
            
            # 启动线程
            self.bot_worker.start()
            
            # 更新UI
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.restart_btn.setEnabled(True)
            
            self.log_widget.append_log("正在启动Discord Bot...")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动失败: {str(e)}")
    
    def stop_bot(self):
        """停止Bot"""
        try:
            if self.bot_worker and self.bot_worker.isRunning():
                self.bot_worker.stop_bot()
                self.bot_worker.quit()
                self.bot_worker.wait(5000)  # 等待最多5秒
            
            # 更新UI
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.restart_btn.setEnabled(False)
            
            self.update_status("已停止")
            self.log_widget.append_log("Discord Bot已停止")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"停止失败: {str(e)}")
    
    def restart_bot(self):
        """重启Bot"""
        self.stop_bot()
        QTimer.singleShot(2000, self.start_bot)  # 2秒后重启
    
    def update_status(self, status):
        """更新状态显示"""
        self.status_label.setText(f"状态: {status}")
        self.statusBar().showMessage(status)
    
    def show_error(self, error):
        """显示错误信息"""
        QMessageBox.critical(self, "错误", error)
        self.log_widget.append_log(f"错误: {error}")
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.bot_worker and self.bot_worker.isRunning():
            reply = QMessageBox.question(self, "确认", "Bot正在运行，确定要退出吗？")
            if reply == QMessageBox.StandardButton.Yes:
                self.stop_bot()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Discord Bot Manager")
    app.setApplicationVersion("1.0")
    
    # 设置应用图标（如果有的话）
    # app.setWindowIcon(QIcon("icon.ico"))
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()