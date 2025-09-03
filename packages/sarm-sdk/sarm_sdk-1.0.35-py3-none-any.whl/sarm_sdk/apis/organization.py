#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 组织架构 API

提供组织架构相关的API操作，包括创建、查询、更新、删除等功能。
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from ..models.organization import OrganizeInsert, Organization, OrganizationTree, OrganizeUser
from ..models.response import BatchOperationResult
from ..exceptions import SARMValidationError

if TYPE_CHECKING:
    from ..client import SARMClient


class OrganizationAPI:
    """组织架构API类"""
    
    def __init__(self, client: 'SARMClient'):
        self.client = client
    
    def _validate_organization_data(self, organization: Dict[str, Any], record_index: int = 1) -> None:
        """
        验证组织数据的格式和内容
        
        Args:
            organization: 组织数据字典
            record_index: 记录索引，用于错误提示
            
        Raises:
            SARMValidationError: 当数据验证失败时抛出
        """
        import re
        
        # 验证必填字段
        if 'organize_name' not in organization:
            raise SARMValidationError(f"第{record_index}条记录缺少必填字段 organize_name")
        if 'organize_unique_id' not in organization:
            raise SARMValidationError(f"第{record_index}条记录缺少必填字段 organize_name")
        if 'organize_punique_id' not in organization:
            raise SARMValidationError(f"第{record_index}条记录缺少必填字段 organize_name")


        # 验证数据类型
        if 'organize_unique_id' in organization and not isinstance(organization['organize_unique_id'], str):
            raise SARMValidationError(f"第{record_index}条记录的 organize_unique_id 必须是字符串类型")
        
        if not isinstance(organization['organize_name'], str):
            raise SARMValidationError(f"第{record_index}条记录的 organize_name 必须是字符串类型")
        
        if 'organize_punique_id' in organization and not isinstance(organization['organize_punique_id'], str):
            raise SARMValidationError(f"第{record_index}条记录的 organize_punique_id 必须是字符串类型")
        
        if 'organize_leader_unique_id' in organization and not isinstance(organization['organize_leader_unique_id'], str):
            raise SARMValidationError(f"第{record_index}条记录的 organize_leader_unique_id 必须是字符串类型")
        
        if 'desc' in organization and not isinstance(organization['desc'], str):
            raise SARMValidationError(f"第{record_index}条记录的 desc 必须是字符串类型")
        
        if 'dep_id' in organization and not isinstance(organization['dep_id'], str):
            raise SARMValidationError(f"第{record_index}条记录的 dep_id 必须是字符串类型")
        
        # 验证字段值
        if organization['organize_name'].strip() == '':
            raise SARMValidationError(f"第{record_index}条记录的 organize_name 不能为空字符串")
        if organization['organize_unique_id'].strip() == '':
            raise SARMValidationError(f"第{record_index}条记录的 organize_unique_id 不能为空字符串")

    def create_batch(
        self,
        organizations: List[Dict[str, Any]],
        execute_release: bool = False
    ):
        """
        批量创建组织
        
        Args:
            organizations: 组织数据列表，每个元素为字典格式
            execute_release: 是否直接发布，默认False进入预处理状态
            
        Returns:
            批量操作结果
            
        Raises:
            SARMValidationError: 数据验证失败
            SARMAPIError: API调用失败
        """
        if not organizations:
            raise SARMValidationError("组织列表不能为空")
        
        if len(organizations) > 1000:
            raise SARMValidationError("单次批量操作不能超过1000条记录")
        
        # 验证数据
        org_data = []
        for i, org in enumerate(organizations):
            if isinstance(org, dict):
                self._validate_organization_data(org, i + 1)
                org_data.append(org)
            else:
                raise SARMValidationError(f"第{i+1}条组织数据必须是字典类型")
        
        # 发送请求
        response = self.client.post(
            '/api/organize/openapi/create',
            data=org_data,
            execute_release=execute_release
        )
        
        # 处理简单的成功响应
        if isinstance(response, dict) and 'code' in response:
            success = response.get('code') == 200
            # 创建批量操作结果
            from ..models.response import BatchOperationItem
            items = []
            for i, org in enumerate(organizations):
                # 正确获取组织信息
                unique_id = org.get('organize_unique_id', f"org_{i}")
                name = org.get('organize_name', '')
                
                items.append(BatchOperationItem(
                    unique_id=unique_id,
                    name=name,
                    success=success,
                    msg="创建成功" if success else "创建失败"
                ))
            
            return BatchOperationResult(
                data=items,
                code=response.get('code', 200)
            )
        
        return BatchOperationResult(**response)
    
    def create(self, organization: Dict[str, Any], execute_release: bool = False):
        """
        创建单个组织
        
        Args:
            organization: 组织数据，字典格式
            execute_release: 是否直接发布
            
        Returns:
            批量操作结果
        """
        if not isinstance(organization, dict):
            raise SARMValidationError("组织数据必须是字典类型")
        
        return self.create_batch([organization], execute_release=execute_release)
    
    def update_batch(
        self,
        organizations: List[Dict[str, Any]],
        execute_release: bool = False
    ):
        """
        批量更新组织
        
        Args:
            organizations: 组织数据列表，每个元素为字典格式
            execute_release: 是否直接发布
            
        Returns:
            批量操作结果
        """
        if not organizations:
            raise SARMValidationError("组织列表不能为空")
        
        # 验证数据
        org_data = []
        for i, org in enumerate(organizations):
            if isinstance(org, dict):
                self._validate_organization_data(org, i + 1)
                org_data.append(org)
            else:
                raise SARMValidationError(f"第{i+1}条组织数据必须是字典类型")
        
        # 发送请求
        response = self.client.post(
            '/api/organize/openapi/update',
            data=org_data,
            execute_release=execute_release
        )
        
        # 处理简单的成功响应
        if isinstance(response, dict) and 'code' in response:
            success = response.get('code') == 200
            # 创建批量操作结果
            from ..models.response import BatchOperationItem
            items = []
            for i, org in enumerate(organizations):
                # 正确获取组织信息
                unique_id = org.get('organize_unique_id', f"org_{i}")
                name = org.get('organize_name', '')
                
                items.append(BatchOperationItem(
                    unique_id=unique_id,
                    name=name,
                    success=success,
                    msg="更新成功" if success else "更新失败"
                ))
            
            return BatchOperationResult(
                data=items,
                code=response.get('code', 200)
            )
        
        return BatchOperationResult(**response)
    
    def update(self, organization: Dict[str, Any], execute_release: bool = False):
        """
        更新单个组织
        
        Args:
            organization: 组织数据，字典格式
            execute_release: 是否直接发布
            
        Returns:
            批量操作结果
        """
        if not isinstance(organization, dict):
            raise SARMValidationError("组织数据必须是字典类型")
        
        return self.update_batch([organization], execute_release=execute_release)
    
    def delete_batch(self, unique_ids: List[str]) -> Dict[str, Any]:
        """
        批量删除组织
        
        Args:
            unique_ids: 组织唯一ID列表
            
        Returns:
            删除结果
            
        Note:
            当层及下级存在关联数据时不允许删除
        """
        if not unique_ids:
            raise SARMValidationError("组织ID列表不能为空")
        
        if not isinstance(unique_ids, list):
            raise SARMValidationError("组织ID列表必须是列表类型")
        
        # 验证每个ID都是字符串类型
        for i, unique_id in enumerate(unique_ids):
            if not isinstance(unique_id, str):
                raise SARMValidationError(f"第{i+1}个组织ID必须是字符串类型")
            if unique_id.strip() == '':
                raise SARMValidationError(f"第{i+1}个组织ID不能为空字符串")
        
        response = self.client.post(
            '/api/organize/openapi/delete',
            data = unique_ids
        )
        
        return response
    
    def delete(self, unique_id: str) -> Dict[str, Any]:
        """
        删除单个组织
        
        Args:
            unique_id: 组织唯一ID
            
        Returns:
            删除结果
        """
        if not isinstance(unique_id, str):
            raise SARMValidationError("组织ID必须是字符串类型")
        
        if unique_id.strip() == '':
            raise SARMValidationError("组织ID不能为空字符串")
        
        return self.delete_batch([unique_id])
    
    def get(
        self,
        organize_unique_id: Optional[str] = None,
        organize_name: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        查询组织列表
        
        Args:
            organize_unique_id: 组织唯一ID（精确匹配）
            organize_name: 组织名称（模糊匹配）
            page: 页码
            limit: 每页数量
            
        Returns:
            组织列表和分页信息
        """
        # 验证参数
        if not isinstance(page, int) or page < 1:
            raise SARMValidationError("页码必须是大于0的整数")
        
        if not isinstance(limit, int) or limit < 1 or limit > 1000:
            raise SARMValidationError("每页条数必须是1-1000之间的整数")
        
        if organize_unique_id is not None and not isinstance(organize_unique_id, str):
            raise SARMValidationError("组织唯一ID必须是字符串类型")
        
        if organize_name is not None and not isinstance(organize_name, str):
            raise SARMValidationError("组织名称必须是字符串类型")
        
        query_data = {
            "page": page,
            "limit": limit
        }
        
        if organize_unique_id:
            query_data["organize_unique_id"] = organize_unique_id
        if organize_name:
            query_data["organize_name"] = organize_name
        
        response = self.client.post('/api/organize/openapi/get', data=query_data)
        return response
    
    def refresh_cache(self) -> Dict[str, Any]:
        """
        刷新组织架构树缓存
        
        这是一个异步操作，用于在批量导入组织数据后刷新组织架构树缓存，
        确保组织层级关系的数据一致性。
        
        Returns:
            操作结果
            
        Note:
            - 这是异步操作，调用成功仅表示任务已提交
            - 建议在批量导入组织后调用此方法
            - 大量组织数据的缓存刷新可能需要一定时间
        """
        response = self.client.get('/api/organize/async_refresh_organize_tree_cache')
        return response
    
    def get_tree(self) :
        """
        获取组织架构树
        
        Returns:
            组织架构树列表
            
        Note:
            如果组织架构缓存未更新，建议先调用 refresh_cache() 方法
        """
        # 获取所有组织
        all_orgs = []
        page = 1
        limit = 100
        
        while True:
            response = self.get(page=page, limit=limit)
            data_list = response.get('data', {}).get('data_list', [])
            
            if not data_list:
                break
                
            all_orgs.extend(data_list)
            
            # 检查是否还有更多数据
            total = response.get('data', {}).get('total', 0)
            if len(all_orgs) >= total:
                break
                
            page += 1
        
        # 构建组织树
        return self._build_organization_tree(all_orgs)
    
    def _build_organization_tree(self, organizations: List[Dict[str, Any]]):
        """
        构建组织架构树
        
        Args:
            organizations: 组织数据列表
            
        Returns:
            组织架构树列表
        """
        # 创建组织字典，便于查找
        org_dict = {org['organize_uuid']: org for org in organizations}
        
        # 查找根节点（父ID为'0'或None的组织）
        roots = []
        
        for org in organizations:
            parent_id = org.get('organize_puuid')
            if parent_id == '0' or parent_id is None:
                tree_node = OrganizationTree(
                    organize_unique_id=org['organize_uuid'],
                    organize_name=org['organize_name'],
                    level=0,
                    children=[]
                )
                self._build_children(tree_node, org_dict, 1)
                roots.append(tree_node)
        
        return roots
    
    def _build_children(
        self,
        parent_node: OrganizationTree,
        org_dict: Dict[str, Dict[str, Any]],
        level: int
    ):
        """
        递归构建子组织节点
        
        Args:
            parent_node: 父节点
            org_dict: 组织字典
            level: 当前层级
        """
        parent_id = parent_node.organize_unique_id
        
        for org_id, org in org_dict.items():
            if org.get('organize_puuid') == parent_id:
                child_node = OrganizationTree(
                    organize_unique_id=org['organize_uuid'],
                    organize_name=org['organize_name'],
                    level=level,
                    children=[]
                )
                self._build_children(child_node, org_dict, level + 1)
                parent_node.children.append(child_node)
    
    # 用户管理相关方法
    def create_users(
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
            创建结果
        """
        if not users:
            raise SARMValidationError("用户列表不能为空")
        
        if not isinstance(organize_unique_id, str):
            raise SARMValidationError("组织唯一ID必须是字符串类型")
        
        if organize_unique_id.strip() == '':
            raise SARMValidationError("组织唯一ID不能为空字符串")
        
        if not isinstance(users, list):
            raise SARMValidationError("用户列表必须是列表类型")
        
        user_data = []
        for i, user in enumerate(users):
            if isinstance(user, OrganizeUser):
                user_data.append(user.dict())
            else:
                if not isinstance(user, dict):
                    raise SARMValidationError(f"第{i+1}个用户数据必须是字典类型")
                user_data.append(user)
        
        request_data = {
            "organize_unique_id": organize_unique_id,
            "user_list": user_data
        }
        
        response = self.client.post('/api/organize_user/create', data=request_data)
        return response
    
    def update_users(self, users: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量更新组织用户
        
        Args:
            users: 用户数据列表
            
        Returns:
            更新结果
        """
        if not users:
            raise SARMValidationError("用户列表不能为空")
        
        if not isinstance(users, list):
            raise SARMValidationError("用户列表必须是列表类型")
        
        user_data = []
        for i, user in enumerate(users):
            if not isinstance(user, dict):
                raise SARMValidationError(f"第{i+1}个用户数据必须是字典类型")
            user_data.append(user)
        
        response = self.client.post('/api/organize_user/update', data=user_data)
        return response
    
    def delete_users(self, user_unique_ids: List[str]) -> Dict[str, Any]:
        """
        批量删除组织用户
        
        Args:
            user_unique_ids: 用户唯一ID列表
            
        Returns:
            删除结果
        """
        if not user_unique_ids:
            raise SARMValidationError("用户ID列表不能为空")
        
        response = self.client.post('/api/organize_user/delete', data=user_unique_ids)
        return response

    def delete_parent_id(self, organize_id: List[str]) -> Dict[str, Any]:
        """
        删除组织的父级ID关联

        Args:
            organize_id: 组织ID

        Returns:
            操作结果
        """
        if not organize_id:
            raise SARMValidationError("组织ID列表不能为空")
        
        if not isinstance(organize_id, list):
            raise SARMValidationError("组织ID列表必须是列表类型")
        
        # 验证每个ID都是字符串类型
        for i, org_id in enumerate(organize_id):
            if not isinstance(org_id, str):
                raise SARMValidationError(f"第{i+1}个组织ID必须是字符串类型")
            if org_id.strip() == '':
                raise SARMValidationError(f"第{i+1}个组织ID不能为空字符串")
        
        response = self.client.post('/api/organize/openapi/delete_pid', data=organize_id)
        return response

    def delete_leader(self, organize_id: List[str]) -> Dict[str, Any]:
        """
        删除组织的负责人关联

        Args:
            organize_id: 组织ID

        Returns:
            操作结果
        """
        if not organize_id:
            raise SARMValidationError("组织ID列表不能为空")
        
        if not isinstance(organize_id, list):
            raise SARMValidationError("组织ID列表必须是列表类型")
        
        # 验证每个ID都是字符串类型
        for i, org_id in enumerate(organize_id):
            if not isinstance(org_id, str):
                raise SARMValidationError(f"第{i+1}个组织ID必须是字符串类型")
            if org_id.strip() == '':
                raise SARMValidationError(f"第{i+1}个组织ID不能为空字符串")
        
        response = self.client.post('/api/organize/openapi/delete_leader', data=organize_id)
        return response
    
    def get_users(
        self,
        organize_unique_id: str,
        user_unique_id: Optional[str] = None,
        user_name: Optional[str] = None,
        enterprise_email: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        查询组织用户列表
        
        Args:
            organize_union_id: 组织唯一ID
            user_unique_id: 用户唯一ID
            user_name: 用户名
            enterprise_email: 企业邮箱
            page: 页码
            limit: 每页数量
            
        Returns:
            用户列表和分页信息
        """
        # 验证参数
        if not isinstance(organize_unique_id, str):
            raise SARMValidationError("组织唯一ID必须是字符串类型")
        
        if organize_unique_id.strip() == '':
            raise SARMValidationError("组织唯一ID不能为空字符串")
        
        if not isinstance(page, int) or page < 1:
            raise SARMValidationError("页码必须是大于0的整数")
        
        if not isinstance(limit, int) or limit < 1 or limit > 1000:
            raise SARMValidationError("每页条数必须是1-1000之间的整数")
        
        if user_unique_id is not None and not isinstance(user_unique_id, str):
            raise SARMValidationError("用户唯一ID必须是字符串类型")
        
        if user_name is not None and not isinstance(user_name, str):
            raise SARMValidationError("用户名称必须是字符串类型")
        
        if enterprise_email is not None and not isinstance(enterprise_email, str):
            raise SARMValidationError("企业邮箱必须是字符串类型")
        
        user_info = {}
        if user_unique_id:
            user_info["organize_user_unique_id"] = user_unique_id
        if user_name:
            user_info["organize_user_name"] = user_name
        if enterprise_email:
            user_info["organize_user_enterprise_email"] = enterprise_email
        
        query_data = {
            "organize_unique_id": organize_unique_id,
            "user_info": user_info,
            "page": page,
            "limit": limit
        }
        
        response = self.client.post('/api/organize_user/list', data=query_data)
        return response
