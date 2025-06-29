#!/usr/bin/env python3
"""
清理聊天历史中的重复消息
"""
import os
import sys
import logging
from chat_history import ChatHistoryManager
from config import Config

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """清理重复消息的主函数"""
    logger.info("开始清理重复消息...")
    
    # 获取所有聊天历史文件
    data_dir = "../data"
    if not os.path.exists(data_dir):
        data_dir = "data"  # 如果在根目录运行
        if not os.path.exists(data_dir):
            logger.warning("数据目录不存在")
            return
    
    total_cleaned = 0
    
    # 遍历所有聊天历史文件
    for filename in os.listdir(data_dir):
        if filename.startswith("chat_history_") and filename.endswith(".json"):
            # 提取channel_id
            channel_id = filename.replace("chat_history_", "").replace(".json", "")
            logger.info(f"处理频道 {channel_id} 的聊天记录...")
            
            try:
                # 创建聊天历史管理器
                chat_manager = ChatHistoryManager(channel_id)
                
                # 清理重复消息
                cleaned_count = chat_manager.remove_duplicate_messages()
                total_cleaned += cleaned_count
                
                logger.info(f"频道 {channel_id} 清理了 {cleaned_count} 条重复消息")
                
            except Exception as e:
                logger.error(f"处理频道 {channel_id} 时出错: {e}")
    
    logger.info(f"清理完成！总共清理了 {total_cleaned} 条重复消息")

if __name__ == "__main__":
    main()