#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 插件基类

提供可复用的 BasePlugin 抽象类，封装通用的参数解析、日志、客户端初始化、
批处理与统计上报等能力。用户可继承该类实现 extract/transform/load 三个方法。

使用方式：
    from sarm_sdk.plugin import BasePlugin
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from abc import ABC, abstractmethod
from typing import Generator, List, Union, Dict, Optional

from .client import SARMClient


class BasePlugin(ABC):
    """
    通用插件基类，封装了所有与具体业务无关的底层逻辑。
    """

    # 定义数据上传批次大小
    UPLOAD_BATCH_SIZE = 50
    # 为测试运行定义一个数据处理上限
    TEST_RUN_LIMIT = 10

    def __init__(self):
        self.args = None
        self.config = {}
        self.logger = self._setup_logger()
        self.client = None

    def _setup_logger(self):
        """初始化日志记录器"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            stream=sys.stdout,
        )
        return logging.getLogger(self.__class__.__name__)

    def _parse_args(self):
        """解析平台运行时传入的参数"""
        parser = argparse.ArgumentParser()
        parser.add_argument("--server_addr", required=True, help="平台服务地址")
        parser.add_argument("--token", required=True, help="平台认证令牌")
        parser.add_argument("--params", default="{}", help="插件配置的JSON字符串")
        parser.add_argument("--factory_id", help="当前执行任务的标识")
        parser.add_argument("--mode", default="running", help="运行模式 (running 或 test)")
        self.args = parser.parse_args()

    def _load_config(self):
        """加载并合并插件配置"""
        try:
            params_data = json.loads(self.args.params)
            if isinstance(params_data, list):
                params_config = {item.get('key'): item.get('value') for item in params_data}
            else:
                params_config = params_data
            self.config.update(params_config)
        except json.JSONDecodeError:
            self.logger.error("无法解析 --params 参数，请检查是否为合法的JSON字符串。")
            raise
        except Exception as e:
            self.logger.error(f"处理 --params 参数时出错: {e}", exc_info=True)
            raise

    def _report_statistics(self, success_count: int, sample_data: List[Dict]):
        """执行完毕后上报统计信息"""
        # 如果没有 factory_id，则跳过统计上报
        if self.args.factory_id is None:
            self.logger.info("未提供 factory_id，跳过统计信息上报。")
            return
            
        self.logger.info("正在上报执行统计信息...")
        
        data_type = self.args.mode
        
        is_test_mode = self.args.mode == 'test'
        
        data_to_report = sample_data if is_test_mode else (sample_data[:1] if sample_data else [])

        statistical_info = {}

        data_key = getattr(self, 'DATA_TYPE_KEY', 'normal')

        statistical_info = {
            data_key: {"count": success_count}
        }
                
        critical_data_count = success_count

        try:
            response = self.client.common.statistics(
                data=data_to_report,
                statistical_info=statistical_info,
                critical_data_count=critical_data_count,
                data_type=data_type
            )
            if response and response.get("code") == 200:
                self.logger.info("统计信息上报成功。")
            else:
                self.logger.error(f"统计信息上报失败: {response}")
        except Exception as e:
            self.logger.error(f"上报统计信息时发生异常: {e}", exc_info=True)

# 内置获取组织架构唯一ID方法
    def _get_organizations_unique_id(self, org_name: Optional[str] = None) -> str:
        """根据组织名称获取组织唯一ID"""
        try:
            result = self.client.organizations.get(
                page=1, limit=10, organize_name=org_name
            )
            data = result.get("data", {})
            data_list = data.get("data_list", []) or data.get("list", [])
            if data_list:
                return data_list[0].get("organize_uuid")
            return None
        except Exception as e:
            self.logger.error(f"获取组织唯一ID失败: {e}")
            return None

    # 内置获取组织架构用户唯一ID方法
    def _get_organizations_user_unique_id(
        self,
        user_name: Optional[str] = None,
        user_enterprise_email: Optional[str] = None,
    ) -> str:
        """
        根据用户名称或企业邮箱获取用户唯一ID。
        - 可仅传 user_name，或仅传 user_enterprise_email，或两者都传。
        - 若两者皆为空，则返回 None 并记录警告日志。
        """
        try:
            params = {
                "page": 1,
                "limit": 10,
                "user_info": {},
                "organize_unique_id": ""
            }

            if user_name:
                params["user_info"]["organize_user_name"] = user_name
            if user_enterprise_email:
                params["user_info"]["organize_user_enterprise_email"] = user_enterprise_email

            result = self.client.organize_users.get_list(**params)
            data = result.get("data", {})
            data_list = data.get("data_list", []) or data.get("list", [])
            if data_list:
                return data_list[0].get("organize_user_unique_id")
            return None
        except Exception as e:
            self.logger.error(f"获取用户唯一ID失败: {e}")
            return None

    # 内置获取业务系统唯一ID方法
    def _get_business_system_unique_id(
        self, business_system_name: Optional[str] = None
    ) -> str:
        """根据业务系统名称获取系统唯一ID"""
        try:
            result = self.client.business_systems.get_list(
                page=1, limit=10, business_system_name=business_system_name
            )
            data = result.get("data", {})
            data_list = data.get("data_list", []) or data.get("list", [])
            if data_list:
                return data_list[0].get("business_system_uuid")
            return None
        except Exception as e:
            self.logger.error(f"获取系统唯一ID失败: {e}")
            return None

    # 内置获取应用唯一ID方法
    def _get_applications_unique_id(
        self, application_name: Optional[str] = None
    ) -> str:
        """根据应用名称获取应用唯一ID"""
        try:
            result = self.client.applications.get_list(
                page=1, limit=10, application_name=application_name
            )
            data = result.get("data", {})
            data_list = data.get("data_list", []) or data.get("list", [])
            if data_list:
                return data_list[0].get("application_unique_id")
            return None
        except Exception as e:
            self.logger.error(f"获取应用唯一ID失败: {e}")
            return None

    # 内置获取成分唯一ID方法
    def _get_component_unique_id(
        self,
        component_name: Optional[str] = None,
        component_version: Optional[str] = None,
    ) -> str:
        """根据成分名称获取成分唯一ID"""
        try:
            result = self.client.components.get_component_unique_id(
                page=1,
                limit=10,
                component_name=component_name,
                component_version=component_version,
            )
            data = result.get("data", {})
            data_list = data.get("data_list", []) or data.get("list", [])
            if data_list:
                return data_list[0].get("component_unique_id")
            return None
        except Exception as e:
            self.logger.error(f"获取组件唯一ID失败: {e}")
            return None

    # 内置获取载体唯一ID方法
    def _get_carriers_unique_id(
            self, name: Optional[str] = None, carrier_type: Optional[str] = None
    ) -> str:
        """根据名称获取载体唯一ID"""
        try:
            result = self.client.carriers.get_carrier_unique_id(
                filters={
                    "name": name,
                    "carrier_type": carrier_type,
                }
            )
            data = result.get("data", {})
            data_list = data.get("data_list", []) or data.get("list", [])
            if data_list:
                return data_list[0].get("carrier_unique_id")
            return None
        except Exception as e:
            self.logger.error(f"获取载体唯一ID失败: {e}")
            return None
    # 内置获取安全能力唯一ID方法
    def _get_security_capabilities_unique_id(self, name: Optional[str] = None) -> str:
        """根据名称获取安全能力唯一ID"""
        try:
            result = self.client.security_capabilities.get_list(
                page=1, limit=10, capability_name=name
            )
            data = result.get("data", {})
            data_list = data.get("data_list", []) or data.get("list", [])
            if data_list:
                return data_list[0].get("capability_unique_id")
            return None
        except Exception as e:
            self.logger.error(f"获取安全能力唯一ID失败: {e}")
            return None

    def run(self):
        """插件主执行入口，包含完整的执行流程"""
        all_successful_data = []
        success_count = 0
        try:
            self._parse_args()
            self._load_config()
            
            client_kwargs = {
                "base_url": self.args.server_addr,
                "token": self.args.token
            }
            # 核心改动：处理 factory_id，并确保其为字符串
            if self.args.factory_id is not None:
                client_kwargs["factory_log_id"] = str(self.args.factory_id)
            
            self.client = SARMClient(**client_kwargs)

            self.logger.info("开始流式处理数据...")
            buffer = []
            error_count = 0
            
            is_test_mode = self.args.mode == 'test'

            for raw_item in self.extract():
                try:
                    transformed_dict = self.transform(raw_item)
                    if transformed_dict is None:
                        continue
                    buffer.append(transformed_dict)
                    all_successful_data.append(transformed_dict)
                    success_count += 1
                except Exception:
                    error_count += 1
                    self.logger.error(
                        "数据转换失败，已跳过。详细错误追溯信息如下:", exc_info=True
                    )
                    self.logger.debug(f"导致失败的原始数据: {raw_item}")
                    continue

                if len(buffer) >= self.UPLOAD_BATCH_SIZE:
                    self.load(buffer)
                    buffer.clear()

                if is_test_mode and success_count >= self.TEST_RUN_LIMIT:
                    self.logger.info(
                        f"[测试运行] 已达到 {self.TEST_RUN_LIMIT} 条数据处理上限，测试提前结束。"
                    )
                    break

            if buffer and not is_test_mode:
                self.load(buffer)

            self.logger.info("插件执行完毕。")
            self.logger.info(f"成功处理: {success_count} 条，失败: {error_count} 条。")

        except Exception as e:
            self.logger.error(f"插件执行过程中发生严重错误，已终止: {e}", exc_info=True)
            sys.exit(1)
        finally:
            if self.client:
                self._report_statistics(success_count, all_successful_data)


    @abstractmethod
    def extract(self) -> Generator[any, None, None]:
        """从数据源提取原始数据。"""
        pass

    @abstractmethod
    def transform(self, raw_item: any) -> Union[Dict, None]:
        """将一条原始数据转换为一个字典。"""
        pass

    @abstractmethod
    def load(self, buffer: List[Dict]):
        """将一个批次的数据上报到平台。"""
        pass


