"""
载体API测试演示
测试所有载体相关API方法
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sarm_sdk.apis.carrier import Carrier
from data_generator import DataGenerator
import json


def test_carrier_api():
    """测试载体API的所有方法"""
    print("=== 开始测试载体API ===")
    
    # 初始化API客户端和数据生成器
    carrier_api = Carrier()
    generator = DataGenerator()
    
    try:
        # 1. 测试创建单个载体
        print("\n1. 测试创建单个载体...")
        carrier_data = generator.generate_carrier("测试服务地址", "service_address")
        create_result = carrier_api.create(carrier_data)
        print(f"创建结果: {json.dumps(create_result, indent=2, ensure_ascii=False)}")
        
        if create_result.get('code') == 200:
            created_carrier_id = create_result.get('data', {}).get('carrier', {}).get('carrier_unique_id')
            print(f"成功创建载体，ID: {created_carrier_id}")
        
        # 2. 测试批量创建载体
        print("\n2. 测试批量创建载体...")
        batch_carriers = []
        carrier_types = ["service_address", "domain", "ip", "url"]
        for i in range(4):
            carrier_type = carrier_types[i % len(carrier_types)]
            carrier = generator.generate_carrier(f"测试载体{i+1}", carrier_type)
            batch_carriers.append(carrier)
        
        batch_result = carrier_api.create_batch(batch_carriers)
        print(f"批量创建结果: {json.dumps(batch_result, indent=2, ensure_ascii=False)}")
        
        # 3. 测试查询载体列表
        print("\n3. 测试查询载体列表...")
        list_result = carrier_api.get_list()
        print(f"查询结果: {json.dumps(list_result, indent=2, ensure_ascii=False)}")
        
        # 4. 测试更新载体
        print("\n4. 测试更新载体...")
        if batch_carriers:
            update_carrier = batch_carriers[0].copy()
            update_carrier["carrier"]["name"] = "更新后的载体名称"
            update_carrier["carrier"]["description"] = "这是更新后的载体描述"
            update_result = carrier_api.update_batch([update_carrier])
            print(f"更新结果: {json.dumps(update_result, indent=2, ensure_ascii=False)}")
        
        # 5. 测试批量删除载体
        print("\n5. 测试批量删除载体...")
        if batch_carriers and len(batch_carriers) > 1:
            delete_carrier_ids = [
                carrier["carrier"]["carrier_unique_id"] 
                for carrier in batch_carriers[1:]
            ]
            delete_result = carrier_api.delete_batch(delete_carrier_ids)
            print(f"删除结果: {json.dumps(delete_result, indent=2, ensure_ascii=False)}")
        
        print("\n=== 载体API测试完成 ===")
        
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
        print(f"错误类型: {type(e).__name__}")


if __name__ == "__main__":
    test_carrier_api()