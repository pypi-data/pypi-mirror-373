"""
ThingsBoardLink 核心客户端模块 | ThingsBoardLink Core Client Module

本模块提供了与 ThingsBoard 平台交互的核心客户端类。
客户端负责认证管理、HTTP 请求处理和服务模块的统一访问。

This module provides the core client class for interacting with the ThingsBoard platform.
The client handles authentication management, HTTP request processing, and unified access to service modules.
"""

import json
import time
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .exceptions import (
    AuthenticationError,
    APIError,
    ConnectionError,
    TimeoutError,
    ConfigurationError
)


class ThingsBoardClient:
    """
    ThingsBoard 核心客户端类
    提供与 ThingsBoard 平台交互的统一接口。
    负责认证管理、HTTP 请求处理和错误处理。

    ThingsBoard Core Client Class
    Provides a unified interface for interacting with the ThingsBoard platform.
    Handles authentication management, HTTP request processing, and error handling.
    """

    def __init__(self,
                 base_url: str,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 timeout: float = 30.0,
                 max_retries: int = 3,
                 retry_backoff_factor: float = 0.3,
                 verify_ssl: bool = True):
        """
        初始化 ThingsBoard 客户端 | Initialize ThingsBoard client
        
        Args:
            base_url: ThingsBoard 服务器基础 URL | ThingsBoard server base URL
            username: 用户名（可选） | Username (optional)
            password: 密码（可选） | Password (optional)
            timeout: 请求超时时间（秒） | Request timeout in seconds
            max_retries: 最大重试次数 | Maximum number of retries
            retry_backoff_factor: 重试退避因子 | Retry backoff factor
            verify_ssl: 是否验证 SSL 证书 | Whether to verify SSL certificates
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        # 认证相关属性 | Authentication related attributes
        self._jwt_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._token_expires_at: Optional[float] = None

        # 创建 HTTP 会话 | Create HTTP session
        self._session = requests.Session()

        # 配置重试策略，兼容不同版本的 urllib3 | Configure retry strategy, compatible with different versions of urllib3
        try:
            # 尝试使用新版本的参数名 | Try using new version parameter name
            retry_strategy = Retry(
                total=max_retries,
                backoff_factor=retry_backoff_factor,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS"]
            )
        except TypeError:
            # 回退到旧版本的参数名 | Fallback to old version parameter name
            retry_strategy = Retry(
                total=max_retries,
                backoff_factor=retry_backoff_factor,
                status_forcelist=[429, 500, 502, 503, 504],
                method_whitelist=["HEAD", "GET", "OPTIONS"]
            )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

        # 设置默认请求头 | Set default request headers
        self._session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

        # 延迟导入服务模块以避免循环导入 | Lazy import service modules to avoid circular imports
        self._device_service = None
        self._telemetry_service = None
        self._attribute_service = None
        self._alarm_service = None
        self._rpc_service = None
        self._relation_service = None

    @property
    def device_service(self):
        """获取设备服务实例 | Get device service instance"""
        if self._device_service is None:
            from .services.device_service import DeviceService
            self._device_service = DeviceService(self)
        return self._device_service

    @property
    def telemetry_service(self):
        """获取遥测服务实例 | Get telemetry service instance"""
        if self._telemetry_service is None:
            from .services.telemetry_service import TelemetryService
            self._telemetry_service = TelemetryService(self)
        return self._telemetry_service

    @property
    def attribute_service(self):
        """获取属性服务实例 | Get attribute service instance"""
        if self._attribute_service is None:
            from .services.attribute_service import AttributeService
            self._attribute_service = AttributeService(self)
        return self._attribute_service

    @property
    def alarm_service(self):
        """获取警报服务实例 | Get alarm service instance"""
        if self._alarm_service is None:
            from .services.alarm_service import AlarmService
            self._alarm_service = AlarmService(self)
        return self._alarm_service

    @property
    def rpc_service(self):
        """获取 RPC 服务实例 | Get RPC service instance"""
        if self._rpc_service is None:
            from .services.rpc_service import RpcService
            self._rpc_service = RpcService(self)
        return self._rpc_service

    @property
    def relation_service(self):
        """获取关系服务实例 | Get relation service instance"""
        if self._relation_service is None:
            from .services.relation_service import RelationService
            self._relation_service = RelationService(self)
        return self._relation_service

    @property
    def is_authenticated(self) -> bool:
        """检查是否已认证 | Check if authenticated"""
        return (self._jwt_token is not None and
                self._token_expires_at is not None and
                time.time() < self._token_expires_at)

    def login(self, username: Optional[str] = None, password: Optional[str] = None) -> bool:
        """
        用户登录 | User login
        
        Args:
            username: 用户名（可选，使用初始化时的用户名） | Username (optional, use username from initialization)
            password: 密码（可选，使用初始化时的密码） | Password (optional, use password from initialization)
            
        Returns:
            bool: 登录是否成功 | Whether login was successful
            
        Raises:
            AuthenticationError: 认证失败时抛出 | Raised when authentication fails
            ConfigurationError: 配置错误时抛出 | Raised when configuration is invalid
        """
        # 使用提供的凭据或初始化时的凭据 | Use provided credentials or credentials from initialization
        auth_username = username or self.username
        auth_password = password or self.password

        if not auth_username or not auth_password:
            raise ConfigurationError(
                "用户名和密码不能为空 | Username and password cannot be empty",
                config_key="username/password",
                expected_value="非空字符串 | Non-empty string"
            )

        login_data = {
            "username": auth_username,
            "password": auth_password
        }

        try:
            response = self._session.post(
                urljoin(self.base_url, "/api/auth/login"),
                json=login_data,
                timeout=self.timeout,
                verify=self.verify_ssl
            )

            if response.status_code == 200:
                auth_data = response.json()
                self._jwt_token = auth_data.get("token")
                self._refresh_token = auth_data.get("refreshToken")

                # 设置令牌过期时间（假设令牌有效期为 1 小时） | Set token expiration time (assume token is valid for 1 hour)
                self._token_expires_at = time.time() + 3600

                # 更新会话头部 | Update session headers
                self._session.headers.update({
                    'X-Authorization': f'Bearer {self._jwt_token}'
                })

                # 更新客户端凭据 | Update client credentials
                self.username = auth_username
                self.password = auth_password

                return True
            else:
                error_data = {}
                try:
                    error_data = response.json()
                except (ValueError, json.JSONDecodeError):
                    pass

                raise AuthenticationError(
                    f"登录失败，状态码: {response.status_code} | Login failed, status code: {response.status_code}",
                    details={
                        "status_code": response.status_code,
                        "response_data": error_data,
                        "username": auth_username
                    }
                )

        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"无法连接到 ThingsBoard 服务器 | Unable to connect to ThingsBoard server: {str(e)}",
                server_url=self.base_url
            )
        except requests.exceptions.Timeout as e:
            raise TimeoutError(
                f"登录请求超时 | Login request timeout: {str(e)}",
                timeout_seconds=self.timeout,
                operation="login"
            )

    def logout(self) -> bool:
        """
        用户登出 | User logout
        
        Returns:
            bool: 登出是否成功 | Whether logout was successful
        """
        if not self.is_authenticated:
            return True

        try:
            response = self._session.post(
                urljoin(self.base_url, "/api/auth/logout"),
                timeout=self.timeout,
                verify=self.verify_ssl
            )

            # 清除认证信息 | Clear authentication information
            self._jwt_token = None
            self._refresh_token = None
            self._token_expires_at = None

            # 移除认证头部 | Remove authentication headers
            if 'X-Authorization' in self._session.headers:
                del self._session.headers['X-Authorization']

            return response.status_code == 200

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            # 即使网络错误，也清除本地认证信息 | Clear local authentication info even on network errors
            self._jwt_token = None
            self._refresh_token = None
            self._token_expires_at = None

            if 'X-Authorization' in self._session.headers:
                del self._session.headers['X-Authorization']

            return True

    def refresh_token(self) -> bool:
        """
        刷新访问令牌 | Refresh access token
        
        Returns:
            bool: 刷新是否成功 | Whether refresh was successful
        """
        if not self._refresh_token:
            return False

        try:
            response = self._session.post(
                urljoin(self.base_url, "/api/auth/token"),
                json={"refreshToken": self._refresh_token},
                timeout=self.timeout,
                verify=self.verify_ssl
            )

            if response.status_code == 200:
                auth_data = response.json()
                self._jwt_token = auth_data.get("token")
                self._refresh_token = auth_data.get("refreshToken")
                self._token_expires_at = time.time() + 3600

                # 更新会话头部 | Update session headers
                self._session.headers.update({
                    'X-Authorization': f'Bearer {self._jwt_token}'
                })

                return True

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            pass

        return False

    def _ensure_authenticated(self):
        """
        确保客户端已认证 | Ensure client is authenticated
        
        Raises:
            AuthenticationError: 未认证时抛出 | Raised when not authenticated
        """
        if not self.is_authenticated:
            # 尝试刷新令牌 | Try to refresh token
            if not self.refresh_token():
                # 尝试重新登录 | Try to re-login
                if self.username and self.password:
                    if not self.login():
                        raise AuthenticationError("认证失败，请重新登录 | Authentication failed, please login again")
                else:
                    raise AuthenticationError("未认证，请先登录 | Not authenticated, please login first")

    def request(self,
                method: str,
                endpoint: str,
                data: Optional[Union[Dict[str, Any], str]] = None,
                params: Optional[Dict[str, Any]] = None,
                headers: Optional[Dict[str, str]] = None,
                require_auth: bool = True,
                timeout: Optional[float] = None) -> requests.Response:
        """
        发送 HTTP 请求 | Send HTTP request
        
        Args:
            method: HTTP 方法 | HTTP method
            endpoint: API 端点 | API endpoint
            data: 请求数据 | Request data
            params: 查询参数 | Query parameters
            headers: 请求头部 | Request headers
            require_auth: 是否需要认证 | Whether authentication is required
            timeout: 请求超时时间 | Request timeout
            
        Returns:
            requests.Response: HTTP 响应对象 | HTTP response object
            
        Raises:
            AuthenticationError: 认证失败时抛出 | Raised when authentication fails
            APIError: API 调用失败时抛出 | Raised when API call fails
            ConnectionError: 连接失败时抛出 | Raised when connection fails
            TimeoutError: 请求超时时抛出 | Raised when request times out
        """
        if require_auth:
            self._ensure_authenticated()

        # 构建完整 URL | Build full URL
        url = urljoin(self.base_url, endpoint.lstrip('/'))

        # 准备请求参数 | Prepare request parameters
        request_kwargs = {
            'timeout': timeout or self.timeout,
            'verify': self.verify_ssl
        }

        if params:
            request_kwargs['params'] = params

        if headers:
            request_kwargs['headers'] = headers

        if data is not None:
            if isinstance(data, str):
                request_kwargs['data'] = data
            else:
                request_kwargs['json'] = data

        try:
            response = self._session.request(method, url, **request_kwargs)

            # 检查响应状态 | Check response status
            if response.status_code >= 400:
                raise APIError.from_response(response)

            return response

        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"连接失败 | Connection failed: {str(e)}",
                server_url=self.base_url
            )
        except requests.exceptions.Timeout as e:
            raise TimeoutError(
                f"请求超时 | Request timeout: {str(e)}",
                timeout_seconds=timeout or self.timeout,
                operation=f"{method} {endpoint}"
            )

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """发送 GET 请求 | Send GET request"""
        return self.request('GET', endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> requests.Response:
        """发送 POST 请求 | Send POST request"""
        return self.request('POST', endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> requests.Response:
        """发送 PUT 请求 | Send PUT request"""
        return self.request('PUT', endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """发送 DELETE 请求 | Send DELETE request"""
        return self.request('DELETE', endpoint, **kwargs)

    def close(self):
        """关闭客户端连接 | Close client connection"""
        if self._session:
            self._session.close()

    def __enter__(self):
        """上下文管理器入口 | Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出 | Context manager exit"""
        self.logout()
        self.close()
