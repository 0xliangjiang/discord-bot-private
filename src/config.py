import os
import json
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class Config:
    # AI设置
    AI_API_KEY = os.getenv('AI_API_KEY')
    AI_API_URL = os.getenv('AI_API_URL', 'https://geekai.dev/api/v1/chat/completions')
    AI_MODEL = os.getenv('AI_MODEL', 'gpt-4o-mini')
    
    # 机器人行为设置
    MESSAGE_LIMIT = int(os.getenv('MESSAGE_LIMIT', '20'))
    REPLY_DELAY_MIN = int(os.getenv('REPLY_DELAY_MIN', '300'))
    REPLY_DELAY_MAX = int(os.getenv('REPLY_DELAY_MAX', '350'))
    REPLY_LANGUAGE = os.getenv('REPLY_LANGUAGE', '中文')
    
    # 线程设置
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', '4'))
    
    # 白名单设置
    WHITELIST_USERS = os.getenv('WHITELIST_USERS', '')
    ENABLE_WHITELIST_MODE = os.getenv('ENABLE_WHITELIST_MODE', 'false').lower() == 'true'
    
    # 聊天记录设置
    CHAT_HISTORY_MAX_LENGTH = int(os.getenv('CHAT_HISTORY_MAX_LENGTH', '50'))
    
    # 活跃度监控设置
    ENABLE_ACTIVITY_MONITOR = os.getenv('ENABLE_ACTIVITY_MONITOR', 'true').lower() == 'true'
    ACTIVITY_CHECK_MINUTES = int(os.getenv('ACTIVITY_CHECK_MINUTES', '10'))
    MIN_ACTIVE_USERS = int(os.getenv('MIN_ACTIVE_USERS', '5'))
    
    # 关键词自动回复设置
    KEYWORD_RESPONSES_PATH = os.getenv('KEYWORD_RESPONSES_PATH', 'keyword_responses.json')
    
    # 白名单模式是否使用自定义AI模板
    USE_CUSTOM_TEMPLATE_FOR_WHITELIST = os.getenv('USE_CUSTOM_TEMPLATE_FOR_WHITELIST', 'false').lower() == 'true'
    
    # 是否在重启时清空聊天记录
    CLEAR_DATA_ON_RESTART = os.getenv('CLEAR_DATA_ON_RESTART', 'false').lower() == 'true'
    
    # 机器人账号识别设置
    BOT_USERNAMES = os.getenv('BOT_USERNAMES', '').split(',')
    
    # AI提示词模板
    AI_PROMPT_TEMPLATE = os.getenv('AI_PROMPT_TEMPLATE', 
        '你是一个资深web3从业者，对各种撸毛词汇和行话了如指掌，精通各大交易所操作，交易经验丰富，能够根据不同社群氛围灵活调整聊天风格。你幽默风趣，轻松化解社群尴尬，擅长加入他们的对话，精通语言且能与各国人交流，擅用web3行话、撸毛术语，随时带动气氛。现在在discord社群与陌生人互动，你只能看到20条聊天记录，并且你只能发10个字用来总结这20条记录、符合逻辑、句子通顺、简洁直白的方式混入他们当中，不要被管理员发现你是AI，保持活跃，避免尴尬,并且用{language}生成。你的语言风格可以嘻哈、随意，但要与当前聊天内容相关，避免美式俚语和玩笑，不鼓励他人行为，避免使用任何标点符号，避免使用任何禁忌词汇（包括煽动性、色情、脚本和机器人相关内容）。{history_context}消息内容：')
    
    @classmethod
    def get_whitelist_users(cls):
        """获取白名单用户ID列表"""
        if not cls.WHITELIST_USERS:
            return []
        
        try:
            # 支持逗号分隔的用户ID
            user_ids = [uid.strip() for uid in cls.WHITELIST_USERS.split(',') if uid.strip()]
            return user_ids
        except Exception as e:
            logger.warning(f"解析白名单用户失败: {e}")
            return []
    
    @classmethod
    def get_discord_accounts(cls):
        """获取Discord账号配置列表"""
        accounts = []
        
        # 方式1: 尝试从环境变量读取JSON配置
        accounts_str = os.getenv('DISCORD_ACCOUNTS', '')
        if accounts_str:
            try:
                # 清理字符串，移除换行符和多余空格
                cleaned_str = accounts_str.replace('\n', '').replace('\r', '').strip()
                accounts = json.loads(cleaned_str)
                if accounts:
                    return accounts
            except json.JSONDecodeError as e:
                logger.warning(f"解析DISCORD_ACCOUNTS失败: {e}")
        
        # 方式2: 尝试从配置文件读取
        try:
            with open('accounts.json', 'r', encoding='utf-8') as f:
                accounts = json.load(f)
                if accounts:
                    return accounts
        except FileNotFoundError:
            pass
        except json.JSONDecodeError as e:
            logger.warning(f"解析accounts.json失败: {e}")
        
        # 方式3: 向后兼容单账号配置
        single_token = os.getenv('DISCORD_TOKEN')
        single_channel = os.getenv('TARGET_CHANNEL_ID')
        if single_token and single_channel:
            return [{
                'token': single_token,
                'channel_id': single_channel,
                'name': '默认账号'
            }]
        
        return []
    
    @classmethod
    def validate_config(cls):
        """验证配置是否正确"""
        # 检查AI配置
        if not cls.AI_API_KEY:
            raise ValueError("缺少必需的环境变量: AI_API_KEY")
        
        # 检查Discord账号配置
        accounts = cls.get_discord_accounts()
        if not accounts:
            raise ValueError("未找到Discord账号配置，请设置DISCORD_ACCOUNTS或使用单账号配置")
        
        # 验证每个账号配置
        for i, account in enumerate(accounts):
            if not account.get('token'):
                raise ValueError(f"账号{i+1}缺少token配置")
            if not account.get('channel_id'):
                raise ValueError(f"账号{i+1}缺少channel_id配置")
        
        return True