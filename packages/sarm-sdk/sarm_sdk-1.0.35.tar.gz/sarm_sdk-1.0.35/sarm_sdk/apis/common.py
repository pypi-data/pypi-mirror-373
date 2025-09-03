#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 应用载体 API

提供应用载体相关的API操作。
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from ..models.carrier import CarrierInsert, Carrier
from ..models.response import BatchOperationResult
from ..exceptions import SARMValidationError

if TYPE_CHECKING:
    from ..client import SARMClient


class CommonAPI:
    def __init__(self, client: 'SARMClient'):
        self.client = client

    def statistics(
        self,
        data: Dict[str,any],
        statistical_info: Dict[str, Any],
        critical_data_count: int = 0,
        data_type: str = "running",
    ) -> Dict[str, Any]:
        """
        上报工厂统计信息

        Args:
            statistical_info: 统计信息对象（必填）
            factory_id: 工厂ID（必填）
            critical_data_count: 插入核心数据数量（可选，默认0）
            data_type: 数据类型（必填，取值：running 或 test）
            data:实际发送样例(必填)

        Returns:
            响应数据
        """
        # 校验
        # if not isinstance(statistical_info, dict) or not statistical_info:
        #     raise SARMValidationError("statistical_info 必须为非空对象")

        if not isinstance(critical_data_count, int) or critical_data_count < 0:
            raise SARMValidationError("critical_data_count 必须为大于等于0的整数")

        if not isinstance(data_type, str):
            raise SARMValidationError("data_type 必须为字符串")
        allowed_types = {"running", "test"}
        if data_type not in allowed_types:
            raise SARMValidationError(f"data_type 必须为以下值之一: {', '.join(sorted(allowed_types))}")

        payload = {
            "statistical_info": statistical_info,
            "critical_data_count": critical_data_count,
            "data_type": data_type,
            "factory_id": self.client.factory_log_id,
            "data":data
        }

        return self.client.post('/api/factory/statistics', data=payload)

    def create_factory(
        self,
        factory_name: str,
        plug_type: str,
        plug_data_type: str,
        plug_market_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        创建工厂任务

        Args:
            factory_name: 任务名称（必填）
            plug_type: 任务依据插件类型（必填）
            plug_data_type: 任务依据插件数据类型（必填）
            plug_market_id: 任务依据插件id（可选）

        Returns:
            响应数据
        """
        # 校验
        if not isinstance(factory_name, str) or not factory_name.strip():
            raise SARMValidationError("factory_name 必须为非空字符串")

        if not isinstance(plug_type, str) or not plug_type.strip():
            raise SARMValidationError("plug_type 必须为非空字符串")

        if not isinstance(plug_data_type, str) or not plug_data_type.strip():
            raise SARMValidationError("plug_data_type 必须为非空字符串")

        if plug_market_id is not None and (not isinstance(plug_market_id, str) or not plug_market_id.strip()):
            raise SARMValidationError("plug_market_id 必须为非空字符串")

        payload = {
            "factory_name": factory_name,
            "plug_type": plug_type,
            "plug_data_type": plug_data_type,
        }

        if plug_market_id:
            payload["plug_market_id"] = plug_market_id

        return self.client.post('/api/factory/create_log', data=payload)

    def factory_done(
        self,
        plug_log_id: int,
        plug_log_status: str,
    ) -> Dict[str, Any]:
        """
        更新工厂任务状态

        Args:
            plug_log_id: 任务执行记录id（必填）
            plug_log_status: 任务状态（必填，取值：success 或 fail）

        Returns:
            响应数据
        """
        # 校验
        if not isinstance(plug_log_id, int) or plug_log_id <= 0:
            raise SARMValidationError("plug_log_id 必须为大于0的整数")

        if not isinstance(plug_log_status, str):
            raise SARMValidationError("plug_log_status 必须为字符串")
        allowed_statuses = {"success", "fail"}
        if plug_log_status not in allowed_statuses:
            raise SARMValidationError(f"plug_log_status 必须为以下值之一: {', '.join(sorted(allowed_statuses))}")

        payload = {
            "plug_log_id": plug_log_id,
            "plug_log_status": plug_log_status,
        }

        return self.client.post('/api/factory/factory_done', data=payload)
