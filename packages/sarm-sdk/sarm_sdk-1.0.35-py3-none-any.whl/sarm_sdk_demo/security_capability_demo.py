"""
安全能力API测试演示
测试所有安全能力相关API方法
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sarm_sdk.apis.security_capability import SecurityCapability
from data_generator import DataGenerator
import json


def test_security_capability_api():
    """测试安全能力API的所有方法"""
    print("=== 开始测试安全能力API ===")
    
    # 初始化API客户端和数据生成器
    capability_api = SecurityCapability()
    generator = DataGenerator()
    
    try:
        # 1. 测试创建单个安全能力
        print("\n1. 测试创建单个安全能力...")
        capability_data = generator.generate_security_capability("漏洞扫描引擎", "检测")
        create_result = capability_api.create(capability_data)
        print(f"创建结果: {json.dumps(create_result, indent=2, ensure_ascii=False)}")
        
        if create_result.get('code') == 200:
            created_capability_id = create_result.get('data', {}).get('capability_unique_id')
            print(f"成功创建安全能力，ID: {created_capability_id}")
        
        # 2. 测试批量创建安全能力
        print("\n2. 测试批量创建安全能力...")
        batch_capabilities = []
        capability_types = ["检测", "防护", "响应", "恢复"]
        for i in range(4):
            capability_type = capability_types[i % len(capability_types)]
            capability = generator.generate_security_capability(f"测试安全能力{i+1}", capability_type)
            batch_capabilities.append(capability)
        
        batch_result = capability_api.create_batch(batch_capabilities)
        print(f"批量创建结果: {json.dumps(batch_result, indent=2, ensure_ascii=False)}")
        
        # 3. 测试查询安全能力列表
        print("\n3. 测试查询安全能力列表...")
        list_result = capability_api.get_list()
        print(f"查询结果: {json.dumps(list_result, indent=2, ensure_ascii=False)}")
        
        # 4. 测试更新安全能力
        print("\n4. 测试更新安全能力...")
        if batch_capabilities:
            update_capability = batch_capabilities[0].copy()
            update_capability["capability_name"] = "更新后的安全能力名称"
            update_capability["capability_desc"] = "这是更新后的安全能力描述"
            update_capability["capability_version"] = "2.0.0"
            update_result = capability_api.update(update_capability)
            print(f"更新结果: {json.dumps(update_result, indent=2, ensure_ascii=False)}")
        
        # 5. 测试批量更新安全能力
        print("\n5. 测试批量更新安全能力...")
        if batch_capabilities and len(batch_capabilities) > 1:
            update_capabilities = []
            for capability in batch_capabilities[1:]:
                updated_capability = capability.copy()
                updated_capability["capability_version"] = "1.5.0"
                update_capabilities.append(updated_capability)
            
            batch_update_result = capability_api.update_batch(update_capabilities)
            print(f"批量更新结果: {json.dumps(batch_update_result, indent=2, ensure_ascii=False)}")
        
        # 6. 测试批量删除安全能力
        print("\n6. 测试批量删除安全能力...")
        if batch_capabilities and len(batch_capabilities) > 2:
            delete_capability_ids = [
                capability["capability_unique_id"] 
                for capability in batch_capabilities[2:]
            ]
            delete_result = capability_api.delete_batch(delete_capability_ids)
            print(f"删除结果: {json.dumps(delete_result, indent=2, ensure_ascii=False)}")
        
        print("\n=== 安全能力API测试完成 ===")
        
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
        print(f"错误类型: {type(e).__name__}")


if __name__ == "__main__":
    test_security_capability_api()