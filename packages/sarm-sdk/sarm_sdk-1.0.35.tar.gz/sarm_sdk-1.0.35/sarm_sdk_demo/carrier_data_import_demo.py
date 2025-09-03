"""
载体数据导入API测试演示
测试载体数据导入相关API方法
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sarm_sdk.apis.carrier_data_import import CarrierDataImport
from data_generator import DataGenerator
import json


def test_carrier_data_import_api():
    """测试载体数据导入API的所有方法"""
    print("=== 开始测试载体数据导入API ===")
    
    # 初始化API客户端和数据生成器
    import_api = CarrierDataImport()
    generator = DataGenerator()
    
    try:
        # 1. 测试导入载体数据
        print("\n1. 测试导入载体数据...")
        
        # 构建测试数据
        test_data = {
            "carriers": [
                {
                    "carrier_unique_id": "test_carrier_001",
                    "carrier_type": "service_address",
                    "name": "测试服务地址",
                    "description": "测试服务描述",
                    "source": "测试来源",
                    "protocol": "https",
                    "ip": "192.168.1.100",
                    "port": 8080,
                    "path": "/api/test",
                    "domain": "test.example.com",
                    "tags": ["测试", "演示"]
                }
            ],
            "components": [
                {
                    "component_unique_id": "test_component_001",
                    "component_name": "测试组件",
                    "component_version": "1.0.0",
                    "component_desc": "测试组件描述",
                    "status": "active",
                    "asset_category": "软件组件",
                    "asset_type": "开源组件",
                    "vendor": "测试供应商",
                    "ecosystem": "npm",
                    "repository": "https://github.com/test/test",
                    "tags": ["测试", "开源"]
                }
            ],
            "vulnerabilities": [
                {
                    "vuln_unique_id": "test_vuln_001",
                    "title": "测试漏洞",
                    "description": "这是一个测试漏洞",
                    "severity": "high",
                    "status": "open",
                    "cve_id": "CVE-2024-1001",
                    "cwe_id": "CWE-79",
                    "vulnerability_type": "代码注入",
                    "impact": "可能导致系统被攻击",
                    "discovery_at": "2024-01-01T00:00:00Z",
                    "tags": ["测试", "高危"]
                }
            ]
        }
        
        import_result = import_api.import_carrier_data(test_data)
        print(f"数据导入结果: {json.dumps(import_result, indent=2, ensure_ascii=False)}")
        
        # 2. 测试创建载体数据结构
        print("\n2. 测试创建载体数据结构...")
        carrier_structure = {
            "carrier_unique_id": "test_carrier_structure_001",
            "carrier_type": "domain",
            "name": "测试域名结构",
            "description": "测试域名结构描述",
            "source": "测试数据源",
            "protocol": "https",
            "domain": "test-structure.example.com",
            "tags": ["结构测试"]
        }
        
        structure_result = import_api.create_carrier_data_structure(carrier_structure)
        print(f"创建载体数据结构结果: {json.dumps(structure_result, indent=2, ensure_ascii=False)}")
        
        # 3. 测试创建安全问题
        print("\n3. 测试创建安全问题...")
        issue_data = {
            "issue_unique_id": "test_issue_001",
            "issue_title": "测试安全问题",
            "issue_description": "这是一个测试安全问题",
            "issue_level": "medium",
            "issue_status": "open",
            "discovery_at": "2024-01-01T00:00:00Z",
            "owner_name": "测试负责人",
            "tags": ["测试", "安全问题"]
        }
        
        issue_result = import_api.create_issue(issue_data)
        print(f"创建安全问题结果: {json.dumps(issue_result, indent=2, ensure_ascii=False)}")
        
        # 4. 测试创建组件
        print("\n4. 测试创建组件...")
        component_data = {
            "component_unique_id": "test_import_component_001",
            "component_name": "测试导入组件",
            "component_version": "2.0.0",
            "component_desc": "测试导入组件描述",
            "status": "active",
            "asset_category": "软件组件",
            "asset_type": "商业组件",
            "vendor": "商业供应商",
            "ecosystem": "java",
            "repository": "https://repo.example.com/commercial",
            "tags": ["商业", "测试"]
        }
        
        component_result = import_api.create_component(component_data)
        print(f"创建组件结果: {json.dumps(component_result, indent=2, ensure_ascii=False)}")
        
        print("\n=== 载体数据导入API测试完成 ===")
        
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
        print(f"错误类型: {type(e).__name__}")


if __name__ == "__main__":
    test_carrier_data_import_api()