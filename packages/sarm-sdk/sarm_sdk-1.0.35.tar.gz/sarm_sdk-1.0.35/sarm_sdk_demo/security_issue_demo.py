"""
安全问题API测试演示
测试所有安全问题相关API方法，包括组件漏洞关联
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sarm_sdk.apis.security_issue import SecurityIssue
from data_generator import DataGenerator
import json


def test_security_issue_api():
    """测试安全问题API的所有方法"""
    print("=== 开始测试安全问题API ===")
    
    # 初始化API客户端和数据生成器
    issue_api = SecurityIssue()
    generator = DataGenerator()
    
    # 测试用的组件ID和漏洞ID
    test_component_id = "test_component_001"
    test_vuln_id = "test_vuln_001"
    
    try:
        # 1. 测试创建单个安全问题
        print("\n1. 测试创建单个安全问题...")
        issue_data = generator.generate_security_issue("high")
        create_result = issue_api.create(issue_data)
        print(f"创建结果: {json.dumps(create_result, indent=2, ensure_ascii=False)}")
        
        if create_result.get('code') == 200:
            created_issue_id = create_result.get('data', {}).get('issue_unique_id')
            print(f"成功创建安全问题，ID: {created_issue_id}")
        
        # 2. 测试批量创建安全问题
        print("\n2. 测试批量创建安全问题...")
        batch_issues = []
        levels = ["critical", "high", "medium", "low"]
        for i in range(4):
            issue = generator.generate_security_issue(levels[i % len(levels)])
            batch_issues.append(issue)
        
        batch_result = issue_api.create_batch(batch_issues)
        print(f"批量创建结果: {json.dumps(batch_result, indent=2, ensure_ascii=False)}")
        
        # 3. 测试查询安全问题列表
        print("\n3. 测试查询安全问题列表...")
        list_result = issue_api.get_list()
        print(f"查询结果: {json.dumps(list_result, indent=2, ensure_ascii=False)}")
        
        # 4. 测试更新安全问题
        print("\n4. 测试更新安全问题...")
        if batch_issues:
            update_issue = batch_issues[0].copy()
            update_issue["issue_title"] = "更新后的安全问题标题"
            update_issue["issue_description"] = "这是更新后的安全问题描述"
            update_issue["issue_status"] = "resolved"
            update_result = issue_api.update(update_issue)
            print(f"更新结果: {json.dumps(update_result, indent=2, ensure_ascii=False)}")
        
        # 5. 测试批量更新安全问题
        print("\n5. 测试批量更新安全问题...")
        if batch_issues and len(batch_issues) > 1:
            update_issues = []
            for issue in batch_issues[1:]:
                updated_issue = issue.copy()
                updated_issue["issue_status"] = "in_progress"
                update_issues.append(updated_issue)
            
            batch_update_result = issue_api.update_batch(update_issues)
            print(f"批量更新结果: {json.dumps(batch_update_result, indent=2, ensure_ascii=False)}")
        
        # 6. 测试获取组件漏洞关联列表
        print("\n6. 测试获取组件漏洞关联列表...")
        vuln_list_result = issue_api.get_component_vuln_list(test_component_id)
        print(f"组件漏洞关联查询结果: {json.dumps(vuln_list_result, indent=2, ensure_ascii=False)}")
        
        # 7. 测试更新组件漏洞关联列表
        print("\n7. 测试更新组件漏洞关联列表...")
        vuln_associations = [
            {
                "component_unique_id": test_component_id,
                "vuln_unique_id": test_vuln_id,
                "status": "affected",
                "severity": "high"
            }
        ]
        update_vuln_result = issue_api.update_component_vuln_list(vuln_associations)
        print(f"更新组件漏洞关联结果: {json.dumps(update_vuln_result, indent=2, ensure_ascii=False)}")
        
        # 8. 测试更新漏洞列表
        print("\n8. 测试更新漏洞列表...")
        vuln_updates = [
            {
                "vuln_unique_id": test_vuln_id,
                "status": "fixed",
                "fix_version": "2.0.0"
            }
        ]
        update_vuln_list_result = issue_api.update_vuln_list(vuln_updates)
        print(f"更新漏洞列表结果: {json.dumps(update_vuln_list_result, indent=2, ensure_ascii=False)}")
        
        # 9. 测试批量删除安全问题
        print("\n9. 测试批量删除安全问题...")
        if batch_issues and len(batch_issues) > 2:
            delete_issue_ids = [
                issue["issue_unique_id"] 
                for issue in batch_issues[2:]
            ]
            delete_result = issue_api.delete_batch(delete_issue_ids)
            print(f"删除结果: {json.dumps(delete_result, indent=2, ensure_ascii=False)}")
        
        print("\n=== 安全问题API测试完成 ===")
        
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
        print(f"错误类型: {type(e).__name__}")


if __name__ == "__main__":
    test_security_issue_api()