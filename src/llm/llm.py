
import requests
from typing import Optional, List, Dict, Any

class LLM:
    def __init__(self, api_url: str = "http://localhost:1234", role: str = "default", max_context_length: int = 10):
        self.api_url = api_url
        self.system_prompt = self._load_system_prompt(role)
        self.max_context_length = max_context_length
        self.conversation_history: List[Dict[str, str]] = []
    
    def _load_system_prompt(self, role: str) -> dict:
        try:
            from config.system_prompts import SYSTEM_PROMPTS
            return SYSTEM_PROMPTS.get(role, SYSTEM_PROMPTS["default"])
        except Exception as e:
            print(f"Warning: 无法加载角色配置，使用默认设置: {e}")
            return {"name": "AI助手", "prompt": "你是一个乐于助人的AI助手。"}

    def chat(self, message: str) -> Optional[str]:
        try:
            # 添加用户消息到历史记录
            self.conversation_history.append({"role": "user", "content": message})
            
            # 构建完整消息列表，包括系统提示和对话历史
            messages = [
                {"role": "system", "content": self.system_prompt["prompt"]}
            ]
            
            # 添加历史记录，如果超过最大长度则截断
            if len(self.conversation_history) > self.max_context_length:
                self.conversation_history = self.conversation_history[-self.max_context_length:]
            
            messages.extend(self.conversation_history)
            
            response = requests.post(
                f"{self.api_url}/v1/chat/completions",
                json={
                    "messages": messages,
                    "stream": False
                }
            )
            response.raise_for_status()
            
            # 获取AI回复并添加到历史记录
            ai_response = response.json()["choices"][0]["message"]["content"]
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            return ai_response
        except Exception as e:
            print(f"Error: {e}")
            return None
            
    def clear_context(self) -> None:
        """清除对话历史记录"""
        self.conversation_history = []
        
    def get_context(self) -> List[Dict[str, str]]:
        """获取当前对话历史记录"""
        return self.conversation_history.copy()