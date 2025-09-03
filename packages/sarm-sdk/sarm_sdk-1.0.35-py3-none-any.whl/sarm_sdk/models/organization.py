#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 组织架构数据模型

定义组织架构相关的数据结构。
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class OrganizeInsert(BaseModel):
    """组织创建数据模型"""
    organize_name: str = Field(..., description="组织名称")
    organize_unique_id: str = Field(..., description="组织唯一ID")
    organize_punique_id: str = Field(..., description="上级组织唯一ID，顶级组织使用'0'")
    organize_leader_unique_id: Optional[str] = Field(None, description="组织负责人唯一ID")
    desc: Optional[str] = Field(None, description="组织描述")
    # status: str = Field(..., description="组织状态(active、maintenance、retired)")
    dep_id: Optional[str] = Field(None, description="外部部门ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "organize_name": "技术研发中心",
                "organize_unique_id": "1930296734248865792",
                "organize_punique_id": "1930296726111916032",
                "organize_leader_unique_id": "1932296734248865792",
                "desc": "负责公司核心技术平台研发、基础设施建设和技术创新",
                "dep_id": "DEPT002"
            }
        }


class Organization(BaseModel):
    """组织完整信息模型"""
    organize_id: Optional[int] = Field(None, description="组织ID（系统生成）")
    organize_name: str = Field(..., description="组织名称")
    organize_unique_id: str = Field(..., description="组织唯一ID")
    organize_punique_id: str = Field(..., description="上级组织唯一ID")
    organize_leader_unique_id: Optional[str] = Field(None, description="组织负责人唯一ID")
    desc: Optional[str] = Field(None, description="组织描述")
    # status: str = Field(..., description="组织状态")
    dep_id: Optional[str] = Field(None, description="外部部门ID")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    
    # 扩展属性（运行时计算）
    children: Optional[List['Organization']] = Field(None, description="子组织列表")
    level: Optional[int] = Field(None, description="组织层级（0为顶级）")
    full_path: Optional[str] = Field(None, description="完整路径")


class OrganizeUser(BaseModel):
    """组织用户模型"""
    organize_user_unique_id: str = Field(..., description="用户唯一ID")
    organize_user_name: str = Field(..., description="用户名")
    organize_user_enterprise_email: str = Field(..., description="企业邮箱")
    organize_user_employee_no: Optional[str] = Field(None, description="工号")
    organize_nick_name: Optional[str] = Field(None, description="用户姓名")
    organize_user_avatar: Optional[str] = Field(None, description="头像地址")
    organize_user_mobile: Optional[str] = Field(None, description="手机号码")
    organize_user_job_title: Optional[str] = Field(None, description="职务")
    organize_unique_ids: Optional[List[str]] = Field(None, description="关联组织唯一ID列表")
    password: str = Field(..., description="用户密码")
    source: str = Field(..., description="来源：ldap-ad 或 sys")
    
    class Config:
        json_schema_extra = {
            "example": {
                "organize_user_unique_id": "user-001",
                "organize_user_name": "zhang.san",
                "organize_user_enterprise_email": "zhang.san@company.com",
                "organize_user_employee_no": "EMP001",
                "organize_nick_name": "张三",
                "organize_user_mobile": "13800138000",
                "organize_user_job_title": "高级工程师",
                "organize_union_ids": ["1930296734248865792"],
                "password": "password123",
                "source": "sys"
            }
        }


class OrganizationTree(BaseModel):
    """组织架构树模型"""
    organize_unique_id: str = Field(..., description="组织唯一ID")
    organize_name: str = Field(..., description="组织名称")
    level: int = Field(..., description="组织层级")
    children: List['OrganizationTree'] = Field(default_factory=list, description="子组织列表")
    user_count: Optional[int] = Field(None, description="用户数量")
    
    def flatten(self) -> List['OrganizationTree']:
        """扁平化组织树"""
        result = [self]
        for child in self.children:
            result.extend(child.flatten())
        return result
    
    def find_by_id(self, unique_id: str) -> Optional['OrganizationTree']:
        """根据ID查找组织节点"""
        if self.organize_unique_id == unique_id:
            return self
        for child in self.children:
            found = child.find_by_id(unique_id)
            if found:
                return found
        return None


# 更新前向引用
Organization.update_forward_refs()
OrganizationTree.update_forward_refs() 