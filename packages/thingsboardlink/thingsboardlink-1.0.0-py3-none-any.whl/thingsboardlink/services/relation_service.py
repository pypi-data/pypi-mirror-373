"""
ThingsBoardLink 关系服务模块 | ThingsBoardLink Relation Service Module

本模块提供实体关系管理相关的 API 调用功能。
包括实体间关系的创建、删除、查询等操作。

This module provides API call functionality related to entity relationship management.
Includes creation, deletion, querying operations for relationships between entities.
"""

from typing import List, Optional, Dict, Any
from urllib.parse import urljoin

from ..models import EntityRelation, EntityId, EntityType
from ..exceptions import ValidationError, NotFoundError, APIError


class RelationService:
    """
    关系服务类 | Relation Service Class
    
    提供实体关系管理相关的所有操作。
    支持实体间关系的完整生命周期管理。
    
    Provides all operations related to entity relationship management.
    Supports complete lifecycle management of relationships between entities.
    """

    def __init__(self, client):
        """
        初始化关系服务 | Initialize relation service
        
        Args:
            client: ThingsBoardClient 实例 | ThingsBoardClient instance
        """
        self.client = client

    def create_relation(self,
                        from_id: str,
                        from_type: EntityType,
                        to_id: str,
                        to_type: EntityType,
                        relation_type: str,
                        type_group: str = "COMMON",
                        additional_info: Optional[Dict[str, Any]] = None) -> EntityRelation:
        """
        创建实体关系 | Create entity relation
        
        Args:
            from_id: 源实体 ID | Source entity ID
            from_type: 源实体类型 | Source entity type
            to_id: 目标实体 ID | Target entity ID
            to_type: 目标实体类型 | Target entity type
            relation_type: 关系类型 | Relation type
            type_group: 类型组 | Type group
            additional_info: 附加信息 | Additional information
            
        Returns:
            EntityRelation: 创建的关系对象 | Created relation object
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
            APIError: 关系创建失败时抛出 | Raised when relation creation fails
        """
        if not from_id or not from_id.strip():
            raise ValidationError(
                field_name="from_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=from_id,
                message="源实体 ID 不能为空 | Source entity ID cannot be empty"
            )

        if not to_id or not to_id.strip():
            raise ValidationError(
                field_name="to_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=to_id,
                message="目标实体 ID 不能为空 | Target entity ID cannot be empty"
            )

        if not relation_type or not relation_type.strip():
            raise ValidationError(
                field_name="relation_type",
                expected_type="非空字符串 | Non-empty string",
                actual_value=relation_type,
                message="关系类型不能为空 | Relation type cannot be empty"
            )

        relation = EntityRelation(
            from_id=EntityId(id=from_id.strip(), entity_type=from_type),
            to_id=EntityId(id=to_id.strip(), entity_type=to_type),
            type=relation_type.strip(),
            type_group=type_group,
            additional_info=additional_info or {}
        )

        try:
            response = self.client.post(
                "/api/relation",
                data=relation.to_dict()
            )

            if response.status_code == 200:
                return relation
            else:
                raise APIError(
                    f"创建实体关系失败，状态码: {response.status_code} | Failed to create entity relation, status code: {response.status_code}",
                    status_code=response.status_code
                )

        except Exception as e:
            if isinstance(e, (ValidationError, APIError)):
                raise
            raise APIError(
                f"创建实体关系失败 | Failed to create entity relation: {str(e)}"
            )

    def delete_relation(self,
                        from_id: str,
                        from_type: EntityType,
                        to_id: str,
                        to_type: EntityType,
                        relation_type: str,
                        type_group: str = "COMMON") -> bool:
        """
        删除实体关系 | Delete entity relation
        
        Args:
            from_id: 源实体 ID | Source entity ID
            from_type: 源实体类型 | Source entity type
            to_id: 目标实体 ID | Target entity ID
            to_type: 目标实体类型 | Target entity type
            relation_type: 关系类型 | Relation type
            type_group: 类型组 | Type group
            
        Returns:
            bool: 删除是否成功 | Whether deletion was successful
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
            APIError: 关系删除失败时抛出 | Raised when relation deletion fails
        """
        if not from_id or not from_id.strip():
            raise ValidationError(
                field_name="from_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=from_id,
                message="源实体 ID 不能为空 | Source entity ID cannot be empty"
            )

        if not to_id or not to_id.strip():
            raise ValidationError(
                field_name="to_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=to_id,
                message="目标实体 ID 不能为空 | Target entity ID cannot be empty"
            )

        if not relation_type or not relation_type.strip():
            raise ValidationError(
                field_name="relation_type",
                expected_type="非空字符串 | Non-empty string",
                actual_value=relation_type,
                message="关系类型不能为空 | Relation type cannot be empty"
            )

        try:
            params = {
                "fromId": from_id.strip(),
                "fromType": from_type.value,
                "toId": to_id.strip(),
                "toType": to_type.value,
                "relationType": relation_type.strip(),
                "relationTypeGroup": type_group
            }

            response = self.client.delete("/api/relation", params=params)
            return response.status_code == 200

        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise APIError(
                f"删除实体关系失败 | Failed to delete entity relation: {str(e)}"
            )

    def get_relation(self,
                     from_id: str,
                     from_type: EntityType,
                     to_id: str,
                     to_type: EntityType,
                     relation_type: str,
                     type_group: str = "COMMON") -> Optional[EntityRelation]:
        """
        获取实体关系 | Get entity relation
        
        Args:
            from_id: 源实体 ID | Source entity ID
            from_type: 源实体类型 | Source entity type
            to_id: 目标实体 ID | Target entity ID
            to_type: 目标实体类型 | Target entity type
            relation_type: 关系类型 | Relation type
            type_group: 类型组 | Type group
            
        Returns:
            Optional[EntityRelation]: 关系对象，不存在时返回 None | Relation object, None if not exists
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
        """
        if not from_id or not from_id.strip():
            raise ValidationError(
                field_name="from_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=from_id,
                message="源实体 ID 不能为空 | Source entity ID cannot be empty"
            )

        if not to_id or not to_id.strip():
            raise ValidationError(
                field_name="to_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=to_id,
                message="目标实体 ID 不能为空 | Target entity ID cannot be empty"
            )

        if not relation_type or not relation_type.strip():
            raise ValidationError(
                field_name="relation_type",
                expected_type="非空字符串 | Non-empty string",
                actual_value=relation_type,
                message="关系类型不能为空 | Relation type cannot be empty"
            )

        try:
            params = {
                "fromId": from_id.strip(),
                "fromType": from_type.value,
                "toId": to_id.strip(),
                "toType": to_type.value,
                "relationType": relation_type.strip(),
                "relationTypeGroup": type_group
            }

            response = self.client.get("/api/relation", params=params)

            if response.status_code == 200:
                relation_data = response.json()
                return EntityRelation.from_dict(relation_data)
            elif response.status_code == 404:
                return None
            else:
                raise APIError(
                    f"获取实体关系失败，状态码: {response.status_code} | Failed to get entity relation, status code: {response.status_code}",
                    status_code=response.status_code
                )

        except Exception as e:
            if isinstance(e, (ValidationError, APIError)):
                raise
            raise APIError(
                f"获取实体关系失败 | Failed to get entity relation: {str(e)}"
            )

    def find_by_from(self,
                     from_id: str,
                     from_type: EntityType,
                     relation_type_group: str = "COMMON") -> List[EntityRelation]:
        """
        查找从指定实体出发的所有关系 | Find all relations from specified entity
        
        Args:
            from_id: 源实体 ID | Source entity ID
            from_type: 源实体类型 | Source entity type
            relation_type_group: 关系类型组 | Relation type group
            
        Returns:
            List[EntityRelation]: 关系列表 | List of relations
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
        """
        if not from_id or not from_id.strip():
            raise ValidationError(
                field_name="from_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=from_id,
                message="源实体 ID 不能为空 | Source entity ID cannot be empty"
            )

        try:
            params = {
                "fromId": from_id.strip(),
                "fromType": from_type.value,
                "relationTypeGroup": relation_type_group
            }

            response = self.client.get("/api/relations", params=params)
            relations_data = response.json()

            return [EntityRelation.from_dict(rel) for rel in relations_data]

        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise APIError(
                f"查找实体关系失败 | Failed to find entity relations: {str(e)}"
            )

    def find_by_to(self,
                   to_id: str,
                   to_type: EntityType,
                   relation_type_group: str = "COMMON") -> List[EntityRelation]:
        """
        查找指向指定实体的所有关系 | Find all relations to specified entity
        
        Args:
            to_id: 目标实体 ID | Target entity ID
            to_type: 目标实体类型 | Target entity type
            relation_type_group: 关系类型组 | Relation type group
            
        Returns:
            List[EntityRelation]: 关系列表 | List of relations
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
        """
        if not to_id or not to_id.strip():
            raise ValidationError(
                field_name="to_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=to_id,
                message="目标实体 ID 不能为空 | Target entity ID cannot be empty"
            )

        try:
            params = {
                "toId": to_id.strip(),
                "toType": to_type.value,
                "relationTypeGroup": relation_type_group
            }

            response = self.client.get("/api/relations", params=params)
            relations_data = response.json()

            return [EntityRelation.from_dict(rel) for rel in relations_data]

        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise APIError(
                f"查找实体关系失败 | Failed to find entity relations: {str(e)}"
            )

    def find_by_query(self,
                      entity_id: str,
                      entity_type: EntityType,
                      direction: str = "FROM",
                      max_level: int = 1,
                      fetch_last_level_only: bool = False,
                      relation_type_group: str = "COMMON") -> List[EntityId]:
        """
        通过查询条件查找相关实体 | Find related entities by query conditions
        
        Args:
            entity_id: 实体 ID | Entity ID
            entity_type: 实体类型 | Entity type
            direction: 查询方向（FROM/TO） | Query direction (FROM/TO)
            max_level: 最大查询层级 | Maximum query level
            fetch_last_level_only: 是否只获取最后一层 | Whether to fetch only last level
            relation_type_group: 关系类型组 | Relation type group
            
        Returns:
            List[EntityId]: 相关实体 ID 列表 | List of related entity IDs
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
        """
        if not entity_id or not entity_id.strip():
            raise ValidationError(
                field_name="entity_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=entity_id,
                message="实体 ID 不能为空 | Entity ID cannot be empty"
            )

        if direction not in ["FROM", "TO"]:
            raise ValidationError(
                field_name="direction",
                expected_type="FROM 或 TO | FROM or TO",
                actual_value=direction,
                message="查询方向必须是 FROM 或 TO | Query direction must be FROM or TO"
            )

        if max_level <= 0:
            raise ValidationError(
                field_name="max_level",
                expected_type="正整数 | Positive integer",
                actual_value=max_level,
                message="最大查询层级必须大于 0 | Maximum query level must be greater than 0"
            )

        try:
            query_data = {
                "rootId": entity_id.strip(),
                "rootType": entity_type.value,
                "direction": direction,
                "maxLevel": max_level,
                "fetchLastLevelOnly": fetch_last_level_only,
                "relationTypeGroup": relation_type_group
            }

            response = self.client.post("/api/relations/info", data=query_data)
            entities_data = response.json()

            result = []
            for entity_data in entities_data:
                if "id" in entity_data and "entityType" in entity_data:
                    result.append(EntityId.from_dict(entity_data))

            return result

        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise APIError(
                f"查询相关实体失败 | Failed to query related entities: {str(e)}"
            )

    def relation_exists(self,
                        from_id: str,
                        from_type: EntityType,
                        to_id: str,
                        to_type: EntityType,
                        relation_type: str,
                        type_group: str = "COMMON") -> bool:
        """
        检查实体关系是否存在 | Check if entity relation exists
        
        Args:
            from_id: 源实体 ID | Source entity ID
            from_type: 源实体类型 | Source entity type
            to_id: 目标实体 ID | Target entity ID
            to_type: 目标实体类型 | Target entity type
            relation_type: 关系类型 | Relation type
            type_group: 类型组 | Type group
            
        Returns:
            bool: 关系是否存在 | Whether relation exists
        """
        try:
            relation = self.get_relation(
                from_id=from_id,
                from_type=from_type,
                to_id=to_id,
                to_type=to_type,
                relation_type=relation_type,
                type_group=type_group
            )
            return relation is not None
        except Exception:
            return False

    def delete_relations(self,
                         entity_id: str,
                         entity_type: EntityType,
                         direction: str = "FROM") -> bool:
        """
        删除实体的所有关系 | Delete all relations of entity
        
        Args:
            entity_id: 实体 ID | Entity ID
            entity_type: 实体类型 | Entity type
            direction: 删除方向（FROM/TO/BOTH） | Delete direction (FROM/TO/BOTH)
            
        Returns:
            bool: 删除是否成功 | Whether deletion was successful
            
        Raises:
            ValidationError: 参数验证失败时抛出 | Raised when parameter validation fails
        """
        if not entity_id or not entity_id.strip():
            raise ValidationError(
                field_name="entity_id",
                expected_type="非空字符串 | Non-empty string",
                actual_value=entity_id,
                message="实体 ID 不能为空 | Entity ID cannot be empty"
            )

        if direction not in ["FROM", "TO", "BOTH"]:
            raise ValidationError(
                field_name="direction",
                expected_type="FROM、TO 或 BOTH | FROM, TO or BOTH",
                actual_value=direction,
                message="删除方向必须是 FROM、TO 或 BOTH | Delete direction must be FROM, TO or BOTH"
            )

        try:
            success = True

            if direction in ["FROM", "BOTH"]:
                # 删除从该实体出发的关系 | Delete relations from this entity
                relations = self.find_by_from(entity_id, entity_type)
                for relation in relations:
                    result = self.delete_relation(
                        from_id=relation.from_id.id,
                        from_type=relation.from_id.entity_type,
                        to_id=relation.to_id.id,
                        to_type=relation.to_id.entity_type,
                        relation_type=relation.type,
                        type_group=relation.type_group
                    )
                    success = success and result

            if direction in ["TO", "BOTH"]:
                # 删除指向该实体的关系 | Delete relations to this entity
                relations = self.find_by_to(entity_id, entity_type)
                for relation in relations:
                    result = self.delete_relation(
                        from_id=relation.from_id.id,
                        from_type=relation.from_id.entity_type,
                        to_id=relation.to_id.id,
                        to_type=relation.to_id.entity_type,
                        relation_type=relation.type,
                        type_group=relation.type_group
                    )
                    success = success and result

            return success

        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise APIError(
                f"删除实体关系失败 | Failed to delete entity relations: {str(e)}"
            )
