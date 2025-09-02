#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
并发测试：验证 fingerprint_loader 的线程安全性
"""

import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from xtls_client.fingerprint_loader import (
    get_fingerprint_config, 
    list_available_fingerprints,
    get_fingerprints_by_browser,
    _get_fingerprint_loader
)

def test_concurrent_access():
    """测试多线程并发访问指纹配置"""
    
    def worker(thread_id):
        """工作线程函数"""
        results = []
        errors = []
        
        try:
            # 模拟真实使用场景：获取指纹列表和配置
            for i in range(10):
                
                # 获取所有指纹列表
                fingerprints = list_available_fingerprints()
                results.append(f"Thread {thread_id}: Found {len(fingerprints)} fingerprints")
                
                # 获取浏览器指纹
                chrome_fingerprints = get_fingerprints_by_browser("chrome")
                safari_fingerprints = get_fingerprints_by_browser("safari")
                firefox_fingerprints = get_fingerprints_by_browser("firefox")
                
                results.append(f"Thread {thread_id}: Chrome={len(chrome_fingerprints)}, Safari={len(safari_fingerprints)}, Firefox={len(firefox_fingerprints)}")
                
                # 随机获取一个指纹的配置
                if fingerprints:
                    random_fingerprint = random.choice(fingerprints)
                    config = get_fingerprint_config(random_fingerprint)
                    if config:
                        results.append(f"Thread {thread_id}: Got config for {random_fingerprint} with {len(config)} keys")
                    else:
                        results.append(f"Thread {thread_id}: Config for {random_fingerprint} is None")
                
                # 短暂休眠，模拟真实使用
                time.sleep(0.01)
                
        except Exception as e:
            errors.append(f"Thread {thread_id} error: {str(e)}")
            
        return thread_id, results, errors

    print("🧪 开始并发安全测试...")
    
    # 测试1: 多线程并发访问
    print("\n📋 测试1: 多线程并发访问")
    
    num_threads = 200
    threads_results = {}
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        # 提交所有任务
        futures = {executor.submit(worker, i): i for i in range(num_threads)}
        
        # 收集结果
        for future in as_completed(futures):
            thread_id, results, errors = future.result()
            threads_results[thread_id] = (results, errors)
    
    # 分析结果
    total_operations = 0
    total_errors = 0
    
    for thread_id, (results, errors) in threads_results.items():
        total_operations += len(results)
        total_errors += len(errors)
        
        if errors:
            print(f"❌ Thread {thread_id} 发生错误: {errors}")
        else:
            print(f"✅ Thread {thread_id} 成功完成 {len(results)} 次操作")
    
    print(f"\n📊 测试结果:")
    print(f"   总操作数: {total_operations}")
    print(f"   总错误数: {total_errors}")
    print(f"   成功率: {((total_operations - total_errors) / total_operations * 100):.2f}%")
    
    # 测试2: 验证单例模式
    print("\n📋 测试2: 验证单例模式")
    
    def get_loader_instance(thread_id):
        """获取加载器实例"""
        return thread_id, id(_get_fingerprint_loader())
    
    instance_ids = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(get_loader_instance, i) for i in range(10)]
        for future in as_completed(futures):
            thread_id, instance_id = future.result()
            instance_ids.append(instance_id)
            print(f"Thread {thread_id}: 实例ID = {instance_id}")
    
    # 检查所有实例是否相同
    unique_instances = set(instance_ids)
    if len(unique_instances) == 1:
        print("✅ 单例模式工作正常，所有线程使用同一个实例")
    else:
        print(f"❌ 单例模式失败，发现 {len(unique_instances)} 个不同实例")
    
    # 测试3: 数据一致性验证
    print("\n📋 测试3: 数据一致性验证")
    
    def check_data_consistency(thread_id):
        """检查数据一致性"""
        fingerprints_1 = list_available_fingerprints()
        fingerprints_2 = list_available_fingerprints()
        
        chrome_1 = get_fingerprints_by_browser("chrome")
        chrome_2 = get_fingerprints_by_browser("chrome")
        
        return thread_id, (fingerprints_1 == fingerprints_2), (chrome_1 == chrome_2)
    
    consistency_results = []
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(check_data_consistency, i) for i in range(15)]
        for future in as_completed(futures):
            thread_id, fingerprint_consistent, chrome_consistent = future.result()
            consistency_results.append((fingerprint_consistent, chrome_consistent))
            if fingerprint_consistent and chrome_consistent:
                print(f"✅ Thread {thread_id}: 数据一致")
            else:
                print(f"❌ Thread {thread_id}: 数据不一致")
    
    # 总结一致性测试
    consistent_count = sum(1 for fp_ok, chrome_ok in consistency_results if fp_ok and chrome_ok)
    consistency_rate = consistent_count / len(consistency_results) * 100
    
    print(f"\n📊 数据一致性结果:")
    print(f"   一致性检查通过: {consistent_count}/{len(consistency_results)}")
    print(f"   一致性率: {consistency_rate:.2f}%")
    
    # 最终结论
    print("\n🎯 测试结论:")
    if total_errors == 0 and len(unique_instances) == 1 and consistency_rate == 100:
        print("✅ 所有测试通过！fingerprint_loader 是线程安全的")
        return True
    else:
        print("❌ 存在线程安全问题，需要进一步检查")
        return False

def stress_test():
    """压力测试：高并发场景"""
    print("\n🔥 开始压力测试...")
    
    def stress_worker(thread_id):
        """压力测试工作线程"""
        operations = 0
        errors = 0
        
        start_time = time.time()
        while time.time() - start_time < 5:  # 运行5秒
            try:
                # 快速连续操作
                list_available_fingerprints()
                get_fingerprints_by_browser("chrome")
                fingerprints = list_available_fingerprints()
                if fingerprints:
                    config = get_fingerprint_config(fingerprints[0])
                operations += 4
                
            except Exception as e:
                errors += 1
                print(f"Thread {thread_id} error: {e}")
        
        return thread_id, operations, errors
    
    # 启动大量线程进行压力测试
    with ThreadPoolExecutor(max_workers=200) as executor:
        futures = [executor.submit(stress_worker, i) for i in range(50)]
        
        total_ops = 0
        total_errs = 0
        
        for future in as_completed(futures):
            thread_id, ops, errs = future.result()
            total_ops += ops
            total_errs += errs
            print(f"Thread {thread_id}: {ops} 操作, {errs} 错误")
    
    print(f"\n📊 压力测试结果:")
    print(f"   总操作数: {total_ops}")
    print(f"   总错误数: {total_errs}")
    print(f"   错误率: {(total_errs / total_ops * 100):.2f}%")
    
    return total_errs == 0

if __name__ == "__main__":
    print("🚀 fingerprint_loader 线程安全测试")
    print("=" * 50)
    
    # 运行基础并发测试
    basic_test_passed = test_concurrent_access()
    
    # 运行压力测试
    stress_test_passed = stress_test()
    
    print("\n" + "=" * 50)
    print("🏁 测试总结:")
    
    if basic_test_passed and stress_test_passed:
        print("🎉 所有测试通过！fingerprint_loader 线程安全性良好")
    else:
        print("⚠️  发现线程安全问题，建议进一步优化")
        if not basic_test_passed:
            print("   - 基础并发测试失败")
        if not stress_test_passed:
            print("   - 压力测试失败")
