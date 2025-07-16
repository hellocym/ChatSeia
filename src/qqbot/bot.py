import time
from ncatbot.core import BotClient, GroupMessage, PrivateMessage
from ncatbot.utils import get_log
from dotenv import load_dotenv
from ..llm.llm import LLM
import os
from typing import Dict

bot = BotClient()
_log = get_log()
load_dotenv()
qqid = os.getenv("ID")
api_url = os.getenv("API_URL")

# 为每个群聊和私聊创建独立的LLM实例，以维护不同对话的上下文
group_llm_instances: Dict[str, LLM] = {}
private_llm_instances: Dict[str, LLM] = {}

def get_llm_for_group(group_id: str) -> LLM:
    """获取或创建特定群聊的LLM实例"""
    if group_id not in group_llm_instances:
        _log.info(f"为群 {group_id} 创建新的LLM实例")
        group_llm_instances[group_id] = LLM(api_url=api_url)
    return group_llm_instances[group_id]

def get_llm_for_private(user_id: str) -> LLM:
    """获取或创建特定私聊的LLM实例"""
    if user_id not in private_llm_instances:
        _log.info(f"为用户 {user_id} 创建新的LLM实例")
        private_llm_instances[user_id] = LLM(api_url=api_url)
    return private_llm_instances[user_id]

@bot.group_event()
async def on_at_message(msg: GroupMessage):
    _log.info(f"收到群消息: {msg}")
    # 如果是at我的
    if any(seg.get('type') == 'at' and str(seg.get('data', {}).get('qq')) == str(qqid) for seg in msg.message):
        group_id = str(msg.group_id)
        _log.info(f"收到来自群 {group_id} 的@消息")
        
        # 获取该群的LLM实例
        group_llm = get_llm_for_group(group_id)
        
        all_texts = '\n'.join(seg.get('data', {}).get('text') for seg in msg.message if seg.get('type') == 'text')
        _log.info(f"@消息内容: {all_texts}")
        
        # 检查是否是清除上下文的命令
        if "清除上下文" in all_texts or "清空上下文" in all_texts:
            group_llm.clear_context()
            await msg.reply("已清空对话上下文记录")
            return
            
        # 使用群聊特定的LLM实例处理消息
        response = group_llm.chat(all_texts)
        if "<think>" in response:
            think, response = response.split("<think>")[1].split("</think>")[:2]
            _log.info(f"思考: {think}")
        _log.info(f"回复: {response}")
        
        if response:
            await msg.reply(response)
        else:
            await msg.reply("我现在有点忙，稍后回复你")

@bot.private_event()
async def on_private_message(msg: PrivateMessage):
    _log.info(f"收到私聊消息: {msg}")
    user_id = str(msg.user_id)
    
    # 获取该用户的LLM实例
    user_llm = get_llm_for_private(user_id)
    
    message_text = ''.join(seg.get('data', {}).get('text', '') for seg in msg.message if seg.get('type') == 'text')
    _log.info(f"私聊消息内容: {message_text}")
    
    # 检查是否是清除上下文的命令
    if "清除上下文" in message_text or "清空上下文" in message_text:
        user_llm.clear_context()
        await msg.reply("已清空对话上下文记录")
        return
        
    # 使用用户特定的LLM实例处理消息
    response = user_llm.chat(message_text)
    if "<think>" in response:
        think, response = response.split("<think>")[1].split("</think>")[:2]
        _log.info(f"思考: {think}")
    _log.info(f"回复: {response}")
    
    if response:
        await msg.reply(response)
    else:
        await msg.reply("我现在有点忙，稍后回复你")

if __name__ == "__main__":
    print(qqid)
    bot.run(bt_uin=qqid)