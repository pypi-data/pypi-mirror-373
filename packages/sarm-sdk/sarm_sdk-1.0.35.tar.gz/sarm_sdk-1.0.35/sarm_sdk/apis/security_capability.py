#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 安全能力 API

提供安全能力相关的API操作。
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from ..models.security_capability import SecurityCapability
from ..exceptions import SARMValidationError

if TYPE_CHECKING:
    from ..client import SARMClient


class SecurityCapabilityAPI:
    """安全能力API类"""
    
    def __init__(self, client: 'SARMClient'):
        self.client = client


    def create_batch(
        self,
        capabilities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        批量创建安全能力
        
        Args:
            capabilities: List[Dict[str, Any]] - 安全能力数据列表
            
        Returns:
            操作结果
        """
        if not capabilities:
            raise SARMValidationError("安全能力列表不能为空")
        
        # 验证数据
        capability_data = []
        for capability in capabilities:
            if isinstance(capability, SecurityCapability):
                capability_data.append(capability.dict())
            else:
                capability_data.append(capability)
        
        # 发送请求
        response = self.client.post('/api/security_capability/add_list', data=capability_data)
        return response
    
    def create(self, capability: Dict[str, Any]) -> Dict[str, Any]:
        """创建单个安全能力"""
        return self.create_batch([capability])
    
    def get_list(
        self,
        capability_type: Optional[str] = None,
        capability_name: Optional[str] = None,
        capability_unique_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取安全能力列表"""
        params: Dict[str, Any] = {}
        if capability_type:
            params["capability_type"] = capability_type
        if capability_name:
            params["capability_name"] = capability_name
        if capability_unique_id:
            params["capability_unique_id"] = capability_unique_id
        
        response = self.client.get('/api/security_capability/', params=params)
        return response
    
    def update_batch(self, capabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批量更新安全能力"""
        if not capabilities:
            raise SARMValidationError("安全能力列表不能为空")
        
        response = self.client.post('/api/security_capability/update_list', data=capabilities)
        return response
    

    
    def delete(self, capability_id: List[str]) -> Dict[str, Any]:
        """删除安全能力"""
        response = self.client.delete('/api/security_capability/', data=capability_id)
        return response