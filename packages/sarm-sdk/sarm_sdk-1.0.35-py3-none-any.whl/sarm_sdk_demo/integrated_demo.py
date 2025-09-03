"""
综合测试脚本
展示SARM SDK所有API之间的完整数据流和关联关系
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sarm_sdk.apis.organization import Organization
from sarm_sdk.apis.organize_user import OrganizeUser
from sarm_sdk.apis.business_system import BusinessSystem
from sarm_sdk.apis.application import Application
from sarm_sdk.apis.carrier import Carrier
from sarm_sdk.apis.component import Component
from sarm_sdk.apis.vulnerability import Vulnerability
from sarm_sdk.apis.security_issue import SecurityIssue
from sarm_sdk.apis.security_capability import SecurityCapability
from data_generator import DataGenerator
import json


def run_integrated_test():
    """运行综合测试，展示完整数据流"""
    print("=== SARM SDK 综合测试开始 ===")
    
    # 初始化所有API客户端
    org_api = Organization()
    user_api = OrganizeUser()
    bs_api = BusinessSystem()
    app_api = Application()
    carrier_api = Carrier()
    component_api = Component()
    vuln_api = Vulnerability()
    issue_api = SecurityIssue()
    capability_api = SecurityCapability()
    
    generator = DataGenerator()
    
    try:
        # 1. 创建基础组织架构
        print("\n1. 创建基础组织架构...")
        org_data = generator.generate_organization("测试企业组织")
        org_result = org_api.create(org_data)
        org_id = org_result.get('data', {}).get('organize_unique_id')
        print(f"创建组织架构: {org_id}")
        
        # 2. 创建组织用户
        print("\n2. 创建组织用户...")
        user_data = generator.generate_organize_user(org_id, "安全管理员")
        user_result = user_api.create(user_data)
        user_id = user_result.get('data', {}).get('organize_user_unique_id')
        print(f"创建组织用户: {user_id}")
        
        # 3. 创建业务系统
        print("\n3. 创建业务系统...")
        bs_data = generator.generate_business_system("核心业务系统")
        bs_result = bs_api.create(bs_data)
        bs_id = bs_result.get('data', {}).get('business_system', {}).get('business_system_uuid')
        print(f"创建业务系统: {bs_id}")
        
        # 4. 创建应用
        print("\n4. 创建应用...")
        app_data = generator.generate_application("核心业务应用")
        app_result = app_api.create(app_data)
        app_id = app_result.get('data', {}).get('application', {}).get('application_unique_id')
        print(f"创建应用: {app_id}")
        
        # 5. 创建载体
        print("\n5. 创建载体...")
        carrier_data = generator.generate_carrier("核心业务域名", "domain")
        carrier_result = carrier_api.create(carrier_data)
        carrier_id = carrier_result.get('data', {}).get('carrier', {}).get('carrier_unique_id')
        print(f"创建载体: {carrier_id}")
        
        # 6. 创建组件
        print("\n6. 创建组件...")
        component_data = generator.generate_component("核心依赖组件", "2.1.0")
        component_result = component_api.create(component_data)
        component_id = component_result.get('data', {}).get('component_unique_id')
        print(f"创建组件: {component_id}")
        
        # 7. 将组件添加到载体
        print("\n7. 关联组件与载体...")
        add_result = component_api.add_to_carrier(component_id, carrier_id)
        print(f"组件添加到载体: {json.dumps(add_result, indent=2, ensure_ascii=False)}")
        
        # 8. 创建漏洞
        print("\n8. 创建漏洞...")
        vuln_data = generator.generate_vulnerability("high")
        vuln_result = vuln_api.create(vuln_data)
        vuln_id = vuln_result.get('data', {}).get('vuln_unique_id')
        print(f"创建漏洞: {vuln_id}")
        
        # 9. 创建安全问题
        print("\n9. 创建安全问题...")
        issue_data = generator.generate_security_issue("high")
        issue_result = issue_api.create(issue_data)
        issue_id = issue_result.get('data', {}).get('issue_unique_id')
        print(f"创建安全问题: {issue_id}")
        
        # 10. 创建安全能力
        print("\n10. 创建安全能力...")
        capability_data = generator.generate_security_capability("漏洞扫描引擎", "检测")
        capability_result = capability_api.create(capability_data)
        capability_id = capability_result.get('data', {}).get('capability_unique_id')
        print(f"创建安全能力: {capability_id}")
        
        # 11. 建立组件漏洞关联
        print("\n11. 建立组件漏洞关联...")
        vuln_association = {
            "component_unique_id": component_id,
            "vuln_unique_id": vuln_id,
            "status": "affected",
            "severity": "high"
        }
        vuln_assoc_result = issue_api.update_component_vuln_list([vuln_association])
        print(f"组件漏洞关联结果: {json.dumps(vuln_assoc_result, indent=2, ensure_ascii=False)}")
        
        # 12. 查询完整关联数据
        print("\n12. 查询完整关联数据...")
        
        # 查询组织架构
        org_list = org_api.get_list()
        print(f"组织架构列表: {len(org_list.get('data', []))} 个")
        
        # 查询组织用户
        user_list = user_api.get_list()
        print(f"组织用户列表: {len(user_list.get('data', []))} 个")
        
        # 查询业务系统
        bs_list = bs_api.get_list()
        print(f"业务系统列表: {len(bs_list.get('data', []))} 个")
        
        # 查询应用
        app_list = app_api.get_list()
        print(f"应用列表: {len(app_list.get('data', []))} 个")
        
        # 查询载体
        carrier_list = carrier_api.get_list()
        print(f"载体列表: {len(carrier_list.get('data', []))} 个")
        
        # 查询组件
        component_list = component_api.get_list()
        print(f"组件列表: {len(component_list.get('data', []))} 个")
        
        # 查询漏洞
        vuln_list = vuln_api.get_list()
        print(f"漏洞列表: {len(vuln_list.get('data', []))} 个")
        
        # 查询安全问题
        issue_list = issue_api.get_list()
        print(f"安全问题列表: {len(issue_list.get('data', []))} 个")
        
        # 查询安全能力
        capability_list = capability_api.get_list()
        print(f"安全能力列表: {len(capability_list.get('data', []))} 个")
        
        # 13. 清理测试数据
        print("\n13. 清理测试数据...")
        
        # 删除安全能力
        if capability_id:
            capability_api.delete_batch([capability_id])
            print("已删除安全能力")
        
        # 删除安全问题
        if issue_id:
            issue_api.delete_batch([issue_id])
            print("已删除安全问题")
        
        # 删除漏洞
        if vuln_id:
            vuln_api.delete_batch([vuln_id])
            print("已删除漏洞")
        
        # 删除组件
        if component_id:
            component_api.delete_batch([component_id])
            print("已删除组件")
        
        # 删除载体
        if carrier_id:
            carrier_api.delete_batch([carrier_id])
            print("已删除载体")
        
        # 删除应用
        if app_id:
            app_api.delete_batch([app_id])
            print("已删除应用")
        
        # 删除业务系统
        if bs_id:
            bs_api.delete_batch([bs_id])
            print("已删除业务系统")
        
        # 删除组织用户
        if user_id:
            user_api.delete_batch([user_id])
            print("已删除组织用户")
        
        # 删除组织架构
        if org_id:
            org_api.delete_batch([org_id])
            print("已删除组织架构")
        
        print("\n=== SARM SDK 综合测试完成 ===")
        print("所有测试数据已成功创建、关联并清理")
        
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
        print(f"错误类型: {type(e).__name__}")


if __name__ == "__main__":
    run_integrated_test()