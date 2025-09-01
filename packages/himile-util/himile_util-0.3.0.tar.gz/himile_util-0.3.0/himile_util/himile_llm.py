import asyncio
import traceback
import base64
import cv2
import numpy as np
import os

from mimetypes import guess_type
from typing import List, Dict, Union, AsyncGenerator
from dataclasses import dataclass
from openai import AsyncOpenAI, AsyncStream
from openai.types.chat import ChatCompletionChunk
from himile_util.himile_log import logger


@dataclass
class MultiModalResponse:
    """多模态响应数据类"""
    content: str
    image_urls: List[str] = None


@dataclass
class LLMConfig:
    """LLM配置类"""
    api_key: str
    base_url: str
    model: str

class MultiModalClient:
    """
    多模态大模型工具类，支持图片和文本交互

    功能:
    - 支持文本对话
    - 支持图片识别和分析
    - 支持流式和非流式输出
    - 支持并发请求处理
    """

    def __init__(
            self,
            api_key: str,
            base_url: str,
            model: str,
    ):
        """
        初始化客户端

        :param api_key:
        :param base_url: API基础URL，None则使用默认
        :param model: 使用的模型名称
        :param max_tokens: 最大token数
        :param timeout: 请求超时时间(秒)
        """
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("API key must be provided or set in OPENAI_API_KEY environment variable")

        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.default_image_params = {
            "detail": "auto",  # 自动选择详细程度
            "model": self.model
        }

    async def _file_to_base64(self, file_path: Union[str, bytes, os.PathLike]) -> str:
        """
        将本地图片文件转换为Base64编码

        :param file_path: 图片文件路径
        :return: Base64编码的图片数据
        """
        with open(file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

        # 猜测MIME类型
        mime_type, _ = guess_type(file_path)
        if not mime_type or not mime_type.startswith("image/"):
            mime_type = "image/jpeg"  # 默认值

        return f"data:{mime_type};base64,{encoded_string}"

    async def _ndarray_to_base64(self, img: np.ndarray, mime_type: str = "image/jpeg") -> str:
        """
        将 numpy 图像数组转换为 Base64 编码的数据 URI

        :param img: 图像数组 (numpy.ndarray)
        :param mime_type: 图像的 MIME 类型 (默认 "image/jpeg")
        :return: Base64 编码的数据 URI
        """
        # 确保输入是 numpy 数组
        if not isinstance(img, np.ndarray):
            raise TypeError("Input must be a numpy.ndarray")

        # 将图像数组编码为字节流
        success, encoded_image = cv2.imencode(".jpg", img)  # 默认使用 JPEG 格式
        if not success:
            raise ValueError("Could not encode image")

        # 转换为 Base64 字符串
        encoded_string = base64.b64encode(encoded_image.tobytes()).decode("utf-8")

        # 确保 MIME 类型是有效的图像类型
        if not mime_type.startswith("image/"):
            mime_type = "image/jpeg"  # 默认值

        return f"data:{mime_type};base64,{encoded_string}"

    async def chat(
            self,
            messages: List[Dict[str, str]],
            stream: bool = False,
            **kwargs
    ) -> Union[MultiModalResponse, AsyncGenerator[MultiModalResponse, None]]:
        """
        普通文本对话

        :param messages: 消息列表，格式如 [{"role": "user", "content": "你好"}]
        :param stream: 是否使用流式输出
        :param kwargs: 其他传递给API的参数
        :return: 如果是流式则返回异步生成器，否则返回完整响应
        """
        try:
            params = {
                "model": self.model,
                "messages": messages,
                **kwargs
            }

            if stream:
                return self._handle_stream_response(
                    await self.client.chat.completions.create(**params, stream=True)
                )
            else:
                response = await self.client.chat.completions.create(**params, stream=False)
                return MultiModalResponse(content=response.choices[0].message.content)
        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.error(f'普通文本对话报错：{error_traceback}, {e}')

    async def analyze_image(
            self,
            image_source: Union[str, bytes, os.PathLike, np.ndarray],
            prompt: str,
            stream: bool = False,
            **kwargs
    ) -> Union[MultiModalResponse, AsyncGenerator[MultiModalResponse, None]]:
        """
        分析单张图片

        :param image_source: 图片源，可以是URL或本地文件路径
        :param prompt: 用户提示
        :param stream: 是否使用流式输出
        :param kwargs: 其他传递给API的参数
        :return: 如果是流式则返回异步生成器，否则返回完整响应
        """
        return await self.analyze_images([image_source], prompt, stream=stream, **kwargs)

    async def analyze_images(
            self,
            image_sources: List[Union[str, bytes, os.PathLike, np.ndarray]],
            prompt: str,
            stream: bool = False,
            **kwargs
    ) -> Union[MultiModalResponse, AsyncGenerator[MultiModalResponse, None]]:
        """
        分析多张图片

        :param image_sources: 图片源列表，可以是URL或本地文件路径
        :param prompt: 用户提示
        :param stream: 是否使用流式输出
        :param kwargs: 其他传递给API的参数
        :return: 响应对象
        """
        # 构建消息内容
        try:
            content = [{"type": "text", "text": prompt}]
            processed_urls = []

            for source in image_sources:
                if isinstance(source, (bytes, os.PathLike)) or (
                        isinstance(source, str) and not source.startswith(("http://", "https://"))
                ):
                    # 处理本地文件
                    image_data = await self._file_to_base64(source)
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": image_data, **self.default_image_params}
                    })
                    processed_urls.append("local_image")

                elif isinstance(source, np.ndarray):
                    image_data = await self._ndarray_to_base64(source)
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": image_data, **self.default_image_params}
                    })
                    processed_urls.append("local_image")
                else:
                    # 处理URL
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": source, **self.default_image_params}
                    })
                    processed_urls.append(source)

            messages = [{"role": "user", "content": content}]

            params = {
                "model": self.model,
                "messages": messages,
                **kwargs
            }

            if stream:
                return self._handle_stream_response(
                    await self.client.chat.completions.create(**params, stream=True)
                )
            else:
                response = await self.client.chat.completions.create(**params, stream=False)
                return MultiModalResponse(
                    content=response.choices[0].message.content,
                    image_urls=processed_urls
                )
        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.error(f'分析多张图片报错：{error_traceback}, {e}')

    async def _handle_stream_response(
            self,
            stream: AsyncStream[ChatCompletionChunk]
    ) -> AsyncGenerator[MultiModalResponse, None]:
        """
        处理流式响应

        :param stream: 异步流对象
        :return: 异步生成器，每次产生部分响应
        """
        try:
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield MultiModalResponse(content=chunk.choices[0].delta.content)
        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.error(f'处理流式响应报错：{error_traceback}, {e}')

    async def batch_chat(
            self,
            messages_list: List[List[Dict[str, str]]],
            stream: bool = False,
            max_concurrent: int = 5,
            **kwargs
    ) -> List[Union[MultiModalResponse, AsyncGenerator[MultiModalResponse, None]]]:
        """
        批量处理文本对话请求

        :param messages_list: 多个消息列表的列表
        :param stream: 是否使用流式输出
        :param max_concurrent: 最大并发请求数
        :param kwargs: 其他传递给API的参数
        :return: 响应列表，顺序与输入一致
        """
        try:
            semaphore = asyncio.Semaphore(max_concurrent)

            async def limited_chat(messages):
                async with semaphore:
                    return await self.chat(messages, stream=stream, **kwargs)

            tasks = [limited_chat(messages) for messages in messages_list]
            return await asyncio.gather(*tasks)
        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.error(f'批量处理文本对话请求应报错：{error_traceback}, {e}')

    async def batch_analyze_images(
            self,
            image_sources_list: List[List[Union[str, bytes, os.PathLike]]],
            prompts: List[str],
            stream: bool = False,
            max_concurrent: int = 5,
            **kwargs
    ) -> List[Union[MultiModalResponse, AsyncGenerator[MultiModalResponse, None]]]:
        """
        批量分析图片(增强版)

        :param image_sources_list: 多个图片源列表的列表
        :param prompts: 对应的提示列表
        :param stream: 是否使用流式输出
        :param max_concurrent: 最大并发请求数
        :param kwargs: 其他传递给API的参数
        :return: 响应列表
        """
        try:
            if len(image_sources_list) != len(prompts):
                raise ValueError("image_sources_list and prompts must have the same length")

            semaphore = asyncio.Semaphore(max_concurrent)

            async def limited_analyze(sources, prompt):
                async with semaphore:
                    return await self.analyze_images(sources, prompt, stream=stream, **kwargs)

            tasks = [
                limited_analyze(sources, prompt)
                for sources, prompt in zip(image_sources_list, prompts)
            ]
            return await asyncio.gather(*tasks)
        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.error(f'批量处理图片分析请求报错：{error_traceback}, {e}')

    async def close(self):
        """关闭客户端连接"""
        await self.client.close()

    async def create_embeddings(
            self,
            texts: Union[str, List[str]],
            model: str = "qwen3-embedding",
            dimensions: int = None,
            **kwargs
    ) -> List[List[float]]:
        """
        生成文本的向量表示(嵌入)

        :param texts: 要向量化的文本或文本列表
        :param model: 使用的嵌入模型 (默认 "text-embedding-3-small")
        :param dimensions: 可选，指定输出向量的维度
        :param kwargs: 其他传递给API的参数
        :return: 向量列表，每个文本对应一个向量
        """
        try:
            # 确保输入是列表形式
            if isinstance(texts, str):
                texts = [texts]

            params = {
                "model": model,
                "input": texts,
                **kwargs
            }

            # 如果指定了维度
            if dimensions:
                params["dimensions"] = dimensions

            response = await self.client.embeddings.create(**params)

            # 按原始顺序返回向量
            return [item.embedding for item in response.data]

        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.error(f'文本向量化报错：{error_traceback}, {e}')
            raise


# 示例用法
async def example_usage():
    # 初始化客户端
    client = MultiModalClient()

    try:
        # 示例1: 普通文本对话(非流式)
        # messages = [{"role": "user", "content": "请用中文解释量子计算"}]
        # response = await client.chat(messages)
        # print("普通文本响应:", response.content)

        # 示例2: 图片分析(非流式)
        local_image_path = "http://gbbbs.himile.com/assets/uploads/files/1719575055979-71935a38-6c7f-46e4-ad09-1dc503e9f038-image.png"  # 替换为实际图片路径
        response = await client.analyze_image(local_image_path, "描述这张图片的内容")
        print("本地图片分析结果:", response.content)

        # 示例3: 流式文本对话
        # messages = [{"role": "user", "content": "写一篇关于人工智能的短文"}]
        # async for chunk in await client.chat(messages, stream=True):
        #     print(chunk.content, end="", flush=True)
        # print("\n")
        #
        # 示例4: 批量处理请求
        messages_list = [
            [{"role": "user", "content": "第一个问题"}],
            [{"role": "user", "content": "第二个问题"}]
        ]
        responses = await client.batch_chat(messages_list)
        for i, resp in enumerate(responses):
            print(f"批量响应 {i + 1}:", resp.content)

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(example_usage())
