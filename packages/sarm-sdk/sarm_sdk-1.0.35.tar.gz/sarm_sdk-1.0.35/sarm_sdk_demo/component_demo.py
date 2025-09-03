"""
组件API测试演示
测试所有组件相关API方法
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sarm_sdk.apis.component import Component
from data_generator import DataGenerator
import json


def test_component_api():
    """测试组件API的所有方法"""
    print("=== 开始测试组件API ===")
    
    # 初始化API客户端和数据生成器
    component_api = Component()
    generator = DataGenerator()
    
    # 测试用的载体ID
    test_carrier_id = "test_carrier_001"
    
    try:
        # 1. 测试创建单个组件
        print("\n1. 测试创建单个组件...")
        component_data = generator.generate_component("测试核心组件", "1.0.0")
        create_result = component_api.create(component_data)
        print(f"创建结果: {json.dumps(create_result, indent=2, ensure_ascii=False)}")
        
        if create_result.get('code') == 200:
            created_component_id = create_result.get('data', {}).get('component_unique_id')
            print(f"成功创建组件，ID: {created_component_id}")
        
        # 2. 测试批量创建组件
        print("\n2. 测试批量创建组件...")
        batch_components = []
        for i in range(3):
            component = generator.generate_component(f"测试组件{i+1}", f"1.{i+1}.0")
            batch_components.append(component)
        
        batch_result = component_api.create_batch(batch_components)
        print(f"批量创建结果: {json.dumps(batch_result, indent=2, ensure_ascii=False)}")
        
        # 3. 测试查询组件列表
        print("\n3. 测试查询组件列表...")
        list_result = component_api.get_list()
        print(f"查询结果: {json.dumps(list_result, indent=2, ensure_ascii=False)}")
        
        # 4. 测试更新组件
        print("\n4. 测试更新组件...")
        if batch_components:
            update_component = batch_components[0].copy()
            update_component["component_name"] = "更新后的组件名称"
            update_component["component_desc"] = "这是更新后的组件描述"
            update_component["component_version"] = "2.0.0"
            update_result = component_api.update(update_component)
            print(f"更新结果: {json.dumps(update_result, indent=2, ensure_ascii=False)}")
        
        # 5. 测试将组件添加到载体
        print("\n5. 测试将组件添加到载体...")
        if batch_components:
            component_id = batch_components[1]["component_unique_id"]
            add_result = component_api.add_to_carrier(component_id, test_carrier_id)
            print(f"添加结果: {json.dumps(add_result, indent=2, ensure_ascii=False)}")
        
        # 6. 测试从载体删除组件
        print("\n6. 测试从载体删除组件...")
        if batch_components:
            component_id = batch_components[1]["component_unique_id"]
            delete_result = component_api.delete_from_carrier(component_id, test_carrier_id)
            print(f"删除结果: {json.dumps(delete_result, indent=2, ensure_ascii=False)}")
        
        # 7. 测试批量删除组件
        print("\n7. 测试批量删除组件...")
        if batch_components and len(batch_components) > 2:
            delete_component_ids = [
                component["component_unique_id"] 
                for component in batch_components[2:]
            ]
            delete_result = component_api.delete_batch(delete_component_ids)
            print(f"批量删除结果: {json.dumps(delete_result, indent=2, ensure_ascii=False)}")
        
        print("\n=== 组件API测试完成 ===")
        
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
        print(f"错误类型: {type(e).__name__}")


if __name__ == "__main__":
    test_component_api()