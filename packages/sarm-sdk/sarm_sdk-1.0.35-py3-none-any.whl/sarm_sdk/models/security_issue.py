#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 安全问题数据模型

定义安全问题相关的数据结构。
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class SecurityIssueInsert(BaseModel):
    """安全问题创建模型"""
    issue_unique_id: str = Field(..., description="安全问题唯一ID")
    issue_owner_unique_id: Optional[str] = Field(None, description="安全问题负责人唯一ID")
    issue_status: Optional[str] = Field(None, description="安全问题处置状态(open, close)")
    issue_title: Optional[str] = Field(None, description="安全问题标题")
    issue_level: Optional[str] = Field(None, description="安全问题级别(critical-严重 high-高 medium-中 low-低)")
    issue_desc: Optional[str] = Field(None, description="安全问题描述")
    solution: Optional[str] = Field(None, description="安全问题修复方案")
    discovery_at: Optional[datetime] = Field(None, description="发现时间")



class SecurityIssueUpdate(BaseModel):
    """安全问题更新模型"""
    issue_unique_id: str = Field(..., description="安全问题唯一ID")
    issue_owner_unique_id: Optional[str] = Field(None, description="安全问题负责人唯一ID")
    issue_status: Optional[str] = Field(None, description="安全问题处置状态(open, close)")
    issue_title: Optional[str] = Field(None, description="安全问题标题")
    issue_level: Optional[str] = Field(None, description="安全问题级别(critical-严重 high-高 medium-中 low-低)")
    issue_desc: Optional[str] = Field(None, description="安全问题描述")
    solution: Optional[str] = Field(None, description="安全问题修复方案")
    discovery_at: Optional[datetime] = Field(None, description="发现时间")