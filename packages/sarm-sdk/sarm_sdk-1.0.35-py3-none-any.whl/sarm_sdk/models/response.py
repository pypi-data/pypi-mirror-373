#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 响应数据模型

定义API响应的数据结构，包括成功响应、错误响应、批量操作结果等。
"""

from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field


class ValidationError(BaseModel):
    """参数验证错误详情"""
    field: str = Field(..., description="出错的字段名")
    message: str = Field(..., description="验证错误消息")
    value: Optional[str] = Field(None, description="错误的字段值")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    data: Optional[str] = Field(None, description="错误相关数据")
    code: str = Field(..., description="错误代码")
    msg_en: Optional[str] = Field(None, description="英文错误消息")
    msg_zh: str = Field(..., description="中文错误消息")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详细信息")


class SuccessResponse(BaseModel):
    """成功响应模型"""
    data: Optional[Union[str, Dict[str, Any], List[Any]]] = Field(None, description="响应数据")
    code: Union[str, int] = Field(..., description="响应代码")
    msg_en: Optional[str] = Field(None, description="英文消息")
    msg_zh: Optional[str] = Field(None, description="中文消息")


class BatchOperationItem(BaseModel):
    """批量操作结果项"""
    unique_id: str = Field(..., description="操作对象的唯一ID")
    name: Optional[str] = Field(None, description="操作对象的名称")
    success: bool = Field(..., description="操作是否成功")
    msg: Optional[str] = Field(None, description="操作结果消息")


class BatchOperationSummary(BaseModel):
    """批量操作汇总信息"""
    total: int = Field(..., description="总数量")
    success: int = Field(..., description="成功数量")
    failed: int = Field(..., description="失败数量")


class BatchOperationResult(BaseModel):
    """批量操作结果模型"""
    data: List[BatchOperationItem] = Field(..., description="操作结果详情列表")
    code: int = Field(..., description="响应状态码")
    summary: Optional[BatchOperationSummary] = Field(None, description="操作汇总信息")
    
    @property
    def total_count(self) -> int:
        """总数量"""
        return self.summary.total if self.summary else len(self.data)
    
    @property
    def success_count(self) -> int:
        """成功数量"""
        return self.summary.success if self.summary else sum(1 for item in self.data if item.success)
    
    @property
    def failed_count(self) -> int:
        """失败数量"""
        return self.summary.failed if self.summary else sum(1 for item in self.data if not item.success)
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        total = self.total_count
        return self.success_count / total if total > 0 else 0.0
    
    @property
    def failed_items(self) -> List[BatchOperationItem]:
        """失败的项目列表"""
        return [item for item in self.data if not item.success]
    
    @property
    def success_items(self) -> List[BatchOperationItem]:
        """成功的项目列表"""
        return [item for item in self.data if item.success]


class PaginatedResponse(BaseModel):
    """分页响应模型"""
    data: List[Any] = Field(..., description="数据列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    limit: int = Field(..., description="每页记录数")
    
    @property
    def total_pages(self) -> int:
        """总页数"""
        return (self.total + self.limit - 1) // self.limit
    
    @property
    def has_next(self) -> bool:
        """是否有下一页"""
        return self.page < self.total_pages
    
    @property
    def has_prev(self) -> bool:
        """是否有上一页"""
        return self.page > 1 