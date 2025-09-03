"""
统一数据生成工具类
为所有API测试提供一致的测试数据
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional


class DataGenerator:
    """统一测试数据生成器"""
    
    def __init__(self):
        self.base_timestamp = int(datetime.now().timestamp())
        self.counter = 0
    
    def _generate_id(self, prefix: str) -> str:
        """生成唯一ID"""
        self.counter += 1
        return f"{prefix}_{self.base_timestamp}_{self.counter}"
    
    def generate_organization(self, name: str = None) -> Dict[str, Any]:
        """生成组织架构数据"""
        return {
            "organize_unique_id": self._generate_id("org"),
            "organize_name": name or f"测试组织_{self.counter}",
            "organize_punique_id": "",
            "organize_leader_unique_id": "",
            "desc": f"测试组织描述_{self.counter}",
            "dep_id": f"dep_{self.counter}",
            "tags": ["测试", "演示"]
        }
    
    def generate_organize_user(self, organize_unique_id: str, name: str = None) -> Dict[str, Any]:
        """生成组织用户数据"""
        return {
            "organize_user_unique_id": self._generate_id("user"),
            "organize_user_name": name or f"测试用户_{self.counter}",
            "organize_user_enterprise_email": f"user{self.counter}@test.com",
            "organize_user_phone": f"138{self.counter:08d}",
            "organize_user_department": f"测试部门_{self.counter}",
            "organize_user_position": "测试工程师",
            "organize_user_status": "active"
        }
    
    def generate_business_system(self, name: str = None) -> Dict[str, Any]:
        """生成业务系统数据"""
        return {
            "business_system": {
                "business_system_uuid": self._generate_id("bs"),
                "business_system_name": name or f"测试业务系统_{self.counter}",
                "business_system_status": "active",
                "business_system_desc": f"测试业务系统描述_{self.counter}",
                "business_system_puuid": "",
                "dep_id": f"dep_{self.counter}",
                "dep_name": f"测试部门_{self.counter}",
                "group_own": "测试团队",
                "group_own_id": f"team_{self.counter}",
                "system_owner_name": f"负责人_{self.counter}",
                "application_level_desc": "核心业务系统",
                "develop_mode": "自主开发",
                "cooperate_comp": "内部开发"
            }
        }
    
    def generate_application(self, name: str = None) -> Dict[str, Any]:
        """生成应用数据"""
        return {
            "application": {
                "application_unique_id": self._generate_id("app"),
                "application_name": name or f"测试应用_{self.counter}",
                "application_status": "active",
                "application_desc": f"测试应用描述_{self.counter}",
                "application_version": "1.0.0",
                "tags": ["测试", "演示"]
            }
        }
    
    def generate_carrier(self, name: str = None, carrier_type: str = "service_address") -> Dict[str, Any]:
        """生成载体数据"""
        return {
            "carrier": {
                "carrier_unique_id": self._generate_id("carrier"),
                "carrier_type": carrier_type,
                "name": name or f"测试载体_{self.counter}",
                "description": f"测试载体描述_{self.counter}",
                "source": "测试来源",
                "protocol": "https",
                "ip": f"192.168.{self.counter}.1",
                "port": 8080 + self.counter,
                "path": "/api/test",
                "domain": f"test{self.counter}.example.com",
                "tags": ["测试", "演示"]
            }
        }
    
    def generate_component(self, name: str = None, version: str = "1.0.0") -> Dict[str, Any]:
        """生成组件数据"""
        return {
            "component_unique_id": self._generate_id("comp"),
            "component_name": name or f"测试组件_{self.counter}",
            "component_version": version,
            "component_desc": f"测试组件描述_{self.counter}",
            "status": "active",
            "asset_category": "软件组件",
            "asset_type": "开源组件",
            "vendor": "测试供应商",
            "ecosystem": "npm",
            "repository": "https://github.com/test/test",
            "tags": ["测试", "开源"]
        }
    
    def generate_vulnerability(self, severity: str = "medium") -> Dict[str, Any]:
        """生成漏洞数据"""
        vuln_id = self._generate_id("vuln")
        return {
            "vuln_unique_id": vuln_id,
            "title": f"测试漏洞_{vuln_id}",
            "description": f"这是一个测试漏洞描述_{self.counter}",
            "severity": severity,
            "status": "open",
            "cve_id": f"CVE-2024-{1000 + self.counter}",
            "cwe_id": f"CWE-{100 + self.counter}",
            "vulnerability_type": "代码注入",
            "impact": "可能导致系统被攻击",
            "discovery_at": (datetime.now() - timedelta(days=self.counter)).isoformat(),
            "tags": ["测试", "高危"]
        }
    
    def generate_security_issue(self, level: str = "medium") -> Dict[str, Any]:
        """生成安全问题数据"""
        issue_id = self._generate_id("issue")
        return {
            "issue_unique_id": issue_id,
            "issue_title": f"测试安全问题_{issue_id}",
            "issue_description": f"这是一个测试安全问题描述_{self.counter}",
            "issue_level": level,
            "issue_status": "open",
            "discovery_at": (datetime.now() - timedelta(days=self.counter)).isoformat(),
            "owner_name": f"负责人_{self.counter}",
            "tags": ["测试", "安全问题"]
        }
    
    def generate_security_capability(self, name: str = None, capability_type: str = "检测") -> Dict[str, Any]:
        """生成安全能力数据"""
        return {
            "capability_unique_id": self._generate_id("cap"),
            "capability_name": name or f"测试安全能力_{self.counter}",
            "capability_type": capability_type,
            "capability_desc": f"测试安全能力描述_{self.counter}",
            "capability_version": "1.0.0",
            "vendor": "测试供应商",
            "tags": ["测试", "安全能力"]
        }
    
    def generate_batch_data(self, count: int, data_type: str) -> List[Dict[str, Any]]:
        """生成批量数据"""
        generators = {
            "organization": self.generate_organization,
            "organize_user": lambda: self.generate_organize_user("org_placeholder"),
            "business_system": self.generate_business_system,
            "application": self.generate_application,
            "carrier": self.generate_carrier,
            "component": self.generate_component,
            "vulnerability": self.generate_vulnerability,
            "security_issue": self.generate_security_issue,
            "security_capability": self.generate_security_capability
        }
        
        if data_type not in generators:
            raise ValueError(f"不支持的数据类型: {data_type}")
        
        result = []
        for i in range(count):
            if data_type == "organize_user":
                # 需要组织ID参数
                result.append(self.generate_organize_user(f"test_org_{i}"))
            else:
                result.append(generators[data_type]())
        return result
    
    def create_complete_test_package(self) -> Dict[str, Any]:
        """创建完整的测试数据包，包含所有关联关系"""
        # 生成基础数据
        organization = self.generate_organization()
        user = self.generate_organize_user(organization["organize_unique_id"])
        business_system = self.generate_business_system()
        application = self.generate_application()
        carrier = self.generate_carrier()
        component = self.generate_component()
        vulnerability = self.generate_vulnerability()
        security_issue = self.generate_security_issue()
        security_capability = self.generate_security_capability()
        
        return {
            "organization": organization,
            "organize_user": user,
            "business_system": business_system,
            "application": application,
            "carrier": carrier,
            "component": component,
            "vulnerability": vulnerability,
            "security_issue": security_issue,
            "security_capability": security_capability
        }