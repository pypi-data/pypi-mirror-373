"""
AIHubMax API异步客户端
"""
import os
import json
import httpx
import traceback
import asyncio
from typing import Dict, List, Union, Optional, Any, BinaryIO
from pathlib import Path

from ..utils.log import logger
from .const import *
from .exception import AIHubMaxException
from .. import __version__


class AIHubMaxClient:
    """
    AIHubMax API异步客户端
    提供对AIHubMax API的异步访问
    """
    def __init__(self, token: str = os.getenv("AIHUBMAX_TOKEN"), timeout: float = 30.0, print_log: bool = True, max_retries: int = 3):
        """
        初始化AIHubMax API客户端

        Args:
            token: AIHubMax API令牌
            timeout: API请求超时时间（秒）
            print_log: 是否打印API请求日志
            max_retries: 最大重试次数
        """
        if not token:
            raise ValueError("AIHubMax API令牌不能为空，请提供token参数或设置AIHUBMAX_TOKEN环境变量")

        self._token = token
        self.print_log = print_log
        self.max_retries = max_retries
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self) -> None:
        """
        关闭异步客户端
        """
        if self.client:
            await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _request_with_retry(self, method: str, url: str, data: Dict = None, files: Dict = None, check_code: bool = True) -> Dict:
        """
        带重试机制的请求方法
        
        Args:
            method: HTTP方法
            url: API URL  
            data: 请求数据
            files: 文件数据
            check_code: 是否检查响应代码
            
        Returns:
            API响应数据
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    # 指数退避：1s, 2s, 4s, 8s...
                    wait_time = min(2 ** (attempt - 1), 30)  # 最大等待30秒
                    logger.warning(f"[zdpytools v{__version__}] 第 {attempt + 1} 次重试，等待 {wait_time} 秒...")
                    await asyncio.sleep(wait_time)
                
                return await self._request(method, url, data, files, check_code)
                
            except (httpx.HTTPStatusError, httpx.ConnectTimeout, httpx.ReadTimeout) as e:
                last_exception = e
                if attempt < self.max_retries:
                    # 只对特定错误进行重试
                    if isinstance(e, httpx.HTTPStatusError):
                        # 5xx 服务器错误或 429 限流错误才重试
                        if e.response.status_code >= 500 or e.response.status_code == 429:
                            logger.warning(f"[zdpytools v{__version__}] 遇到可重试错误 {e.response.status_code}，第 {attempt + 1}/{self.max_retries + 1} 次尝试")
                            continue
                    else:
                        # 超时错误直接重试
                        logger.warning(f"[zdpytools v{__version__}] 请求超时，第 {attempt + 1}/{self.max_retries + 1} 次尝试")
                        continue
                
                # 不可重试的错误或达到最大重试次数
                break
            except Exception as e:
                # 其他异常不重试，直接抛出
                last_exception = e
                break
        
        # 所有重试都失败了，抛出最后一个异常
        if isinstance(last_exception, httpx.HTTPStatusError):
            logger.error(f"[zdpytools v{__version__}] 重试 {self.max_retries} 次后仍然失败，HTTP状态码: {last_exception.response.status_code}")
        
        raise last_exception

    async def _request(self, method: str, url: str, data: Dict = None, files: Dict = None, check_code: bool = True) -> Dict:
        """
        发送API请求

        Args:
            method: HTTP方法（GET, POST, PUT, DELETE）
            url: API URL
            data: 请求数据
            files: 文件数据
            check_code: 是否检查响应代码

        Returns:
            API响应数据
        """
        headers = {
            "Authorization": f"Bearer {self._token}"
        }

        if not files:
            headers["Content-Type"] = "application/json"

        if self.print_log:
            logger.debug(f"{method} 请求AIHubMax接口: {url}")
            if data and not files:
                logger.debug(f"请求体: {data}")
            elif files:
                logger.debug(f"上传文件: {list(files.keys())}")

        try:
            if method.upper() == "GET":
                response = await self.client.get(url, headers=headers)
            elif method.upper() == "POST" and files:
                logger.debug(f"上传文件到 {url}，headers: {headers}")
                response = await self.client.post(url, headers=headers, files=files)
            else:
                response = await self.client.request(
                    method.upper(),
                    url,
                    headers=headers,
                    json=data
                )

            # 先记录响应基本信息
            if self.print_log:
                logger.info(f"[zdpytools v{__version__}] HTTP响应状态码: {response.status_code}")
                logger.info(f"[zdpytools v{__version__}] HTTP响应头: {dict(response.headers)}")
                logger.info(f"[zdpytools v{__version__}] HTTP响应体: {response.text}")

            response.raise_for_status()
            resp_data = response.json()

            if self.print_log:
                logger.info(f"[zdpytools v{__version__}] 解析后的JSON响应: {resp_data}")

            if check_code and resp_data.get("code", -1) != 0:
                logger.error(f"[zdpytools v{__version__}] 接口返回错误, URL: {url}, 错误信息: {resp_data}")
                raise AIHubMaxException(
                    code=resp_data.get("code"),
                    msg=resp_data.get("msg"),
                    url=url,
                    req_body=data,
                    headers=headers
                )

            return resp_data
        except httpx.HTTPError as e:
            # 记录详细的错误信息
            logger.error(f"[zdpytools v{__version__}] 请求AIHubMax接口异常: {e}, URL: {url}")
            
            # 如果是HTTP状态错误，记录响应详情
            if isinstance(e, httpx.HTTPStatusError) and hasattr(e, 'response'):
                logger.error(f"[zdpytools v{__version__}] 错误响应状态码: {e.response.status_code}")
                logger.error(f"[zdpytools v{__version__}] 错误响应头: {dict(e.response.headers)}")
                logger.error(f"[zdpytools v{__version__}] 错误响应体: {e.response.text}")
                
                # 尝试解析错误响应的JSON
                try:
                    error_json = e.response.json()
                    logger.error(f"[zdpytools v{__version__}] 错误响应JSON: {error_json}")
                except:
                    logger.error(f"[zdpytools v{__version__}] 无法解析错误响应JSON")
            
            logger.error(f"[zdpytools v{__version__}] 异常详情: {traceback.format_exc()}")
            raise AIHubMaxException(
                code=-1,
                msg=f"请求失败: {str(e)}",
                url=url,
                req_body=data,
                headers=headers
            )
        except json.JSONDecodeError as e:
            logger.error(f"[zdpytools v{__version__}] 解析响应JSON失败: {e}, URL: {url}")
            raise AIHubMaxException(
                code=-1,
                msg="响应解析失败",
                url=url,
                req_body=data,
                headers=headers
            )
        except Exception as e:
            tb = traceback.format_exc()
            logger.error(f"[zdpytools v{__version__}] 请求AIHubMax接口未知异常: {e}, URL: {url}\n{tb}")
            raise AIHubMaxException(
                code=-1,
                msg=f"未知错误: {str(e)}",
                url=url,
                req_body=data,
                headers=headers
            )

    async def upload_file(self, file_path: Union[str, Path, BinaryIO], file_name: str = None, is_long_term:bool = False) -> Dict:
        """
        上传文件到临时文件服务

        Args:
            file_path: 文件路径或文件对象
            file_name: 文件名（如果file_path是文件对象，则必须提供）
            is_long_term: 是否长期保存

        Returns:
            上传结果，包含访问URL
            {
                "url": "https://tmpfile.zooai.cc/uploads/2023/04/10/abc123.jpg",
                "quota": 1
            }
        """
        url = f"{AIHUBMAX_API_HOST}{TMPFILE_UPLOAD_URI}?is_long_term={is_long_term}"

        # 处理不同类型的文件输入
        if isinstance(file_path, (str, Path)):
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")

            # 检查文件大小
            file_size = file_path.stat().st_size
            file_size_mb = file_size / 1024 / 1024
            logger.info(f"[zdpytools v{__version__}] 准备上传文件: {file_path.name}, 大小: {file_size_mb:.2f} MB")
            
            if file_size > 100 * 1024 * 1024:  # 100MB限制
                logger.warning(f"[zdpytools v{__version__}] 文件大小 {file_size_mb:.2f} MB 可能过大，建议小于100MB")

            if not file_name:
                file_name = file_path.name

            with open(file_path, "rb") as f:
                files = {"file": (file_name, f.read())}
                response = await self._request_with_retry("POST", url, files=files, check_code=False)
        else:
            # 文件对象
            if not file_name:
                raise ValueError("使用文件对象时必须提供file_name参数")

            # 尝试获取文件大小信息
            try:
                if hasattr(file_path, 'seek') and hasattr(file_path, 'tell'):
                    current_pos = file_path.tell()
                    file_path.seek(0, 2)  # 移动到文件末尾
                    file_size = file_path.tell()
                    file_path.seek(current_pos)  # 恢复原位置
                    file_size_mb = file_size / 1024 / 1024
                    logger.info(f"[zdpytools v{__version__}] 准备上传文件对象: {file_name}, 大小: {file_size_mb:.2f} MB")
            except:
                logger.info(f"[zdpytools v{__version__}] 准备上传文件对象: {file_name}")

            files = {"file": (file_name, file_path)}
            response = await self._request_with_retry("POST", url, files=files, check_code=False)

        # 处理不同的API响应格式
        if response.get("success"):
            # 新格式API：直接有success字段
            logger.info(f"[zdpytools v{__version__}] 文件上传成功，URL: {response.get('url')}")
            logger.info(f"[zdpytools v{__version__}] 文件大小: {response.get('file_size')} bytes")
            logger.info(f"[zdpytools v{__version__}] 过期时间: {response.get('expire_time')}")
            return response
        elif response.get("code") == 0 and response.get("data"):
            # 旧格式API：code=0表示成功，数据在data字段中
            data = response.get("data")
            logger.info(f"[zdpytools v{__version__}] 文件上传成功，URL: {data.get('url')}")
            if data.get("file_size"):
                logger.info(f"[zdpytools v{__version__}] 文件大小: {data.get('file_size')} bytes")
            if data.get("expire_time"):
                logger.info(f"[zdpytools v{__version__}] 过期时间: {data.get('expire_time')}")
            # 统一返回格式
            return {
                "success": True,
                "url": data.get("url"),
                "file_size": data.get("file_size"),
                "expire_time": data.get("expire_time"),
                "is_long_term": data.get("is_long_term", is_long_term)
            }
        else:
            logger.error(f"[zdpytools v{__version__}] 文件上传失败: {response}")
            raise AIHubMaxException(
                code=response.get("code", -1),
                msg=f"上传失败: {response.get('message', response)}",
                url=url,
                req_body=None,
                headers={"Authorization": f"Bearer {self._token}"}
            )
