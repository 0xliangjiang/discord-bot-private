import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional
from config import Config

logger = logging.getLogger(__name__)

class ChatHistoryManager:
    """聊天记录管理器"""
    
    def __init__(self, channel_id: str, whitelist_users: List[str] = None):
        self.channel_id = channel_id
        self.history_file = f"data/chat_history_{channel_id}.json"
        self.chat_history = {}
        self.whitelist_users = whitelist_users or []
        self.enable_whitelist = Config.ENABLE_WHITELIST_MODE
        self.max_length = Config.CHAT_HISTORY_MAX_LENGTH
        self.last_processed_messages = {}  # 记录每个用户最后处理的消息
        
        # 确保数据目录存在
        os.makedirs("data", exist_ok=True)
        
        # 加载历史记录
        self.load_history()
    
    def load_history(self):
        """加载聊天历史记录"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.chat_history = json.load(f)
                
                # 转换list为set以便快速查找
                for user_id, data in self.chat_history.items():
                    if 'processed_message_ids' in data:
                        data['processed_message_ids'] = set(data['processed_message_ids'])
                    else:
                        data['processed_message_ids'] = set()
                
                logger.info(f"加载聊天历史记录: {len(self.chat_history)} 个用户")
            else:
                self.chat_history = {}
        except Exception as e:
            logger.error(f"加载聊天历史记录失败: {e}")
            self.chat_history = {}
    
    def save_history(self):
        """保存聊天历史记录"""
        try:
            # 转换set为list以便JSON序列化
            history_to_save = {}
            for user_id, data in self.chat_history.items():
                history_to_save[user_id] = {
                    'username': data['username'],
                    'conversations': data['conversations']
                }
                if 'processed_message_ids' in data:
                    history_to_save[user_id]['processed_message_ids'] = list(data['processed_message_ids'])
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history_to_save, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存聊天历史记录失败: {e}")
    
    def is_whitelisted_user(self, user_id: str) -> bool:
        """检查用户是否在白名单中"""
        if not self.enable_whitelist:
            return True
        return user_id in self.whitelist_users
    
    def add_user_message(self, user_id: str, username: str, message: str, msg_id: str = None):
        """添加用户消息到历史记录"""
        if not self.is_whitelisted_user(user_id):
            return False
        
        if user_id not in self.chat_history:
            self.chat_history[user_id] = {
                'username': username,
                'conversations': [],
                'processed_message_ids': set()  # 记录已处理的消息ID
            }
        
        # 更新用户名（可能会变化）
        self.chat_history[user_id]['username'] = username
        
        # 确保processed_message_ids存在
        if 'processed_message_ids' not in self.chat_history[user_id]:
            self.chat_history[user_id]['processed_message_ids'] = set()
        
        # 基于消息ID去重（最可靠的方式）
        if msg_id and msg_id in self.chat_history[user_id]['processed_message_ids']:
            # logger.debug(f"跳过已处理的消息ID {msg_id}: {username}({user_id}): {message}")
            return False
        
        # 检查是否为已处理的消息（基于内容和时间窗口）
        current_time = datetime.now()
        message_key = f"{user_id}:{message}"
        
        # 检查是否在短时间内处理过相同消息（5分钟内）
        if hasattr(self, '_recent_messages'):
            for key, timestamp in list(self._recent_messages.items()):
                # 清理5分钟前的记录
                if (current_time - timestamp).total_seconds() > 300:
                    del self._recent_messages[key]
            
            if message_key in self._recent_messages:
                # logger.debug(f"跳过5分钟内的重复消息: {username}({user_id}): {message}")
                return False
        else:
            self._recent_messages = {}
        
        # 添加用户消息
        conversation_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'user',
            'message': message
        }
        
        if msg_id:
            conversation_entry['msg_id'] = msg_id
        
        self.chat_history[user_id]['conversations'].append(conversation_entry)
        
        # 记录已处理的消息ID和时间
        if msg_id:
            self.chat_history[user_id]['processed_message_ids'].add(msg_id)
        self._recent_messages[message_key] = current_time
        
        # 限制历史记录长度
        if len(self.chat_history[user_id]['conversations']) > self.max_length:
            self.chat_history[user_id]['conversations'] = \
                self.chat_history[user_id]['conversations'][-self.max_length:]
        
        # 限制processed_message_ids的大小（保留最近1000个）
        if len(self.chat_history[user_id]['processed_message_ids']) > 1000:
            # 转换为列表，保留最近的500个
            ids_list = list(self.chat_history[user_id]['processed_message_ids'])
            self.chat_history[user_id]['processed_message_ids'] = set(ids_list[-500:])
        
        self.save_history()
        logger.info(f"保存用户消息: {username}({user_id}): {message}")
        return True
    
    def add_bot_reply(self, user_id: str, reply: str):
        """添加机器人回复到历史记录"""
        if not self.is_whitelisted_user(user_id) or user_id not in self.chat_history:
            return
        
        # 检查是否为重复回复（检查最近的几条机器人消息）
        conversations = self.chat_history[user_id]['conversations']
        recent_bot_messages = [conv['message'] for conv in conversations[-5:] if conv['type'] == 'bot']
        if reply in recent_bot_messages:
            # logger.debug(f"跳过重复回复给用户 {user_id}: {reply}")
            return
        
        conversation_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'bot',
            'message': reply
        }
        
        self.chat_history[user_id]['conversations'].append(conversation_entry)
        
        # 限制历史记录长度
        if len(self.chat_history[user_id]['conversations']) > self.max_length:
            self.chat_history[user_id]['conversations'] = \
                self.chat_history[user_id]['conversations'][-self.max_length:]
        
        self.save_history()
        logger.info(f"保存机器人回复给用户 {user_id}: {reply}")
    
    def get_user_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """获取用户的聊天历史"""
        if user_id not in self.chat_history:
            return []
        
        conversations = self.chat_history[user_id]['conversations']
        return conversations[-limit:] if limit > 0 else conversations
    
    def get_context_for_ai(self, user_id: str = None) -> str:
        """获取用于AI的上下文信息"""
        if not self.enable_whitelist or not user_id or user_id not in self.chat_history:
            return ""
        
        user_history = self.get_user_history(user_id, limit=10)
        if not user_history:
            return ""
        
        # 构建对话历史上下文
        context_parts = []
        username = self.chat_history[user_id]['username']
        
        # 找到用户的最新消息
        latest_user_message = None
        for entry in reversed(user_history):
            if entry['type'] == 'user':
                latest_user_message = entry['message']
                break
        
        context_parts.append(f"\\n\\n与{username}的对话历史：")
        
        # 显示历史对话（最近8条）
        recent_history = user_history[-8:]
        for entry in recent_history:
            if entry['type'] == 'user':
                context_parts.append(f"{username}: {entry['message']}")
            else:
                context_parts.append(f"我: {entry['message']}")
        
        # 强调最新消息
        if latest_user_message:
            context_parts.append(f"\\n{username}最新说: {latest_user_message}")
            context_parts.append("\\n记住：要像真人朋友回复，别太完美，偶尔有点慢反应或者岔话题都行。")
        
        return "\\n".join(context_parts)
    
    def should_respond_to_user(self, user_id: str) -> bool:
        """判断是否应该回复某个用户"""
        if not self.enable_whitelist:
            return True
        return self.is_whitelisted_user(user_id)
    
    def get_all_users_stats(self) -> Dict:
        """获取所有用户的聊天统计"""
        stats = {}
        for user_id, data in self.chat_history.items():
            stats[user_id] = {
                'username': data['username'],
                'total_messages': len(data['conversations']),
                'user_messages': len([c for c in data['conversations'] if c['type'] == 'user']),
                'bot_replies': len([c for c in data['conversations'] if c['type'] == 'bot'])
            }
        return stats
    
    def clear_user_history(self, user_id: str):
        """清除指定用户的聊天历史"""
        if user_id in self.chat_history:
            del self.chat_history[user_id]
            self.save_history()
            logger.info(f"已清除用户 {user_id} 的聊天历史")
    
    def clear_all_history(self):
        """清除所有聊天历史"""
        self.chat_history = {}
        self.save_history()
        logger.info("已清除所有聊天历史")
    
    def remove_duplicate_messages(self):
        """清理重复的消息记录"""
        cleaned_count = 0
        
        for user_id, data in self.chat_history.items():
            conversations = data['conversations']
            cleaned_conversations = []
            seen_messages = set()
            
            for conv in conversations:
                # 创建消息的唯一标识
                message_key = f"{conv['type']}:{conv['message']}"
                
                # 如果是新消息或者时间间隔超过1小时，则保留
                if message_key not in seen_messages:
                    cleaned_conversations.append(conv)
                    seen_messages.add(message_key)
                else:
                    cleaned_count += 1
                    # logger.debug(f"移除重复消息: {conv['message']}")
            
            # 更新对话记录
            data['conversations'] = cleaned_conversations
        
        if cleaned_count > 0:
            self.save_history()
            logger.info(f"清理完成，移除了 {cleaned_count} 条重复消息")
            return cleaned_count
        else:
            logger.info("没有发现重复消息")
            return 0