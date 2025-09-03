#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 载体数据录入 API

提供载体维度的多数据录入功能，一次性录入载体、组件和漏洞数据。
这是创建组件和漏洞的主要接口。
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from ..models.response import BatchOperationResult
from ..exceptions import SARMValidationError

if TYPE_CHECKING:
    from ..client import SARMClient


class VulnDataImportAPI:
    """
    漏洞数据导入API

    提供漏洞维度的多数据录入功能，一次性录入载体、组件和漏洞数据。
    这是创建载体、组件和漏洞的推荐方式。
    """
    
    def __init__(self, client: 'SARMClient'):
        """
        初始化载体数据导入API

        Args:
            client: SARM客户端实例
        """
        self.client = client

    # 内部校验方法
    def _validate_carrier_block(self, carrier: Dict[str, Any], record_index: int) -> None:
        if not isinstance(carrier, dict):
            raise SARMValidationError(f"第{record_index}条数据的 carrier 必须是字典类型")
        if 'carrier_unique_id' not in carrier:
            raise SARMValidationError(f"第{record_index}条数据缺少 carrier.carrier_unique_id 必填字段")
        if not isinstance(carrier['carrier_unique_id'], str) or not carrier['carrier_unique_id'].strip():
            raise SARMValidationError(f"第{record_index}条数据的 carrier.carrier_unique_id 必须为非空字符串")

    def _validate_component_item(self, component: Dict[str, Any], record_index: int, list_index: int) -> None:
        if not isinstance(component, dict):
            raise SARMValidationError(f"第{record_index}条数据的 component_list[{list_index}] 必须是字典类型")
        # 必填字段
        for field in ('component_unique_id', 'component_name'):
            if field not in component:
                raise SARMValidationError(f"第{record_index}条数据的 component_list[{list_index}] 缺少必填字段 {field}")
            if not isinstance(component[field], str) or not component[field].strip():
                raise SARMValidationError(f"第{record_index}条数据的 component_list[{list_index}].{field} 必须为非空字符串")
        # 可选类型校验
        optional_string_fields = [
            'component_version', 'status', 'component_desc', 'asset_category', 'asset_type',
            'vendor', 'ecosystem', 'repository', 'supplier_name'
        ]
        for f in optional_string_fields:
            if f in component and component[f] is not None and not isinstance(component[f], str):
                raise SARMValidationError(f"第{record_index}条数据的 component_list[{list_index}].{f} 必须是字符串类型")
        if 'tags' in component:
            if not isinstance(component['tags'], list):
                raise SARMValidationError(f"第{record_index}条数据的 component_list[{list_index}].tags 必须是列表类型")
            for ti, tag in enumerate(component['tags']):
                if not isinstance(tag, str):
                    raise SARMValidationError(f"第{record_index}条数据的 component_list[{list_index}].tags[{ti}] 必须是字符串类型")
        if 'attributes' in component and component['attributes'] is not None and not isinstance(component['attributes'], dict):
            raise SARMValidationError(f"第{record_index}条数据的 component_list[{list_index}].attributes 必须是字典类型")

    def _validate_vuln_item(self, vuln: Dict[str, Any], record_index: int, list_index: int) -> None:
        if not isinstance(vuln, dict):
            raise SARMValidationError(f"第{record_index}条数据的 vuln_list[{list_index}] 必须是字典类型")
        # 必填字段
        required_string_fields = [
            'vuln_unique_id', 'severity', 'status', 'security_capability_unique_id'
        ]
        for f in required_string_fields:
            if f not in vuln:
                raise SARMValidationError(f"第{record_index}条数据的 vuln_list[{list_index}] 缺少必填字段 {f}")
            if not isinstance(vuln[f], str) or not vuln[f].strip():
                raise SARMValidationError(f"第{record_index}条数据的 vuln_list[{list_index}].{f} 必须为非空字符串")
        # 枚举校验
        severity_set = {"critical", "high", "medium", "low", "info"}
        status_set = {"open", "resolved", "in progress", "closed", "false positive", "risk accepted"}
        if vuln['severity'] not in severity_set:
            raise SARMValidationError(
                f"第{record_index}条数据的 vuln_list[{list_index}].severity 取值无效，必须为: {', '.join(sorted(severity_set))}")
        if vuln['status'] not in status_set:
            raise SARMValidationError(
                f"第{record_index}条数据的 vuln_list[{list_index}].status 取值无效，必须为: {', '.join(sorted(status_set))}")
        # 其余可选字段类型校验
        optional_string_fields = [
            'title', 'description', 'vulnerability_type', 'cwe_id', 'cve_id', 'impact',
            'report_url', 'discovery_at', 'owner_name'
        ]
        for f in optional_string_fields:
            if f in vuln and vuln[f] is not None and not isinstance(vuln[f], str):
                raise SARMValidationError(f"第{record_index}条数据的 vuln_list[{list_index}].{f} 必须是字符串类型")
        if 'tags' in vuln:
            if not isinstance(vuln['tags'], list):
                raise SARMValidationError(f"第{record_index}条数据的 vuln_list[{list_index}].tags 必须是列表类型")
            for ti, tag in enumerate(vuln['tags']):
                if not isinstance(tag, str):
                    raise SARMValidationError(f"第{record_index}条数据的 vuln_list[{list_index}].tags[{ti}] 必须是字符串类型")
        if 'vuln_identifiers' in vuln:
            if not isinstance(vuln['vuln_identifiers'], list):
                raise SARMValidationError(f"第{record_index}条数据的 vuln_list[{list_index}].vuln_identifiers 必须是列表类型")
            for vi, ident in enumerate(vuln['vuln_identifiers']):
                if not isinstance(ident, dict):
                    raise SARMValidationError(f"第{record_index}条数据的 vuln_list[{list_index}].vuln_identifiers[{vi}] 必须是字典类型")
                for f in ('type', 'id'):
                    if f in ident and ident[f] is not None and not isinstance(ident[f], str):
                        raise SARMValidationError(f"第{record_index}条数据的 vuln_list[{list_index}].vuln_identifiers[{vi}].{f} 必须是字符串类型")
        if 'cvss' in vuln:
            if not isinstance(vuln['cvss'], list):
                raise SARMValidationError(f"第{record_index}条数据的 vuln_list[{list_index}].cvss 必须是列表类型")
            for ci, c in enumerate(vuln['cvss']):
                if not isinstance(c, dict):
                    raise SARMValidationError(f"第{record_index}条数据的 vuln_list[{list_index}].cvss[{ci}] 必须是字典类型")
                for f in ('score', 'vector', 'version'):
                    if f in c and c[f] is not None and not isinstance(c[f], str):
                        raise SARMValidationError(f"第{record_index}条数据的 vuln_list[{list_index}].cvss[{ci}].{f} 必须是字符串类型")
        if 'context' in vuln:
            if not isinstance(vuln['context'], list):
                raise SARMValidationError(f"第{record_index}条数据的 vuln_list[{list_index}].context 必须是列表类型")
            for ci, ctx in enumerate(vuln['context']):
                if not isinstance(ctx, dict):
                    raise SARMValidationError(f"第{record_index}条数据的 vuln_list[{list_index}].context[{ci}] 必须是字典类型")
                # 基本字段
                for f in ('name', 'type', 'content'):
                    if f in ctx and ctx[f] is not None and not isinstance(ctx[f], str):
                        raise SARMValidationError(f"第{record_index}条数据的 vuln_list[{list_index}].context[{ci}].{f} 必须是字符串类型")
                if 'description' in ctx and ctx['description'] is not None and not isinstance(ctx['description'], str):
                    raise SARMValidationError(f"第{record_index}条数据的 vuln_list[{list_index}].context[{ci}].description 必须是字符串类型")
        if 'solution' in vuln:
            if not isinstance(vuln['solution'], list):
                raise SARMValidationError(f"第{record_index}条数据的 vuln_list[{list_index}].solution 必须是列表类型")
            for si, s in enumerate(vuln['solution']):
                if not isinstance(s, dict):
                    raise SARMValidationError(f"第{record_index}条数据的 vuln_list[{list_index}].solution[{si}] 必须是字典类型")
                for f in ('type', 'details', 'description'):
                    if f in s and s[f] is not None and not isinstance(s[f], str):
                        raise SARMValidationError(f"第{record_index}条数据的 vuln_list[{list_index}].solution[{si}].{f} 必须是字符串类型")
        if 'reference' in vuln:
            if not isinstance(vuln['reference'], list):
                raise SARMValidationError(f"第{record_index}条数据的 vuln_list[{list_index}].reference 必须是列表类型")
            for ri, r in enumerate(vuln['reference']):
                if not isinstance(r, dict):
                    raise SARMValidationError(f"第{record_index}条数据的 vuln_list[{list_index}].reference[{ri}] 必须是字典类型")
                for f in ('type', 'url'):
                    if f in r and r[f] is not None and not isinstance(r[f], str):
                        raise SARMValidationError(f"第{record_index}条数据的 vuln_list[{list_index}].reference[{ri}].{f} 必须是字符串类型")
        if 'component_unique_ids' in vuln:
            if not isinstance(vuln['component_unique_ids'], list):
                raise SARMValidationError(f"第{record_index}条数据的 vuln_list[{list_index}].component_unique_ids 必须是列表类型")
            for ui, uid in enumerate(vuln['component_unique_ids']):
                if not isinstance(uid, str):
                    raise SARMValidationError(f"第{record_index}条数据的 vuln_list[{list_index}].component_unique_ids[{ui}] 必须是字符串类型")

    def import_carrier_data(self, carrier_data_list: List[Dict[str, Any]], execute_release: bool = False):
        """
        载体维度多数据录入，一次性录入载体、组件和漏洞数据  

        Args:
            carrier_data_list: 载体数据列表
            execute_release: 是否直接发布

        Returns:
            BatchOperationResult: 批量操作结果
        """
        # 验证数据
        if not isinstance(carrier_data_list, list):
            raise SARMValidationError("carrier_data_list 必须是列表类型")
        if not carrier_data_list:
            raise SARMValidationError("carrier_data_list 不能为空")
        for idx, item in enumerate(carrier_data_list):
            if not isinstance(item, dict):
                raise SARMValidationError(f"第{idx+1}条数据必须是字典类型")
            if 'carrier' not in item:
                raise SARMValidationError(f"第{idx+1}条数据缺少必填字段 carrier")
            # 校验 carrier 块
            self._validate_carrier_block(item['carrier'], idx + 1)
            # 校验 component_list（可选）
            if 'component_list' in item and item['component_list'] is not None:
                if not isinstance(item['component_list'], list):
                    raise SARMValidationError(f"第{idx+1}条数据的 component_list 必须是列表类型")
                for ci, comp in enumerate(item['component_list']):
                    self._validate_component_item(comp, idx + 1, ci)
            # 校验 vuln_list（可选）
            if 'vuln_list' in item and item['vuln_list'] is not None:
                if not isinstance(item['vuln_list'], list):
                    raise SARMValidationError(f"第{idx+1}条数据的 vuln_list 必须是列表类型")
                for vi, vuln in enumerate(item['vuln_list']):
                    self._validate_vuln_item(vuln, idx + 1, vi)

        response = self.client.post('/api/insert/insert_carrier_vuln', data=carrier_data_list, execute_release=execute_release)
        
        # 处理响应
        # result = BatchOperationResult(**response.get('data', {}))
        return response
    
    def create_carrier_data_structure(
        self,
        carrier: Dict[str, Any],
        component_list: Optional[List[Dict[str, Any]]] = None,
        vuln_list: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        创建标准的漏洞数据结构

        Args:
            carrier: 载体基础信息
            component_list: 组件列表
            vuln_list: 漏洞列表

        Returns:
            Dict[str, Any]: 标准漏洞数据结构
        """
        # 验证载体信息
        if not isinstance(carrier, dict):
            raise SARMValidationError("carrier must be a dictionary")
        
        if 'carrier_unique_id' not in carrier:
            raise SARMValidationError("carrier must contain 'carrier_unique_id'")
        
        # 构建标准数据结构
        carrier_data: Dict[str, Any] = {
            "carrier": carrier
        }

        if component_list:
            carrier_data["component_list"] = component_list
        
        if vuln_list:
            carrier_data["vuln_list"] = vuln_list
        
        return carrier_data
    
    # def create_issue(
    #     self,
    #     carrier_unique_id: str,
    #     issue_data: Dict[str, Any],
    #     execute_release: bool = False
    # ) -> Dict[str, Any]:
    #     """
    #     创建安全问题并关联到指定载体

    #     Args:
    #         carrier_unique_id: 载体唯一ID
    #         issue_data: 安全问题数据
    #         execute_release: 是否直接发布

    #     Returns:
    #         Dict[str, Any]: 操作结果
    #     """
    #     # 验证数据
    #     if not carrier_unique_id:
    #         raise SARMValidationError("carrier_unique_id cannot be empty")
        
    #     if not isinstance(issue_data, dict):
    #         raise SARMValidationError("issue_data must be a dictionary")
        
    #     if 'issue_unique_id' not in issue_data:
    #         raise SARMValidationError("issue_data must contain 'issue_unique_id'")

    #     # 构建载体数据结构
    #     carrier_info = {
    #         "carrier_unique_id": carrier_unique_id
    #     }
        
    #     carrier_data = self.create_carrier_data_structure(
    #         carrier=carrier_info,
    #         vuln_list=[issue_data]
    #     )
        
    #     # 发送请求
    #     result = self.import_carrier_data([carrier_data], execute_release=execute_release)
        
    #     # 简化返回结果
    #     if result.success_count == 1:
    #         return {"code": 200, "msg": "Success", "msg_zh": "成功"}
    #     else:
    #         error_item = next((item for item in result.data if not item.success), None)
    #         if error_item:
    #             return {"code": 400, "msg": error_item.msg, "msg_zh": error_item.msg}
    #         return {"code": 400, "msg": "Failed to create issue", "msg_zh": "创建安全问题失败"}
    
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
            carrier=carrier_info,
            component_list=[component_with_capability]
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
            return {"code": 400, "msg": "Failed to create component", "msg_zh": "创建组件失败"}
    
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
            carrier=carrier_info,
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