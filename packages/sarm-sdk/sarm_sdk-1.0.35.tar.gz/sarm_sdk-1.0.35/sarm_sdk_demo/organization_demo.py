"""
组织架构API测试演示
测试所有组织架构相关API方法
"""

import sys
import os

import sarm_sdk
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sarm_sdk import client
from sarm_sdk.apis.organization import Organization
from data_generator import DataGenerator
import json


def test_organization_api():
    """测试组织架构API的所有方法"""
    print("=== 开始测试组织架构API ===")
    # 初始化API客户端和数据生成器
    sarm_sdk.client(
        base_url="https://sarm.mofei.com",
        api_key="",
        api_secret=""
    )
    org_api = client.Organization()
    generator = DataGenerator()
    
    try:
        # 1. 测试创建单个组织架构
        print("\n1. 测试创建单个组织架构...")
        org_data = generator.generate_organization("测试组织单元")
        create_result = org_api.create_organization(org_data)
        print(f"创建结果: {json.dumps(create_result, indent=2, ensure_ascii=False)}")
        
        if create_result.get('code') == 200:
            created_org_id = create_result.get('data', {}).get('organize_unique_id')
            print(f"成功创建组织架构，ID: {created_org_id}")
        
        # 2. 测试批量创建组织架构
        print("\n2. 测试批量创建组织架构...")
        batch_orgs = generator.generate_batch_data(3, "organization")
        batch_result = org_api.create_batch(batch_orgs)
        print(f"批量创建结果: {json.dumps(batch_result, indent=2, ensure_ascii=False)}")
        
        # 3. 测试更新组织架构
        print("\n3. 测试更新组织架构...")
        if batch_orgs:
            update_org = batch_orgs[0].copy()
            update_org["organize_name"] = "更新后的组织名称"
            update_org["desc"] = "这是更新后的描述"
            update_result = org_api.update_batch([update_org])
            print(f"更新结果: {json.dumps(update_result, indent=2, ensure_ascii=False)}")
        
        # 4. 测试查询组织架构列表
        print("\n4. 测试查询组织架构列表...")
        list_result = org_api.get_list()
        print(f"查询结果: {json.dumps(list_result, indent=2, ensure_ascii=False)}")
        
        print("\n=== 组织架构API测试完成 ===")
        
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
        print(f"错误类型: {type(e).__name__}")


if __name__ == "__main__":
    test_organization_api()