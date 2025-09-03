#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 异常类定义

基于平台 API 的错误响应规范设计的异常体系。
"""

from typing import Optional, Dict, Any, List


class SARMException(Exception):
    """SARM SDK 基础异常类"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class SARMAPIError(SARMException):
    """API 调用错误基类"""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        msg_en: Optional[str] = None,
        msg_zh: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.status_code = status_code
        self.error_code = error_code
        self.msg_en = msg_en
        self.msg_zh = msg_zh
        self.response_data = response_data or {}
    
    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code:
            parts.append(f"(HTTP {self.status_code})")
        if self.error_code:
            parts.append(f"[{self.error_code}]")
        return " ".join(parts)


class SARMValidationError(SARMAPIError):
    """参数验证错误 (HTTP 400)"""
    
    def __init__(
        self,
        message: str = "请求参数验证失败",
        validation_errors: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ):
        super().__init__(message, status_code=400, **kwargs)
        self.validation_errors = validation_errors or []
    
    @property
    def field_errors(self) -> Dict[str, List[str]]:
        """获取按字段分组的验证错误"""
        errors = {}
        for error in self.validation_errors:
            field = error.get("field", "unknown")
            message = error.get("message", "验证失败")
            if field not in errors:
                errors[field] = []
            errors[field].append(message)
        return errors


class SARMNetworkError(SARMException):
    """网络连接错误"""
    
    def __init__(self, message: str = "网络连接失败", original_error: Optional[Exception] = None):
        super().__init__(message)
        self.original_error = original_error


class SARMAuthenticationError(SARMAPIError):
    """认证失败错误 (HTTP 401)"""
    
    def __init__(self, message: str = "认证失败，请检查Token是否有效", **kwargs):
        super().__init__(message, status_code=401, **kwargs)


class SARMAuthorizationError(SARMAPIError):
    """权限不足错误 (HTTP 403)"""
    
    def __init__(self, message: str = "权限不足，无法执行此操作", **kwargs):
        super().__init__(message, status_code=403, **kwargs)


class SARMServerError(SARMAPIError):
    """服务器内部错误 (HTTP 500)"""
    
    def __init__(self, message: str = "服务器内部错误，请稍后重试", **kwargs):
        super().__init__(message, status_code=500, **kwargs)


class SARMBatchOperationError(SARMAPIError):
    """批量操作部分失败错误"""
    
    def __init__(
        self,
        message: str,
        total: int,
        success: int,
        failed: int,
        failed_items: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.total = total
        self.success = success
        self.failed = failed
        self.failed_items = failed_items or []
    
    def __str__(self) -> str:
        return f"{self.message} (总数: {self.total}, 成功: {self.success}, 失败: {self.failed})"


def create_exception_from_response(response_data: Dict[str, Any], status_code: int) -> SARMAPIError:
    """根据 API 响应创建相应的异常对象"""
    
    error_code = response_data.get("code", str(status_code))
    msg_zh = response_data.get("msg_zh", "")
    msg_en = response_data.get("msg_en", "")
    details = response_data.get("details", {})
    
    # 使用中文消息作为主要错误消息，英文作为备选
    message = msg_zh or msg_en or f"API调用失败 (HTTP {status_code})"
    
    # 根据 HTTP 状态码选择异常类型
    if status_code == 400:
        # 检查是否包含验证错误详情
        validation_errors = None
        if isinstance(details, dict) and "errors" in details:
            validation_errors = details["errors"]
        return SARMValidationError(
            message=message,
            validation_errors=validation_errors,
            error_code=error_code,
            msg_en=msg_en,
            msg_zh=msg_zh,
            details=details,
            response_data=response_data
        )
    
    elif status_code == 401:
        return SARMAuthenticationError(
            message=message,
            error_code=error_code,
            msg_en=msg_en,
            msg_zh=msg_zh,
            details=details,
            response_data=response_data
        )
    
    elif status_code == 403:
        return SARMAuthorizationError(
            message=message,
            error_code=error_code,
            msg_en=msg_en,
            msg_zh=msg_zh,
            details=details,
            response_data=response_data
        )
    
    elif status_code >= 500:
        return SARMServerError(
            message=message,
            error_code=error_code,
            msg_en=msg_en,
            msg_zh=msg_zh,
            details=details,
            response_data=response_data
        )
    
    else:
        return SARMAPIError(
            message=message,
            status_code=status_code,
            error_code=error_code,
            msg_en=msg_en,
            msg_zh=msg_zh,
            details=details,
            response_data=response_data
        ) 