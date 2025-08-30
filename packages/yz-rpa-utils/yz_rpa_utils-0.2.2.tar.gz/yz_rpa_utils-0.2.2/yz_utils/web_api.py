import traceback
from concurrent.futures import ThreadPoolExecutor

import requests, json, time, base64, asyncio
import threading
from typing import Callable, List, Optional
import aiohttp
from tenacity import (
    retry,
    retry_if_result,
    stop_after_attempt,
    wait_fixed
)


# 定义重试条件
def retry_in_expected_code(response, expected_code_list):
    """状态码在范围内"""
    return response.status_code in expected_code_list


class ApiClient:
    def __init__(self, base_url: str, user_name: str, password: str, _print: Callable = print):
        self.user_name = user_name
        self.password = password
        self.base_url = base_url
        self.token: Optional[str] = None
        self.token_refresh_time: float = 0.0
        self.print = _print
        self.token_thread_running = False
        self.token_refresh_thread = None

        if not self.base_url.startswith('http'):
            raise ValueError('请检查base_url格式是否正确')
        if not self.user_name or not self.password:
            raise ValueError('请配置正确的用户名和密码')

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def initialize(self):
        """初始化客户端并获取访问令牌"""
        self.get_access_token()
        self.token_thread_running = True
        # 启动后台令牌刷新线程
        self.token_refresh_thread = threading.Thread(target=self.token_refresh_loop, daemon=True)
        self.token_refresh_thread.start()

    def token_refresh_loop(self):
        """后台令牌刷新循环"""
        while self.token_thread_running:
            try:
                self.get_access_token()
            except Exception as ex:
                self.print(f"令牌刷新失败: {ex}\n{traceback.format_exc()}")
            time.sleep(30)  # 每30秒检查一次

    # 同步重试装饰器
    @retry(
        retry=retry_if_result(lambda response: retry_in_expected_code(
            response, [401, 408, 429, 500, 502, 503, 504]
        )),
        stop=stop_after_attempt(10),  # 最大重试次数
        wait=wait_fixed(6),  # 每次重试间隔10秒
    )
    def retry_request(self, func: Callable):
        """带重试机制的同步请求"""
        try:
            response = func()
            self.print(f"请求结果: {response.status_code} {response.text}")
            return response
        except Exception as ex:
            self.print(f"请求异常: {ex}\n{traceback.format_exc()}")
            raise

    def get_access_token(self):
        """获取或刷新访问令牌"""
        if self.token and time.time() < self.token_refresh_time:
            self.print(f"令牌过期时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.token_refresh_time))}")
            return

        auth = base64.b64encode(f"{self.user_name}:{self.password}".encode()).decode()
        response = self.retry_request(
            lambda: requests.post(
                url=f"{self.base_url}/api/v1/oauth2/token?grant_type=client_credentials",
                headers={'Authorization': f'Basic {auth}'},
                verify=False
            )
        )

        token_data = response.json()
        self.token = token_data['data']['accessToken']
        expires_in = token_data['data']['expiresIn']
        # 提前60秒刷新令牌
        self.token_refresh_time = time.time() + expires_in - 60
        self.print(f"更新令牌: {self.token}")

    @staticmethod
    def handle_response(response: requests.Response):
        """处理响应数据"""
        data = response.json()
        return data.get('data')

    def get(self, request_path: str, request_params: Optional[dict] = None):
        """同步GET请求"""
        if request_params is None:
            request_params = {}

        response = self.retry_request(
            lambda: requests.get(
                url=f"{self.base_url}/api/v1{request_path}",
                headers={'Authorization': f'Bearer {self.token}'},
                params=request_params,
                verify=False
            )
        )
        return self.handle_response(response)

    def post(self, request_path: str, request_data: dict):
        """同步POST请求(表单数据)"""
        if not request_data:
            raise ValueError('请传入请求参数')

        response = self.retry_request(
            lambda: requests.post(
                url=f"{self.base_url}/api/v1{request_path}",
                headers={'Authorization': f'Bearer {self.token}'},
                data=request_data,
                verify=False
            )
        )
        return self.handle_response(response)

    def post_json(self, request_path: str, request_json: dict):
        """同步POST请求(JSON数据)"""
        if not request_json:
            raise ValueError('请传入请求参数')

        response = self.retry_request(
            lambda: requests.post(
                url=f"{self.base_url}/api/v1{request_path}",
                headers={'Authorization': f'Bearer {self.token}'},
                json=request_json,
                verify=False
            )
        )
        return self.handle_response(response)

    def post_file(self, request_path: str, request_data: dict, files: dict):
        """同步文件上传"""
        if not request_data or not files:
            raise ValueError('请传入请求参数和文件')

        # 处理文件上传格式
        prepared_files = {}
        for field_name, file_info in files.items():
            filename, fileobj = file_info
            if isinstance(fileobj, str):  # 文件路径
                prepared_files[field_name] = (filename, open(fileobj, 'rb'))
            elif hasattr(fileobj, 'read'):  # 文件对象
                prepared_files[field_name] = (filename, fileobj)
            else:  # 直接是二进制数据
                prepared_files[field_name] = (filename, fileobj)

        try:
            response = self.retry_request(
                lambda: requests.post(
                    url=f"{self.base_url}/api/v1{request_path}",
                    headers={'Authorization': f'Bearer {self.token}'},
                    data=request_data,
                    files=prepared_files,
                    verify=False
                )
            )
            return self.handle_response(response)
        finally:
            # 确保关闭所有打开的文件
            for field_name, file_info in prepared_files.items():
                if hasattr(file_info[1], 'close'):
                    file_info[1].close()

    def close(self):
        """关闭客户端并清理资源"""
        self.token_thread_running = False
        if self.token_refresh_thread and self.token_refresh_thread.is_alive():
            self.token_refresh_thread.join(timeout=5.0)
        self.token = None


# 定义重试条件
def retry_in_expected_code_async(response, expected_code_list):
    """状态码在范围内"""
    return response.status in expected_code_list


class AsyncApiClient:
    def __init__(self, base_url: str, user_name: str, password: str, _print: Callable = print):
        self.user_name = user_name
        self.password = password
        self.base_url = base_url
        self.token: Optional[str] = None
        self.token_refresh_time: float = 0.0
        self.print = _print
        self.token_thread_running = None
        self.token_refresh_task = None
        self.executor = ThreadPoolExecutor(max_workers=4)  # 线程池执行同步IO操作

        if not self.base_url.startswith('http'):
            raise ValueError('请检查base_url格式是否正确')
        if not self.user_name or not self.password:
            raise ValueError('请配置正确的用户名和密码')

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def initialize(self):
        await self.get_access_token()
        self.token_thread_running = True
        # 启动后台令牌刷新任务
        self.token_refresh_task = asyncio.create_task(self.token_refresh_loop())

    async def token_refresh_loop(self):
        """后台令牌刷新循环"""
        while self.token_thread_running:
            try:
                await self.get_access_token()
            except Exception as ex:
                self.print(f"令牌刷新失败: {ex}\n{traceback.format_exc()}")
            await asyncio.sleep(30)  # 每30秒检查一次

    # 异步重试装饰器
    @retry(
        retry=retry_if_result(lambda response: retry_in_expected_code(
            response, [401, 408, 429, 500, 502, 503, 504]
        )),
        stop=stop_after_attempt(10),  # 最大重试次数
        wait=wait_fixed(6),  # 每次重试间隔10秒
    )
    async def retry_request(self, func: Callable):
        """带重试机制的异步请求"""
        try:
            # 将同步请求放入线程池执行
            response = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                func
            )
            self.print(f"请求结果: {response.status_code} {response.text}")
            return response
        except Exception as ex:
            self.print(f"请求异常: {ex}\n{traceback.format_exc()}")
            raise

    async def get_access_token(self):
        """获取或刷新访问令牌"""
        if self.token and time.time() < self.token_refresh_time:
            return

        auth = base64.b64encode(f"{self.user_name}:{self.password}".encode()).decode()
        response = await self.retry_request(
            lambda: requests.post(
                url=f"{self.base_url}/api/v1/oauth2/token?grant_type=client_credentials",
                headers={'Authorization': f'Basic {auth}'},
                verify=False
            )
        )

        token_data = response.json()
        self.token = token_data['data']['accessToken']
        expires_in = token_data['data']['expiresIn']
        # 提前60秒刷新令牌
        self.token_refresh_time = time.time() + expires_in - 60
        self.print(f"更新令牌: {self.token}")

    @staticmethod
    def handle_response(response: requests.Response):
        """处理响应数据"""
        data = response.json()
        return data.get('data')

    async def get(self, request_path: str, request_params: Optional[dict] = None):
        """异步GET请求"""
        if request_params is None:
            request_params = {}

        response = await self.retry_request(
            lambda: requests.get(
                url=f"{self.base_url}/api/v1{request_path}",
                headers={'Authorization': f'Bearer {self.token}'},
                params=request_params,
                verify=False
            )
        )
        return self.handle_response(response)

    async def post(self, request_path: str, request_data: dict):
        """异步POST请求(表单数据)"""
        if not request_data:
            raise ValueError('请传入请求参数')

        response = await self.retry_request(
            lambda: requests.post(
                url=f"{self.base_url}/api/v1{request_path}",
                headers={'Authorization': f'Bearer {self.token}'},
                data=request_data,
                verify=False
            )
        )
        return self.handle_response(response)

    async def post_json(self, request_path: str, request_json: dict):
        """异步POST请求(JSON数据)"""
        if not request_json:
            raise ValueError('请传入请求参数')

        response = await self.retry_request(
            lambda: requests.post(
                url=f"{self.base_url}/api/v1{request_path}",
                headers={'Authorization': f'Bearer {self.token}'},
                json=request_json,
                verify=False
            )
        )
        return self.handle_response(response)

    async def post_file(self, request_path: str, request_data: dict, files: dict):
        """异步文件上传"""
        if not request_data or not files:
            raise ValueError('请传入请求参数和文件')

        # 处理文件上传格式
        prepared_files = {}
        for field_name, file_info in files.items():
            filename, fileobj = file_info
            if isinstance(fileobj, str):  # 文件路径
                prepared_files[field_name] = (filename, open(fileobj, 'rb'))
            elif hasattr(fileobj, 'read'):  # 文件对象
                prepared_files[field_name] = (filename, fileobj)
            else:  # 直接是二进制数据
                prepared_files[field_name] = (filename, fileobj)

        try:
            response = await self.retry_request(
                lambda: requests.post(
                    url=f"{self.base_url}/api/v1{request_path}",
                    headers={'Authorization': f'Bearer {self.token}'},
                    data=request_data,
                    files=prepared_files,
                    verify=False
                )
            )
            return self.handle_response(response)
        finally:
            # 确保关闭所有打开的文件
            for field_name, file_info in prepared_files.items():
                if hasattr(file_info[1], 'close'):
                    file_info[1].close()

    async def close(self):
        """关闭客户端并清理资源"""
        self.token_thread_running = False
        if self.token_refresh_task:
            self.token_refresh_task.cancel()
            try:
                await self.token_refresh_task
            except asyncio.CancelledError:
                pass
        self.executor.shutdown()
        self.token = None
