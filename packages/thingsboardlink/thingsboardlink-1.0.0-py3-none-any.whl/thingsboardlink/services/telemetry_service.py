"""
ThingsBoardLink 遥测服务模块 | ThingsBoardLink Telemetry Service Module

本模块提供遥测数据相关的 API 调用功能。
包括遥测数据的上传、查询、历史数据获取等操作。

This module provides API call functionality related to telemetry data.
Includes telemetry data upload, querying, historical data retrieval operations.
"""

import time
from typing import List, Optional, Dict, Any, Union
from urllib.parse import urljoin

from ..models import TelemetryData, TimeseriesData
from ..exceptions import ValidationError, TelemetryError, NotFoundError


class TelemetryService:
    """
    遥测服务类 | Telemetry Service Class
    
    提供遥测数据相关的所有操作。
    包括数据上传、最新数据获取、历史数据查询等功能。
    
    Provides all operations related to telemetry data.
    Includes data upload, latest data retrieval, historical data querying.
    """

    def __init__(self, client):
        """
        初始化遥测服务 | Initialize telemetry service
        
        Args:
            client: ThingsBoardClient 实例 | ThingsBoardClient instance
        """
        self.client = client

    def post_telemetry(self,
                       device_id: str,
                       telemetry_data: Union[Dict[str, Any], List[TelemetryData], TelemetryData],
                       timestamp: Optional[int] = None) -> bool:
        """
        上传遥测数据 | Upload telemetry data
        
        Args:
            device_id: 设备 ID | Device ID
            telemetry_data: 遥测数据 | Telemetry data
            timestamp: 时间戳（毫秒），可选 | Timestamp in milliseconds (optional)
            
        Returns:
            bool: 上传是否成功 | Whether upload was successful
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
            TelemetryError: 遥测数据上传失败时抛出 | Raised when telemetry upload fails
        """
        if not device_id or not device_id.strip():
            raise ValidationError(
                field_name="device_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=device_id,
                message="设备 ID 不能为空 | Device ID cannot be empty"
            )

        if not telemetry_data:
            raise ValidationError(
                field_name="telemetry_data",
                expected_type="非空数据 | Non-empty data",
                actual_value=telemetry_data,
                message="遥测数据不能为空 | Telemetry data cannot be empty"
            )

        try:
            # 获取设备凭证 | Get device credentials
            credentials = self.client.device_service.get_device_credentials(device_id)

            if not credentials or not credentials.credentials_value:
                raise TelemetryError(
                    "无法获取设备访问令牌 | Cannot get device access token"
                )

            # 使用设备令牌上传遥测数据 | Upload telemetry data using device token
            return self.post_telemetry_with_device_token(
                device_token=credentials.credentials_value,
                telemetry_data=telemetry_data,
                timestamp=timestamp
            )

        except Exception as e:
            if isinstance(e, (ValidationError, TelemetryError)):
                raise
            raise TelemetryError(
                f"上传遥测数据失败 | Failed to upload telemetry data: {str(e)}"
            )

    def post_telemetry_with_device_token(self,
                                         device_token: str,
                                         telemetry_data: Union[Dict[str, Any], List[TelemetryData], TelemetryData],
                                         timestamp: Optional[int] = None) -> bool:
        """
        使用设备令牌上传遥测数据 | Upload telemetry data using device token
        
        Args:
            device_token: 设备访问令牌 | Device access token
            telemetry_data: 遥测数据 | Telemetry data
            timestamp: 时间戳（毫秒），可选 | Timestamp in milliseconds (optional)
            
        Returns:
            bool: 上传是否成功 | Whether upload was successful
        """
        if not device_token or not device_token.strip():
            raise ValidationError(
                field_name="device_token",
                expected_type="非空字符串 | Non-empty string",
                actual_value=device_token,
                message="设备令牌不能为空 | Device token cannot be empty"
            )

        try:
            # 统一时间戳 | Unify timestamp
            if timestamp is None:
                timestamp = int(time.time() * 1000)

            # 转换数据格式 | Convert data format
            if isinstance(telemetry_data, dict):
                # 字典格式：{"key1": value1, "key2": value2} | Dictionary format
                payload = {
                    "ts": timestamp,
                    "values": telemetry_data
                }
            elif isinstance(telemetry_data, TelemetryData):
                # 单个 TelemetryData 对象 | Single TelemetryData object
                payload = telemetry_data.to_dict()
            elif isinstance(telemetry_data, list):
                # TelemetryData 对象列表 | List of TelemetryData objects
                if not telemetry_data:
                    raise ValidationError(
                        field_name="telemetry_data",
                        message="遥测数据列表不能为空 | Telemetry data list cannot be empty"
                    )

                # 按时间戳分组数据 | Group data by timestamp
                grouped_data = {}
                for item in telemetry_data:
                    if not isinstance(item, TelemetryData):
                        raise ValidationError(
                            field_name="telemetry_data",
                            expected_type="TelemetryData 对象列表 | List of TelemetryData objects",
                            actual_value=type(item).__name__
                        )

                    ts = item.timestamp or timestamp
                    if ts not in grouped_data:
                        grouped_data[ts] = {}
                    grouped_data[ts][item.key] = item.value

                # 转换为 API 格式 | Convert to API format
                if len(grouped_data) == 1:
                    # 单个时间戳 | Single timestamp
                    ts, values = next(iter(grouped_data.items()))
                    payload = {"ts": ts, "values": values}
                else:
                    # 多个时间戳 | Multiple timestamps
                    payload = [
                        {"ts": ts, "values": values}
                        for ts, values in grouped_data.items()
                    ]
            else:
                raise ValidationError(
                    field_name="telemetry_data",
                    expected_type="Dict, TelemetryData 或 List[TelemetryData] | Dict, TelemetryData or List[TelemetryData]",
                    actual_value=type(telemetry_data).__name__
                )

            # 使用设备令牌直接发送HTTP请求 | Send HTTP request directly using device token
            import requests

            headers = {
                'Content-Type': 'application/json'
            }

            # ThingsBoard 设备遥测数据上传端点 | ThingsBoard device telemetry upload endpoint
            # 设备令牌作为URL路径的一部分 | Device token as part of URL path
            response = requests.post(
                f"{self.client.base_url}/api/v1/{device_token}/telemetry",
                json=payload,
                headers=headers,
                timeout=self.client.timeout,
                verify=self.client.verify_ssl
            )

            if response.status_code == 200:
                return True
            else:
                raise TelemetryError(
                    f"遥测数据上传失败，状态码: {response.status_code} | Telemetry upload failed, status code: {response.status_code}"
                )

        except Exception as e:
            if isinstance(e, (ValidationError, TelemetryError)):
                raise
            raise TelemetryError(
                f"上传遥测数据失败 | Failed to upload telemetry data: {str(e)}"
            )

    def get_latest_telemetry(self,
                             device_id: str,
                             keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        获取最新遥测数据 | Get latest telemetry data
        
        Args:
            device_id: 设备 ID | Device ID
            keys: 要获取的数据键列表，为空则获取所有 | List of data keys to retrieve, empty for all
            
        Returns:
            Dict[str, Any]: 最新遥测数据 | Latest telemetry data
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
            NotFoundError: 设备不存在时抛出 | Raised when device does not exist
            TelemetryError: 获取数据失败时抛出 | Raised when data retrieval fails
        """
        if not device_id or not device_id.strip():
            raise ValidationError(
                field_name="device_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=device_id,
                message="设备 ID 不能为空 | Device ID cannot be empty"
            )

        try:
            endpoint = f"/api/plugins/telemetry/DEVICE/{device_id}/values/timeseries"

            params = {}
            if keys:
                params["keys"] = ",".join(keys)

            response = self.client.get(endpoint, params=params)

            telemetry_data = response.json()

            # 转换为更友好的格式 | Convert to more friendly format
            result = {}
            for key, values in telemetry_data.items():
                if values and len(values) > 0:
                    latest_value = values[0]  # 第一个值是最新的 | First value is the latest
                    result[key] = {
                        "value": latest_value.get("value"),
                        "timestamp": latest_value.get("ts")
                    }

            return result

        except Exception as e:
            if "404" in str(e) or "Not Found" in str(e):
                raise NotFoundError(
                    resource_type="设备 | Device",
                    resource_id=device_id
                )
            raise TelemetryError(
                f"获取最新遥测数据失败 | Failed to get latest telemetry data: {str(e)}"
            )

    def get_timeseries_telemetry(self,
                                 device_id: str,
                                 keys: List[str],
                                 start_ts: int,
                                 end_ts: int,
                                 interval: Optional[int] = None,
                                 limit: Optional[int] = None,
                                 agg: Optional[str] = None) -> Dict[str, TimeseriesData]:
        """
        获取时间序列遥测数据 | Get time series telemetry data
        
        Args:
            device_id: 设备 ID | Device ID
            keys: 数据键列表 | List of data keys
            start_ts: 开始时间戳（毫秒） | Start timestamp in milliseconds
            end_ts: 结束时间戳（毫秒） | End timestamp in milliseconds
            interval: 聚合间隔（毫秒），可选 | Aggregation interval in milliseconds (optional)
            limit: 数据点数量限制，可选 | Data point limit (optional)
            agg: 聚合方式（MIN, MAX, AVG, SUM, COUNT），可选 | Aggregation method (optional)
            
        Returns:
            Dict[str, TimeseriesData]: 时间序列数据字典 | Time series data dictionary
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
            TelemetryError: 获取数据失败时抛出 | Raised when data retrieval fails
        """
        if not device_id or not device_id.strip():
            raise ValidationError(
                field_name="device_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=device_id,
                message="设备 ID 不能为空 | Device ID cannot be empty"
            )

        if not keys:
            raise ValidationError(
                field_name="keys",
                expected_type="非空列表 | Non-empty list",
                actual_value=keys,
                message="数据键列表不能为空 | Data keys list cannot be empty"
            )

        if start_ts >= end_ts:
            raise ValidationError(
                field_name="start_ts/end_ts",
                message="开始时间必须小于结束时间 | Start time must be less than end time"
            )

        try:
            endpoint = f"/api/plugins/telemetry/DEVICE/{device_id}/values/timeseries"

            params = {
                "keys": ",".join(keys),
                "startTs": start_ts,
                "endTs": end_ts
            }

            if interval is not None:
                params["interval"] = interval
            if limit is not None:
                params["limit"] = limit
            if agg is not None:
                params["agg"] = agg.upper()

            response = self.client.get(endpoint, params=params)
            telemetry_data = response.json()

            # 转换为 TimeseriesData 对象 | Convert to TimeseriesData objects
            result = {}
            for key, values in telemetry_data.items():
                result[key] = TimeseriesData.from_dict(key, values)

            return result

        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise TelemetryError(
                f"获取时间序列遥测数据失败 | Failed to get time series telemetry data: {str(e)}"
            )

    def delete_telemetry(self,
                         device_id: str,
                         keys: List[str],
                         delete_all_data_for_keys: bool = False,
                         start_ts: Optional[int] = None,
                         end_ts: Optional[int] = None) -> bool:
        """
        删除遥测数据 | Delete telemetry data
        
        Args:
            device_id: 设备 ID | Device ID
            keys: 要删除的数据键列表 | List of data keys to delete
            delete_all_data_for_keys: 是否删除键的所有数据 | Whether to delete all data for keys
            start_ts: 开始时间戳（毫秒），可选 | Start timestamp in milliseconds (optional)
            end_ts: 结束时间戳（毫秒），可选 | End timestamp in milliseconds (optional)
            
        Returns:
            bool: 删除是否成功 | Whether deletion was successful
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
            TelemetryError: 删除数据失败时抛出 | Raised when data deletion fails
        """
        if not device_id or not device_id.strip():
            raise ValidationError(
                field_name="device_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=device_id,
                message="设备 ID 不能为空 | Device ID cannot be empty"
            )

        if not keys:
            raise ValidationError(
                field_name="keys",
                expected_type="非空列表 | Non-empty list",
                actual_value=keys,
                message="数据键列表不能为空 | Data keys list cannot be empty"
            )

        try:
            endpoint = f"/api/plugins/telemetry/DEVICE/{device_id}/timeseries/delete"

            params = {
                "keys": ",".join(keys),
                "deleteAllDataForKeys": str(delete_all_data_for_keys).lower()
            }

            if not delete_all_data_for_keys:
                if start_ts is not None:
                    params["startTs"] = start_ts
                if end_ts is not None:
                    params["endTs"] = end_ts

            response = self.client.delete(endpoint, params=params)
            return response.status_code == 200

        except Exception as e:
            raise TelemetryError(
                f"删除遥测数据失败 | Failed to delete telemetry data: {str(e)}"
            )

    def get_telemetry_keys(self, device_id: str) -> List[str]:
        """
        获取设备的所有遥测数据键 | Get all telemetry data keys for device
        
        Args:
            device_id: 设备 ID | Device ID
            
        Returns:
            List[str]: 遥测数据键列表 | List of telemetry data keys
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
            TelemetryError: 获取数据键失败时抛出 | Raised when getting data keys fails
        """
        if not device_id or not device_id.strip():
            raise ValidationError(
                field_name="device_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=device_id,
                message="设备 ID 不能为空 | Device ID cannot be empty"
            )

        try:
            endpoint = f"/api/plugins/telemetry/DEVICE/{device_id}/keys/timeseries"
            response = self.client.get(endpoint)

            keys_data = response.json()
            return keys_data if isinstance(keys_data, list) else []

        except Exception as e:
            raise TelemetryError(
                f"获取遥测数据键失败 | Failed to get telemetry keys: {str(e)}"
            )
