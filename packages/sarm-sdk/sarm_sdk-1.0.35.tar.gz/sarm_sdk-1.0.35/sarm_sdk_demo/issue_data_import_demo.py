"""
安全问题数据导入API测试演示
测试安全问题数据导入相关API方法
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sarm_sdk.apis.issue_data_import import IssueDataImport
from data_generator import DataGenerator
import json


def test_issue_data_import_api():
    """测试安全问题数据导入API的所有方法"""
    print("=== 开始测试安全问题数据导入API ===")
    
    # 初始化API客户端和数据生成器
    import_api = IssueDataImport()
    generator = DataGenerator()
    
    try:
        # 1. 测试导入安全问题数据
        print("\n1. 测试导入安全问题数据...")
        
        # 构建测试数据
        test_data = {
            "issues": [
                {
                    "issue_unique_id": "test_import_issue_001",
                    "issue_title": "导入测试安全问题",
                    "issue_description": "这是一个导入测试的安全问题",
                    "issue_level": "high",
                    "issue_status": "open",
                    "discovery_at": "2024-01-01T00:00:00Z",
                    "owner_name": "导入测试负责人",
                    "tags": ["导入", "测试"]
                },
                {
                    "issue_unique_id": "test_import_issue_002",
                    "issue_title": "导入测试安全问题2",
                    "issue_description": "这是第二个导入测试的安全问题",
                    "issue_level": "medium",
                    "issue_status": "in_progress",
                    "discovery_at": "2024-01-02T00:00:00Z",
                    "owner_name": "导入测试负责人2",
                    "tags": ["导入", "测试"]
                }
            ],
            "vulnerabilities": [
                {
                    "vuln_unique_id": "test_import_vuln_001",
                    "title": "导入测试漏洞",
                    "description": "这是一个导入测试的漏洞",
                    "severity": "critical",
                    "status": "open",
                    "cve_id": "CVE-2024-2001",
                    "cwe_id": "CWE-89",
                    "vulnerability_type": "SQL注入",
                    "impact": "可能导致数据泄露",
                    "discovery_at": "2024-01-01T00:00:00Z",
                    "tags": ["导入", "测试", "高危"]
                }
            ],
            "components": [
                {
                    "component_unique_id": "test_import_comp_001",
                    "component_name": "导入测试组件",
                    "component_version": "1.5.0",
                    "component_desc": "导入测试组件描述",
                    "status": "active",
                    "asset_category": "软件组件",
                    "asset_type": "开源组件",
                    "vendor": "导入测试供应商",
                    "ecosystem": "python",
                    "repository": "https://github.com/import/test",
                    "tags": ["导入", "测试", "开源"]
                }
            ]
        }
        
        import_result = import_api.import_carrier_data(test_data)
        print(f"安全问题数据导入结果: {json.dumps(import_result, indent=2, ensure_ascii=False)}")
        
        # 2. 测试创建载体数据结构
        print("\n2. 测试创建载体数据结构...")
        carrier_structure = {
            "carrier_unique_id": "test_issue_carrier_001",
            "carrier_type": "service_address",
            "name": "安全问题测试载体",
            "description": "用于安全问题测试的载体",
            "source": "安全问题测试来源",
            "protocol": "https",
            "ip": "192.168.2.100",
            "port": 9090,
            "path": "/security/test",
            "domain": "security-test.example.com",
            "tags": ["安全问题", "测试"]
        }
        
        structure_result = import_api.create_carrier_data_structure(carrier_structure)
        print(f"创建载体数据结构结果: {json.dumps(structure_result, indent=2, ensure_ascii=False)}")
        
        # 3. 测试创建安全问题
        print("\n3. 测试创建安全问题...")
        issue_data = {
            "issue_unique_id": "test_structured_issue_001",
            "issue_title": "结构化测试安全问题",
            "issue_description": "这是一个结构化测试的安全问题",
            "issue_level": "low",
            "issue_status": "pending",
            "discovery_at": "2024-01-03T00:00:00Z",
            "owner_name": "结构化测试负责人",
            "tags": ["结构化", "测试"]
        }
        
        issue_result = import_api.create_issue(issue_data)
        print(f"创建安全问题结果: {json.dumps(issue_result, indent=2, ensure_ascii=False)}")
        
        # 4. 测试创建组件
        print("\n4. 测试创建组件...")
        component_data = {
            "component_unique_id": "test_structured_comp_001",
            "component_name": "结构化测试组件",
            "component_version": "3.0.0",
            "component_desc": "结构化测试组件描述",
            "status": "deprecated",
            "asset_category": "软件组件",
            "asset_type": "商业组件",
            "vendor": "结构化测试供应商",
            "ecosystem": "dotnet",
            "repository": "https://repo.example.com/structured",
            "tags": ["结构化", "测试", "商业"]
        }
        
        component_result = import_api.create_component(component_data)
        print(f"创建组件结果: {json.dumps(component_result, indent=2, ensure_ascii=False)}")
        
        print("\n=== 安全问题数据导入API测试完成 ===")
        
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
        print(f"错误类型: {type(e).__name__}")


if __name__ == "__main__":
    test_issue_data_import_api()