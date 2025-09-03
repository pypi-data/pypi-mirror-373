#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 软件成分 API

提供软件成分相关的API操作。
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from ..exceptions import SARMValidationError

if TYPE_CHECKING:
    from ..client import SARMClient


class ComponentAPI:
    """
    软件成分API类
    
    注意：软件成分创建可以通过以下两种方式实现：
    1. CarrierDataImportAPI.import_carrier_data() 方法进行批量创建
    2. ComponentAPI.add_to_carrier() 方法添加到特定载体
    
    本API主要提供更新、查询和关联管理功能。
    """
    
    def __init__(self, client: 'SARMClient'):
        self.client = client
    
    def _validate_component_data(self, component: Dict[str, Any], record_index: int = 1) -> None:
        """
        验证软件成分数据的格式和内容
        
        Args:
            component: 软件成分数据字典
            record_index: 记录索引，用于错误提示
            
        Raises:
            SARMValidationError: 当数据验证失败时抛出
        """
        import re
        
        # 验证必填字段
        if 'component_name' not in component:
            raise SARMValidationError(f"第{record_index}条记录缺少必填字段 component_name")
        if 'component_version' not in component:
            raise SARMValidationError(f"第{record_index}条记录缺少必填字段 component_version")
        if 'status' not in component:
            raise SARMValidationError(f"第{record_index}条记录缺少必填字段 status")
        if 'component_unique_id' not in component:
            raise SARMValidationError(f"第{record_index}条记录缺少必填字段 component_unique_id")
        
        # 验证数据类型
        if not isinstance(component['component_name'], str):
            raise SARMValidationError(f"第{record_index}条记录的 component_name 必须是字符串类型")
        
        if not isinstance(component['component_version'], str):
            raise SARMValidationError(f"第{record_index}条记录的 component_version 必须是字符串类型")
        
        if not isinstance(component['status'], str):
            raise SARMValidationError(f"第{record_index}条记录的 status 必须是字符串类型")
        
        if not isinstance(component['component_unique_id'], str):
            raise SARMValidationError(f"第{record_index}条记录的 component_unique_id 必须是字符串类型")
        
        # 验证可选字段的数据类型
        optional_string_fields = [
            'component_desc', 'asset_category', 'asset_type', 'vendor', 
            'ecosystem', 'repository', 'supplier_name'
        ]
        
        for field in optional_string_fields:
            if field in component and not isinstance(component[field], str):
                raise SARMValidationError(f"第{record_index}条记录的 {field} 必须是字符串类型")
        
        # 验证tags字段
        if 'tags' in component:
            if not isinstance(component['tags'], list):
                raise SARMValidationError(f"第{record_index}条记录的 tags 必须是列表类型")
            for i, tag in enumerate(component['tags']):
                if not isinstance(tag, str):
                    raise SARMValidationError(f"第{record_index}条记录的 tags[{i}] 必须是字符串类型")
        
        # 验证attributes字段
        if 'attributes' in component and not isinstance(component['attributes'], dict):
            raise SARMValidationError(f"第{record_index}条记录的 attributes 必须是字典类型")
        
        # 验证component_closed_source_software字段
        if 'component_closed_source_software' in component:
            closed_source = component['component_closed_source_software']
            if not isinstance(closed_source, dict):
                raise SARMValidationError(f"第{record_index}条记录的 component_closed_source_software 必须是字典类型")
            
            # 验证closed_source内部字段
            closed_source_string_fields = [
                'procurement_type', 'supplier_country', 'supplier_identifier', 
                'contract_reference_id', 'owner_team_unique_id', 'owner_unique_id',
                'operations_owner_team_unique_id', 'operations_owner_unique_id',
                'deployment_model', 'installation_path', 'network_exposure',
                'access_url', 'data_sensitivity_level'
            ]
            
            for field in closed_source_string_fields:
                if field in closed_source and not isinstance(closed_source[field], str):
                    raise SARMValidationError(f"第{record_index}条记录的 component_closed_source_software.{field} 必须是字符串类型")
            
            # 验证deployed_ip_addresses字段
            if 'deployed_ip_addresses' in closed_source:
                if not isinstance(closed_source['deployed_ip_addresses'], list):
                    raise SARMValidationError(f"第{record_index}条记录的 component_closed_source_software.deployed_ip_addresses 必须是列表类型")
                for i, ip in enumerate(closed_source['deployed_ip_addresses']):
                    if not isinstance(ip, str):
                        raise SARMValidationError(f"第{record_index}条记录的 component_closed_source_software.deployed_ip_addresses[{i}] 必须是字符串类型")
        
        # 验证context字段
        if 'context' in component:
            if not isinstance(component['context'], list):
                raise SARMValidationError(f"第{record_index}条记录的 context 必须是列表类型")
            for i, ctx in enumerate(component['context']):
                if not isinstance(ctx, dict):
                    raise SARMValidationError(f"第{record_index}条记录的 context[{i}] 必须是字典类型")
                
                # 验证context内部字段
                if 'name' not in ctx:
                    raise SARMValidationError(f"第{record_index}条记录的 context[{i}] 缺少必填字段 name")
                if 'type' not in ctx:
                    raise SARMValidationError(f"第{record_index}条记录的 context[{i}] 缺少必填字段 type")
                if 'content' not in ctx:
                    raise SARMValidationError(f"第{record_index}条记录的 context[{i}] 缺少必填字段 content")
                
                if not isinstance(ctx['name'], str):
                    raise SARMValidationError(f"第{record_index}条记录的 context[{i}].name 必须是字符串类型")
                if not isinstance(ctx['type'], str):
                    raise SARMValidationError(f"第{record_index}条记录的 context[{i}].type 必须是字符串类型")
                if not isinstance(ctx['content'], str):
                    raise SARMValidationError(f"第{record_index}条记录的 context[{i}].content 必须是字符串类型")
                
                if 'description' in ctx and not isinstance(ctx['description'], str):
                    raise SARMValidationError(f"第{record_index}条记录的 context[{i}].description 必须是字符串类型")
        
        # 验证字段值
        if component['component_name'].strip() == '':
            raise SARMValidationError(f"第{record_index}条记录的 component_name 不能为空字符串")
        
        if component['component_version'].strip() == '':
            raise SARMValidationError(f"第{record_index}条记录的 component_version 不能为空字符串")
        
        if component['status'].strip() == '':
            raise SARMValidationError(f"第{record_index}条记录的 status 不能为空字符串")
        
        if component['component_unique_id'].strip() == '':
            raise SARMValidationError(f"第{record_index}条记录的 component_unique_id 不能为空字符串")
        

    
    def update(self, component_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新软件成分信息
        
        Args:
            component_data: 软件成分数据
            
        Returns:
            操作结果
        """
        if 'component_unique_id' not in component_data:
            raise SARMValidationError("更新软件成分时必须提供 component_unique_id")
        
        response = self.client.post('/api/component/update', data=component_data)
        return response
    
    def add_to_carrier(
        self, 
        carrier_unique_id: str,
        component_data: List[Dict[str, Any]],
        security_capability_unique_id: str
    ) -> Dict[str, Any]:
        """
        增加应用载体下软件成分
        
        注意：此方法可用于创建新的软件成分并关联到特定载体。
        
        Args:
            carrier_unique_id: 载体唯一ID
            component_data: 软件成分数据
            security_capability_unique_id: 安全能力唯一ID
            
        Returns:
            操作结果
        """
        params = {"security_capability_unique_id": security_capability_unique_id}
        response = self.client.post(
            f'/api/carrier/add_components/{carrier_unique_id}',
            data=component_data,
            params=params
        )
        return response
    
    def delete_from_carrier(
        self, 
        carrier_unique_id: str, 
        component_ids: List[str]
    ) -> Dict[str, Any]:
        """
        删除应用载体下软件成分
        注意：删除软件成分的同时会同步删除对应漏洞
        
        Args:
            carrier_unique_id: 载体唯一ID
            component_ids: 要删除的成分ID列表
            
        Returns:
            操作结果
        """
        if not component_ids:
            raise SARMValidationError("成分ID列表不能为空")
        
        response = self.client.delete(
            f'/api/carrier/components/{carrier_unique_id}',
            data=component_ids
        )
        return response
    
    def get_carrier_components(
        self, 
        carrier_unique_id: str,
        page: int = 1,
        limit: int = 50,
        component_unique_id: Optional[str] = None,
        component_name: Optional[str] = None,
        component_version: Optional[str] = None,
        status: Optional[str] = None,
        asset_category: Optional[str] = None,
        asset_type: Optional[str] = None,
        vendor: Optional[str] = None,
        ecosystem: Optional[str] = None,
        repository: Optional[str] = None,
        package_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取载体下的软件成分列表
        
        Args:
            carrier_unique_id: 载体唯一ID
            page: 页码
            limit: 每页条数
            component_unique_id: 成分唯一ID
            component_name: 成分名称
            component_version: 成分版本
            status: 状态
            asset_category: 资产类别
            asset_type: 资产类型
            vendor: 供应商
            ecosystem: 生态系统
            repository: 仓库
            package_type: 包类型
            
        Returns:
            成分列表
        """
        # 验证必填参数
        if not carrier_unique_id or not isinstance(carrier_unique_id, str):
            raise SARMValidationError("carrier_unique_id 是必填参数且必须是字符串类型")
        
        if carrier_unique_id.strip() == '':
            raise SARMValidationError("carrier_unique_id 不能为空字符串")
        
        # 验证分页参数
        if not isinstance(page, int) or page < 1:
            raise SARMValidationError("页码必须是大于0的整数")
        
        if not isinstance(limit, int) or limit < 1 or limit > 1000:
            raise SARMValidationError("每页条数必须是1-1000之间的整数")
        
        # 构建请求数据
        data = {
            "carrier_unique_id": carrier_unique_id,
            "page": page,
            "limit": limit
        }
        
        # 添加可选查询参数
        if component_unique_id is not None:
            if not isinstance(component_unique_id, str):
                raise SARMValidationError("component_unique_id 必须是字符串类型")
            data["component_unique_id"] = component_unique_id
            
        if component_name is not None:
            if not isinstance(component_name, str):
                raise SARMValidationError("component_name 必须是字符串类型")
            data["component_name"] = component_name
            
        if component_version is not None:
            if not isinstance(component_version, str):
                raise SARMValidationError("component_version 必须是字符串类型")
            data["component_version"] = component_version
            
        if status is not None:
            if not isinstance(status, str):
                raise SARMValidationError("status 必须是字符串类型")
            data["status"] = status
            
        if asset_category is not None:
            if not isinstance(asset_category, str):
                raise SARMValidationError("asset_category 必须是字符串类型")
            data["asset_category"] = asset_category
            
        if asset_type is not None:
            if not isinstance(asset_type, str):
                raise SARMValidationError("asset_type 必须是字符串类型")
            data["asset_type"] = asset_type
            
        if vendor is not None:
            if not isinstance(vendor, str):
                raise SARMValidationError("vendor 必须是字符串类型")
            data["vendor"] = vendor
            
        if ecosystem is not None:
            if not isinstance(ecosystem, str):
                raise SARMValidationError("ecosystem 必须是字符串类型")
            data["ecosystem"] = ecosystem
            
        if repository is not None:
            if not isinstance(repository, str):
                raise SARMValidationError("repository 必须是字符串类型")
            data["repository"] = repository
            
        if package_type is not None:
            if not isinstance(package_type, str):
                raise SARMValidationError("package_type 必须是字符串类型")
            data["package_type"] = package_type
        
        response = self.client.post('/api/carrier/components', data=data)
        return response
        


    def get_component_unique_id(
        self,
        component_name: str,
        component_version: Optional[str] = None,
        vendor: Optional[str] = None,
        ecosystem: Optional[str] = None,
        repository: Optional[str] = None
    ) -> Dict[str, Any]:
    
        
        # 验证必填参数
        if not component_name or not isinstance(component_name, str):
            raise SARMValidationError("component_name 是必填参数且必须是字符串类型")
        
        if component_name.strip() == '':
            raise SARMValidationError("component_name 不能为空字符串")
        
        # 构建请求数据
        data = {
            "component_name": component_name
        }
        
        # 添加可选参数
        if component_version is not None:
            if not isinstance(component_version, str):
                raise SARMValidationError("component_version 必须是字符串类型")
            data["component_version"] = component_version
            
        if vendor is not None:
            if not isinstance(vendor, str):
                raise SARMValidationError("vendor 必须是字符串类型")
            data["vendor"] = vendor
            
        if ecosystem is not None:
            if not isinstance(ecosystem, str):
                raise SARMValidationError("ecosystem 必须是字符串类型")
            data["ecosystem"] = ecosystem
            
        if repository is not None:
            if not isinstance(repository, str):
                raise SARMValidationError("repository 必须是字符串类型")
            data["repository"] = repository
        
        # 发送请求
        response = self.client.post('/api/component/get_component_unique_id', data=data)
        return response
