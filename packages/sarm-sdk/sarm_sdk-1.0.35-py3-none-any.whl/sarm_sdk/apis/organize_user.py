#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 组织用户 API

提供组织用户相关的API操作。
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from ..exceptions import SARMValidationError

if TYPE_CHECKING:
    from ..client import SARMClient


class OrganizeUserAPI:
    """组织用户API类"""

    def __init__(self, client: 'SARMClient'):
        self.client = client

    def create_batch(
            self,
            organize_unique_id: str,
            users: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        批量创建组织用户

        Args:
            organize_unique_id: 组织唯一ID
            users: 用户数据列表

        Returns:
            操作结果
        """
        if not users:
            raise SARMValidationError("用户列表不能为空")

        data = {
            "organize_unique_id": organize_unique_id,
            "user_list": users
        }

        response = self.client.post('/api/organize_user/create', data=data)
        return response

    def create(
            self,
            organize_unique_id: str,
            user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建单个组织用户"""
        return self.create_batch(organize_unique_id, [user_data])

    def delete_batch(self, user_ids: List[str]) -> Dict[str, Any]:
        """
        批量删除组织用户

        Args:
            user_ids: 用户唯一ID列表

        Returns:
            操作结果
        """
        if not user_ids:
            raise SARMValidationError("用户ID列表不能为空")

        response = self.client.post('/api/organize_user/delete', data=user_ids)
        return response

    def delete(self, user_id: str) -> Dict[str, Any]:
        """删除单个组织用户"""
        return self.delete_batch([user_id])

    def get_list(
            self,
            organize_unique_id: str,
            page: int = 1,
            limit: int = 10,
            user_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        获取组织用户列表

        Args:
            organize_unique_id: 组织唯一ID
            page: 页码
            limit: 每页条数
            user_info: 用户信息过滤条件

        Returns:
            用户列表
        """
        data = {
            "organize_unique_id": organize_unique_id,
            "page": page,
            "limit": limit,
            "user_info": user_info or {}
        }

        response = self.client.post('/api/organize_user/list', data=data)
        return response

    def update_batch(self, users: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量更新组织用户

        Args:
            users: 用户数据列表

        Returns:
            操作结果
        """
        if not users:
            raise SARMValidationError("用户列表不能为空")

        # 验证必填字段
        for user in users:
            if 'organize_user_unique_id' not in user:
                raise SARMValidationError("缺少 organize_user_unique_id 字段")
            if 'organize_user_name' not in user:
                raise SARMValidationError("缺少 organize_user_name 字段")
            if 'organize_user_enterprise_email' not in user:
                raise SARMValidationError("缺少 organize_user_enterprise_email 字段")
        data = users
        response = self.client.post('/api/organize_user/update', data=data)
        return response

    def update(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新单个组织用户"""
        return self.update_batch([user_data])

    def delete_organize(self, organize_user_id: List[str]):
        """删除组织用户的组织关联"""
        response = self.client.post('/api/organize_user/delete_organize', data=organize_user_id)
        return response
