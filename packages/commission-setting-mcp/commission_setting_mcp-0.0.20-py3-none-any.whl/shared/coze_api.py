# -*- coding: utf-8 -*-
import os
import time
import traceback

import httpx
from typing import Optional, Dict, Any, List
import json

from dotenv import load_dotenv

from shared.log_util import log_info

load_dotenv()

class CozeAPI:
    def __init__(self, token: Optional[str] = None, bot_id: Optional[str] = None):
        """
        初始化Coze API客户端
        
        Args:
            token: Coze API访问令牌，如果不提供则从环境变量COZE_TOKEN读取
            bot_id: 智能体ID，如果不提供则从环境变量COZE_BOT_ID读取
        """
        self.token = token or os.getenv('COZE_TOKEN')
        self.bot_id = bot_id or os.getenv('COZE_BOT_ID')
        log_info(f"Using Coze Bot ID: {self.bot_id}, Token: {self.token[:4]}****{self.token[-4:] if self.token else 'None'}")
        self.base_url = 'https://api.coze.cn'
        
        if not self.token:
            raise ValueError("Coze token not provided and COZE_TOKEN environment variable not set")
        if not self.bot_id:
            raise ValueError("Bot ID not provided and COZE_BOT_ID environment variable not set")
        
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def start_chat(self, question: str, user_id: str = "1234") -> Dict[str, Any]:
        """
        发起对话
        
        Args:
            question: 用户问题
            user_id: 用户ID，默认为"1234"
        
        Returns:
            包含对话ID和会话ID的字典
        """
        url = f"{self.base_url}/v3/chat"
        
        payload = {
            "bot_id": self.bot_id,
            "user_id": user_id,
            "stream": False,
            "auto_save_history": True,
            "additional_messages": [
                {
                    "role": "user",
                    "content": question,
                    "content_type": "text"
                }
            ]
        }
        
        with httpx.Client(timeout=30.0, verify=False) as client:
            response = client.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            if result.get('code') != 0:
                print(f"Start chat response: {result}")
                raise Exception(f"Start chat failed: {result.get('msg', 'Unknown error')}")
            
            data = result.get('data', {})
            return {
                'chat_id': data.get('id'),
                'conversation_id': data.get('conversation_id'),
                'status': data.get('status')
            }
    
    def get_chat_status(self, chat_id: str, conversation_id: str) -> Dict[str, Any]:
        """
        查看对话详情/状态
        
        Args:
            chat_id: 对话ID
            conversation_id: 会话ID
        
        Returns:
            对话状态信息
        """
        url = f"{self.base_url}/v3/chat/retrieve"
        params = {
            'chat_id': chat_id,
            'conversation_id': conversation_id
        }
        
        with httpx.Client(timeout=30.0, verify=False) as client:
            response = client.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            if result.get('code') != 0:
                raise Exception(f"Get chat status failed: {result.get('msg', 'Unknown error')}")
            
            data = result.get('data', {})
            return {
                'status': data.get('status'),
                'usage': data.get('usage', {}),
                'completed_at': data.get('completed_at'),
                'last_error': data.get('last_error', {})
            }
    
    def get_chat_messages(self, chat_id: str, conversation_id: str) -> List[Dict[str, Any]]:
        """
        查看对话消息详情
        
        Args:
            chat_id: 对话ID
            conversation_id: 会话ID
        
        Returns:
            消息列表
        """
        url = f"{self.base_url}/v3/chat/message/list"
        params = {
            'chat_id': chat_id,
            'conversation_id': conversation_id
        }
        
        with httpx.Client(timeout=30.0, verify=False) as client:
            response = client.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            if result.get('code') != 0:
                raise Exception(f"Get chat messages failed: {result.get('msg', 'Unknown error')}")
            
            return result.get('data', [])
    
    def wait_for_completion(self, chat_id: str, conversation_id: str, max_wait_time: int = 60) -> Dict[str, Any]:
        """
        等待对话完成
        
        Args:
            chat_id: 对话ID
            conversation_id: 会话ID
            max_wait_time: 最大等待时间（秒），默认60秒
        
        Returns:
            最终的对话状态
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            status_info = self.get_chat_status(chat_id, conversation_id)
            status = status_info.get('status')
            
            if status in ['completed', 'failed', 'canceled', 'required_action']:
                return status_info
            
            time.sleep(1)  # 每秒轮询一次
        
        raise TimeoutError(f"Chat did not complete within {max_wait_time} seconds")
    
    def get_bot_reply(self, question: str, user_id: str = "1234", max_wait_time: int = 60) -> str:
        """
        完整的对话流程：发起对话并获取机器人回复
        
        Args:
            question: 用户问题
            user_id: 用户ID，默认为"1234"
            max_wait_time: 最大等待时间（秒），默认60秒
        
        Returns:
            机器人的回复内容
        """
        # 1. 发起对话
        chat_info = self.start_chat(question, user_id)
        chat_id = chat_info['chat_id']
        conversation_id = chat_info['conversation_id']
        
        # 2. 等待对话完成
        final_status = self.wait_for_completion(chat_id, conversation_id, max_wait_time)
        
        if final_status['status'] == 'failed':
            error_info = final_status.get('last_error', {})
            raise Exception(f"Chat failed: {error_info.get('msg', 'Unknown error')}")
        elif final_status['status'] != 'completed':
            raise Exception(f"Chat ended with unexpected status: {final_status['status']}")
        
        # 3. 获取消息详情
        messages = self.get_chat_messages(chat_id, conversation_id)
        
        # 4. 提取机器人的回复（type为answer的消息）
        for message in messages:
            if message.get('type') == 'answer' and message.get('role') == 'assistant':
                return message.get('content', '')
        
        raise Exception("No bot reply found in chat messages")


def ask_coze_bot(question: str, user_id: str = "1234") -> str:
    """
    便捷函数：向Coze机器人提问并获取回复
    
    Args:
        question: 要询问的问题
        user_id: 用户ID，默认为"1234"
    
    Returns:
        机器人的回复
    
    Example:
        reply = ask_coze_bot("小笼包的品牌是什么？")
        print(reply)
    """
    coze = CozeAPI()
    return coze.get_bot_reply(question, user_id)


if __name__ == "__main__":
    # 示例用法
    try:
        reply = ask_coze_bot("查询公司小笼包的商品ID和品牌是什么？")
        print(f"机器人回复: {reply}")
    except Exception as e:
        print(f"错误: {e}")
        traceback.print_exc()