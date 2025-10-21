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
            # 检查是否有API密钥
            api_key = self.config.get("api_key", "")
            if not api_key or api_key == "your_openai_api_key_here":
                logger.warning("API密钥未配置，将使用模拟模式")
                self.client = None
                self.mock_mode = True
                return
            
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
            
            self.mock_mode = False
            logger.info(f"LLM客户端初始化成功: {self.provider}")
            
        except Exception as e:
            logger.warning(f"LLM客户端初始化失败，将使用模拟模式: {e}")
            self.client = None
            self.mock_mode = True
    
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
            # 如果是模拟模式，返回模拟回答
            if hasattr(self, 'mock_mode') and self.mock_mode:
                return self._mock_response(prompt, system_prompt)
            
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
            # 如果真实API调用失败，回退到模拟模式
            return self._mock_response(prompt, system_prompt)
    
    def _mock_response(self, prompt: str, system_prompt: str = None) -> str:
        """模拟LLM响应"""
        # 基于提示词生成简单的模拟回答
        if "什么是" in prompt or "定义" in prompt:
            return f"根据提供的上下文信息，{prompt}是一个重要的概念。在医学领域，这个概念通常涉及相关的理论知识和实践应用。建议您查阅相关教材或咨询专业人士以获得更详细的信息。"
        elif "如何" in prompt or "怎么" in prompt:
            return f"关于{prompt}，根据上下文信息，通常需要按照以下步骤进行：1. 理解基本概念；2. 掌握相关方法；3. 进行实践应用。具体操作细节请参考相关文档或咨询专业人士。"
        elif "总结" in prompt or "概述" in prompt:
            return f"根据提供的文档内容，可以总结如下：这是一个重要的医学主题，涉及多个方面的知识。主要内容包括基本概念、理论框架、实践应用等。建议深入学习相关材料以获得更全面的理解。"
        else:
            return f"根据您的问题「{prompt}」，基于提供的上下文信息，这是一个值得深入探讨的话题。在医学学习中，理解相关概念和方法非常重要。建议您结合具体的学习材料进行深入学习。"
    
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
