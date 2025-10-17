"""LLM客户端封装"""
from typing import Optional, Dict, Any
from loguru import logger
from .config import Config
import openai
import anthropic
import dashscope
from dashscope import Generation

class LLMClient:
    """统一的LLM客户端"""
    
    def __init__(self):
        self.provider = Config.LLM_PROVIDER
        self.model = Config.LLM_MODEL
        self.config = Config.get_llm_config()
        
        # 初始化客户端
        self._init_client()
    
    def _init_client(self):
        """初始化LLM客户端"""
        try:
            if self.provider == "openai":
                self.client = openai.OpenAI(
                    api_key=self.config["api_key"],
                    base_url=self.config["base_url"]
                )
            elif self.provider == "anthropic":
                self.client = anthropic.Anthropic(
                    api_key=self.config["api_key"]
                )
            elif self.provider == "dashscope":
                dashscope.api_key = self.config["api_key"]
                self.client = dashscope
            else:
                raise ValueError(f"不支持的LLM提供商: {self.provider}")
            
            logger.info(f"LLM客户端初始化成功: {self.provider}")
            
        except Exception as e:
            logger.error(f"LLM客户端初始化失败: {e}")
            raise
    
    def invoke(self, prompt: str, system_prompt: str = None) -> str:
        """
        调用LLM生成文本
        
        Args:
            prompt: 用户提示
            system_prompt: 系统提示（可选）
            
        Returns:
            生成的文本
        """
        try:
            if self.provider == "openai":
                return self._call_openai(prompt, system_prompt)
            elif self.provider == "anthropic":
                return self._call_anthropic(prompt, system_prompt)
            elif self.provider == "dashscope":
                return self._call_dashscope(prompt, system_prompt)
            else:
                raise ValueError(f"不支持的LLM提供商: {self.provider}")
                
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            raise
    
    def _call_openai(self, prompt: str, system_prompt: str = None) -> str:
        """调用OpenAI API"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    
    def _call_anthropic(self, prompt: str, system_prompt: str = None) -> str:
        """调用Anthropic API"""
        messages = [{"role": "user", "content": prompt}]
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            temperature=0.1,
            system=system_prompt or "",
            messages=messages
        )
        
        return response.content[0].text
    
    def _call_dashscope(self, prompt: str, system_prompt: str = None) -> str:
        """调用阿里通义千问API"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = Generation.call(
            model=self.model,
            messages=messages,
            temperature=0.1,
            max_tokens=2000
        )
        
        if response.status_code == 200:
            return response.output.text
        else:
            raise Exception(f"DashScope API调用失败: {response.message}")
    
    def stream_invoke(self, prompt: str, system_prompt: str = None):
        """
        流式调用LLM（用于实时响应）
        
        Args:
            prompt: 用户提示
            system_prompt: 系统提示（可选）
            
        Yields:
            生成的文本片段
        """
        try:
            if self.provider == "openai":
                yield from self._stream_openai(prompt, system_prompt)
            elif self.provider == "anthropic":
                yield from self._stream_anthropic(prompt, system_prompt)
            elif self.provider == "dashscope":
                # DashScope暂不支持流式，回退到普通调用
                result = self._call_dashscope(prompt, system_prompt)
                yield result
            else:
                raise ValueError(f"不支持的LLM提供商: {self.provider}")
                
        except Exception as e:
            logger.error(f"流式LLM调用失败: {e}")
            yield f"生成失败: {str(e)}"
    
    def _stream_openai(self, prompt: str, system_prompt: str = None):
        """流式调用OpenAI API"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1,
            max_tokens=2000,
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def _stream_anthropic(self, prompt: str, system_prompt: str = None):
        """流式调用Anthropic API"""
        messages = [{"role": "user", "content": prompt}]
        
        with self.client.messages.stream(
            model=self.model,
            max_tokens=2000,
            temperature=0.1,
            system=system_prompt or "",
            messages=messages
        ) as stream:
            for text in stream.text_stream:
                yield text
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "provider": self.provider,
            "model": self.model,
            "config": self.config
        }
    
    def test_connection(self) -> bool:
        """测试连接"""
        try:
            test_prompt = "请回答：1+1=?"
            result = self.invoke(test_prompt)
            logger.info(f"LLM连接测试成功: {result[:50]}...")
            return True
        except Exception as e:
            logger.error(f"LLM连接测试失败: {e}")
            return False

# 全局LLM客户端实例
llm_client = LLMClient()

# 测试代码
if __name__ == "__main__":
    client = LLMClient()
    
    # 测试连接
    if client.test_connection():
        print("✓ LLM连接正常")
        
        # 测试普通调用
        result = client.invoke("请简单介绍一下人工智能")
        print(f"普通调用结果: {result[:100]}...")
        
        # 测试流式调用
        print("\n流式调用结果:")
        for chunk in client.stream_invoke("请数一下1到5"):
            print(chunk, end="", flush=True)
        print()
        
    else:
        print("✗ LLM连接失败")
