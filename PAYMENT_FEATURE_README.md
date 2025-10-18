# 支付测试功能说明

## 概述

在成功获取Access Token后，现在可以进行支付测试。这个功能允许你创建支付请求，获取用户同意，并查询支付状态。

## 新增功能

### 1. 后端API端点

#### `/api/payment/create` (POST)
创建支付请求，需要用户同意

**请求参数:**
```json
{
    "access_token": "your_access_token_here",
    "payment_data": {
        // 可选的支付数据，如果不提供将使用默认测试数据
    }
}
```

**响应示例:**
```json
{
    "success": true,
    "data": {
        "payment_id": "75868263-ac17-11f0-a456-d9247a3c1ddd",
        "transaction_status": "RCVD",
        "sca_redirect_url": "https://hub-i.redsys.es:16443/api-oauth-xs2a-sb/services/rest/sca/v1.1/...",
        "links": {
            "scaRedirect": {...},
            "self": {...},
            "status": {...},
            "scaStatus": {...}
        },
        "request_id": "unique-request-id"
    },
    "message": "支付请求创建成功，需要用户同意"
}
```

#### `/api/payment/status` (POST)
查询支付状态

**请求参数:**
```json
{
    "access_token": "your_access_token_here",
    "payment_id": "payment_id_here"
}
```

**响应示例:**
```json
{
    "success": true,
    "data": {
        "transactionStatus": "RCVD"
    },
    "message": "支付状态查询成功"
}
```

### 2. 前端界面

在成功获取Access Token后，界面会显示：
- Token信息
- "Crear Pago de Prueba" 按钮
- 支付创建后的用户同意界面
- 支付状态查询功能

### 3. 支付流程

1. **获取Access Token** - 通过现有的登录流程
2. **创建支付请求** - 点击"Crear Pago de Prueba"按钮
3. **用户同意** - 点击"Autorizar Pago"按钮，在新窗口中完成授权
4. **查询状态** - 点击"Verificar Estado"按钮查看支付状态

## 使用方法

### 方法1: 通过Web界面

1. 启动Flask应用: `python app.py`
2. 访问 `http://localhost:8080`
3. 点击"Iniciar Sesión"完成登录流程
4. 获取Access Token后，点击"Crear Pago de Prueba"
5. 按照界面提示完成支付测试

### 方法2: 通过API直接调用

```python
import requests

# 创建支付请求
response = requests.post('http://localhost:8080/api/payment/create', 
    json={
        'access_token': 'your_access_token_here'
    })

if response.status_code == 200:
    data = response.json()
    if data['success']:
        payment_id = data['data']['payment_id']
        sca_url = data['data']['sca_redirect_url']
        
        print(f"支付ID: {payment_id}")
        print(f"用户同意URL: {sca_url}")
        
        # 查询支付状态
        status_response = requests.post('http://localhost:8080/api/payment/status',
            json={
                'access_token': 'your_access_token_here',
                'payment_id': payment_id
            })
        
        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"支付状态: {status_data['data']['transactionStatus']}")
```

### 方法3: 使用测试脚本

1. 编辑 `test_payment.py` 文件
2. 将 `TEST_ACCESS_TOKEN` 替换为实际的access token
3. 运行测试脚本: `python test_payment.py`

## 默认支付数据

如果不提供自定义支付数据，系统将使用以下默认测试数据：

```json
{
    "instructedAmount": {
        "currency": "EUR",
        "amount": "500.00"
    },
    "debtorAccount": {
        "iban": "ES6200810602620003333338",
        "currency": "EUR"
    },
    "creditorAccount": {
        "iban": "ES2640000418401234567599",
        "currency": "EUR"
    },
    "creditorName": "Nombre Beneficiario",
    "creditorAgent": "XXXLESMMXXX",
    "creditorAddress": {
        "streetName": "Ejemplo de Calle",
        "buildingNumber": "5",
        "townName": "Cordoba",
        "postCode": "14100",
        "country": "ES"
    },
    "chargeBearer": "SHAR",
    "remittanceInformationUnstructured": "Concepto"
}
```

## 错误处理

系统包含完整的错误处理机制：

- **HTTP错误**: 显示具体的HTTP状态码和错误信息
- **API错误**: 显示API返回的错误详情
- **网络错误**: 显示连接异常信息
- **参数错误**: 显示缺少必要参数的错误

## 注意事项

1. **Access Token**: 确保使用有效的access token
2. **用户同意**: 支付创建后需要用户在新窗口中完成授权
3. **状态查询**: 可以多次查询支付状态以跟踪进度
4. **测试环境**: 这是测试环境，不会进行真实的资金转移

## 文件结构

```
├── app.py                    # 主应用文件，包含新的API端点
├── RedsysClient.py          # 客户端类，包含支付方法
├── templates/index.html     # 前端模板，包含支付界面
├── static/style.css         # 样式文件，包含支付相关样式
├── test_payment.py          # 测试脚本
└── PAYMENT_FEATURE_README.md # 本说明文档
```

## 技术实现

- **后端**: Flask + Python
- **前端**: HTML + JavaScript + CSS
- **API**: RESTful API设计
- **认证**: OAuth 2.0 + Access Token
- **支付**: Redsys PSD2 API
- **样式**: 响应式设计，支持移动端
