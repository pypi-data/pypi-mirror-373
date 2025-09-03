#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 应用载体数据模型

定义应用载体相关的数据结构。
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class CarrierType(str, Enum):
    """载体类型枚举"""
    CODE_REPO = "code_repo"
    SERVICE_ADDRESS = "service_address"

class Carrier(BaseModel):
    """应用载体完整信息模型"""
    carrier_id: Optional[int] = Field(None, description="载体ID（系统生成）")
    carrier_unique_id: str = Field(..., description="应用载体唯一ID")
    application_unique_id: Optional[List[str]] = Field(None, description="应用唯一ID列表")
    carrier_type: str = Field(..., description="应用载体类型")
    name: str = Field(..., description="应用载体名称")
    description: Optional[str] = Field(None, description="应用载体的描述")
    source: Optional[str] = Field(None, description="应用载体信息的来源")
    tags: Optional[List[str]] = Field(None, description="标签")
    protocol: Optional[str] = Field(None, description="协议类型")
    ip: Optional[str] = Field(None, description="ip地址")
    port: Optional[int] = Field(None, description="端口号")
    path: Optional[str] = Field(None, description="URL路径")
    domain: Optional[str] = Field(None, description="域名")
    internet_ip: Optional[str] = Field(None, description="互联网IP")
    nat_ip: Optional[str] = Field(None, description="NAT IP")
    internal_ip: str = Field(..., description="内网IP")
    repo_namespace: Optional[str] = Field(None, description="仓库命名空间/组织")
    repo_name: Optional[str] = Field(None, description="仓库名称")
    repo_url: Optional[str] = Field(None, description="仓库URL")
    branch: Optional[str] = Field(None, description="git branch")
    carrier_owner_unique_id: Optional[str] = Field(None, description="负责人唯一ID")
    security_capability_id: Optional[int] = Field(None, description="安全能力ID")
    source_type: Optional[str] = Field(None, description="来源类型")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    
    @property
    def is_code_repository(self) -> bool:
        """是否为代码仓库类型"""
        return self.carrier_type == CarrierType.CODE_REPO.value
    
    @property
    def is_service_address(self) -> bool:
        """是否为服务地址类型"""
        return self.carrier_type == CarrierType.SERVICE_ADDRESS.value
    
    @property
    def full_url(self) -> Optional[str]:
        """完整URL（仅服务地址类型）"""
        if not self.is_service_address:
            return None
        if self.domain:
            url = f"{self.protocol or 'http'}://{self.domain}"
            if self.port and self.port not in [80, 443]:
                url += f":{self.port}"
            if self.path:
                url += self.path
            return url
        return None 


class CarrierInsert(BaseModel):
    carrier: Carrier
    app_ids: Optional[List[str]] = None
    organize_user_unique_id: Optional[str] = None

class CarrierCreationPayload(BaseModel):
    carrier: Carrier
    app_ids: Optional[List[str]] = None
    organize_user_unique_id: Optional[str] = None