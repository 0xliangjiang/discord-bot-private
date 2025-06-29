import requests
import time
import random
import logging
import re
import threading
import json
import os
import shutil
import glob
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from config import Config
from chat_history import ChatHistoryManager
from keyword_manager import KeywordManager

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class DiscordBot:
    """单个Discord账号的机器人实例"""
    
    def __init__(self, account_info):
        self.token = account_info['token']
        self.channel_id = account_info['channel_id']
        self.name = account_info.get('name', f'账号_{self.channel_id[-4:]}')
        
        # 公共配置
        self.ai_api_key = Config.AI_API_KEY
        self.ai_api_url = Config.AI_API_URL
        self.ai_model = Config.AI_MODEL
        self.language = Config.REPLY_LANGUAGE
        self.message_limit = Config.MESSAGE_LIMIT
        self.min_delay = Config.REPLY_DELAY_MIN
        self.max_delay = Config.REPLY_DELAY_MAX
        self.prompt_template = Config.AI_PROMPT_TEMPLATE
        
        self.running = False
        self.thread_id = threading.current_thread().ident
        
        # 初始化聊天历史管理器
        self.chat_history = ChatHistoryManager(self.channel_id)
        
        # 初始化关键词管理器
        self.keyword_manager = KeywordManager(Config.KEYWORD_RESPONSES_PATH)
        
        # Discord API base URL
        self.discord_api_base = "https://discord.com/api/v10"
        
        # Headers for Discord API
        self.discord_headers = {
            'Authorization': self.token,
            'Content-Type': 'application/json'
        }
        
        # Headers for AI API
        self.ai_headers = {
            'Authorization': f'Bearer {self.ai_api_key}',
            'Content-Type': 'application/json'
        }
        
        # 获取当前机器人用户信息
        self.bot_user_id = None
        self.bot_username = None
        self._get_bot_user_info()
    
    def _get_bot_user_info(self):
        """获取当前机器人的用户信息"""
        try:
            # 调用 Discord API 获取当前用户信息
            user_url = f"{self.discord_api_base}/users/@me"
            response = requests.get(user_url, headers=self.discord_headers, timeout=5)
            if response.status_code == 200:
                user_data = response.json()
                self.bot_user_id = user_data.get('id')
                self.bot_username = user_data.get('username')
                logger.info(f"[{self.name}] 获取机器人信息成功: {self.bot_username} (ID: {self.bot_user_id})")
            else:
                logger.warning(f"[{self.name}] 获取机器人信息失败: {response.status_code}")
        except Exception as e:
            logger.warning(f"[{self.name}] 获取机器人信息异常: {e}")
    
    def _is_my_message(self, user_id, username):
        """判断消息是否是当前机器人发出的"""
        if self.bot_user_id and user_id == self.bot_user_id:
            return True
        if self.bot_username and username == self.bot_username:
            return True
        return False
    
    def check_channel_activity(self, messages_data):
        """检查频道活跃度"""
        if not Config.ENABLE_ACTIVITY_MONITOR:
            return True, "活跃度监控已关闭"
        
        try:
            from datetime import timezone
            current_time = datetime.now(timezone.utc)
            cutoff_time = current_time - timedelta(minutes=Config.ACTIVITY_CHECK_MINUTES)
            
            # 统计活跃用户
            active_users = set()
            recent_message_count = 0
            
            for msg in messages_data:
                # 解析消息时间戳
                timestamp_str = msg.get('timestamp', '')
                if timestamp_str:
                    try:
                        # 直接解析Discord时间戳（通常已经是正确格式）
                        try:
                            msg_time = datetime.fromisoformat(timestamp_str)
                        except ValueError:
                            # 如果直接解析失败，尝试格式化
                            processed_timestamp = timestamp_str
                            
                            # 处理Z结尾的格式
                            if timestamp_str.endswith('Z'):
                                processed_timestamp = timestamp_str[:-1] + '+00:00'
                            # 如果没有时区信息，添加UTC
                            elif '+' not in timestamp_str and '-' not in timestamp_str[-6:]:
                                processed_timestamp = timestamp_str + '+00:00'
                            
                            msg_time = datetime.fromisoformat(processed_timestamp)
                        
                        # 确保时间戳有时区信息
                        if msg_time.tzinfo is None:
                            msg_time = msg_time.replace(tzinfo=timezone.utc)
                        
                        # 检查是否在时间窗口内
                        if msg_time >= cutoff_time:
                            user_id = msg.get('author', {}).get('id')
                            is_bot = msg.get('author', {}).get('bot', False)
                            content = msg.get('content', '')
                            
                            # 只统计非机器人的有效消息
                            if not is_bot and content and not re.search(r'[<>@http?0x]', content):
                                active_users.add(user_id)
                                recent_message_count += 1
                    except Exception as e:
                        logger.warning(f"[{self.name}] 跳过无效时间戳: {timestamp_str} - {e}")
                        continue
            
            is_active = len(active_users) >= Config.MIN_ACTIVE_USERS
            status_msg = f"活跃度检查: {len(active_users)}/{Config.MIN_ACTIVE_USERS}个用户, {recent_message_count}条消息 ({Config.ACTIVITY_CHECK_MINUTES}分钟内)"
            
            return is_active, status_msg
            
        except Exception as e:
            logger.error(f"[{self.name}] 活跃度检查失败: {e}")
            return True, "活跃度检查失败，默认允许"
    
    def get_messages(self):
        """获取频道最近的消息"""
        try:
            url = f"{self.discord_api_base}/channels/{self.channel_id}/messages"
            params = {'limit': self.message_limit}
            
            response = requests.get(url, headers=self.discord_headers, params=params)
            
            if response.status_code == 200:
                messages = response.json()
                
                # 检查频道活跃度
                is_active, activity_status = self.check_channel_activity(messages)
                logger.info(f"[{self.name}] {activity_status}")
                
                if not is_active:
                    logger.info(f"[{self.name}] 频道不够活跃，跳过AI回复")
                    return [], None, None
                
                # 过滤消息并提取内容
                filtered_messages = []
                target_user_id = None  # 用于存储白名单用户ID
                reply_to_message_id = None  # 用于存储要回复的消息ID
                
                has_new_message = False  # 标记是否有新的白名单用户消息
                new_user_messages = []  # 存储所有新的白名单用户消息（用于时间排序）
                
                for msg in messages:
                    content = msg.get('content', '')
                    user_id = msg.get('author', {}).get('id')
                    username = msg.get('author', {}).get('username', 'Unknown')
                    is_bot = msg.get('author', {}).get('bot', False)
                    msg_id = msg.get('id')  # 获取消息ID
                    message_reference = msg.get('message_reference')  # 检查是否为引用回复
                    
                    # 过滤掉包含特殊字符的消息
                    if content and not re.search(r'[<>@http?0x]', content):
                        # 如果开启白名单模式，只保留我和白名单用户的对话
                        if Config.ENABLE_WHITELIST_MODE:
                            # 检查是否为白名单用户或机器人消息
                            if self.chat_history.should_respond_to_user(user_id) or is_bot:
                                filtered_messages.append(content)
                                # 只存储白名单用户的新消息（不存储机器人消息）
                                if not is_bot and self.chat_history.should_respond_to_user(user_id):
                                    # 白名单模式：只有引用回复机器人消息时才回复
                                    should_respond = False
                                    if message_reference:
                                        # 获取被引用消息的ID
                                        referenced_msg_id = message_reference.get('message_id')
                                        
                                        # 先检查本地消息列表中是否有被引用的消息
                                        ref_is_bot = None
                                        logger.info(f"[{self.name}] 查找被引用消息ID: {referenced_msg_id}")
                                        
                                        for local_msg in messages:
                                            if local_msg.get('id') == referenced_msg_id:
                                                ref_user_id = local_msg.get('author', {}).get('id')
                                                ref_username = local_msg.get('author', {}).get('username', 'Unknown')
                                                ref_is_bot = self._is_my_message(ref_user_id, ref_username)
                                                logger.info(f"[{self.name}] 在本地找到被引用消息，作者: {ref_username} (ID: {ref_user_id}), 判定为本机器人: {ref_is_bot}")
                                                break
                                        
                                        # 如果本地找不到，再请求API
                                        if ref_is_bot is None:
                                            logger.info(f"[{self.name}] 本地未找到被引用消息，请求API获取详情")
                                            try:
                                                ref_url = f"{self.discord_api_base}/channels/{self.channel_id}/messages/{referenced_msg_id}"
                                                ref_response = requests.get(ref_url, headers=self.discord_headers, timeout=3)
                                                if ref_response.status_code == 200:
                                                    ref_msg = ref_response.json()
                                                    ref_user_id = ref_msg.get('author', {}).get('id')
                                                    ref_username = ref_msg.get('author', {}).get('username', 'Unknown')
                                                    ref_is_bot = self._is_my_message(ref_user_id, ref_username)
                                                    logger.info(f"[{self.name}] API获取成功，被引用消息作者: {ref_username} (ID: {ref_user_id}), 判定为本机器人: {ref_is_bot}")
                                                else:
                                                    # API请求失败，保守处理：跳过回复
                                                    logger.warning(f"[{self.name}] API请求失败 {ref_response.status_code}，跳过回复: {referenced_msg_id}")
                                                    ref_is_bot = False
                                            except Exception as e:
                                                logger.warning(f"[{self.name}] 检查引用消息异常，跳过回复: {e}")
                                                ref_is_bot = False
                                        
                                        # 根据被引用消息是否为本机器人消息决定是否回复
                                        if ref_is_bot:
                                            should_respond = True
                                            logger.info(f"[{self.name}] 白名单用户 {username} 引用回复本机器人消息，将生成AI回复: {content}")
                                        else:
                                            logger.info(f"[{self.name}] 白名单用户 {username} 引用回复其他用户消息，跳过AI回复: {content}")
                                    else:
                                        # 直接消息（非引用回复）不回复
                                        logger.info(f"[{self.name}] 白名单用户 {username} 发送直接消息，白名单模式不回复: {content}")
                                    
                                    if should_respond:
                                        is_new_message = self.chat_history.add_user_message(user_id, username, content, msg_id)
                                        if is_new_message:
                                            # 收集所有新消息，包含时间戳信息
                                            timestamp_str = msg.get('timestamp', '')
                                            new_user_messages.append({
                                                'user_id': user_id,
                                                'username': username,
                                                'content': content,
                                                'msg_id': msg_id,
                                                'timestamp': timestamp_str
                                            })
                                            has_new_message = True
                                            logger.info(f"[{self.name}] 检测到白名单用户 {username} 的新消息: {content}")
                        else:
                            # 未开启白名单模式，保留所有消息，不存储聊天记录
                            filtered_messages.append(content)
                            has_new_message = True  # 非白名单模式总是生成回复
                            # 记录最新非机器人消息的ID用于引用回复
                            if not is_bot and not reply_to_message_id:
                                reply_to_message_id = msg_id
                
                # 反转列表，按时间顺序排列
                filtered_messages.reverse()
                
                # 如果是白名单模式且有新消息，按时间顺序选择最早的用户回复
                if Config.ENABLE_WHITELIST_MODE and new_user_messages:
                    # 按时间戳排序，选择最早的消息
                    try:
                        from datetime import datetime
                        # 解析时间戳并排序
                        for msg_data in new_user_messages:
                            timestamp_str = msg_data['timestamp']
                            if timestamp_str:
                                try:
                                    # 尝试解析时间戳
                                    if timestamp_str.endswith('Z'):
                                        timestamp_str = timestamp_str[:-1] + '+00:00'
                                    msg_data['parsed_time'] = datetime.fromisoformat(timestamp_str)
                                except Exception:
                                    msg_data['parsed_time'] = datetime.now()  # 使用当前时间作为备选
                            else:
                                msg_data['parsed_time'] = datetime.now()
                        
                        # 按时间排序，最早的在前
                        new_user_messages.sort(key=lambda x: x['parsed_time'])
                        
                        # 选择最早的消息对应的用户
                        earliest_msg = new_user_messages[0]
                        target_user_id = earliest_msg['user_id']
                        reply_to_message_id = earliest_msg['msg_id']
                        
                        logger.info(f"[{self.name}] 白名单模式：按时间顺序回复最早消息的用户 {earliest_msg['username']}: {earliest_msg['content']}")
                    except Exception as e:
                        # 如果时间排序失败，使用第一个找到的用户
                        if new_user_messages:
                            target_user_id = new_user_messages[0]['user_id']
                            reply_to_message_id = new_user_messages[0]['msg_id']
                        logger.warning(f"[{self.name}] 时间排序失败，使用第一个用户: {e}")
                
                if Config.ENABLE_WHITELIST_MODE:
                    logger.info(f"[{self.name}] 白名单模式：获取到 {len(filtered_messages)} 条消息，回复用户: {target_user_id if target_user_id else '无'}")
                else:
                    logger.info(f"[{self.name}] 普通模式：获取到 {len(filtered_messages)} 条消息，将生成回复")
                
                return filtered_messages, target_user_id, reply_to_message_id
            else:
                logger.error(f"[{self.name}] 获取消息失败: {response.status_code}")
                return [], None, None
        except Exception as e:
            logger.error(f"[{self.name}] 请求错误: {e}")
            return [], None, None
    
    def generate_response(self, messages, target_user_id=None):
        """白名单模式：使用智能回复生成"""
        if not messages:
            return ''
        
        try:
            # 优先检查关键词匹配（使用最新的用户消息）
            if target_user_id and target_user_id in self.chat_history.chat_history:
                conversations = self.chat_history.chat_history[target_user_id]['conversations']
                if conversations:
                    # 找到最新的用户消息
                    latest_user_message = None
                    for conv in reversed(conversations):
                        if conv['type'] == 'user':
                            latest_user_message = conv['message']
                            break
                    
                    if latest_user_message:
                        keyword_response = self.keyword_manager.match_keyword(latest_user_message)
                        if keyword_response:
                            logger.info(f"[{self.name}] 关键词匹配回复: {latest_user_message} -> {keyword_response}")
                            # 记录关键词回复到历史
                            self.chat_history.add_bot_reply(target_user_id, keyword_response)
                            # 返回特殊标记，表示这是关键词回复
                            return f"KEYWORD_REPLY:{keyword_response}"
            
            # 获取历史上下文
            history_context = self.chat_history.get_context_for_ai(target_user_id)
            logger.info(f"[{self.name}] 开始AI生成，目标用户: {target_user_id}")
            
            # 选择使用自定义模板还是专门的白名单提示词
            if Config.USE_CUSTOM_TEMPLATE_FOR_WHITELIST:
                # 使用自定义AI模板
                whitelist_prompt = self.prompt_template.format(
                    language=self.language,
                    history_context=history_context
                )
            else:
                # 使用专门的白名单提示词
                whitelist_prompt = f"""你是个游戏玩家在聊天。重要：只回复最新的那条消息！

回复要求：
- 针对最新消息回答，不要混合其他话题
- 长度3-20字，自然变化
- 口语化，98%的回复不用emoji，极偶尔用😂
- 不要反问句！多用陈述句，像真人一样随意回复
- 不要标点符号，直接文字回复
- 避免语气助词：不要用"呀、嘛、啦、呢"等
- 简单直接，别想太多

{history_context}

最新消息（只回复这个）：
"""
            
            # 取最新消息和少量上下文
            if messages:
                latest_message = messages[-1]  # 最新消息
                context_messages = messages[-3:-1] if len(messages) > 1 else []  # 前2条作为上下文
                
                context_text = ""
                if context_messages:
                    context_text = "参考上下文：\n" + '\n'.join(context_messages) + "\n\n"
                
                full_prompt = whitelist_prompt + context_text + latest_message
            else:
                full_prompt = whitelist_prompt + "无消息"
            
            # 超字数重复生成机制，最多尝试3次
            max_retries = 3
            for retry in range(max_retries):
                try:
                    # 准备API请求数据
                    data = {
                        'model': self.ai_model,
                        'messages': [{'role': 'user', 'content': full_prompt}],
                        'stream': False
                    }
                    
                    logger.info(f"[{self.name}] 白名单模式发送AI请求，重试次数: {retry+1}")
                    response = requests.post(self.ai_api_url, headers=self.ai_headers, json=data, timeout=15)
                    logger.info(f"[{self.name}] 白名单模式AI响应状态码: {response.status_code}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        ai_response = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                        logger.info(f"[{self.name}] 白名单模式原始AI回复: {ai_response}")
                        
                        # 简化的回复处理，只保留基本清理和字数限制
                        if ai_response:
                            # 移除"我:"开头的内容
                            ai_response = ai_response.replace("我:", "").replace("我：", "")
                            # 移除换行符，只取第一句
                            ai_response = ai_response.split('\n')[0].strip()
                            
                            # 限制字数（20字以内）
                            if len(ai_response) > 30:
                                if retry < max_retries - 1:
                                    logger.warning(f"[{self.name}] 回复过长({len(ai_response)}字)，重试第{retry+1}次: {ai_response}")
                                    continue
                                else:
                                    logger.warning(f"[{self.name}] 多次重试仍超字数，跳过发言: {ai_response}")
                                    return ''
                            
                            # 过滤空回复
                            if not ai_response or len(ai_response.strip()) == 0:
                                if retry < max_retries - 1:
                                    logger.warning(f"[{self.name}] 空回复，重试第{retry+1}次")
                                    continue
                                else:
                                    logger.warning(f"[{self.name}] 多次重试仍为空回复，跳过发言")
                                    return ''
                            
                            # 如果通过检查，跳出重试循环
                            break
                    else:
                        logger.error(f"[{self.name}] 白名单模式AI生成失败: {response.status_code}")
                        if retry < max_retries - 1:
                            continue
                        return ''
                except requests.exceptions.Timeout:
                    logger.warning(f"[{self.name}] AI请求超时，重试第{retry+1}次")
                    if retry < max_retries - 1:
                        continue
                    return ''
                except Exception as e:
                    logger.error(f"[{self.name}] AI请求异常: {e}")
                    if retry < max_retries - 1:
                        continue
                    return ''
            
            # 循环结束后检查是否有有效回复
            if ai_response:
                logger.info(f"[{self.name}] 白名单模式AI生成结果: {ai_response}")
                
                # 如果有目标用户，存储机器人回复
                if target_user_id and ai_response:
                    self.chat_history.add_bot_reply(target_user_id, ai_response)
                
                return ai_response
            else:
                logger.warning(f"[{self.name}] 白名单模式AI生成失败，返回空回复")
                return ''
        except Exception as e:
            logger.error(f"[{self.name}] 白名单模式AI请求错误: {e}")
            return ''
    
    def generate_response_simple(self, messages):
        """普通模式：使用配置的提示词生成回复，不记录历史"""
        if not messages:
            return ''
        
        try:
            # 优先检查关键词匹配（使用最新消息）
            if messages:
                latest_message = messages[-1]  # 获取最新消息
                keyword_response = self.keyword_manager.match_keyword(latest_message)
                if keyword_response:
                    logger.info(f"[{self.name}] 普通模式关键词匹配回复: {latest_message} -> {keyword_response}")
                    # 返回特殊标记，表示这是关键词回复
                    return f"KEYWORD_REPLY:{keyword_response}"
            # 普通模式使用简化的提示词
            prompt = f"""你是个游戏玩家在随意聊天。重要：只回复最新的那条消息！

回复要求：
- 针对最新消息直接回答
- 长度3-20字
- 口语化，98%回复不用emoji，极偶尔用😂
- 不要反问句！多用陈述句，像真人一样随意回复
- 不要标点符号，直接文字回复
- 避免语气助词：不要用"呀、嘛、啦、呢"等
- 别想太多，简单自然

最新消息（只回复这个）：
"""
            
            # 只传递最新消息给普通模式
            if messages:
                latest_message = messages[-1]
                full_prompt = prompt + latest_message
            else:
                full_prompt = prompt + "无消息"
            
            # 超字数重复生成机制，最多尝试3次
            max_retries = 3
            for retry in range(max_retries):
                try:
                    # 准备API请求数据
                    data = {
                        'model': self.ai_model,
                        'messages': [{'role': 'user', 'content': full_prompt}],
                        'stream': False
                    }
                    
                    logger.info(f"[{self.name}] 普通模式发送AI请求，重试次数: {retry+1}")
                    response = requests.post(self.ai_api_url, headers=self.ai_headers, json=data, timeout=15)
                    logger.info(f"[{self.name}] 普通模式AI响应状态码: {response.status_code}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        ai_response = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                        logger.info(f"[{self.name}] 普通模式原始AI回复: {ai_response}")
                    
                        # 简化的回复处理，只保留基本清理和字数限制
                        if ai_response:
                            # 移除"我:"开头的内容
                            ai_response = ai_response.replace("我:", "").replace("我：", "")
                            # 移除换行符，只取第一句
                            ai_response = ai_response.split('\n')[0].strip()
                            
                            # 限制字数（20字以内）
                            if len(ai_response) > 30:
                                if retry < max_retries - 1:
                                    logger.warning(f"[{self.name}] 普通模式回复过长({len(ai_response)}字)，重试第{retry+1}次: {ai_response}")
                                    continue
                                else:
                                    logger.warning(f"[{self.name}] 普通模式多次重试仍超字数，跳过发言: {ai_response}")
                                    return ''
                            
                            # 过滤空回复
                            if not ai_response or len(ai_response.strip()) == 0:
                                if retry < max_retries - 1:
                                    logger.warning(f"[{self.name}] 普通模式空回复，重试第{retry+1}次")
                                    continue
                                else:
                                    logger.warning(f"[{self.name}] 普通模式多次重试仍为空回复，跳过发言")
                                    return ''
                            
                            # 如果通过检查，跳出重试循环
                            break
                    else:
                        logger.error(f"[{self.name}] 普通模式AI生成失败: {response.status_code}")
                        if retry < max_retries - 1:
                            continue
                        return ''
                except requests.exceptions.Timeout:
                    logger.warning(f"[{self.name}] 普通模式AI请求超时，重试第{retry+1}次")
                    if retry < max_retries - 1:
                        continue
                    return ''
                except Exception as e:
                    logger.error(f"[{self.name}] 普通模式AI请求异常: {e}")
                    if retry < max_retries - 1:
                        continue
                    return ''
                
            logger.info(f"[{self.name}] 普通模式AI生成结果: {ai_response}")
            return ai_response
        except Exception as e:
            logger.error(f"[{self.name}] 普通模式AI请求错误: {e}")
            return ''
    
    def send_message(self, message, reply_to_message_id=None):
        """发送消息到频道，支持引用回复"""
        if not message:
            return False
        
        try:
            url = f"{self.discord_api_base}/channels/{self.channel_id}/messages"
            data = {
                'content': message,
                'tts': False
            }
            
            # 如果有要回复的消息ID，添加引用回复
            if reply_to_message_id:
                data['message_reference'] = {
                    'channel_id': self.channel_id,
                    'message_id': reply_to_message_id
                }
                logger.info(f"[{self.name}] 准备引用回复消息ID: {reply_to_message_id}")
            
            response = requests.post(url, headers=self.discord_headers, json=data)

            if response.status_code == 200:
                logger.info(f"[{self.name}] 发送成功: {message}")
                return True
            else:
                logger.error(f"[{self.name}] 发送失败: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"[{self.name}] 发送错误: {e}")
            return False
    
    def get_random_delay(self):
        """获取随机延迟时间"""
        return random.randint(self.min_delay, self.max_delay)
    
    def run(self):
        """运行单个机器人实例"""
        logger.info(f"[{self.name}] 机器人启动，线程ID: {threading.current_thread().ident}")
        self.running = True
        
        while self.running:
            try:
                # 获取消息
                messages, target_user_id, reply_to_message_id = self.get_messages()
                
                if messages:
                    # 如果开启白名单模式，检查是否有白名单用户的新消息
                    if Config.ENABLE_WHITELIST_MODE:
                        if not target_user_id:
                            # logger.debug(f"[{self.name}] 白名单模式：没有白名单用户的新消息，跳过发言")
                            # 随机延迟
                            delay = self.get_random_delay()
                            logger.info(f"[{self.name}] 等待 {delay} 秒...")
                            time.sleep(delay)
                            continue
                        
                        # 白名单模式：生成回复并记录到历史
                        ai_response = self.generate_response(messages, target_user_id)
                        
                        if ai_response:
                            # 检查是否为关键词回复
                            if ai_response.startswith("KEYWORD_REPLY:"):
                                # 关键词回复使用引用回复
                                actual_response = ai_response[14:]  # 移除"KEYWORD_REPLY:"前缀
                                self.send_message(actual_response, reply_to_message_id)
                                logger.info(f"[{self.name}] 关键词引用回复已发送: {actual_response}")
                            else:
                                # 普通AI回复使用引用回复
                                logger.info(f"[{self.name}] 准备发送白名单AI回复: {ai_response}")
                                self.send_message(ai_response, reply_to_message_id)
                                logger.info(f"[{self.name}] 白名单AI回复已发送: {ai_response}")
                        else:
                            logger.warning(f"[{self.name}] 白名单模式未生成有效回复")
                    else:
                        # 普通模式：直接生成回复，不记录历史
                        ai_response = self.generate_response_simple(messages)
                        
                        if ai_response:
                            # 检查是否为关键词回复
                            if ai_response.startswith("KEYWORD_REPLY:"):
                                # 关键词回复使用引用回复
                                actual_response = ai_response[14:]  # 移除"KEYWORD_REPLY:"前缀
                                self.send_message(actual_response, reply_to_message_id)
                                logger.info(f"[{self.name}] 普通模式关键词引用回复已发送: {actual_response}")
                            else:
                                # 普通AI回复直接发送
                                self.send_message(ai_response)
                
                # 随机延迟
                delay = self.get_random_delay()
                logger.info(f"[{self.name}] 等待 {delay} 秒...")
                time.sleep(delay)
                
            except Exception as e:
                logger.error(f"[{self.name}] 循环中发生错误: {e}")
                logger.info(f"[{self.name}] 等待60秒后重试...")
                time.sleep(60)
    
    def stop(self):
        """停止机器人"""
        self.running = False
        logger.info(f"[{self.name}] 机器人已停止")

class MultiAccountBotManager:
    """多账号机器人管理器"""
    
    def __init__(self):
        self.accounts = Config.get_discord_accounts()
        self.bots = []
        self.executor = None
        self.futures = []
        self.running = False
    
    def create_bots(self):
        """创建所有机器人实例"""
        self.bots = []
        for account in self.accounts:
            bot = DiscordBot(account)
            self.bots.append(bot)
        logger.info(f"创建了 {len(self.bots)} 个机器人实例")
    
    def clear_data_directory(self):
        """清空data目录下的聊天记录文件"""
        if not Config.CLEAR_DATA_ON_RESTART:
            return
        
        data_dir = "data"
        try:
            if os.path.exists(data_dir):
                # 获取所有聊天记录文件
                chat_files = glob.glob(os.path.join(data_dir, "chat_history_*.json"))
                
                if chat_files:
                    logger.info(f"正在清空 {len(chat_files)} 个聊天记录文件...")
                    for file_path in chat_files:
                        try:
                            os.remove(file_path)
                            # logger.debug(f"已删除: {file_path}")
                        except Exception as e:
                            logger.warning(f"删除文件失败 {file_path}: {e}")
                    logger.info("聊天记录清空完成，将获取最新对话")
                else:
                    logger.info("data目录下没有找到聊天记录文件")
            else:
                logger.info("data目录不存在，将自动创建")
                os.makedirs(data_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"清空data目录失败: {e}")
    
    def start_all(self):
        """启动所有机器人"""
        if not self.accounts:
            logger.error("没有找到Discord账号配置")
            return
        
        logger.info("正在启动多账号机器人管理器...")
        
        # 清空数据目录（如果配置了）
        self.clear_data_directory()
        
        # 验证配置
        try:
            Config.validate_config()
        except ValueError as e:
            logger.error(f"配置验证失败: {e}")
            return
        
        # 创建机器人实例
        self.create_bots()
        
        # 使用线程池启动所有机器人
        max_workers = min(len(self.bots), Config.MAX_WORKERS)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.running = True
        
        logger.info(f"使用 {max_workers} 个线程启动 {len(self.bots)} 个机器人")
        
        # 提交所有机器人任务
        for bot in self.bots:
            future = self.executor.submit(bot.run)
            self.futures.append(future)
        
        logger.info("所有机器人已启动")
        
        try:
            # 等待所有任务完成或被中断
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("接收到停止信号，正在关闭所有机器人...")
            self.stop_all()
    
    def stop_all(self):
        """停止所有机器人"""
        logger.info("正在停止所有机器人...")
        self.running = False
        
        # 停止所有机器人实例
        for bot in self.bots:
            bot.stop()
        
        # 关闭线程池
        if self.executor:
            self.executor.shutdown(wait=True)
        
        logger.info("所有机器人已停止")
    
    def get_status(self):
        """获取所有机器人状态"""
        status = {
            'total_bots': len(self.bots),
            'running_bots': sum(1 for bot in self.bots if bot.running),
            'accounts': []
        }
        
        for bot in self.bots:
            account_status = {
                'name': bot.name,
                'channel_id': bot.channel_id,
                'running': bot.running,
                'thread_id': bot.thread_id
            }
            status['accounts'].append(account_status)
        
        return status

def main():
    """主函数"""
    manager = MultiAccountBotManager()
    
    try:
        manager.start_all()
    except Exception as e:
        logger.error(f"程序启动失败: {e}")
    finally:
        manager.stop_all()

if __name__ == "__main__":
    main()