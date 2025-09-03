#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 安全能力数据模型

定义安全能力相关的数据结构。
"""

from typing import Optional
from pydantic import BaseModel, Field, validator
from enum import Enum


class SecurityCapabilityType(str, Enum):
    """安全能力类型枚举"""
    SOFTWARE_COMPOSITION_ANALYSIS = "Software Composition Analysis"
    STATIC_APPLICATION_SECURITY_TESTING = "Static Application Security Testing"
    DYNAMIC_APPLICATION_SECURITY_TESTING = "Dynamic Application Security Testing"
    INTERACTIVE_APPLICATION_SECURITY_TESTING = "Interactive Application Security Testing"
    SECRETS_DETECTION = "Secrets Detection"
    INFRASTRUCTURE_AS_CODE_SCAN = "Infrastructure as Code Scan"
    CONTAINER_IMAGE_SECURITY_SCAN = "Container Image Security Scan"
    API_SECURITY_TESTING = "API Security Testing"
    EXTERNAL_ATTACK_SURFACE_MANAGEMENT = "External Attack Surface Management"
    WEB_APPLICATION_FIREWALL = "Web Application Firewall"
    RUNTIME_APPLICATION_SELF_PROTECTION = "Runtime Application Self-Protection"
    VULNERABILITY_INTELLIGENCE = "Vulnerability Intelligence"
    OTHERS = "Others"


class SecurityCapability(BaseModel):
    """安全能力数据模型"""
    capability_name: str = Field(..., description="安全能力名称")
    capability_unique_id: str = Field(..., description="安全能力唯一ID")
    capability_desc: Optional[str] = Field(None, description="安全能力描述")
    missing_rate_value: Optional[float] = Field(None, description="缺失率值", ge=0, le=1)
    capability_type: str = Field(..., description="安全能力类型")
    factory_log_id: str = Field(..., description="任务id")

    @validator('missing_rate_value')
    def validate_missing_rate(cls, v):
        if v is not None and not 0 <= v <= 1:
            raise ValueError('缺失率值必须在0.0-1.0之间')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "capability_name": "SonarQube代码安全扫描",
                "capability_unique_id": "SAST-SONAR-001",
                "capability_desc": "基于SonarQube的静态代码安全分析能力",
                "missing_rate_value": 0.15,
                "capability_type": "Static Application Security Testing"
            }
        }
