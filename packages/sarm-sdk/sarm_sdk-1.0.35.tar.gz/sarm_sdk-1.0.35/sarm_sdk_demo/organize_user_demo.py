"""
组织用户API测试演示
测试所有组织用户相关API方法
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sarm_sdk.apis.organize_user import OrganizeUser
from data_generator import DataGenerator
import json


def test_organize_user_api():
    """测试组织用户API的所有方法"""
    print("=== 开始测试组织用户API ===")
    
    # 初始化API客户端和数据生成器
    user_api = OrganizeUser()
    generator = DataGenerator()
    
    # 测试用的组织ID
    test_org_id = "test_org_001"
    
    try:
        # 1. 测试创建单个组织用户
        print("\n1. 测试创建单个组织用户...")
        user_data = generator.generate_organize_user(test_org_id, "测试用户张三")
        create_result = user_api.create(user_data)
        print(f"创建结果: {json.dumps(create_result, indent=2, ensure_ascii=False)}")
        
        if create_result.get('code') == 200:
            created_user_id = create_result.get('data', {}).get('organize_user_unique_id')
            print(f"成功创建组织用户，ID: {created_user_id}")
        
        # 2. 测试批量创建组织用户
        print("\n2. 测试批量创建组织用户...")
        batch_users = []
        for i in range(3):
            user = generator.generate_organize_user(test_org_id, f"批量用户{i+1}")
            batch_users.append(user)
        
        batch_result = user_api.create_batch(batch_users)
        print(f"批量创建结果: {json.dumps(batch_result, indent=2, ensure_ascii=False)}")
        
        # 3. 测试查询组织用户列表
        print("\n3. 测试查询组织用户列表...")
        list_result = user_api.get_list()
        print(f"查询结果: {json.dumps(list_result, indent=2, ensure_ascii=False)}")
        
        # 4. 测试更新组织用户
        print("\n4. 测试更新组织用户...")
        if batch_users:
            update_user = batch_users[0].copy()
            update_user["organize_user_name"] = "更新后的用户名"
            update_user["organize_user_position"] = "高级测试工程师"
            update_result = user_api.update_batch([update_user])
            print(f"更新结果: {json.dumps(update_result, indent=2, ensure_ascii=False)}")
        
        # 5. 测试删除组织用户（使用批量删除）
        print("\n5. 测试删除组织用户...")
        if batch_users and len(batch_users) > 1:
            delete_user_ids = [user["organize_user_unique_id"] for user in batch_users[1:]]
            delete_result = user_api.delete_batch(delete_user_ids)
            print(f"删除结果: {json.dumps(delete_result, indent=2, ensure_ascii=False)}")
        
        # 6. 测试删除组织（清理测试数据）
        print("\n6. 测试删除组织...")
        if 'created_user_id' in locals():
            delete_org_result = user_api.delete_organize(test_org_id)
            print(f"删除组织结果: {json.dumps(delete_org_result, indent=2, ensure_ascii=False)}")
        
        print("\n=== 组织用户API测试完成 ===")
        
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
        print(f"错误类型: {type(e).__name__}")


if __name__ == "__main__":
    test_organize_user_api()