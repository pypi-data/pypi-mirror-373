"""
ThingsBoardLink 警报服务模块 | ThingsBoardLink Alarm Service Module

本模块提供警报管理相关的 API 调用功能。
包括警报的创建、查询、确认、清除等操作。

This module provides API call functionality related to alarm management.
Includes alarm creation, querying, acknowledgment, clearing operations.
"""

import time
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin

from ..models import Alarm, AlarmSeverity, AlarmStatus, PageData
from ..exceptions import ValidationError, AlarmError, NotFoundError


class AlarmService:
    """
    警报服务类 | Alarm Service Class
    
    提供警报管理相关的所有操作。
    包括警报的创建、查询、状态管理等功能。
    
    Provides all operations related to alarm management.
    Includes alarm creation, querying, status management functions.
    """

    def __init__(self, client):
        """
        初始化警报服务 | Initialize alarm service
        
        Args:
            client: ThingsBoardClient 实例 | ThingsBoardClient instance
        """
        self.client = client

    def create_alarm(self,
                     alarm_type: str,
                     originator_id: str,
                     severity: AlarmSeverity = AlarmSeverity.CRITICAL,
                     details: Optional[Dict[str, Any]] = None,
                     propagate: bool = True) -> Alarm:
        """
        创建警报 | Create alarm
        
        Args:
            alarm_type: 警报类型 | Alarm type
            originator_id: 发起者 ID（通常是设备 ID） | Originator ID (usually device ID)
            severity: 警报严重程度 | Alarm severity
            details: 警报详情 | Alarm details
            propagate: 是否传播警报 | Whether to propagate alarm
            
        Returns:
            Alarm: 创建的警报对象 | Created alarm object
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
            AlarmError: 警报创建失败时抛出 | Raised when alarm creation fails
        """
        if not alarm_type or not alarm_type.strip():
            raise ValidationError(
                field_name="alarm_type",
                expected_type="非空字符串 | Non-empty string",
                actual_value=alarm_type,
                message="警报类型不能为空 | Alarm type cannot be empty"
            )

        if not originator_id or not originator_id.strip():
            raise ValidationError(
                field_name="originator_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=originator_id,
                message="发起者 ID 不能为空 | Originator ID cannot be empty"
            )

        alarm = Alarm(
            type=alarm_type.strip(),
            originator_id=originator_id.strip(),
            severity=severity,
            status=AlarmStatus.ACTIVE_UNACK,
            details=details or {},
            propagate=propagate
        )

        try:
            response = self.client.post(
                "/api/alarm",
                data=alarm.to_dict()
            )

            alarm_data = response.json()
            return Alarm.from_dict(alarm_data)

        except Exception as e:
            raise AlarmError(
                f"创建警报失败 | Failed to create alarm: {str(e)}",
                alarm_type=alarm_type
            )

    def get_alarm(self, alarm_id: str) -> Alarm:
        """
        根据 ID 获取警报 | Get alarm by ID
        
        Args:
            alarm_id: 警报 ID | Alarm ID
            
        Returns:
            Alarm: 警报对象 | Alarm object
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
            NotFoundError: 警报不存在时抛出 | Raised when alarm does not exist
        """
        if not alarm_id or not alarm_id.strip():
            raise ValidationError(
                field_name="alarm_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=alarm_id,
                message="警报 ID 不能为空 | Alarm ID cannot be empty"
            )

        try:
            response = self.client.get(f"/api/alarm/{alarm_id}")
            alarm_data = response.json()
            return Alarm.from_dict(alarm_data)

        except Exception as e:
            if "404" in str(e) or "Not Found" in str(e):
                raise NotFoundError(
                    resource_type="警报 | Alarm",
                    resource_id=alarm_id
                )
            raise AlarmError(
                f"获取警报失败 | Failed to get alarm: {str(e)}",
                alarm_id=alarm_id
            )

    def get_alarms(self,
                   originator_id: str,
                   page_size: int = 10,
                   page: int = 0,
                   text_search: Optional[str] = None,
                   sort_property: Optional[str] = None,
                   sort_order: Optional[str] = None,
                   start_time: Optional[int] = None,
                   end_time: Optional[int] = None,
                   fetch_originator: bool = False,
                   status_list: Optional[List[AlarmStatus]] = None,
                   severity_list: Optional[List[AlarmSeverity]] = None,
                   type_list: Optional[List[str]] = None) -> PageData:
        """
        获取警报列表 | Get alarms list
        
        Args:
            originator_id: 发起者 ID | Originator ID
            page_size: 页面大小 | Page size
            page: 页码（从 0 开始） | Page number (starting from 0)
            text_search: 文本搜索 | Text search
            sort_property: 排序属性 | Sort property
            sort_order: 排序顺序（ASC/DESC） | Sort order (ASC/DESC)
            start_time: 开始时间戳（毫秒） | Start timestamp in milliseconds
            end_time: 结束时间戳（毫秒） | End timestamp in milliseconds
            fetch_originator: 是否获取发起者信息 | Whether to fetch originator info
            status_list: 状态过滤列表 | Status filter list
            severity_list: 严重程度过滤列表 | Severity filter list
            type_list: 类型过滤列表 | Type filter list
            
        Returns:
            PageData: 分页警报数据 | Paginated alarm data
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
        """
        if not originator_id or not originator_id.strip():
            raise ValidationError(
                field_name="originator_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=originator_id,
                message="发起者 ID 不能为空 | Originator ID cannot be empty"
            )

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

        try:
            params = {
                "pageSize": page_size,
                "page": page,
                "fetchOriginator": str(fetch_originator).lower()
            }

            if text_search:
                params["textSearch"] = text_search
            if sort_property:
                params["sortProperty"] = sort_property
            if sort_order:
                params["sortOrder"] = sort_order
            if start_time is not None:
                params["startTime"] = start_time
            if end_time is not None:
                params["endTime"] = end_time

            # 状态过滤 | Status filter
            if status_list:
                params["statusList"] = ",".join([status.value for status in status_list])

            # 严重程度过滤 | Severity filter
            if severity_list:
                params["severityList"] = ",".join([severity.value for severity in severity_list])

            # 类型过滤 | Type filter
            if type_list:
                params["typeList"] = ",".join(type_list)

            endpoint = f"/api/alarm/DEVICE/{originator_id}"
            response = self.client.get(endpoint, params=params)

            page_data = response.json()
            return PageData.from_dict(page_data, Alarm)

        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise AlarmError(
                f"获取警报列表失败 | Failed to get alarms list: {str(e)}"
            )

    def ack_alarm(self, alarm_id: str) -> bool:
        """
        确认警报 | Acknowledge alarm
        
        Args:
            alarm_id: 警报 ID | Alarm ID
            
        Returns:
            bool: 确认是否成功 | Whether acknowledgment was successful
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
            AlarmError: 警报确认失败时抛出 | Raised when alarm acknowledgment fails
        """
        if not alarm_id or not alarm_id.strip():
            raise ValidationError(
                field_name="alarm_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=alarm_id,
                message="警报 ID 不能为空 | Alarm ID cannot be empty"
            )

        try:
            response = self.client.post(f"/api/alarm/{alarm_id}/ack")
            return response.status_code == 200

        except Exception as e:
            raise AlarmError(
                f"确认警报失败 | Failed to acknowledge alarm: {str(e)}",
                alarm_id=alarm_id
            )

    def clear_alarm(self, alarm_id: str) -> bool:
        """
        清除警报 | Clear alarm
        
        Args:
            alarm_id: 警报 ID | Alarm ID
            
        Returns:
            bool: 清除是否成功 | Whether clearing was successful
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
            AlarmError: 警报清除失败时抛出 | Raised when alarm clearing fails
        """
        if not alarm_id or not alarm_id.strip():
            raise ValidationError(
                field_name="alarm_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=alarm_id,
                message="警报 ID 不能为空 | Alarm ID cannot be empty"
            )

        try:
            response = self.client.post(f"/api/alarm/{alarm_id}/clear")
            return response.status_code == 200

        except Exception as e:
            raise AlarmError(
                f"清除警报失败 | Failed to clear alarm: {str(e)}",
                alarm_id=alarm_id
            )

    def delete_alarm(self, alarm_id: str) -> bool:
        """
        删除警报 | Delete alarm
        
        Args:
            alarm_id: 警报 ID | Alarm ID
            
        Returns:
            bool: 删除是否成功 | Whether deletion was successful
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
            AlarmError: 警报删除失败时抛出 | Raised when alarm deletion fails
        """
        if not alarm_id or not alarm_id.strip():
            raise ValidationError(
                field_name="alarm_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=alarm_id,
                message="警报 ID 不能为空 | Alarm ID cannot be empty"
            )

        try:
            response = self.client.delete(f"/api/alarm/{alarm_id}")
            return response.status_code == 200

        except Exception as e:
            raise AlarmError(
                f"删除警报失败 | Failed to delete alarm: {str(e)}",
                alarm_id=alarm_id
            )

    def get_alarm_types(self) -> List[str]:
        """
        获取所有警报类型 | Get all alarm types
        
        Returns:
            List[str]: 警报类型列表 | List of alarm types
            
        Raises:
            AlarmError: 获取警报类型失败时抛出 | Raised when getting alarm types fails
        """
        try:
            response = self.client.get("/api/alarm/types")
            types_data = response.json()
            return types_data if isinstance(types_data, list) else []

        except Exception as e:
            raise AlarmError(
                f"获取警报类型失败 | Failed to get alarm types: {str(e)}"
            )

    def get_highest_alarm_severity(self,
                                   originator_id: str,
                                   alarm_types: Optional[List[str]] = None) -> Optional[AlarmSeverity]:
        """
        获取最高警报严重程度 | Get highest alarm severity
        
        Args:
            originator_id: 发起者 ID | Originator ID
            alarm_types: 警报类型过滤列表 | Alarm types filter list
            
        Returns:
            Optional[AlarmSeverity]: 最高严重程度，无警报时返回 None | Highest severity, None if no alarms
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
        """
        if not originator_id or not originator_id.strip():
            raise ValidationError(
                field_name="originator_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=originator_id,
                message="发起者 ID 不能为空 | Originator ID cannot be empty"
            )

        try:
            endpoint = f"/api/alarm/highestSeverity/DEVICE/{originator_id}"

            params = {}
            if alarm_types:
                params["alarmTypes"] = ",".join(alarm_types)

            response = self.client.get(endpoint, params=params)
            severity_data = response.json()

            if severity_data and "severity" in severity_data:
                return AlarmSeverity(severity_data["severity"])

            return None

        except Exception as e:
            raise AlarmError(
                f"获取最高警报严重程度失败 | Failed to get highest alarm severity: {str(e)}"
            )

    def alarm_exists(self, alarm_id: str) -> bool:
        """
        检查警报是否存在 | Check if alarm exists
        
        Args:
            alarm_id: 警报 ID | Alarm ID
            
        Returns:
            bool: 警报是否存在 | Whether alarm exists
        """
        try:
            self.get_alarm(alarm_id)
            return True
        except NotFoundError:
            return False
        except Exception:
            return False

    def get_active_alarms(self,
                          originator_id: str,
                          page_size: int = 10,
                          page: int = 0) -> PageData:
        """
        获取活跃警报列表 | Get active alarms list
        
        Args:
            originator_id: 发起者 ID | Originator ID
            page_size: 页面大小 | Page size
            page: 页码 | Page number
            
        Returns:
            PageData: 活跃警报分页数据 | Active alarms paginated data
        """
        return self.get_alarms(
            originator_id=originator_id,
            page_size=page_size,
            page=page,
            status_list=[AlarmStatus.ACTIVE_UNACK, AlarmStatus.ACTIVE_ACK]
        )

    def get_cleared_alarms(self,
                           originator_id: str,
                           page_size: int = 10,
                           page: int = 0) -> PageData:
        """
        获取已清除警报列表 | Get cleared alarms list
        
        Args:
            originator_id: 发起者 ID | Originator ID
            page_size: 页面大小 | Page size
            page: 页码 | Page number
            
        Returns:
            PageData: 已清除警报分页数据 | Cleared alarms paginated data
        """
        return self.get_alarms(
            originator_id=originator_id,
            page_size=page_size,
            page=page,
            status_list=[AlarmStatus.CLEARED_UNACK, AlarmStatus.CLEARED_ACK]
        )
