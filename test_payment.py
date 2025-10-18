"""
测试支付功能的脚本
这个脚本演示了如何使用新添加的支付API端点
"""

import requests
import json
import time

# 配置
BASE_URL = "http://localhost:8080"
TEST_ACCESS_TOKEN = "c8630377-ac18-11f0-a4fd-458bb471463d"  # 需要替换为实际的access token

def test_payment_creation():
    """测试支付创建功能"""
    print("=== 测试支付创建 ===")
    
    url = f"{BASE_URL}/api/payment/create"
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'access_token': TEST_ACCESS_TOKEN
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                payment_id = result['data']['payment_id']
                print(f"✅ 支付创建成功! Payment ID: {payment_id}")
                return payment_id
            else:
                print(f"❌ 支付创建失败: {result.get('error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    return None

def test_payment_status(payment_id):
    """测试支付状态查询功能"""
    print("\n=== 测试支付状态查询 ===")
    
    url = f"{BASE_URL}/api/payment/status"
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'access_token': TEST_ACCESS_TOKEN,
        'payment_id': payment_id
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                status = result['data'].get('transactionStatus', 'Unknown')
                print(f"✅ 状态查询成功! 当前状态: {status}")
                return True
            else:
                print(f"❌ 状态查询失败: {result.get('error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    return False

def main():
    """主测试函数"""
    print("🚀 开始测试支付功能...")
    print(f"测试服务器: {BASE_URL}")
    print(f"测试Token: {TEST_ACCESS_TOKEN[:20]}..." if len(TEST_ACCESS_TOKEN) > 20 else f"测试Token: {TEST_ACCESS_TOKEN}")
    
    # 检查服务器是否运行
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ 服务器运行正常")
        else:
            print(f"⚠️ 服务器响应异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        print("请确保Flask应用正在运行 (python app.py)")
        return
    
    # 测试支付创建
    payment_id = test_payment_creation()
    
    if payment_id:
        # 等待一下再查询状态
        print("\n⏳ 等待3秒后查询状态...")
        time.sleep(3)
        
        # 测试支付状态查询
        test_payment_status(payment_id)
    
    print("\n🏁 测试完成!")

if __name__ == "__main__":
    print("=" * 50)
    print("支付功能测试脚本")
    print("=" * 50)
    print()
    print("使用说明:")
    print("1. 确保Flask应用正在运行 (python app.py)")
    print("2. 将TEST_ACCESS_TOKEN替换为实际的access token")
    print("3. 运行此脚本: python test_payment.py")
    print()
    
    if TEST_ACCESS_TOKEN == "your_access_token_here":
        print("⚠️ 请先设置有效的TEST_ACCESS_TOKEN")
        print("你可以通过以下步骤获取access token:")
        print("1. 访问 http://localhost:8080")
        print("2. 点击'Iniciar Sesión'按钮")
        print("3. 完成授权流程")
        print("4. 复制返回的access token")
        print("5. 更新此脚本中的TEST_ACCESS_TOKEN变量")
    else:
        main()
