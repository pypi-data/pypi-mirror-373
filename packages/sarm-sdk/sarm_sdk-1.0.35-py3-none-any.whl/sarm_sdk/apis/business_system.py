#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 业务系统 API

提供业务系统相关的API操作。
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from ..models.response import BatchOperationResult
from ..exceptions import SARMValidationError

if TYPE_CHECKING:
    from ..client import SARMClient


class BusinessSystemAPI:
    """业务系统API类"""
    
    def __init__(self, client: 'SARMClient'):
        self.client = client
    
    def _validate_business_system_data(self, business_system: Dict[str, Any], record_index: int = 1) -> None:
        """
        验证业务系统数据的格式和内容
        
        Args:
            business_system: 业务系统数据字典
            record_index: 记录索引，用于错误提示
            
        Raises:
            SARMValidationError: 当数据验证失败时抛出
        """
        import re
        
        # 验证必填字段
        if 'business_system_name' not in business_system:
            raise SARMValidationError(f"第{record_index}条记录缺少必填字段 business_system_name")
        if 'business_system_status' not in business_system:
            raise SARMValidationError(f"第{record_index}条记录缺少必填字段 business_system_status")
        
        # 验证数据类型
        if 'business_system_uuid' in business_system and not isinstance(business_system['business_system_uuid'], str):
            raise SARMValidationError(f"第{record_index}条记录的 business_system_uuid 必须是字符串类型")
        
        if not isinstance(business_system['business_system_name'], str):
            raise SARMValidationError(f"第{record_index}条记录的 business_system_name 必须是字符串类型")
        
        if 'business_system_puuid' in business_system and not isinstance(business_system['business_system_puuid'], str):
            raise SARMValidationError(f"第{record_index}条记录的 business_system_puuid 必须是字符串类型")
        
        if 'business_system_desc' in business_system and not isinstance(business_system['business_system_desc'], str):
            raise SARMValidationError(f"第{record_index}条记录的 business_system_desc 必须是字符串类型")
        
        if not isinstance(business_system['business_system_status'], str):
            raise SARMValidationError(f"第{record_index}条记录的 business_system_status 必须是字符串类型")
        
        if 'dep_id' in business_system and not isinstance(business_system['dep_id'], str):
            raise SARMValidationError(f"第{record_index}条记录的 dep_id 必须是字符串类型")
        
        if 'dep_name' in business_system and not isinstance(business_system['dep_name'], str):
            raise SARMValidationError(f"第{record_index}条记录的 dep_name 必须是字符串类型")
        
        if 'group_own' in business_system and not isinstance(business_system['group_own'], str):
            raise SARMValidationError(f"第{record_index}条记录的 group_own 必须是字符串类型")
        
        if 'group_own_id' in business_system and not isinstance(business_system['group_own_id'], str):
            raise SARMValidationError(f"第{record_index}条记录的 group_own_id 必须是字符串类型")
        
        if 'system_owner_name' in business_system and not isinstance(business_system['system_owner_name'], str):
            raise SARMValidationError(f"第{record_index}条记录的 system_owner_name 必须是字符串类型")
        
        if 'application_level_desc' in business_system and not isinstance(business_system['application_level_desc'], str):
            raise SARMValidationError(f"第{record_index}条记录的 application_level_desc 必须是字符串类型")
        
        if 'develop_mode' in business_system and not isinstance(business_system['develop_mode'], str):
            raise SARMValidationError(f"第{record_index}条记录的 develop_mode 必须是字符串类型")
        
        if 'cooperate_comp' in business_system and not isinstance(business_system['cooperate_comp'], str):
            raise SARMValidationError(f"第{record_index}条记录的 cooperate_comp 必须是字符串类型")
        
        # 验证字段值
        if business_system['business_system_name'].strip() == '':
            raise SARMValidationError(f"第{record_index}条记录的 business_system_name 不能为空字符串")
        
        valid_statuses = ["active","maintenance","retired"]
        if business_system['business_system_status'] not in valid_statuses:
            raise SARMValidationError(f"第{record_index}条记录的 business_system_status 必须是以下值之一: {', '.join(valid_statuses)}")
    
    def create_batch(
        self,
        business_systems: List[Dict[str, Any]],
        execute_release: bool = False
    ):
        """
        批量创建业务系统
        
        Args:
            business_systems: 业务系统数据列表
            execute_release: 是否直接发布
            
        Returns:
            批量操作结果
        """
        if not business_systems:
            raise SARMValidationError("业务系统列表不能为空")
        
        if len(business_systems) > 1000:
            raise SARMValidationError("单次批量操作不能超过1000条记录")
        
        # 验证业务系统数据
        for i, bs in enumerate(business_systems):
            if 'business_system' not in bs:
                raise SARMValidationError(f"第{i+1}条记录缺少 business_system 字段")
            
            business_system = bs['business_system']
            self._validate_business_system_data(business_system, i + 1)
        
        # 发送请求
        response = self.client.post(
            '/api/business_system/create',
            data=business_systems,
            execute_release=execute_release
        )

        
        return response
    
    def create(self, business_system_data: Dict[str, Any], execute_release: bool = False):
        """
        创建单个业务系统
        
        Args:
            business_system_data: 业务系统数据，格式为 {"business_system": {...}}
            execute_release: 是否直接发布
            
        Returns:
            操作结果
        """
        if not isinstance(business_system_data, dict):
            raise SARMValidationError("业务系统数据必须是字典类型")
        
        if 'business_system' not in business_system_data:
            raise SARMValidationError("缺少 business_system 字段")
        
        # 验证业务系统数据
        self._validate_business_system_data(business_system_data['business_system'])
        
        return self.create_batch([business_system_data], execute_release=execute_release)
    
    def delete_batch(self, business_system_ids: List[str]):
        """
        批量删除业务系统
        注意：业务系统存在关联数据时无法删除
        
        Args:
            business_system_ids: 业务系统ID列表
            
        Returns:
            批量操作结果
        """
        if not business_system_ids:
            raise SARMValidationError("业务系统ID列表不能为空")
        
        if not isinstance(business_system_ids, list):
            raise SARMValidationError("业务系统ID列表必须是列表类型")
        
        # 验证每个ID都是字符串类型
        for i, bs_id in enumerate(business_system_ids):
            if not isinstance(bs_id, str):
                raise SARMValidationError(f"第{i+1}个业务系统ID必须是字符串类型")
            if bs_id.strip() == '':
                raise SARMValidationError(f"第{i+1}个业务系统ID不能为空字符串")
        
        data = {"business_system_id_list": business_system_ids}
        response = self.client.delete('/api/business_system/delete', data=data)
        return response
        # # 处理批量操作结果
        # if isinstance(response, dict) and 'code' in response and 'data' in response:
        #     from ..models.response import BatchOperationItem
        #
        #     if isinstance(response.get('data'), list):
        #         items = [
        #             BatchOperationItem(
        #                 unique_id=item.get('unique_id', ''),
        #                 name=item.get('name', ''),
        #                 success=item.get('success', False),
        #                 msg=item.get('msg', '')
        #             )
        #             for item in response['data']
        #         ]
        #     else:
        #         # 简单成功响应
        #         success = response.get('code') == 200
        #         items = [
        #             BatchOperationItem(
        #                 unique_id=bs_id,
        #                 name='',
        #                 success=success,
        #                 msg="删除成功" if success else "删除失败"
        #             )
        #             for bs_id in business_system_ids
        #         ]
        #
        #     return BatchOperationResult(
        #         data=items,
        #         code=response.get('code', 200),
        #         summary=response.get('summary', '')
        #     )
        #
        # return BatchOperationResult(**response)
    
    def delete(self, business_system_id: str) -> BatchOperationResult:
        """
        删除单个业务系统
        
        Args:
            business_system_id: 业务系统ID
            
        Returns:
            操作结果
        """
        if not isinstance(business_system_id, str):
            raise SARMValidationError("业务系统ID必须是字符串类型")
        
        if business_system_id.strip() == '':
            raise SARMValidationError("业务系统ID不能为空字符串")
        
        return self.delete_batch([business_system_id])
    
    def get_list(
        self,
        page: int = 1,
        limit: int = 10,
        business_system_name: Optional[str] = None,
        business_system_status: Optional[str] = None,
        data_status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取业务系统列表
        
        Args:
            page: 页码
            limit: 每页条数
            business_system_name: 业务系统名称
            business_system_status: 业务系统状态(active、maintenance、retired)
            data_status: 数据状态(imperfect,perfect,published)
            
        Returns:
            业务系统列表
        """
        # 验证参数
        if not isinstance(page, int) or page < 1:
            raise SARMValidationError("页码必须是大于0的整数")
        
        if not isinstance(limit, int) or limit < 1 or limit > 1000:
            raise SARMValidationError("每页条数必须是1-1000之间的整数")
        
        if business_system_name is not None and not isinstance(business_system_name, str):
            raise SARMValidationError("业务系统名称必须是字符串类型")
        
        if business_system_status is not None:
            if not isinstance(business_system_status, str):
                raise SARMValidationError("业务系统状态必须是字符串类型")
            valid_statuses = ['active', 'maintenance', 'retired']
            if business_system_status not in valid_statuses:
                raise SARMValidationError(f"业务系统状态必须是以下值之一: {', '.join(valid_statuses)}")
        data: Dict[str, Any] = {"page": page, "limit": limit}
        
        if business_system_name:
            data["business_system_name"] = business_system_name
        if business_system_status:
            data["business_system_status"] = business_system_status
        if data_status:
            data["data_status"] = data_status
        
        response = self.client.post('/api/business_system/list', data=data)
        return response
    
    def update(
            self,
            business_system_data: List[Dict[str, Any]],
            execute_release: bool = False
        ) -> Dict[str, Any]:
        """
        更新业务系统

        Args:
            business_system_data: 业务系统数据列表（每个元素为一个业务系统字典）
            execute_release: 是否直接发布

        Returns:
            操作结果
        """
        # 验证是否为列表类型
        if not isinstance(business_system_data, list):
            raise SARMValidationError("业务系统数据必须是列表类型")

        # 验证列表不为空
        if not business_system_data:
            raise SARMValidationError("业务系统数据列表不能为空")

        # 逐个验证列表中的业务系统数据
        for item in business_system_data:
            # 验证列表中的每个元素是否为字典
            if not isinstance(item, dict):
                raise SARMValidationError("业务系统列表中的元素必须是字典类型")

            # 验证每个字典是否包含 'business_system' 字段
            if 'business_system' not in item:
                raise SARMValidationError("业务系统数据缺少 business_system 字段")

            # 验证具体的业务系统数据
            self._validate_business_system_data(item['business_system'])

        # 发送请求更新业务系统
        response = self.client.post(
            '/api/business_system/update',
            data=business_system_data,
            execute_release=execute_release
        )
        return response
    
    def delete_organize(self, businessUniqueId: List[str]) -> Dict[str, Any]:
        """
        删除业务系统的组织关联
        
        Args:
            organize_id: 组织ID
            
        Returns:
            操作结果
        """
        if not isinstance(businessUniqueId, list):
            raise SARMValidationError("业务系统ID列表必须是列表类型")
        
        if not businessUniqueId:
            raise SARMValidationError("业务系统ID列表不能为空")
        
        data = businessUniqueId
        response = self.client.delete('/api/business_system/delete_organize', data=data)
        return response 