import argparse
from typing import Optional
import json
import requests
import os

class LocalLLM:
    def __init__(self, api_url: str = "http://localhost:8000", role: str = "default"):
        self.api_url = api_url
        self.system_prompt = self._load_system_prompt(role)
    
    def _load_system_prompt(self, role: str) -> dict:
        try:
            from config.system_prompts import SYSTEM_PROMPTS
            return SYSTEM_PROMPTS.get(role, SYSTEM_PROMPTS["default"])
        except Exception as e:
            print(f"Warning: 无法加载角色配置，使用默认设置: {e}")
            return {"name": "AI助手", "prompt": "你是一个乐于助人的AI助手。"}

    def chat(self, message: str) -> Optional[str]:
        try:
            response = requests.post(
                f"{self.api_url}/v1/chat/completions",
                json={
                    "messages": [
                        {"role": "system", "content": self.system_prompt["prompt"]},
                        {"role": "user", "content": message}
                    ],
                    "stream": False
                }
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Error: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description="与本地大模型对话")
    parser.add_argument("--api-url", default="http://192.168.31.58:1234", help="本地大模型API地址")
    parser.add_argument("--role", default="default", help="选择预设角色")
    args = parser.parse_args()

    llm = LocalLLM(api_url=args.api_url, role=args.role)
    print(f"开始对话 - 当前角色：{llm.system_prompt['name']}（输入 'quit' 或 'exit' 退出）")

    while True:
        user_input = input("\n用户: ")
        if user_input.lower() in ["quit", "exit"]:
            break

        response = llm.chat(user_input)
        if response:
            print("\n助手:", response)

if __name__ == "__main__":
    main()