#!/usr/bin/env python3
"""
DT-Study-Companion 系统测试脚本
"""
import sys
import os
import requests
import json
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_api_health():
    """测试API健康检查"""
    print("🔍 测试API健康检查...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API健康检查通过: {data['message']}")
            return True
        else:
            print(f"❌ API健康检查失败: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API连接失败: {e}")
        return False

def test_user_registration():
    """测试用户注册"""
    print("\n🔍 测试用户注册...")
    try:
        test_phone = "13800138000"
        response = requests.post(
            "http://localhost:8000/auth/register",
            json={"phone": test_phone, "nickname": "测试用户"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 用户注册成功: {data['user']['nickname']}")
            return data['token']
        else:
            print(f"❌ 用户注册失败: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ 用户注册请求失败: {e}")
        return None

def test_agent_list():
    """测试Agent列表获取"""
    print("\n🔍 测试Agent列表获取...")
    try:
        response = requests.get("http://localhost:8000/agents", timeout=5)
        if response.status_code == 200:
            data = response.json()
            agents = data['agents']
            print(f"✅ 获取到 {len(agents)} 个Agent:")
            for agent in agents:
                print(f"   - {agent['icon']} {agent['display_name']}: {agent['description']}")
            return True
        else:
            print(f"❌ 获取Agent列表失败: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 获取Agent列表请求失败: {e}")
        return False

def test_query_with_auth(token):
    """测试带认证的查询"""
    print("\n🔍 测试带认证的查询...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        query_data = {
            "query": "什么是流行病学？",
            "top_k": 3
        }
        
        response = requests.post(
            "http://localhost:8000/query?agent_name=general_medical",
            json=query_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 查询成功:")
            print(f"   问题: {data['question']}")
            print(f"   答案: {data['answer'][:100]}...")
            print(f"   置信度: {data['confidence']:.2%}")
            print(f"   来源数量: {len(data['sources'])}")
            return True
        else:
            print(f"❌ 查询失败: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 查询请求失败: {e}")
        return False

def test_user_profile(token):
    """测试用户资料获取"""
    print("\n🔍 测试用户资料获取...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            "http://localhost:8000/user/profile",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 用户资料获取成功:")
            print(f"   昵称: {data['nickname']}")
            print(f"   手机: {data['phone']}")
            return True
        else:
            print(f"❌ 用户资料获取失败: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 用户资料请求失败: {e}")
        return False

def test_system_info():
    """测试系统信息获取"""
    print("\n🔍 测试系统信息获取...")
    try:
        response = requests.get("http://localhost:8000/system/info", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 系统信息获取成功:")
            print(f"   总书籍数: {data['total_books']}")
            print(f"   总集合数: {data['total_collections']}")
            print(f"   Embedding模型: {data['embedding_model']}")
            print(f"   LLM模型: {data['llm_model']}")
            return True
        else:
            print(f"❌ 系统信息获取失败: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 系统信息请求失败: {e}")
        return False

def main():
    print("🎓 DT-Study-Companion 系统测试")
    print("=" * 50)
    
    # 等待服务器启动
    print("⏳ 等待服务器启动...")
    time.sleep(2)
    
    # 执行测试
    tests = [
        ("API健康检查", test_api_health),
        ("Agent列表获取", test_agent_list),
        ("系统信息获取", test_system_info),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    # 测试需要认证的功能
    print("\n" + "=" * 50)
    print("🔐 测试需要认证的功能...")
    
    token = test_user_registration()
    if token:
        auth_tests = [
            ("用户资料获取", lambda: test_user_profile(token)),
            ("带认证查询", lambda: test_query_with_auth(token)),
        ]
        
        for test_name, test_func in auth_tests:
            try:
                if test_func():
                    passed += 1
                total += 1
            except Exception as e:
                print(f"❌ {test_name} 测试异常: {e}")
                total += 1
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)
    print(f"通过: {passed}/{total}")
    print(f"成功率: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 所有测试通过！系统运行正常")
        return 0
    else:
        print("⚠️  部分测试失败，请检查系统配置")
        return 1

if __name__ == "__main__":
    sys.exit(main())