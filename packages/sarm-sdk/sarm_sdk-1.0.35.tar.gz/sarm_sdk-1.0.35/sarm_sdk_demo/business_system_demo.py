"""
业务系统API测试演示
测试所有业务系统相关API方法
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sarm_sdk.apis.business_system import BusinessSystem
from data_generator import DataGenerator
import json


def test_business_system_api():
    """测试业务系统API的所有方法"""
    print("=== 开始测试业务系统API ===")
    
    # 初始化API客户端和数据生成器
    bs_api = BusinessSystem()
    generator = DataGenerator()
    try:
        # 1. 测试创建单个业务系统
        print("\n1. 测试创建单个业务系统...")
        bs_data = generator.generate_business_system("核心业务系统")
        create_result = bs_api.create(bs_data)
        print(f"创建结果: {json.dumps(create_result, indent=2, ensure_ascii=False)}")
        
        if create_result.get('code') == 200:
            created_bs_id = create_result.get('data', {}).get('business_system', {}).get('business_system_uuid')
            print(f"成功创建业务系统，ID: {created_bs_id}")
        
        # 2. 测试批量创建业务系统
        print("\n2. 测试批量创建业务系统...")
        batch_systems = []
        for i in range(3):
            bs = generator.generate_business_system(f"测试业务系统{i+1}")
            batch_systems.append(bs)
        
        batch_result = bs_api.create_batch(batch_systems)
        print(f"批量创建结果: {json.dumps(batch_result, indent=2, ensure_ascii=False)}")
        
        # 3. 测试查询业务系统列表
        print("\n3. 测试查询业务系统列表...")
        list_result = bs_api.get_list()
        print(f"查询结果: {json.dumps(list_result, indent=2, ensure_ascii=False)}")
        
        # 4. 测试更新业务系统
        print("\n4. 测试更新业务系统...")
        if batch_systems:
            update_bs = batch_systems[0].copy()
            update_bs["business_system"]["business_system_name"] = "更新后的业务系统名称"
            update_bs["business_system"]["business_system_desc"] = "这是更新后的业务系统描述"
            update_result = bs_api.update_batch([update_bs])
            print(f"更新结果: {json.dumps(update_result, indent=2, ensure_ascii=False)}")
        
        # 5. 测试批量删除业务系统
        print("\n5. 测试批量删除业务系统...")
        if batch_systems and len(batch_systems) > 1:
            delete_bs_ids = [
                bs["business_system"]["business_system_uuid"] 
                for bs in batch_systems[1:]
            ]
            delete_result = bs_api.delete_batch(delete_bs_ids)
            print(f"删除结果: {json.dumps(delete_result, indent=2, ensure_ascii=False)}")
        
        print("\n=== 业务系统API测试完成 ===")
        
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
        print(f"错误类型: {type(e).__name__}")


if __name__ == "__main__":
    test_business_system_api()