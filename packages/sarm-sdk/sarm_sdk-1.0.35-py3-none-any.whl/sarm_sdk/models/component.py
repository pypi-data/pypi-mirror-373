#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 软件成分数据模型

定义软件成分相关的数据结构。
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ComponentInsert(BaseModel):
    """软件成分创建模型"""
    component_unique_id: str = Field(..., description="成分唯一标识")
    component_name: str = Field(..., description="应用成分名称")
    component_version: Optional[str] = Field(None, description="应用成分版本")
    status: str = Field(..., description="状态(active,approved,deprecated,eol)")
    component_desc: Optional[str] = Field(None, description="描述")
    asset_category: Optional[str] = Field(None, description="大分类")
    asset_type: Optional[str] = Field(None, description="子分类")
    vendor: Optional[str] = Field(None, description="供应商/来源")
    ecosystem: Optional[str] = Field(None, description="生态")
    repository: Optional[str] = Field(None, description="仓库")
    tags: Optional[List[str]] = Field(default_factory=list, description="标签")
    supplier_name: Optional[str] = Field(None, description="供应商名称")
    attributes: Optional[Dict[str, Any]] = Field(default_factory=dict, description="用于存储不同asset_type异性数据")
    vuln_unique_ids: Optional[List[str]] = Field(default_factory=list, description="成分关联漏洞唯一id")


class ComponentUpdate(BaseModel):
    """软件成分更新模型"""
    component_unique_id: str = Field(..., description="成分唯一标识")
    component_name: Optional[str] = Field(None, description="应用成分名称")
    component_version: Optional[str] = Field(None, description="应用成分版本")
    status: Optional[str] = Field(None, description="状态")
    component_desc: Optional[str] = Field(None, description="描述")
    asset_category: Optional[str] = Field(None, description="大分类")
    asset_type: Optional[str] = Field(None, description="子分类")
    vendor: Optional[str] = Field(None, description="供应商/来源")
    ecosystem: Optional[str] = Field(None, description="生态")
    repository: Optional[str] = Field(None, description="仓库")
    tags: Optional[List[str]] = Field(None, description="标签")
    supplier_name: Optional[str] = Field(None, description="供应商名称")
    component_closed_source_software_id: Optional[int] = Field(None, description="闭源软件成分关联表id")
    attributes: Optional[Dict[str, Any]] = Field(None, description="用于存储不同asset_type异性数据")
    contract_file_sha256: Optional[str] = Field(None, description="对应组件合同表文件哈希") 