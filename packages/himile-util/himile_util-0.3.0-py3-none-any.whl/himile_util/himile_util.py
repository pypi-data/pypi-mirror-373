import gzip
import json
import pickle
import re

import aiofiles
from pathlib import Path
from typing import Any, Union, Optional, List
from himile_util.himile_log import logger


class CommonUtils:
    """
    通用工具类，包含各种实用方法（所有方法均为静态方法，无需实例化）
    """

    @staticmethod
    async def save_as_pkl(
            data: Any,
            file_path: Union[str, Path],
            compress: bool = False,
            protocol: int = pickle.HIGHEST_PROTOCOL,
            overwrite: bool = False
    ) -> None:
        """
        将Python对象异步保存为PKL文件

        Args:
            data: 需要序列化的Python对象
            file_path: 输出文件路径（如 "data/example.pkl"）
            compress: 是否使用GZIP压缩（默认False）
            protocol: pickle协议版本（默认最高版本）
            overwrite: 是否允许覆盖已有文件（默认False）

        Raises:
            FileExistsError: 当文件已存在且overwrite=False时抛出
            TypeError: 当对象不可序列化时抛出
            IOError: 文件系统相关错误
        """
        path = Path(file_path)

        # --- 同步前置检查（快速失败）---
        if path.exists() and not overwrite:
            logger.error(f"文件已存在（如需覆盖请设置overwrite=True）: {path}")
            raise FileExistsError(f"文件已存在: {path}")

        # 创建父目录（同步操作）
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # --- 异步核心操作 ---
            # 1. 先同步序列化（pickle.dumps是CPU密集型操作，无需异步）
            serialized_data = pickle.dumps(data, protocol=protocol)

            # 2. 异步写入文件
            if compress:
                # 先压缩再写入
                compressed_data = gzip.compress(serialized_data)
                async with aiofiles.open(path, "wb") as f:
                    await f.write(compressed_data)
            else:
                async with aiofiles.open(path, "wb") as f:
                    await f.write(serialized_data)
            logger.info(f"成功保存数据到: {path}")
        except (pickle.PicklingError, TypeError) as e:
            logger.error(f"序列化失败: 对象类型 {type(data)} 不可被pickle")
            raise TypeError(f"不支持的数据类型: {type(data)}") from e
        except Exception as e:
            logger.error(f"保存文件失败 {path}: {str(e)}", exc_info=True)
            raise IOError("文件保存失败") from e


    @staticmethod
    async def load_from_pkl(
            file_path: Union[str, Path],
            compressed: bool = False
    ) -> Any:
        """
        从PKL文件异步加载数据

        参数:
            file_path: PKL文件路径（如 "data/example.pkl"）
            compressed: 是否使用GZIP压缩（默认False）

        返回:
            反序列化后的Python对象

        异常:
            FileNotFoundError: 当文件不存在时抛出
            pickle.UnpicklingError: 当文件损坏或格式不匹配时抛出
            EOFError: 当文件为空时抛出
        """
        path = Path(file_path)

        try:
            # --- 前置检查（同步操作）---
            if not path.exists():
                logger.error(f"文件不存在: {path}")
                raise FileNotFoundError(f"文件不存在: {path}")
            if path.stat().st_size == 0:
                logger.error(f"空文件: {path}")
                raise EOFError(f"空文件: {path}")

            # --- 异步加载操作 ---
            if compressed:
                async with aiofiles.open(path, "rb") as f:
                    compressed_data = await f.read()
                    data = pickle.loads(gzip.decompress(compressed_data))
            else:
                async with aiofiles.open(path, "rb") as f:
                    data = pickle.loads(await f.read())

            logger.info(f"成功从 {path} 加载数据")
            return data

        except pickle.UnpicklingError as e:
            logger.error(f"文件损坏或格式错误: {path}")
            raise ValueError("非法的PKL文件格式") from e
        except (gzip.BadGzipFile, pickle.PickleError) as e:
            logger.error(f"解压/反序列化失败: {type(e).__name__}")
            raise IOError("文件可能不是有效的PKL格式") from e
        except Exception as e:
            logger.error(f"未知加载错误: {str(e)}", exc_info=True)
            raise


    @staticmethod
    async def read_json_file(
            file_path: Union[str, Path]
    ) -> Union[dict, list]:
        """
        异步读取并解析JSON文件
        Args:
            file_path: str JSON文件路径

        Returns:
            dict/list: 解析后的JSON数据
        """
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                content = await file.read()
            return json.loads(content)
        except Exception as e:
            logger.error(f"读取{file_path}文件内容时报错，报错信息为{e}")

    @staticmethod
    async def extract_json(text: str,
                     strict: bool = False,
                     multiple: bool = False) -> Optional[Union[dict, list, str, List[Union[dict, list]]]]:
        """
        从字符串中提取JSON内容

        Args:
            text: 输入字符串
            strict: 是否严格模式（True: 只匹配完整的JSON，False: 尝试修复不完整JSON）
            multiple: 是否提取多个JSON（True: 返回列表，False: 返回第一个）

        Returns:
            解析后的JSON对象或对象列表，失败返回None
        """
        # 常见的JSON模式匹配
        patterns = [
            r'\{[^{}]*\{[^{}]*\}[^{}]*\}|\{[^{}]*\}',  # 匹配对象
            r'\[[^\[\]]*\[[^\[\]]*\][^\[\]]*\]|\[[^\[\]]*\]',  # 匹配数组
            r'"[^"]*"',  # 匹配字符串
            r'true|false|null',  # 匹配字面量
            r'-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?'  # 匹配数字
        ]

        json_pattern = re.compile('|'.join(patterns))
        matches = json_pattern.findall(text)

        if not matches:
            return None

        results = []
        for match in matches:
            try:
                # 尝试解析JSON
                parsed = json.loads(match)
                results.append(parsed)
                if not multiple:
                    break
            except json.JSONDecodeError:
                if not strict:
                    # 非严格模式下尝试修复常见问题
                    try:
                        # 尝试添加缺失的引号
                        fixed = CommonUtils._fix_json_string(match)
                        if fixed != match:
                            parsed = json.loads(fixed)
                            results.append(parsed)
                            if not multiple:
                                break
                    except:
                        continue

        if not results:
            return None

        return results if multiple else results[0]

    @staticmethod
    async def _fix_json_string(json_str: str) -> str:
        """尝试修复常见的JSON格式问题"""
        # 移除首尾多余字符
        json_str = json_str.strip()

        # 处理缺少引号的键
        if json_str.startswith('{') and json_str.endswith('}'):
            # 匹配键值对
            pattern = r'(\w+)\s*:'

            def add_quotes(match):
                key = match.group(1)
                if not (key.startswith('"') and key.endswith('"')):
                    return f'"{key}":'
                return match.group(0)

            json_str = re.sub(pattern, add_quotes, json_str)

        return json_str

    @staticmethod
    async def extract_all_json(text: str, strict: bool = False) -> List[Union[dict, list]]:
        """提取所有可能的JSON对象"""
        return await CommonUtils.extract_json(text, strict, multiple=True)

    @staticmethod
    async def find_json_boundaries(text: str) -> List[tuple]:
        """
        找到字符串中所有可能的JSON边界位置

        Returns:
            List of tuples (start_index, end_index, json_string)
        """
        boundaries = []
        stack = []
        in_string = False
        escape = False

        for i, char in enumerate(text):
            if char == '"' and not escape:
                in_string = not in_string
            if in_string:
                escape = (char == '\\' and not escape)
                continue

            if char == '{' or char == '[':
                if not stack:
                    start = i
                stack.append(char)
            elif char == '}' and stack and stack[-1] == '{':
                stack.pop()
                if not stack:
                    boundaries.append((start, i + 1, text[start:i + 1]))
            elif char == ']' and stack and stack[-1] == '[':
                stack.pop()
                if not stack:
                    boundaries.append((start, i + 1, text[start:i + 1]))

        return boundaries
