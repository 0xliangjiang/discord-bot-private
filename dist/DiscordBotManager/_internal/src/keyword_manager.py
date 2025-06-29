import json
import random
import re
import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

class KeywordManager:
    """关键词自动回复管理器"""
    
    def __init__(self, config_path: str = "keyword_responses.json"):
        self.config_path = config_path
        self.config = {}
        self.enabled = True
        self.load_config()
    
    def load_config(self):
        """加载关键词配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            settings = self.config.get('settings', {})
            self.enabled = settings.get('enable_keyword_responses', True)
            self.match_priority = settings.get('match_priority', ['exact_match', 'contains_match', 'regex_match'])
            self.random_response = settings.get('random_response', True)
            self.fallback_to_ai = settings.get('fallback_to_ai', True)
            
            logger.info(f"词库配置加载成功，共 {self._count_keywords()} 个关键词")
        except FileNotFoundError:
            logger.warning(f"词库配置文件不存在: {self.config_path}")
            self.enabled = False
        except json.JSONDecodeError as e:
            logger.error(f"词库配置文件格式错误: {e}")
            self.enabled = False
        except Exception as e:
            logger.error(f"加载词库配置失败: {e}")
            self.enabled = False
    
    def _count_keywords(self) -> int:
        """统计关键词总数"""
        count = 0
        rules = self.config.get('rules', {})
        for rule_type in rules.values():
            if isinstance(rule_type, dict) and 'responses' in rule_type:
                count += len(rule_type['responses'])
        return count
    
    def match_keyword(self, message: str) -> Optional[str]:
        """匹配关键词并返回回复"""
        if not self.enabled or not message:
            return None
        
        message = message.strip().lower()
        rules = self.config.get('rules', {})
        
        # 按优先级顺序匹配
        for match_type in self.match_priority:
            if match_type not in rules:
                continue
            
            response = None
            if match_type == 'exact_match':
                response = self._exact_match(message, rules[match_type])
            elif match_type == 'contains_match':
                response = self._contains_match(message, rules[match_type])
            elif match_type == 'regex_match':
                response = self._regex_match(message, rules[match_type])
            
            if response:
                logger.info(f"关键词匹配成功 [{match_type}]: {message} -> {response}")
                return response
        
        return None
    
    def _exact_match(self, message: str, rule: Dict) -> Optional[str]:
        """精确匹配"""
        responses = rule.get('responses', {})
        for keyword, reply_list in responses.items():
            if message == keyword.lower():
                return self._select_response(reply_list)
        return None
    
    def _contains_match(self, message: str, rule: Dict) -> Optional[str]:
        """包含匹配"""
        responses = rule.get('responses', {})
        for keyword, reply_list in responses.items():
            if keyword.lower() in message:
                return self._select_response(reply_list)
        return None
    
    def _regex_match(self, message: str, rule: Dict) -> Optional[str]:
        """正则匹配"""
        responses = rule.get('responses', {})
        for pattern, reply_list in responses.items():
            try:
                if re.search(pattern, message, re.IGNORECASE):
                    return self._select_response(reply_list)
            except re.error as e:
                logger.warning(f"正则表达式错误: {pattern} - {e}")
        return None
    
    def _select_response(self, reply_list: List[str]) -> str:
        """从回复列表中选择一个回复"""
        if not reply_list:
            return ""
        
        if self.random_response:
            return random.choice(reply_list)
        else:
            return reply_list[0]
    
    def reload_config(self):
        """重新加载配置"""
        logger.info("重新加载词库配置...")
        self.load_config()
    
    def add_keyword(self, match_type: str, keyword: str, responses: List[str]):
        """动态添加关键词"""
        if not self.config.get('rules'):
            self.config['rules'] = {}
        
        if match_type not in self.config['rules']:
            self.config['rules'][match_type] = {'responses': {}}
        
        self.config['rules'][match_type]['responses'][keyword] = responses
        
        # 保存到文件
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            logger.info(f"添加关键词成功: {keyword} -> {responses}")
        except Exception as e:
            logger.error(f"保存词库配置失败: {e}")
    
    def remove_keyword(self, match_type: str, keyword: str):
        """删除关键词"""
        try:
            if (self.config.get('rules', {}).get(match_type, {}).get('responses', {}).get(keyword)):
                del self.config['rules'][match_type]['responses'][keyword]
                
                # 保存到文件
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, ensure_ascii=False, indent=2)
                logger.info(f"删除关键词成功: {keyword}")
                return True
        except Exception as e:
            logger.error(f"删除关键词失败: {e}")
        return False
    
    def get_stats(self) -> Dict:
        """获取词库统计信息"""
        if not self.enabled:
            return {"enabled": False, "total_keywords": 0}
        
        rules = self.config.get('rules', {})
        stats = {
            "enabled": self.enabled,
            "total_keywords": self._count_keywords(),
            "exact_match": len(rules.get('exact_match', {}).get('responses', {})),
            "contains_match": len(rules.get('contains_match', {}).get('responses', {})),
            "regex_match": len(rules.get('regex_match', {}).get('responses', {}))
        }
        return stats