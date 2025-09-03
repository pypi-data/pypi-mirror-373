#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 载体数据录入 API

提供载体维度的多数据录入功能，一次性录入载体、安全问题、组件和漏洞数据。
这是创建安全问题、组件和漏洞的主要接口。
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from ..models.response import BatchOperationResult
from ..exceptions import SARMValidationError

if TYPE_CHECKING:
    from ..client import SARMClient


class IssueDataImportAPI:
    """
    安全问题数据导入API

    提供安全问题维度的多数据录入功能，一次性录入安全问题、组件和漏洞数据。
    这是创建安全问题、组件和漏洞的推荐方式。
    """
    
    def __init__(self, client: 'SARMClient'):
        """
        初始化安全问题数据导入API

        Args:
            client: SARM客户端实例
        """
        self.client = client
    
    def import_carrier_data(self, carrier_data_list: List[Dict[str, Any]], execute_release: bool = False) :
        """
        安全问题维度多数据录入，一次性录入载体、安全问题、组件和漏洞数据

        Args:
            carrier_data_list: 载体数据列表
            execute_release: 是否直接发布

        Returns:
            BatchOperationResult: 批量操作结果
        """
        # 验证数据
        if not isinstance(carrier_data_list, list):
            raise SARMValidationError("carrier_data_list must be a list")
        
        if not carrier_data_list:
            raise SARMValidationError("carrier_data_list cannot be empty")
        
        for data in carrier_data_list:
            if not isinstance(data, dict):
                raise SARMValidationError("Each item in carrier_data_list must be a dictionary")
            
            if 'carrier' not in data:
                raise SARMValidationError("Each item must contain 'carrier' field")
            
            if 'carrier_unique_id' not in data['carrier']:
                raise SARMValidationError("Each carrier must have 'carrier_unique_id'")
        if len(carrier_data_list) > 50:
            raise SARMValidationError("carrier_data_list InsertInsertCarrierIssueTooLang ")

        request_data = carrier_data_list

        if execute_release:
            self.client.headers["execute_release"] = "true"
        else:
            self.client.headers["execute_release"] = "false"
        # 发送请求
        response = self.client.post(
            '/api/insert/insert_carrier_issue',
            data=request_data
        )
        #
        # # 处理响应
        # result = BatchOperationResult.from_dict(response)
        return response
    
    def create_carrier_data_structure(
        self,
        carrier_info: Dict[str, Any],
        source_type: str = "automatic",
        issue_list: Optional[List[Dict[str, Any]]] = None,
        component_list: Optional[List[Dict[str, Any]]] = None,
        vuln_list: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        创建标准的安全问题数据结构

        Args:
            carrier_info: 载体基础信息
            source_type: 数据来源类型，默认"automatic"
            issue_list: 安全问题列表
            component_list: 组件列表
            vuln_list: 漏洞列表

        Returns:
            Dict[str, Any]: 标准安全问题数据结构
        """
        # 验证载体信息
        if not isinstance(carrier_info, dict):
            raise SARMValidationError("carrier_info must be a dictionary")
        
        if 'carrier_unique_id' not in carrier_info:
            raise SARMValidationError("carrier_info must contain 'carrier_unique_id'")
        
        if 'name' not in carrier_info:
            raise SARMValidationError("carrier_info must contain 'name'")

        # 构建标准数据结构
        carrier_data = {
            "carrier": carrier_info,
            "source_type": source_type
        }
        
        # 添加可选数据
        if issue_list:
            carrier_data["issue_list"] = issue_list
        
        if component_list:
            carrier_data["component_list"] = component_list
        
        if vuln_list:
            carrier_data["vuln_list"] = vuln_list
        
        return carrier_data
    
    def create_issue(
        self,
        carrier_unique_id: str,
        issue_data: Dict[str, Any],
        execute_release: bool = False
    ) -> Dict[str, Any]:
        """
        创建安全问题并关联到指定载体

        Args:
            carrier_unique_id: 载体唯一ID
            issue_data: 安全问题数据
            execute_release: 是否直接发布

        Returns:
            Dict[str, Any]: 操作结果
        """
        # 验证数据
        if not carrier_unique_id:
            raise SARMValidationError("carrier_unique_id cannot be empty")
        
        if not isinstance(issue_data, dict):
            raise SARMValidationError("issue_data must be a dictionary")
        
        if 'issue_unique_id' not in issue_data:
            raise SARMValidationError("issue_data must contain 'issue_unique_id'")

        # 构建载体数据结构
        carrier_info = {
            "carrier_unique_id": carrier_unique_id
        }
        
        carrier_data = self.create_carrier_data_structure(
            carrier_info=carrier_info,
            issue_list=[issue_data]
        )
        
        # 发送请求
        result = self.import_carrier_data([carrier_data], execute_release=execute_release)
        
        # 简化返回结果
        if result.success_count == 1:
            return {"code": 200, "msg": "Success", "msg_zh": "成功"}
        else:
            error_item = next((item for item in result.data if not item.success), None)
            if error_item:
                return {"code": 400, "msg": error_item.msg, "msg_zh": error_item.msg}
            return {"code": 400, "msg": "Failed to create issue", "msg_zh": "创建安全问题失败"}
    
    def create_component(
        self,
        carrier_unique_id: str,
        component_data: Dict[str, Any],
        security_capability_unique_id: str,
        execute_release: bool = False
    ) -> Dict[str, Any]:
        """
        创建软件组件并关联到指定载体

        Args:
            carrier_unique_id: 载体唯一ID
            component_data: 组件数据
            security_capability_unique_id: 安全能力唯一ID
            execute_release: 是否直接发布

        Returns:
            Dict[str, Any]: 操作结果
        """
        # 验证数据
        if not carrier_unique_id:
            raise SARMValidationError("carrier_unique_id cannot be empty")
        
        if not isinstance(component_data, dict):
            raise SARMValidationError("component_data must be a dictionary")
        
        if 'component_unique_id' not in component_data:
            raise SARMValidationError("component_data must contain 'component_unique_id'")
        
        if not security_capability_unique_id:
            raise SARMValidationError("security_capability_unique_id cannot be empty")

        # 构建载体数据结构
        carrier_info = {
            "carrier_unique_id": carrier_unique_id
        }
        
        # 添加安全能力关联
        component_with_capability = component_data.copy()
        component_with_capability["security_capability_unique_id"] = security_capability_unique_id
        
        carrier_data = self.create_carrier_data_structure(
            carrier_info=carrier_info,
            component_list=[component_with_capability]
        )
        
        # 发送请求
        result = self.import_carrier_data([carrier_data], execute_release=execute_release)
        print(result)
    
    def create_vulnerability(
        self,
        carrier_unique_id: str,
        vuln_data: Dict[str, Any],
        component_unique_id: str,
        security_capability_unique_id: str,
        execute_release: bool = False
    ) -> Dict[str, Any]:
        """
        创建漏洞并关联到指定载体和组件

        Args:
            carrier_unique_id: 载体唯一ID
            vuln_data: 漏洞数据
            component_unique_id: 组件唯一ID
            security_capability_unique_id: 安全能力唯一ID
            execute_release: 是否直接发布

        Returns:
            Dict[str, Any]: 操作结果
        """
        # 验证数据
        if not carrier_unique_id:
            raise SARMValidationError("carrier_unique_id cannot be empty")
        
        if not isinstance(vuln_data, dict):
            raise SARMValidationError("vuln_data must be a dictionary")
        
        if 'vuln_unique_id' not in vuln_data:
            raise SARMValidationError("vuln_data must contain 'vuln_unique_id'")
        
        if not component_unique_id:
            raise SARMValidationError("component_unique_id cannot be empty")
        
        if not security_capability_unique_id:
            raise SARMValidationError("security_capability_unique_id cannot be empty")

        # 构建载体数据结构
        carrier_info = {
            "carrier_unique_id": carrier_unique_id
        }
        
        # 添加组件和安全能力关联
        vuln_with_relations = vuln_data.copy()
        vuln_with_relations["component_unique_id"] = component_unique_id
        vuln_with_relations["security_capability_unique_id"] = security_capability_unique_id
        
        carrier_data = self.create_carrier_data_structure(
            carrier_info=carrier_info,
            vuln_list=[vuln_with_relations]
        )
        
        # 发送请求
        result = self.import_carrier_data([carrier_data], execute_release=execute_release)
        
        # 简化返回结果
        if result.success_count == 1:
            return {"code": 200, "msg": "Success", "msg_zh": "成功"}
        else:
            error_item = next((item for item in result.data if not item.success), None)
            if error_item:
                return {"code": 400, "msg": error_item.msg, "msg_zh": error_item.msg}
            return {"code": 400, "msg": "Failed to create vulnerability", "msg_zh": "创建漏洞失败"} 