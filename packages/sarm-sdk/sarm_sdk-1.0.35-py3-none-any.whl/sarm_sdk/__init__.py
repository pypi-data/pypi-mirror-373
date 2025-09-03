#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK - 安全资产与风险管理平台SDK

提供对SARM平台API的访问能力，用于管理组织、业务系统、应用、载体、安全问题、组件和漏洞等资源。

主要功能：
- 组织架构管理
- 业务系统管理  
- 应用载体管理
- 软件成分管理
- 漏洞管理
- 安全问题管理
- 安全能力管理

使用示例：
    >>> from sarm_sdk import SARMClient
    >>> client = SARMClient(
    ...     base_url="https://api.platform.com",
    ...     token="your-bearer-token"
    ... )
    >>> organizations = client.organizations.create_batch([...])
"""

__version__ = "1.0.35"
__author__ = "Murphysec Team"
__email__ = "developer@murphysec.com"

from .client import SARMClient
from .plugin import BasePlugin
from .exceptions import (
    SARMException,
    SARMAPIError,
    SARMValidationError,
    SARMNetworkError,
    SARMAuthenticationError,
    SARMAuthorizationError,
    SARMServerError,
)

# 导出主要类和异常
__all__ = [
    "SARMClient",
    "BasePlugin",
    "SARMException", 
    "SARMAPIError",
    "SARMValidationError",
    "SARMNetworkError",
    "SARMAuthenticationError",
    "SARMAuthorizationError",
    "SARMServerError",
] 