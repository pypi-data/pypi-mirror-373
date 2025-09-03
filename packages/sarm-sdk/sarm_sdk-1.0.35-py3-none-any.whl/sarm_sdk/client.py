#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 客户端

提供统一的API访问入口。
"""

import json
import requests
from typing import Dict, Any, Optional, List, Union
import time
from urllib.parse import urljoin
from .exceptions import (
    SARMNetworkError,
    SARMAPIError,
    SARMAuthenticationError,
    SARMValidationError
)
from sarm_sdk.apis.application import ApplicationAPI
from sarm_sdk.apis.business_system import BusinessSystemAPI
from sarm_sdk.apis.carrier import CarrierAPI
from sarm_sdk.apis.carrier_data_import import VulnDataImportAPI as CarrierDataImportAPI
from sarm_sdk.apis.issue_data_import import IssueDataImportAPI
from sarm_sdk.apis.component import ComponentAPI
from sarm_sdk.apis.organization import OrganizationAPI
from sarm_sdk.apis.organize_user import OrganizeUserAPI
from sarm_sdk.apis.security_capability import SecurityCapabilityAPI
from sarm_sdk.apis.security_issue import SecurityIssueAPI
from sarm_sdk.apis.vulnerability import VulnerabilityAPI
from sarm_sdk.apis.common import CommonAPI


class SARMClient:
    """SARM API 客户端"""
    
    def __init__(
        self,
        base_url: str,
        token: str,
        factory_log_id: str = "",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        初始化客户端
        
        Args:
            base_url: API 基础URL
            token: 认证令牌
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            retry_delay: 重试间隔（秒）
        """
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.factory_log_id=factory_log_id
        # 设置默认请求头
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # 配置HTTP会话
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # 连接池配置
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=0  # 我们手动处理重试
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        # 初始化API模块
        self._init_apis()
    
    def _init_apis(self):
        """初始化所有API模块"""
        # 原有API - 使用正确的参数
        self.organizations = OrganizationAPI(self)
        self.carriers = CarrierAPI(self)
        self.security_capabilities = SecurityCapabilityAPI(self)
        self.issue_data_import = IssueDataImportAPI(self)
        self.carrier_data_import = CarrierDataImportAPI(self)
        self.common = CommonAPI(self)
        # 恢复的API
        self.vulnerabilities = VulnerabilityAPI(self)
        self.security_issues = SecurityIssueAPI(self)
        self.components = ComponentAPI(self)
        
        # 新增的API
        self.business_systems = BusinessSystemAPI(self)
        self.applications = ApplicationAPI(self)
        self.organize_users = OrganizeUserAPI(self)
    
    def _get_full_url(self, endpoint: str) -> str:
        """获取完整的URL"""
        return urljoin(self.base_url, endpoint.lstrip('/'))
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], List[Any]]] = None,
        params: Optional[Dict[str, Any]] = None,
        execute_release: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法
            endpoint: API端点
            data: 请求数据
            params: URL参数
            execute_release: 是否直接发布
            
        Returns:
            响应数据
            
                    Raises:
                SARMAPIError: API错误
                SARMNetworkError: 连接/网络错误
        """
        url = self._get_full_url(endpoint)
        
        # 设置特殊头部
        headers = self.headers.copy()
        if execute_release is not None:
            headers['Execute-Release'] = 'true' if execute_release else 'false'
        headers['factory_log_id'] = self.factory_log_id
        # 准备请求参数
        request_kwargs = {
            'timeout': self.timeout,
            'headers': headers
        }
        
        if params:
            request_kwargs['params'] = params
        
        if data is not None:
            if method.upper() in ['POST', 'PUT', 'PATCH', 'DELETE']:
                request_kwargs['json'] = data
        
        # 执行请求（带重试）
        last_exception: Optional[SARMNetworkError] = None
        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.request(method, url, **request_kwargs)
                
                # 处理响应
                return self._handle_response(response)
                
            except requests.exceptions.Timeout as e:
                last_exception = SARMNetworkError(f"请求超时: {e}")
                
            except requests.exceptions.ConnectionError as e:
                last_exception = SARMNetworkError(f"连接错误: {e}")
                
            except requests.exceptions.RequestException as e:
                last_exception = SARMNetworkError(f"请求异常: {e}")
            
            # 如果不是最后一次尝试，等待后重试
            if attempt < self.max_retries:
                time.sleep(self.retry_delay * (2 ** attempt))  # 指数退避
        
        # 所有重试都失败了
        if last_exception:
            raise last_exception
        raise SARMNetworkError("Request failed after all retries.")
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        处理HTTP响应
        
        Args:
            response: HTTP响应对象
            
        Returns:
            解析后的响应数据
            
        Raises:
            SARMAPIError: API错误
            SARMAuthenticationError: 认证错误
        """
        # 检查HTTP状态码
        if response.status_code == 401:
            raise SARMAuthenticationError("认证失败，请检查token是否正确")
        
        # 尝试解析JSON响应
        try:
            data = response.json()
        except ValueError:
            # 如果不是JSON响应，检查状态码
            if 200 <= response.status_code < 300:
                return {"code": response.status_code, "data": response.text}
            else:
                raise SARMAPIError(
                    f"API请求失败 (HTTP {response.status_code}): {response.text}",
                    status_code=response.status_code
                )
        
        # 检查业务状态码
        if not (200 <= response.status_code < 300):
            # 构建详细的错误信息
            error_details = []
            
            # 基础错误信息
            base_msg = data.get('msg_zh', data.get('message', f"API错误 (HTTP {response.status_code})"))
            error_details.append(base_msg)
            
            # 添加英文错误信息（如果有）
            if data.get('msg_en') and data.get('msg_en') != base_msg:
                error_details.append(f"English: {data.get('msg_en')}")
            
            # 添加详细错误描述（如果有）
            if data.get('detail'):
                error_details.append(f"详细信息: {data.get('detail')}")
            
            # 添加错误代码（如果有）
            if data.get('code') and data.get('code') != response.status_code:
                error_details.append(f"错误代码: {data.get('code')}")
            
            # 如果有其他错误数据，也包含进来
            if 'err_data_list' in data and data['err_data_list']:
                error_details.append(f"错误数据: {len(data['err_data_list'])} 项")
                for i, err_item in enumerate(data['err_data_list'][:3]):  # 只显示前3个
                    if isinstance(err_item, dict) and 'error' in err_item:
                        error_details.append(f"  [{i+1}] {err_item.get('error', 'Unknown error')}")
                if len(data['err_data_list']) > 3:
                    error_details.append(f"  ... 还有 {len(data['err_data_list']) - 3} 个错误")
            
            # 合并所有错误信息
            detailed_error_msg = " | ".join(error_details)
            
            raise SARMAPIError(detailed_error_msg, status_code=response.status_code, response_data=data)
        
        return data
    
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """发送GET请求"""
        # GET请求可能需要在body中传参（某些API的设计）
        if data:
            return self._make_request('POST', endpoint, data={"page": 1, "limit": 50, **data})
        return self._make_request('GET', endpoint, params=params)
    
    def post(
        self,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], List[Dict[str, Any]], List[str]]] = None,
        params: Optional[Dict[str, Any]] = None,
        execute_release: Optional[bool] = None
    ) -> Dict[str, Any]:
        """发送POST请求"""
        return self._make_request('POST', endpoint, data=data, params=params, execute_release=execute_release)
    
    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        execute_release: Optional[bool] = None
    ) -> Dict[str, Any]:
        """发送PUT请求"""
        return self._make_request('PUT', endpoint, data=data, params=params, execute_release=execute_release)
    
    def delete(
        self,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], List[str]]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """发送DELETE请求"""
        return self._make_request('DELETE', endpoint, data=data, params=params)
    
    def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        execute_release: Optional[bool] = None
    ) -> Dict[str, Any]:
        """发送PATCH请求"""
        return self._make_request('PATCH', endpoint, data=data, params=params, execute_release=execute_release)
    
    def test_connection(self) -> bool:
        """
        测试连接是否正常
        
        Returns:
            连接是否成功
        """
        try:
            # 使用组织列表接口测试连接
            response = self.get('/api/organize/openapi/get', params={'page': 1, 'limit': 1})
            return True
        except Exception as e:
            print(f"连接测试失败: {e}")
            return False
    
    def get_api_info(self) -> Dict[str, Any]:
        """
        获取API信息
        
        Returns:
            包含平台信息的字典
        """
        return {
            'base_url': self.base_url,
            'sdk_version': '1.0.0',
            'connection_status': self.test_connection(),
            'endpoints': {
                'organizations': '/api/organize/',
                'carriers': '/api/carrier/',
                'security_capabilities': '/api/security_capability/',
                'issue_data_import': '/api/insert/insert_carrier_issue'
            }
        }
    
    def close(self):
        """关闭HTTP会话"""
        if self.session:
            self.session.close() 