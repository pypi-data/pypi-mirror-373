import threading
from typing import Dict, Any, Optional

import tiktoken
from vertexai.generative_models import GenerativeModel, ChatSession
import os

class VertexAISingleton:
    _instance: Optional['VertexAISingleton'] = None
    _lock = threading.Lock()
    _tokenizer_cache = {}
    encoding = None

    def __new__(cls, model_name: str = "gemini-2.5-pro"):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(VertexAISingleton, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_name: str = "gemini-2.5-pro"):
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    self.model = GenerativeModel(model_name)
                    self.encoding = tiktoken.get_encoding("cl100k_base")
                    self._initialized = True

    def generate_content(self, prompt: str) -> Dict[str, Any]:
        """複数スレッドから安全に呼び出し可能"""
        try:
            response = self.model.generate_content(prompt)
            return {
                "prompt": prompt,
                "response": self._remove_code_fence(response.text),
                "success": True,
                "error": None
            }
        except Exception as e:
            return {
                "prompt": prompt,
                "response": None,
                "success": False,
                "error": str(e)
            }

    def start_chat(self) -> ChatSession:
        """新しいチャットセッションを開始"""
        return self.model.start_chat()

    def count_tokens(self, text: str) -> int:
        """与えられたテキストのトークン数を返す（bert-base-uncasedのみ使用）"""
        try:
            tokens = self.encoding.encode(text)
            return len(tokens)
        except Exception as e:
            print(f"トークン計算失敗: {e}")
            return 0

    def _remove_code_fence(self, text: str) -> str:
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines)

    @classmethod
    def get_instance(cls, model_name: str = "gemini-2.5-pro") -> 'VertexAISingleton':
        """インスタンスを取得"""
        return cls(model_name)