#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 应用 API

提供应用相关的API操作。
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from ..models.response import BatchOperationResult
from ..exceptions import SARMValidationError, SARMAPIError

if TYPE_CHECKING:
    from ..client import SARMClient


class ApplicationAPI:
    """应用API类"""
    
    def __init__(self, client: 'SARMClient'):
        self.client = client
    
    def _validate_application_data(self, application: Dict[str, Any], record_index: int = 1) -> None:
        """
        验证应用数据的格式和内容
        
        Args:
            application: 应用数据字典
            record_index: 记录索引，用于错误提示
            
        Raises:
            SARMValidationError: 当数据验证失败时抛出
        """
        # 验证必填字段
        if 'application_name' not in application:
            raise SARMValidationError(f"第{record_index}条记录缺少必填字段 application_name")
        if 'application_status' not in application:
            raise SARMValidationError(f"第{record_index}条记录缺少必填字段 application_status")
        
        # 验证数据类型
        if 'application_unique_id' in application and not isinstance(application['application_unique_id'], str):
            raise SARMValidationError(f"第{record_index}条记录的 application_unique_id 必须是字符串类型")
        
        if not isinstance(application['application_name'], str):
            raise SARMValidationError(f"第{record_index}条记录的 application_name 必须是字符串类型")
        
        if 'application_desc' in application and not isinstance(application['application_desc'], str):
            raise SARMValidationError(f"第{record_index}条记录的 application_desc 必须是字符串类型")
        
        if 'application_version' in application and not isinstance(application['application_version'], str):
            raise SARMValidationError(f"第{record_index}条记录的 application_version 必须是字符串类型")
        
        if not isinstance(application['application_status'], str):
            raise SARMValidationError(f"第{record_index}条记录的 application_status 必须是字符串类型")
        
        # 验证字段值
        if application['application_name'].strip() == '':
            raise SARMValidationError(f"第{record_index}条记录的 application_name 不能为空字符串")
        
        valid_statuses = ['active', 'retired', 'maintenance']
        if application['application_status'] not in valid_statuses:
            raise SARMValidationError(f"第{record_index}条记录的 application_status 必须是以下值之一: {', '.join(valid_statuses)}")

    def create_batch(
        self,
        applications: List[Dict[str, Any]],
        execute_release: bool = False
    ):
        """
        批量创建应用
        
        Args:
            applications: 应用数据列表
            execute_release: 是否直接发布
            
        Returns:
            批量操作结果
        """
        if not applications:
            raise SARMValidationError("应用列表不能为空")
        
        if len(applications) > 1000:
            raise SARMValidationError("单次批量操作不能超过1000条记录")
        
        # 验证应用数据
        for i, app in enumerate(applications):
            if 'application' not in app:
                raise SARMValidationError(f"第{i+1}条记录缺少 application 字段")
            
            application = app['application']
            self._validate_application_data(application, i + 1)

        # 发送请求
        response = self.client.post(
            '/api/application/create',
            data=applications,
            execute_release=execute_release
        )
        return response
        # # 处理批量操作结果
        # if isinstance(response, dict) and 'code' in response:
        #     from ..models.response import BatchOperationItem
        #
        #     # 应用API的响应格式比较简单，我们需要构造BatchOperationResult
        #     code = response.get('code')
        #     success = code == 200 or code == '200'
        #     items = [
        #         BatchOperationItem(
        #             unique_id=app['application'].get('application_unique_id', f"app_{i}"),
        #             name=app['application'].get('application_name', ''),
        #             success=success,
        #             msg=response.get('msg_zh', "创建成功" if success else "创建失败")
        #         )
        #         for i, app in enumerate(applications)
        #     ]
        #
        #     return BatchOperationResult(
        #         data=items,
        #         code=200 if success else 500
        #     )
        #
        # return BatchOperationResult(**response)
    
    def create(self, application_data: Dict[str, Any], execute_release: bool = False):
        """
        创建单个应用
        
        Args:
            application_data: 应用数据，格式为 {"application": {...}}
            execute_release: 是否直接发布
            
        Returns:
            操作结果
        """
        if not isinstance(application_data, dict):
            raise SARMValidationError("应用数据必须是字典类型")
        
        if 'application' not in application_data:
            raise SARMValidationError("缺少 application 字段")
        
        # 验证应用数据
        self._validate_application_data(application_data['application'])
        
        return self.create_batch([application_data], execute_release=execute_release)
    
    def delete_batch(self, app_ids: List[str]):
        """
        批量删除应用
        
        Args:
            app_ids: 应用ID列表
            
        Returns:
            批量操作结果
        """
        if not app_ids:
            raise SARMValidationError("应用ID列表不能为空")
        
        if not isinstance(app_ids, list):
            raise SARMValidationError("应用ID列表必须是列表类型")
        
        # 验证每个ID都是字符串类型
        for i, app_id in enumerate(app_ids):
            if not isinstance(app_id, str):
                raise SARMValidationError(f"第{i+1}个应用ID必须是字符串类型")
            if app_id.strip() == '':
                raise SARMValidationError(f"第{i+1}个应用ID不能为空字符串")
        
        data = {"app_id_list": app_ids}
        response = self.client.delete('/api/application/delete', data=data)
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
        #                 unique_id=app_id,
        #                 name='',
        #                 success=success,
        #                 msg="删除成功" if success else "删除失败"
        #             )
        #             for app_id in app_ids
        #         ]
        #
        #     return BatchOperationResult(
        #         data=items,
        #         code=response.get('code', 200)
        #     )
        #
        # return BatchOperationResult(**response)
    
    def delete(self, app_id: str) -> BatchOperationResult:
        """
        删除单个应用
        
        Args:
            app_id: 应用ID
            
        Returns:
            操作结果
        """
        if not isinstance(app_id, str):
            raise SARMValidationError("应用ID必须是字符串类型")
        
        if app_id.strip() == '':
            raise SARMValidationError("应用ID不能为空字符串")
        
        return self.delete_batch([app_id])
    
    def get_list(
        self,
        page: int = 1,
        limit: int = 10,
        application_name: Optional[str] = None,
        application_status: Optional[str] = None,
        data_status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取应用列表
        
        Args:
            page: 页码
            limit: 每页条数
            application_name: 应用名称
            application_status: 应用状态(active、inactive)
            data_status: 数据状态(imperfect,perfect,published)
            
        Returns:
            应用列表
        """
        # 验证参数
        if not isinstance(page, int) or page < 1:
            raise SARMValidationError("页码必须是大于0的整数")
        
        if not isinstance(limit, int) or limit < 1 or limit > 1000:
            raise SARMValidationError("每页条数必须是1-1000之间的整数")
        
        if application_name is not None and not isinstance(application_name, str):
            raise SARMValidationError("应用名称必须是字符串类型")
        
        if application_status is not None:
            if not isinstance(application_status, str):
                raise SARMValidationError("应用状态必须是字符串类型")
            valid_statuses = ['active', 'maintenance','retired']
            if application_status not in valid_statuses:
                raise SARMValidationError(f"应用状态必须是以下值之一: {', '.join(valid_statuses)}")
        
        data = {"page": page, "limit": limit}
        
        if application_name:
            data["application_name"] = application_name
        if application_status:
            data["application_status"] = application_status
        if data_status:
            data["data_status"] = data_status
        
        response = self.client.post('/api/application/list', data=data)
        return response
    
    def update(
        self,
        application_data: List[Dict[str, Any]],
        execute_release: bool = False
    ) -> Dict[str, Any]:
        """
        更新应用
        
        Args:
            application_data: 应用数据，格式为 {"application": {...}}
            execute_release: 是否直接发布
            
        Returns:
            操作结果
        """
        if not isinstance(application_data, list):
            raise SARMValidationError("应用数据必须是列表类型")
        
        if 'application' not in application_data:
            raise SARMValidationError("缺少 application 字段")
        
        # 验证应用数据
        for app in application_data:
            self._validate_application_data(app['application'])
        
        response = self.client.post(
            '/api/application/update',
            data=application_data,
            execute_release=execute_release
        )
        return response
    
    def delete_business_system(self, app_name: List[str]) -> Dict[str, Any]:
        """删除应用的业务系统关联"""
        data = app_name
        response = self.client.delete('/api/application/delete_business_system', data=data)
        return response 