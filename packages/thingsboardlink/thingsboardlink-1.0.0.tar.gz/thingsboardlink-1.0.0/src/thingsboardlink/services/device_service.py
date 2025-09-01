"""
ThingsBoardLink 设备服务模块 | ThingsBoardLink Device Service Module

本模块提供设备管理相关的 API 调用功能。
包括设备的创建、查询、更新、删除以及凭证管理等操作。

This module provides API call functionality related to device management.
Includes device creation, querying, updating, deletion, and credential management operations.
"""

from typing import List, Optional, Dict, Any
from urllib.parse import urljoin

from ..models import Device, DeviceCredentials, PageData
from ..exceptions import NotFoundError, DeviceError, ValidationError


class DeviceService:
    """
    设备服务类 | Device Service Class
    
    提供设备管理相关的所有操作。
    包括 CRUD 操作、凭证管理和批量查询等功能。
    
    Provides all operations related to device management.
    Includes CRUD operations, credential management, and batch querying.
    """

    def __init__(self, client):
        """
        初始化设备服务 | Initialize device service
        
        Args:
            client: ThingsBoardClient 实例 | ThingsBoardClient instance
        """
        self.client = client

    def create_device(self,
                      name: str,
                      device_type: str = "default",
                      label: Optional[str] = None,
                      additional_info: Optional[Dict[str, Any]] = None) -> Device:
        """
        创建设备 | Create device
        
        Args:
            name: 设备名称 | Device name
            device_type: 设备类型 | Device type
            label: 设备标签 | Device label
            additional_info: 附加信息 | Additional information
            
        Returns:
            Device: 创建的设备对象 | Created device object
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
            DeviceError: 设备创建失败时抛出 | Raised when device creation fails
        """
        if not name or not name.strip():
            raise ValidationError(
                field_name="name",
                expected_type="非空字符串 | Non-empty string",
                actual_value=name,
                message="设备名称不能为空 | Device name cannot be empty"
            )

        device = Device(
            name=name.strip(),
            type=device_type,
            label=label,
            additional_info=additional_info or {}
        )

        try:
            response = self.client.post(
                "/api/device",
                data=device.to_dict()
            )

            device_data = response.json()
            return Device.from_dict(device_data)

        except Exception as e:
            raise DeviceError(
                f"创建设备失败 | Failed to create device: {str(e)}",
                device_name=name
            )

    def get_device_by_id(self, device_id: str) -> Device:
        """
        根据 ID 获取设备 | Get device by ID
        
        Args:
            device_id: 设备 ID | Device ID
            
        Returns:
            Device: 设备对象 | Device object
            
        Raises:
            NotFoundError: 设备不存在时抛出 | Raised when device does not exist
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
            response = self.client.get(f"/api/device/{device_id}")
            device_data = response.json()
            return Device.from_dict(device_data)

        except Exception as e:
            if "404" in str(e) or "Not Found" in str(e):
                raise NotFoundError(
                    resource_type="设备 | Device",
                    resource_id=device_id
                )
            raise DeviceError(
                f"获取设备失败 | Failed to get device: {str(e)}",
                device_id=device_id
            )

    def update_device(self, device: Device) -> Device:
        """
        更新设备信息 | Update device information
        
        Args:
            device: 设备对象 | Device object
            
        Returns:
            Device: 更新后的设备对象 | Updated device object
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
            DeviceError: 设备更新失败时抛出 | Raised when device update fails
        """
        if not device.id:
            raise ValidationError(
                field_name="device.id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=device.id,
                message="设备 ID 不能为空 | Device ID cannot be empty"
            )

        if not device.name or not device.name.strip():
            raise ValidationError(
                field_name="device.name",
                expected_type="非空字符串 | Non-empty string",
                actual_value=device.name,
                message="设备名称不能为空 | Device name cannot be empty"
            )

        try:
            response = self.client.post(
                "/api/device",
                data=device.to_dict()
            )

            device_data = response.json()
            return Device.from_dict(device_data)

        except Exception as e:
            raise DeviceError(
                f"更新设备失败 | Failed to update device: {str(e)}",
                device_id=device.id,
                device_name=device.name
            )

    def delete_device(self, device_id: str) -> bool:
        """
        删除设备 | Delete device
        
        Args:
            device_id: 设备 ID | Device ID
            
        Returns:
            bool: 删除是否成功 | Whether deletion was successful
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
            DeviceError: 设备删除失败时抛出 | Raised when device deletion fails
        """
        if not device_id or not device_id.strip():
            raise ValidationError(
                field_name="device_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=device_id,
                message="设备 ID 不能为空 | Device ID cannot be empty"
            )

        try:
            response = self.client.delete(f"/api/device/{device_id}")
            return response.status_code == 200

        except Exception as e:
            raise DeviceError(
                f"删除设备失败 | Failed to delete device: {str(e)}",
                device_id=device_id
            )

    def get_tenant_devices(self,
                           page_size: int = 10,
                           page: int = 0,
                           text_search: Optional[str] = None,
                           sort_property: Optional[str] = None,
                           sort_order: Optional[str] = None) -> PageData:
        """
        获取租户下的设备列表 | Get tenant devices list
        
        Args:
            page_size: 页面大小 | Page size
            page: 页码（从 0 开始） | Page number (starting from 0)
            text_search: 文本搜索 | Text search
            sort_property: 排序属性 | Sort property
            sort_order: 排序顺序（ASC/DESC） | Sort order (ASC/DESC)
            
        Returns:
            PageData: 分页设备数据 | Paginated device data
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
        """
        if page_size <= 0:
            raise ValidationError(
                field_name="page_size",
                expected_type="正整数 | Positive integer",
                actual_value=page_size,
                message="页面大小必须大于 0 | Page size must be greater than 0"
            )

        if page < 0:
            raise ValidationError(
                field_name="page",
                expected_type="非负整数 | Non-negative integer",
                actual_value=page,
                message="页码不能小于 0 | Page number cannot be less than 0"
            )

        params = {
            "pageSize": page_size,
            "page": page
        }

        if text_search:
            params["textSearch"] = text_search
        if sort_property:
            params["sortProperty"] = sort_property
        if sort_order:
            params["sortOrder"] = sort_order

        try:
            response = self.client.get(
                "/api/tenant/devices",
                params=params
            )

            page_data = response.json()
            return PageData.from_dict(page_data, Device)

        except Exception as e:
            raise DeviceError(
                f"获取设备列表失败 | Failed to get device list: {str(e)}"
            )

    def get_device_credentials(self, device_id: str) -> DeviceCredentials:
        """
        获取设备凭证 | Get device credentials
        
        Args:
            device_id: 设备 ID | Device ID
            
        Returns:
            DeviceCredentials: 设备凭证对象 | Device credentials object
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
            NotFoundError: 设备不存在时抛出 | Raised when device does not exist
        """
        if not device_id or not device_id.strip():
            raise ValidationError(
                field_name="device_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=device_id,
                message="设备 ID 不能为空 | Device ID cannot be empty"
            )

        try:
            response = self.client.get(f"/api/device/{device_id}/credentials")
            credentials_data = response.json()
            return DeviceCredentials.from_dict(credentials_data)

        except Exception as e:
            if "404" in str(e) or "Not Found" in str(e):
                raise NotFoundError(
                    resource_type="设备凭证 | Device credentials",
                    resource_id=device_id
                )
            raise DeviceError(
                f"获取设备凭证失败 | Failed to get device credentials: {str(e)}",
                device_id=device_id
            )

    def update_device_credentials(self, credentials: DeviceCredentials) -> DeviceCredentials:
        """
        更新设备凭证 | Update device credentials
        
        Args:
            credentials: 设备凭证对象 | Device credentials object
            
        Returns:
            DeviceCredentials: 更新后的设备凭证对象 | Updated device credentials object
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
            DeviceError: 凭证更新失败时抛出 | Raised when credentials update fails
        """
        if not credentials.device_id:
            raise ValidationError(
                field_name="credentials.device_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=credentials.device_id,
                message="设备 ID 不能为空 | Device ID cannot be empty"
            )

        try:
            response = self.client.post(
                "/api/device/credentials",
                data=credentials.to_dict()
            )

            credentials_data = response.json()
            return DeviceCredentials.from_dict(credentials_data)

        except Exception as e:
            raise DeviceError(
                f"更新设备凭证失败 | Failed to update device credentials: {str(e)}",
                device_id=credentials.device_id
            )

    def get_devices_by_name(self, device_name: str) -> List[Device]:
        """
        根据名称搜索设备 | Search devices by name
        
        Args:
            device_name: 设备名称 | Device name
            
        Returns:
            List[Device]: 匹配的设备列表 | List of matching devices
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
        """
        if not device_name or not device_name.strip():
            raise ValidationError(
                field_name="device_name",
                expected_type="非空字符串 | Non-empty string",
                actual_value=device_name,
                message="设备名称不能为空 | Device name cannot be empty"
            )

        try:
            # 使用分页查询搜索设备 | Use paginated query to search devices
            page_data = self.get_tenant_devices(
                page_size=100,  # 获取更多结果 | Get more results
                text_search=device_name.strip()
            )

            # 过滤精确匹配的设备 | Filter devices with exact name match
            matching_devices = [
                device for device in page_data.data
                if device.name.lower() == device_name.lower()
            ]

            return matching_devices

        except Exception as e:
            raise DeviceError(
                f"搜索设备失败 | Failed to search devices: {str(e)}",
                device_name=device_name
            )

    def device_exists(self, device_id: str) -> bool:
        """
        检查设备是否存在 | Check if device exists
        
        Args:
            device_id: 设备 ID | Device ID
            
        Returns:
            bool: 设备是否存在 | Whether device exists
        """
        try:
            self.get_device_by_id(device_id)
            return True
        except NotFoundError:
            return False
        except Exception:
            return False
