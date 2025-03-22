import argparse
from typing import Optional
import json
import requests

class LocalLLM:
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url

    def chat(self, message: str) -> Optional[str]:
        try:
            response = requests.post(
                f"{self.api_url}/v1/chat/completions",
                json={
                    "messages": [{"role": "user", "content": message}],
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
    args = parser.parse_args()

    llm = LocalLLM(api_url=args.api_url)
    print("开始对话（输入 'quit' 或 'exit' 退出）")

    while True:
        user_input = input("\n用户: ")
        if user_input.lower() in ["quit", "exit"]:
            break

        response = llm.chat(user_input)
        if response:
            print("\n助手:", response)

if __name__ == "__main__":
    main()