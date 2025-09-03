#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 安全问题 API

提供安全问题相关的API操作。
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from ..models.response import BatchOperationResult
from ..exceptions import SARMValidationError

if TYPE_CHECKING:
    from ..client import SARMClient


class SecurityIssueAPI:
    """
    安全问题API类
    
    注意：安全问题创建应通过 CarrierDataImportAPI 的载体维度多数据录入接口实现，
    本API提供查询、更新和关联管理功能。
    """
    
    def __init__(self, client: 'SARMClient'):
        self.client = client
    
    def update(self, issue_data: Dict[str, Any], execute_release: bool = False) -> Dict[str, Any]:
        """
        更新安全问题信息
        
        Args:
            issue_data: 安全问题数据，必须包含 issue_unique_id
            execute_release: 是否直接发布
            
        Returns:
            更新结果
            
        Raises:
            SARMValidationError: 当缺少必要字段时抛出
        """
        if 'issue_unique_id' not in issue_data:
            raise SARMValidationError("更新安全问题时必须提供 issue_unique_id")
        
        response = self.client.post(
            '/api/issue/update', 
            data=issue_data,
            execute_release=execute_release
        )
        return response
    
    def get_list(
        self,
        page: int = 1,
        limit: int = 50,
        status: Optional[str] = None,
        level: Optional[str] = None,
        title:Optional[str] = None,
        uniqueId :Optional[str] = None,
        discovery_at_start: Optional[str] = None,
        discovery_at_end: Optional[str] = None,
        **filters
    ) -> Dict[str, Any]:
        """
        获取安全问题列表
        
        Args:
            page: 页码
            limit: 每页条数
            status: 问题状态
            level: 问题级别
            **filters: 其他过滤条件
            
        Returns:
            安全问题列表
        """
        data = {
            "page": page,
            "limit": limit,
            **filters
        }
        if status:
            data["issue_status"] = status
        if level:
            data["issue_level"] = level
        if title:
            data["issue_title"]=title
        if uniqueId:
            data["issue_unique_id"]=uniqueId
        if discovery_at_start:
            data["discovery_at_start"]=discovery_at_start
        if discovery_at_end:
            data["discovery_at_end"]=discovery_at_end
        response = self.client.post('/api/issue/', data=data)
        return response
    
    def get_component_vuln_list(self, issue_unique_id: str) -> Dict[str, Any]:
        """
        获取安全问题关联的成分和漏洞列表
        
        Args:
            issue_unique_id: 安全问题唯一ID
            
        Returns:
            关联的成分和漏洞列表
        """
        response = self.client.get(f'/api/issue/component_vuln_list/{issue_unique_id}')
        return response
    
    def update_component_vuln_list(
        self, 
        issue_unique_id: str, 
        component_ids: List[str], 
        vuln_ids: List[str]
    ) -> Dict[str, Any]:
        """
        更新安全问题关联的成分和漏洞列表
        
        Args:
            issue_unique_id: 安全问题唯一ID
            component_ids: 成分唯一ID列表
            vuln_ids: 漏洞唯一ID列表
            
        Returns:
            操作结果
        """
        data = {
            "component_unique_id": component_ids,
            "vuln_unique_id": vuln_ids
        }
        response = self.client.post(
            f'/api/issue/update_component_vuln_list/{issue_unique_id}',
            data=data
        )
        return response
    
    def update_vuln_list(
        self, 
        issue_unique_id: str, 
        component_unique_id: List[str]
    ) -> Dict[str, Any]:
        """
        更新安全问题关联的成分列表
        
        Args:
            issue_unique_id: 安全问题唯一ID
            component_unique_id: 成分唯一ID列表
            
        Returns:
            操作结果
        """
        data = {"component_unique_id": component_unique_id}
        response = self.client.post(
            f'/api/issue/update_component_list/{issue_unique_id}',
            data=data
        )
        return response 