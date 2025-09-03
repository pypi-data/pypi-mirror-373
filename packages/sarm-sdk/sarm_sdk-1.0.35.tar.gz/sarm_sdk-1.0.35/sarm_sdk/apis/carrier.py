#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 应用载体 API

提供应用载体相关的API操作。
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from ..models.carrier import CarrierInsert, Carrier
from ..models.response import BatchOperationResult
from ..exceptions import SARMValidationError

if TYPE_CHECKING:
    from ..client import SARMClient


class CarrierAPI:
    """应用载体API类"""
    
    def __init__(self, client: 'SARMClient'):
        self.client = client
    
    def _validate_carrier_data(self, carrier: Dict[str, Any], record_index: int = 1) -> None:
        """
        验证载体数据的格式和内容
        
        Args:
            carrier: 载体数据字典
            record_index: 记录索引，用于错误提示
            
        Raises:
            SARMValidationError: 当数据验证失败时抛出
        """
        import re
        
        # 验证必填字段
        if 'carrier' not in carrier:
            raise SARMValidationError(f"第{record_index}条记录缺少必填字段 carrier")
        
        carrier_info = carrier['carrier']
        
        # 验证载体信息必填字段
        if 'carrier_type' not in carrier_info:
            raise SARMValidationError(f"第{record_index}条记录缺少必填字段 carrier_type")
        if 'name' not in carrier_info:
            raise SARMValidationError(f"第{record_index}条记录缺少必填字段 name")
        
        # 验证数据类型

        if not isinstance(carrier_info['carrier_type'], str):
            raise SARMValidationError(f"第{record_index}条记录的 carrier_type 必须是字符串类型")
        
        if not isinstance(carrier_info['name'], str):
            raise SARMValidationError(f"第{record_index}条记录的 name 必须是字符串类型")
        
        # 验证可选字段的数据类型
        optional_string_fields = [
            'description', 'source', 'protocol', 'ip', 'path', 'domain', 
            'internet_ip', 'nat_ip', 'internal_ip', 'repo_namespace', 
            'repo_name', 'repo_url', 'branch', 'source_type'
        ]
        
        for field in optional_string_fields:
            if field in carrier_info and not isinstance(carrier_info[field], str):
                raise SARMValidationError(f"第{record_index}条记录的 {field} 必须是字符串类型")
        
        # 验证port字段
        if 'port' in carrier_info and not isinstance(carrier_info['port'], int):
            raise SARMValidationError(f"第{record_index}条记录的 port 必须是整数类型")
        
        # 验证security_capability_id字段
        if 'security_capability_id' in carrier_info and not isinstance(carrier_info['security_capability_id'], int):
            raise SARMValidationError(f"第{record_index}条记录的 security_capability_id 必须是整数类型")
        
        # 验证tags字段
        if 'tags' in carrier_info:
            if not isinstance(carrier_info['tags'], list):
                raise SARMValidationError(f"第{record_index}条记录的 tags 必须是列表类型")
            for i, tag in enumerate(carrier_info['tags']):
                if not isinstance(tag, str):
                    raise SARMValidationError(f"第{record_index}条记录的 tags[{i}] 必须是字符串类型")
        
        # 验证app_ids字段
        if 'app_ids' in carrier:
            if not isinstance(carrier['app_ids'], list):
                raise SARMValidationError(f"第{record_index}条记录的 app_ids 必须是列表类型")
            for i, app_id in enumerate(carrier['app_ids']):
                if not isinstance(app_id, str):
                    raise SARMValidationError(f"第{record_index}条记录的 app_ids[{i}] 必须是字符串类型")
        
        # 验证organize_user_unique_id字段
        if 'organize_user_unique_id' in carrier and not isinstance(carrier['organize_user_unique_id'], str):
            raise SARMValidationError(f"第{record_index}条记录的 organize_user_unique_id 必须是字符串类型")
        
        # 验证字段值
        
        if carrier_info['name'].strip() == '':
            raise SARMValidationError(f"第{record_index}条记录的 name 不能为空字符串")
        
        # 验证carrier_type的有效值
        valid_carrier_types = ['code_repo', 'service_address', 'host']
        if carrier_info['carrier_type'] not in valid_carrier_types:
            raise SARMValidationError(f"第{record_index}条记录的 carrier_type 必须是以下值之一: {', '.join(valid_carrier_types)}")
        
        # 验证port范围
        if 'port' in carrier_info:
            if carrier_info['port'] < 1 or carrier_info['port'] > 65535:
                raise SARMValidationError(f"第{record_index}条记录的 port 必须在1-65535之间")
    def create_batch(
        self,
        carriers: List[Dict[str, Any]],
        execute_release: bool = False
    ) :
        """
        批量创建应用载体
        
        Args:
            carriers: 应用载体数据列表，每个元素为包含载体信息的字典
            execute_release: 是否直接发布，默认为False进入预处理状态
            
        Returns:
            Dict[str, Any]: 批量操作结果，包含操作状态和数据信息
            
        Raises:
            SARMValidationError: 当数据验证失败时抛出
            
        Example:
            >>> carriers = [{
            ...     "carrier": {
            ...         "carrier_type": "service_address",
            ...         "name": "example-service",
            ...         "description": "示例服务"
            ...     }
                    "app_ids":["3322"],
                    "organize_user_unique_id":"A001"
            ... }]
            >>> result = carrier_api.create_batch(carriers)
        """
        if not carriers:
            raise SARMValidationError("应用载体列表不能为空")
        
        if len(carriers) > 1000:
            raise SARMValidationError("单次批量操作不能超过1000条记录")
        
        # 验证数据
        carrier_data = []
        for i, carrier in enumerate(carriers):
            if isinstance(carrier, dict):
                self._validate_carrier_data(carrier, i + 1)
                carrier_data.append(carrier)
            else:
                self._validate_carrier_data(carrier.dict(), i + 1)
                carrier_data.append(carrier.dict())
        
        # 发送请求
        response = self.client.post(
            '/api/carrier/create',
            data=carrier_data,
            execute_release=execute_release
        )
        return response

    
    def create(self, carrier: Dict[str,any], execute_release: bool = False):
        """
        创建单个应用载体
        
        Args:
            carrier: 载体数据
            execute_release: 是否直接发布
            
        Returns:
            操作结果
        """
        if not isinstance(carrier, (CarrierInsert, dict)):
            raise SARMValidationError("载体数据必须是 CarrierInsert 对象或字典类型")
        
        return self.create_batch([carrier], execute_release=execute_release)

    def get_list(
            self,
            page: int = 1,
            limit: int = 50,
            carrier_type: str = "",
            name: str = "",
            source: str = "",
            data_status: str = ""
    ) -> Dict[str, Any]:
        """
        获取应用载体列表
        
        Args:
            page: 页码，默认为1
            limit: 每页条数，默认为50，最大1000
            carrier_type: 载体类型，可选值：code_repo, service_address, host
            name: 载体名称，支持模糊搜索
            source: 来源标识
            data_status: 数据状态
            
        Returns:
            Dict[str, Any]: 载体列表，包含分页信息和数据列表
            
        Raises:
            SARMValidationError: 当参数验证失败时抛出
            
        Example:
            >>> result = carrier_api.get_list(
            ...     page=1,
            ...     limit=10,
            ...     carrier_type="code_repo",
            ...     name="my-project"
            ... )
            >>> carriers = result.get('data', {}).get('list', [])
        """
        # 验证参数
        if not isinstance(page, int) or page < 1:
            raise SARMValidationError("页码必须是大于0的整数")
        
        if not isinstance(limit, int) or limit < 1 or limit > 1000:
            raise SARMValidationError("每页条数必须是1-1000之间的整数")
        
        if not isinstance(carrier_type, str):
            raise SARMValidationError("载体类型必须是字符串类型")
        
        if not isinstance(name, str):
            raise SARMValidationError("载体名称必须是字符串类型")
        
        if not isinstance(source, str):
            raise SARMValidationError("来源必须是字符串类型")
        params = {"page": page, "limit": limit}
        if carrier_type:
            params["carrier_type"] = carrier_type
        if name:
            params["name"] = name
        if source:
            params["source"] = source
        if data_status:
            params["data_status"] = data_status
        response = self.client.post('/api/carrier/list', params=params)
        return response
    
    def update_batch(
        self,
        carriers: List[Dict[str, Any]],
        execute_release: bool = False
    ) -> Dict[str, Any]:
        """
        批量更新应用载体
        
        Args:
            carriers: 应用载体数据列表
            execute_release: 是否直接发布
            
        Returns:
            操作结果
        """
        if not carriers:
            raise SARMValidationError("应用载体列表不能为空")
        
        if not isinstance(carriers, list):
            raise SARMValidationError("载体列表必须是列表类型")
        
        # 验证数据
        for i, carrier in enumerate(carriers):
            self._validate_carrier_data(carrier, i + 1)
        
        response = self.client.post(
            '/api/carrier/update',
            data=carriers,
            execute_release=execute_release
        )
        return response
    
    def update(self, carrier_data: Dict[str, Any], execute_release: bool = False) -> Dict[str, Any]:
        """
        更新单个应用载体
        
        Args:
            carrier_data: 载体数据
            execute_release: 是否直接发布
            
        Returns:
            操作结果
        """
        if not isinstance(carrier_data, dict):
            raise SARMValidationError("载体数据必须是字典类型")
        
        return self.update_batch([carrier_data], execute_release=execute_release)

    def delete_batch(self, carrier_ids: List[str]) -> Dict[str, Any]:
        """
        批量删除应用载体

        Args:
            carrier_ids: 载体ID列表

        Returns:
            操作结果
        """
        if not carrier_ids:
            raise SARMValidationError("载体ID列表不能为空")
        
        if not isinstance(carrier_ids, list):
            raise SARMValidationError("载体ID列表必须是列表类型")
        
        # 验证每个ID都是字符串类型
        for i, carrier_id in enumerate(carrier_ids):
            if not isinstance(carrier_id, str):
                raise SARMValidationError(f"第{i+1}个载体ID必须是字符串类型")
            if carrier_id.strip() == '':
                raise SARMValidationError(f"第{i+1}个载体ID不能为空字符串")
        
        req = {}
        req["carrier_id_list"] = carrier_ids
        response = self.client.delete('/api/carrier/delete', data=req)
        return response
    
    def delete(self, carrier_id: str) -> Dict[str, Any]:
        """
        删除单个应用载体
        
        Args:
            carrier_id: 载体ID
            
        Returns:
            操作结果
        """
        if not isinstance(carrier_id, str):
            raise SARMValidationError("载体ID必须是字符串类型")
        
        if carrier_id.strip() == '':
            raise SARMValidationError("载体ID不能为空字符串")
        
        return self.delete_batch([carrier_id])
    
    def get_carrier_unique_id(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        获取载体唯一ID
        
        Args:
            filters: 查询过滤条件
            
        Returns:
            载体唯一ID列表
        """
        if filters is not None and not isinstance(filters, dict):
            raise SARMValidationError("过滤条件必须是字典类型")
        
        data = filters or {}
        response = self.client.post('/api/carrier/get_carrier_unique_id', data=data)
        return response