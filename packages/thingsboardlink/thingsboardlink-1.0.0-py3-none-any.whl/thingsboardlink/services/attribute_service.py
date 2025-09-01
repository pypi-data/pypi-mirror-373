"""
ThingsBoardLink 属性服务模块 | ThingsBoardLink Attribute Service Module

本模块提供属性管理相关的 API 调用功能。
包括客户端属性、服务端属性和共享属性的读写操作。

This module provides API call functionality related to attribute management.
Includes read/write operations for client-side, server-side, and shared attributes.
"""

from typing import List, Optional, Dict, Any, Union
from urllib.parse import urljoin

from ..models import Attribute, AttributeScope
from ..exceptions import ValidationError, NotFoundError, APIError


class AttributeService:
    """
    属性服务类 | Attribute Service Class
    
    提供属性管理相关的所有操作。
    支持客户端属性、服务端属性和共享属性的完整管理。
    
    Provides all operations related to attribute management.
    Supports complete management of client-side, server-side, and shared attributes.
    """

    def __init__(self, client):
        """
        初始化属性服务 | Initialize attribute service

        Args:
            client: ThingsBoardClient 实例 | ThingsBoardClient instance
        """
        self.client = client

    def get_client_attributes(self,
                              device_id: str,
                              keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        获取客户端属性 | Get client-side attributes
        
        Args:
            device_id: 设备 ID | Device ID
            keys: 属性键列表，为空则获取所有 | List of attribute keys, empty for all
            
        Returns:
            Dict[str, Any]: 客户端属性数据 | Client-side attribute data
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
            NotFoundError: 设备不存在时抛出 | Raised when device does not exist
        """
        return self._get_attributes(device_id, AttributeScope.CLIENT_SCOPE, keys)

    def get_server_attributes(self,
                              device_id: str,
                              keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        获取服务端属性 | Get server-side attributes
        
        Args:
            device_id: 设备 ID | Device ID
            keys: 属性键列表，为空则获取所有 | List of attribute keys, empty for all
            
        Returns:
            Dict[str, Any]: 服务端属性数据 | Server-side attribute data
        """
        return self._get_attributes(device_id, AttributeScope.SERVER_SCOPE, keys)

    def get_shared_attributes(self,
                              device_id: str,
                              keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        获取共享属性 | Get shared attributes
        
        Args:
            device_id: 设备 ID | Device ID
            keys: 属性键列表，为空则获取所有 | List of attribute keys, empty for all
            
        Returns:
            Dict[str, Any]: 共享属性数据 | Shared attribute data
        """
        return self._get_attributes(device_id, AttributeScope.SHARED_SCOPE, keys)

    def _get_attributes(self,
                        device_id: str,
                        scope: AttributeScope,
                        keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        获取指定范围的属性 | Get attributes of specified scope
        
        Args:
            device_id: 设备 ID | Device ID
            scope: 属性范围 | Attribute scope
            keys: 属性键列表 | List of attribute keys
            
        Returns:
            Dict[str, Any]: 属性数据 | Attribute data
        """
        if not device_id or not device_id.strip():
            raise ValidationError(
                field_name="device_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=device_id,
                message="设备 ID 不能为空 | Device ID cannot be empty"
            )

        try:
            # 构建端点 URL | Build endpoint URL
            scope_mapping = {
                AttributeScope.CLIENT_SCOPE: "CLIENT_SCOPE",
                AttributeScope.SERVER_SCOPE: "SERVER_SCOPE",
                AttributeScope.SHARED_SCOPE: "SHARED_SCOPE"
            }

            scope_str = scope_mapping[scope]
            endpoint = f"/api/plugins/telemetry/DEVICE/{device_id}/values/attributes/{scope_str}"

            params = {}
            if keys:
                params["keys"] = ",".join(keys)

            response = self.client.get(endpoint, params=params)

            # 处理响应数据 | Process response data
            attributes_data = response.json()

            # 转换为更友好的格式 | Convert to more friendly format
            result = {}
            if isinstance(attributes_data, list):
                # 列表格式：[{"key": "attr1", "value": "value1", "lastUpdateTs": 123456}]
                for attr in attributes_data:
                    key = attr.get("key")
                    if key:
                        result[key] = {
                            "value": attr.get("value"),
                            "lastUpdateTs": attr.get("lastUpdateTs")
                        }
            elif isinstance(attributes_data, dict):
                # 字典格式：{"attr1": [{"value": "value1", "ts": 123456}]}
                for key, values in attributes_data.items():
                    if values and len(values) > 0:
                        latest_value = values[0]  # 第一个值是最新的 | First value is the latest
                        result[key] = {
                            "value": latest_value.get("value"),
                            "lastUpdateTs": latest_value.get("ts")
                        }

            return result

        except Exception as e:
            if "404" in str(e) or "Not Found" in str(e):
                raise NotFoundError(
                    resource_type="设备 | Device",
                    resource_id=device_id
                )
            raise APIError(
                f"获取{scope.value}属性失败 | Failed to get {scope.value} attributes: {str(e)}"
            )

    def set_client_attributes(self,
                              device_id: str,
                              attributes: Union[Dict[str, Any], List[Attribute]]) -> bool:
        """
        设置客户端属性 | Set client-side attributes
        
        Args:
            device_id: 设备 ID | Device ID
            attributes: 属性数据 | Attribute data
            
        Returns:
            bool: 设置是否成功 | Whether setting was successful
        """
        return self._set_attributes(device_id, AttributeScope.CLIENT_SCOPE, attributes)

    def set_server_attributes(self,
                              device_id: str,
                              attributes: Union[Dict[str, Any], List[Attribute]]) -> bool:
        """
        设置服务端属性 | Set server-side attributes
        
        Args:
            device_id: 设备 ID | Device ID
            attributes: 属性数据 | Attribute data
            
        Returns:
            bool: 设置是否成功 | Whether setting was successful
        """
        return self._set_attributes(device_id, AttributeScope.SERVER_SCOPE, attributes)

    def set_shared_attributes(self,
                              device_id: str,
                              attributes: Union[Dict[str, Any], List[Attribute]]) -> bool:
        """
        设置共享属性 | Set shared attributes
        
        Args:
            device_id: 设备 ID | Device ID
            attributes: 属性数据 | Attribute data
            
        Returns:
            bool: 设置是否成功 | Whether setting was successful
        """
        return self._set_attributes(device_id, AttributeScope.SHARED_SCOPE, attributes)

    def _set_attributes(self,
                        device_id: str,
                        scope: AttributeScope,
                        attributes: Union[Dict[str, Any], List[Attribute]]) -> bool:
        """
        设置指定范围的属性 | Set attributes of specified scope
        
        Args:
            device_id: 设备 ID | Device ID
            scope: 属性范围 | Attribute scope
            attributes: 属性数据 | Attribute data
            
        Returns:
            bool: 设置是否成功 | Whether setting was successful
        """
        if not device_id or not device_id.strip():
            raise ValidationError(
                field_name="device_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=device_id,
                message="设备 ID 不能为空 | Device ID cannot be empty"
            )

        if not attributes:
            raise ValidationError(
                field_name="attributes",
                expected_type="非空数据 | Non-empty data",
                actual_value=attributes,
                message="属性数据不能为空 | Attribute data cannot be empty"
            )

        try:
            # 转换属性数据格式 | Convert attribute data format
            if isinstance(attributes, dict):
                payload = attributes
            elif isinstance(attributes, list):
                payload = {}
                for attr in attributes:
                    if isinstance(attr, Attribute):
                        payload[attr.key] = attr.value
                    else:
                        raise ValidationError(
                            field_name="attributes",
                            expected_type="Attribute 对象列表 | List of Attribute objects",
                            actual_value=type(attr).__name__
                        )
            else:
                raise ValidationError(
                    field_name="attributes",
                    expected_type="Dict 或 List[Attribute] | Dict or List[Attribute]",
                    actual_value=type(attributes).__name__
                )

            # 构建端点 URL | Build endpoint URL
            scope_mapping = {
                AttributeScope.CLIENT_SCOPE: "CLIENT_SCOPE",
                AttributeScope.SERVER_SCOPE: "SERVER_SCOPE",
                AttributeScope.SHARED_SCOPE: "SHARED_SCOPE"
            }

            scope_str = scope_mapping[scope]
            endpoint = f"/api/plugins/telemetry/DEVICE/{device_id}/{scope_str}"

            response = self.client.post(endpoint, data=payload)
            return response.status_code == 200

        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise APIError(
                f"设置{scope.value}属性失败 | Failed to set {scope.value} attributes: {str(e)}"
            )

    def delete_attributes(self,
                          device_id: str,
                          scope: AttributeScope,
                          keys: List[str]) -> bool:
        """
        删除属性 | Delete attributes
        
        Args:
            device_id: 设备 ID | Device ID
            scope: 属性范围 | Attribute scope
            keys: 要删除的属性键列表 | List of attribute keys to delete
            
        Returns:
            bool: 删除是否成功 | Whether deletion was successful
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
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
                message="属性键列表不能为空 | Attribute keys list cannot be empty"
            )

        try:
            # 验证scope参数 | Validate scope parameter
            if not isinstance(scope, AttributeScope):
                raise ValidationError(
                    field_name="scope",
                    expected_type="AttributeScope 枚举 | AttributeScope enum",
                    actual_value=type(scope).__name__,
                    message="scope 必须是 AttributeScope 枚举类型 | scope must be AttributeScope enum type"
                )

            scope_mapping = {
                AttributeScope.CLIENT_SCOPE: "CLIENT_SCOPE",
                AttributeScope.SERVER_SCOPE: "SERVER_SCOPE",
                AttributeScope.SHARED_SCOPE: "SHARED_SCOPE"
            }

            if scope not in scope_mapping:
                raise ValidationError(
                    field_name="scope",
                    expected_type="有效的 AttributeScope 值 | Valid AttributeScope value",
                    actual_value=str(scope),
                    message=f"不支持的属性范围: {scope} | Unsupported attribute scope: {scope}"
                )

            scope_str = scope_mapping[scope]
            endpoint = f"/api/plugins/telemetry/DEVICE/{device_id}/{scope_str}"

            params = {"keys": ",".join(keys)}

            response = self.client.delete(endpoint, params=params)
            return response.status_code == 200

        except ValidationError:
            raise
        except Exception as e:
            raise APIError(
                f"删除{scope.value}属性失败 | Failed to delete {scope.value} attributes: {str(e)}"
            )

    def get_attribute_keys(self, device_id: str, scope: AttributeScope) -> List[str]:
        """
        获取属性键列表 | Get attribute keys list
        
        Args:
            device_id: 设备 ID | Device ID
            scope: 属性范围 | Attribute scope
            
        Returns:
            List[str]: 属性键列表 | List of attribute keys
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
        """
        if not device_id or not device_id.strip():
            raise ValidationError(
                field_name="device_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=device_id,
                message="设备 ID 不能为空 | Device ID cannot be empty"
            )

        try:
            scope_mapping = {
                AttributeScope.CLIENT_SCOPE: "CLIENT_SCOPE",
                AttributeScope.SERVER_SCOPE: "SERVER_SCOPE",
                AttributeScope.SHARED_SCOPE: "SHARED_SCOPE"
            }

            scope_str = scope_mapping[scope]
            endpoint = f"/api/plugins/telemetry/DEVICE/{device_id}/keys/attributes/{scope_str}"

            response = self.client.get(endpoint)
            keys_data = response.json()

            return keys_data if isinstance(keys_data, list) else []

        except Exception as e:
            raise APIError(
                f"获取{scope.value}属性键失败 | Failed to get {scope.value} attribute keys: {str(e)}"
            )

    def get_all_attributes(self, device_id: str) -> Dict[str, Dict[str, Any]]:
        """
        获取设备的所有属性 | Get all attributes of device
        
        Args:
            device_id: 设备 ID | Device ID
            
        Returns:
            Dict[str, Dict[str, Any]]: 所有属性数据，按范围分组 | All attribute data, grouped by scope
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
        """
        if not device_id or not device_id.strip():
            raise ValidationError(
                field_name="device_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=device_id,
                message="设备 ID 不能为空 | Device ID cannot be empty"
            )

        result = {}

        try:
            # 获取所有范围的属性 | Get attributes of all scopes
            result["client"] = self.get_client_attributes(device_id)
            result["server"] = self.get_server_attributes(device_id)
            result["shared"] = self.get_shared_attributes(device_id)

            return result

        except Exception as e:
            raise APIError(
                f"获取设备所有属性失败 | Failed to get all device attributes: {str(e)}"
            )

    def update_attribute(self,
                         device_id: str,
                         scope: AttributeScope,
                         key: str,
                         value: Any) -> bool:
        """
        更新单个属性 | Update single attribute
        
        Args:
            device_id: 设备 ID | Device ID
            scope: 属性范围 | Attribute scope
            key: 属性键 | Attribute key
            value: 属性值 | Attribute value
            
        Returns:
            bool: 更新是否成功 | Whether update was successful
        """
        return self._set_attributes(device_id, scope, {key: value})

    def attribute_exists(self,
                         device_id: str,
                         scope: AttributeScope,
                         key: str) -> bool:
        """
        检查属性是否存在 | Check if attribute exists
        
        Args:
            device_id: 设备 ID | Device ID
            scope: 属性范围 | Attribute scope
            key: 属性键 | Attribute key
            
        Returns:
            bool: 属性是否存在 | Whether attribute exists
        """
        try:
            attributes = self._get_attributes(device_id, scope, [key])
            return key in attributes
        except Exception:
            return False
