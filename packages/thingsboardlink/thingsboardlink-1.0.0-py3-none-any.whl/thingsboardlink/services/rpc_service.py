"""
ThingsBoardLink RPC 服务模块 | ThingsBoardLink RPC Service Module

本模块提供 RPC（远程过程调用）相关的 API 调用功能。
包括单向和双向 RPC 调用，支持设备控制和通信。

This module provides RPC (Remote Procedure Call) related API call functionality.
Includes one-way and two-way RPC calls, supporting device control and communication.
"""

import time
import asyncio
from typing import Optional, Dict, Any, Union
from urllib.parse import urljoin

from ..models import RPCRequest, RPCResponse
from ..exceptions import ValidationError, RPCError, TimeoutError, NotFoundError


class RpcService:
    """
    RPC 服务类 | RPC Service Class
    
    提供 RPC 调用相关的所有操作。
    支持单向和双向 RPC 调用，以及超时处理。
    
    Provides all operations related to RPC calls.
    Supports one-way and two-way RPC calls, as well as timeout handling.
    """

    def __init__(self, client):
        """
        初始化 RPC 服务 | Initialize RPC service
        
        Args:
            client: ThingsBoardClient 实例 | ThingsBoardClient instance
        """
        self.client = client

    def send_one_way_rpc(self,
                         device_id: str,
                         method: str,
                         params: Optional[Dict[str, Any]] = None) -> bool:
        """
        发送单向 RPC 请求 | Send one-way RPC request
        
        单向 RPC 不等待设备响应，适用于设备控制命令。
        One-way RPC does not wait for device response, suitable for device control commands.
        
        Args:
            device_id: 设备 ID | Device ID
            method: RPC 方法名 | RPC method name
            params: RPC 参数 | RPC parameters
            
        Returns:
            bool: 发送是否成功 | Whether sending was successful
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
            RPCError: RPC 调用失败时抛出 | Raised when RPC call fails
        """
        if not device_id or not device_id.strip():
            raise ValidationError(
                field_name="device_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=device_id,
                message="设备 ID 不能为空 | Device ID cannot be empty"
            )

        if not method or not method.strip():
            raise ValidationError(
                field_name="method",
                expected_type="非空字符串 | Non-empty string",
                actual_value=method,
                message="RPC 方法名不能为空 | RPC method name cannot be empty"
            )

        rpc_request = RPCRequest(
            method=method.strip(),
            params=params or {},
            persistent=False
        )

        try:
            endpoint = f"/api/plugins/rpc/oneway/{device_id}"
            response = self.client.post(
                endpoint,
                data=rpc_request.to_dict()
            )

            return response.status_code == 200

        except Exception as e:
            raise RPCError(
                f"发送单向 RPC 请求失败 | Failed to send one-way RPC request: {str(e)}",
                method_name=method,
                device_id=device_id
            )

    def send_two_way_rpc(self,
                         device_id: str,
                         method: str,
                         params: Optional[Dict[str, Any]] = None,
                         timeout_seconds: float = 30.0) -> RPCResponse:
        """
        发送双向 RPC 请求 | Send two-way RPC request
        
        双向 RPC 等待设备响应，适用于需要获取设备状态或数据的场景。
        Two-way RPC waits for device response, suitable for scenarios requiring device status or data.
        
        Args:
            device_id: 设备 ID | Device ID
            method: RPC 方法名 | RPC method name
            params: RPC 参数 | RPC parameters
            timeout_seconds: 超时时间（秒） | Timeout in seconds
            
        Returns:
            RPCResponse: RPC 响应对象 | RPC response object
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
            RPCError: RPC 调用失败时抛出 | Raised when RPC call fails
            TimeoutError: RPC 调用超时时抛出 | Raised when RPC call times out
        """
        if not device_id or not device_id.strip():
            raise ValidationError(
                field_name="device_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=device_id,
                message="设备 ID 不能为空 | Device ID cannot be empty"
            )

        if not method or not method.strip():
            raise ValidationError(
                field_name="method",
                expected_type="非空字符串 | Non-empty string",
                actual_value=method,
                message="RPC 方法名不能为空 | RPC method name cannot be empty"
            )

        if timeout_seconds <= 0:
            raise ValidationError(
                field_name="timeout_seconds",
                expected_type="正数 | Positive number",
                actual_value=timeout_seconds,
                message="超时时间必须大于 0 | Timeout must be greater than 0"
            )

        rpc_request = RPCRequest(
            method=method.strip(),
            params=params or {},
            timeout=int(timeout_seconds * 1000),  # 转换为毫秒 | Convert to milliseconds
            persistent=False
        )

        try:
            endpoint = f"/api/plugins/rpc/twoway/{device_id}"

            # 使用自定义超时时间 | Use custom timeout
            response = self.client.post(
                endpoint,
                data=rpc_request.to_dict(),
                timeout=timeout_seconds + 5  # 给网络请求额外的缓冲时间 | Extra buffer time for network request
            )

            if response.status_code == 200:
                response_data = response.json()

                # 创建 RPC 响应对象 | Create RPC response object
                rpc_response = RPCResponse(
                    id=response_data.get("id", ""),
                    method=method,
                    response=response_data,
                    timestamp=int(time.time() * 1000)
                )

                return rpc_response
            else:
                # 处理错误响应 | Handle error response
                error_data = {}
                try:
                    error_data = response.json()
                except:
                    pass

                raise RPCError(
                    f"双向 RPC 调用失败，状态码: {response.status_code} | Two-way RPC call failed, status code: {response.status_code}",
                    method_name=method,
                    device_id=device_id
                )

        except TimeoutError:
            raise TimeoutError(
                f"双向 RPC 调用超时 | Two-way RPC call timeout",
                timeout_seconds=timeout_seconds,
                operation=f"RPC {method}"
            )
        except Exception as e:
            if isinstance(e, (ValidationError, RPCError, TimeoutError)):
                raise
            raise RPCError(
                f"发送双向 RPC 请求失败 | Failed to send two-way RPC request: {str(e)}",
                method_name=method,
                device_id=device_id,
                timeout_seconds=timeout_seconds
            )

    def send_persistent_rpc(self,
                            device_id: str,
                            method: str,
                            params: Optional[Dict[str, Any]] = None,
                            timeout_seconds: float = 60.0) -> str:
        """
        发送持久化 RPC 请求 | Send persistent RPC request
        
        持久化 RPC 请求会被存储，直到设备上线并处理。
        Persistent RPC requests are stored until the device comes online and processes them.
        
        Args:
            device_id: 设备 ID | Device ID
            method: RPC 方法名 | RPC method name
            params: RPC 参数 | RPC parameters
            timeout_seconds: 超时时间（秒） | Timeout in seconds
            
        Returns:
            str: RPC 请求 ID | RPC request ID
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
            RPCError: RPC 调用失败时抛出 | Raised when RPC call fails
        """
        if not device_id or not device_id.strip():
            raise ValidationError(
                field_name="device_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=device_id,
                message="设备 ID 不能为空 | Device ID cannot be empty"
            )

        if not method or not method.strip():
            raise ValidationError(
                field_name="method",
                expected_type="非空字符串 | Non-empty string",
                actual_value=method,
                message="RPC 方法名不能为空 | RPC method name cannot be empty"
            )

        rpc_request = RPCRequest(
            method=method.strip(),
            params=params or {},
            timeout=int(timeout_seconds * 1000),
            persistent=True
        )

        try:
            endpoint = f"/api/plugins/rpc/twoway/{device_id}"
            response = self.client.post(
                endpoint,
                data=rpc_request.to_dict()
            )

            if response.status_code == 200:
                response_data = response.json()
                return response_data.get("rpcId", "")
            else:
                raise RPCError(
                    f"发送持久化 RPC 请求失败，状态码: {response.status_code} | Failed to send persistent RPC request, status code: {response.status_code}",
                    method_name=method,
                    device_id=device_id
                )

        except Exception as e:
            if isinstance(e, (ValidationError, RPCError)):
                raise
            raise RPCError(
                f"发送持久化 RPC 请求失败 | Failed to send persistent RPC request: {str(e)}",
                method_name=method,
                device_id=device_id,
                timeout_seconds=timeout_seconds
            )

    def get_persistent_rpc(self, rpc_id: str) -> Optional[RPCResponse]:
        """
        获取持久化 RPC 响应 | Get persistent RPC response
        
        Args:
            rpc_id: RPC 请求 ID | RPC request ID
            
        Returns:
            Optional[RPCResponse]: RPC 响应对象，未完成时返回 None | RPC response object, None if not completed
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
            RPCError: 获取 RPC 响应失败时抛出 | Raised when getting RPC response fails
        """
        if not rpc_id or not rpc_id.strip():
            raise ValidationError(
                field_name="rpc_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=rpc_id,
                message="RPC 请求 ID 不能为空 | RPC request ID cannot be empty"
            )

        try:
            endpoint = f"/api/plugins/rpc/persistent/{rpc_id}"
            response = self.client.get(endpoint)

            if response.status_code == 200:
                response_data = response.json()
                return RPCResponse.from_dict(response_data)
            elif response.status_code == 404:
                return None  # RPC 请求不存在或尚未完成 | RPC request does not exist or not completed yet
            else:
                raise RPCError(
                    f"获取持久化 RPC 响应失败，状态码: {response.status_code} | Failed to get persistent RPC response, status code: {response.status_code}"
                )

        except Exception as e:
            if isinstance(e, (ValidationError, RPCError)):
                raise
            raise RPCError(
                f"获取持久化 RPC 响应失败 | Failed to get persistent RPC response: {str(e)}"
            )

    def delete_persistent_rpc(self, rpc_id: str) -> bool:
        """
        删除持久化 RPC 请求 | Delete persistent RPC request
        
        Args:
            rpc_id: RPC 请求 ID | RPC request ID
            
        Returns:
            bool: 删除是否成功 | Whether deletion was successful
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
            RPCError: 删除 RPC 请求失败时抛出 | Raised when deleting RPC request fails
        """
        if not rpc_id or not rpc_id.strip():
            raise ValidationError(
                field_name="rpc_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=rpc_id,
                message="RPC 请求 ID 不能为空 | RPC request ID cannot be empty"
            )

        try:
            endpoint = f"/api/plugins/rpc/persistent/{rpc_id}"
            response = self.client.delete(endpoint)

            return response.status_code == 200

        except Exception as e:
            raise RPCError(
                f"删除持久化 RPC 请求失败 | Failed to delete persistent RPC request: {str(e)}"
            )

    def wait_for_rpc_response(self,
                              rpc_id: str,
                              timeout_seconds: float = 60.0,
                              poll_interval: float = 1.0) -> Optional[RPCResponse]:
        """
        等待持久化 RPC 响应 | Wait for persistent RPC response
        
        Args:
            rpc_id: RPC 请求 ID | RPC request ID
            timeout_seconds: 超时时间（秒） | Timeout in seconds
            poll_interval: 轮询间隔（秒） | Poll interval in seconds
            
        Returns:
            Optional[RPCResponse]: RPC 响应对象，超时时返回 None | RPC response object, None if timeout
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
            TimeoutError: 等待超时时抛出 | Raised when wait times out
        """
        if not rpc_id or not rpc_id.strip():
            raise ValidationError(
                field_name="rpc_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=rpc_id,
                message="RPC 请求 ID 不能为空 | RPC request ID cannot be empty"
            )

        if timeout_seconds <= 0:
            raise ValidationError(
                field_name="timeout_seconds",
                expected_type="正数 | Positive number",
                actual_value=timeout_seconds,
                message="超时时间必须大于 0 | Timeout must be greater than 0"
            )

        if poll_interval <= 0:
            raise ValidationError(
                field_name="poll_interval",
                expected_type="正数 | Positive number",
                actual_value=poll_interval,
                message="轮询间隔必须大于 0 | Poll interval must be greater than 0"
            )

        start_time = time.time()

        while time.time() - start_time < timeout_seconds:
            try:
                response = self.get_persistent_rpc(rpc_id)
                if response is not None:
                    return response

                # 等待下次轮询 | Wait for next poll
                time.sleep(poll_interval)

            except RPCError:
                # 如果获取响应失败，继续等待 | Continue waiting if getting response fails
                time.sleep(poll_interval)

        # 超时 | Timeout
        raise TimeoutError(
            f"等待 RPC 响应超时 | Wait for RPC response timeout",
            timeout_seconds=timeout_seconds,
            operation=f"wait_for_rpc_response({rpc_id})"
        )

    def send_rpc_with_retry(self,
                            device_id: str,
                            method: str,
                            params: Optional[Dict[str, Any]] = None,
                            max_retries: int = 3,
                            timeout_seconds: float = 30.0,
                            retry_delay: float = 1.0) -> RPCResponse:
        """
        发送带重试的双向 RPC 请求 | Send two-way RPC request with retry
        
        Args:
            device_id: 设备 ID | Device ID
            method: RPC 方法名 | RPC method name
            params: RPC 参数 | RPC parameters
            max_retries: 最大重试次数 | Maximum retry count
            timeout_seconds: 每次请求的超时时间（秒） | Timeout per request in seconds
            retry_delay: 重试延迟（秒） | Retry delay in seconds
            
        Returns:
            RPCResponse: RPC 响应对象 | RPC response object
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
            RPCError: 所有重试都失败时抛出 | Raised when all retries fail
        """
        if max_retries < 0:
            raise ValidationError(
                field_name="max_retries",
                expected_type="非负整数 | Non-negative integer",
                actual_value=max_retries,
                message="最大重试次数不能小于 0 | Maximum retry count cannot be less than 0"
            )

        last_error = None

        for attempt in range(max_retries + 1):
            try:
                return self.send_two_way_rpc(
                    device_id=device_id,
                    method=method,
                    params=params,
                    timeout_seconds=timeout_seconds
                )

            except (RPCError, TimeoutError) as e:
                last_error = e

                if attempt < max_retries:
                    # 等待后重试 | Wait before retry
                    time.sleep(retry_delay)
                    continue
                else:
                    # 所有重试都失败 | All retries failed
                    break

        # 抛出最后一个错误 | Raise the last error
        if last_error:
            raise last_error
        else:
            raise RPCError(
                f"发送 RPC 请求失败，已重试 {max_retries} 次 | Failed to send RPC request after {max_retries} retries",
                method_name=method,
                device_id=device_id
            )
