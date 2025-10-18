# 用户输入参数功能说明

## 概述

现在用户可以在网页前端输入自定义的支付参数，而不必使用固定的默认值。这提供了更大的灵活性和测试能力。

## 新增功能

### 1. 支付参数输入表单

在成功获取Access Token后，用户可以看到一个完整的支付参数输入表单，包含以下字段：

#### 基本支付信息
- **Cantidad (EUR)**: 支付金额（欧元）
- **IBAN Deudor**: 付款人IBAN账户
- **IBAN Acreedor**: 收款人IBAN账户

#### 收款人信息
- **Nombre Acreedor**: 收款人姓名
- **Código Acreedor**: 收款人代码
- **Concepto**: 支付说明/概念

#### 收款人地址信息
- **Calle**: 街道名称
- **Número**: 门牌号
- **Ciudad**: 城市
- **Código Postal**: 邮政编码

### 2. 表单验证功能

#### 实时验证
- **金额验证**: 必须是正数
- **IBAN验证**: 验证西班牙IBAN格式（ES开头，24位数字）
- **必填字段验证**: 所有字段都必须填写
- **格式验证**: 自动转换IBAN为大写格式

#### 错误提示
- 显示详细的错误信息
- 高亮显示有问题的字段
- 阻止无效数据提交

### 3. 用户界面功能

#### 操作按钮
- **"Usar Valores por Defecto"**: 重置所有字段为默认值
- **"Crear Pago de Prueba"**: 使用当前输入创建支付请求

#### 响应式设计
- 桌面端：两列布局
- 平板端：单列布局
- 移动端：优化的触摸界面

## 使用方法

### 1. 基本使用流程

1. **获取Access Token**: 完成登录流程
2. **填写支付参数**: 在表单中输入所需的支付信息
3. **验证数据**: 系统会自动验证输入的数据
4. **创建支付**: 点击"Crear Pago de Prueba"按钮
5. **完成授权**: 按照提示完成用户授权

### 2. 表单操作

#### 自定义输入
```
1. 修改金额: 在"Cantidad"字段输入新的金额
2. 更改IBAN: 输入不同的付款人或收款人IBAN
3. 更新信息: 修改收款人姓名、地址等信息
4. 点击创建: 使用新数据创建支付请求
```

#### 重置为默认值
```
1. 点击"Usar Valores por Defecto"按钮
2. 所有字段将恢复为预设的测试值
3. 可以重新开始自定义输入
```

### 3. 数据验证规则

#### IBAN验证
- 必须以"ES"开头
- 总长度必须为24位
- 后22位必须为数字
- 自动转换为大写格式

#### 金额验证
- 必须是正数
- 支持小数点后两位
- 最大值：999,999.99 EUR

#### 文本字段验证
- 所有文本字段都不能为空
- 自动去除首尾空格
- 长度限制根据API要求设置

## 技术实现

### 1. 前端实现

#### HTML结构
```html
<div class="payment-form">
    <div class="form-row">
        <div class="form-group">
            <label for="amount">Cantidad (EUR):</label>
            <input type="number" id="amount" name="amount" value="500.00">
        </div>
        <!-- 更多字段... -->
    </div>
</div>
```

#### JavaScript功能
```javascript
// 获取表单数据
function getPaymentFormData() {
    // 收集所有输入值
    // 验证数据格式
    // 返回结构化的支付数据
}

// 表单验证
function validatePaymentForm() {
    // 验证每个字段
    // 显示错误信息
    // 返回验证结果
}
```

### 2. 后端集成

#### API调用
```javascript
fetch('/api/payment/create', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        access_token: accessToken,
        payment_data: userInputData  // 用户输入的数据
    })
})
```

#### 数据格式
```json
{
    "instructedAmount": {
        "currency": "EUR",
        "amount": "用户输入的金额"
    },
    "debtorAccount": {
        "iban": "用户输入的付款人IBAN",
        "currency": "EUR"
    },
    "creditorAccount": {
        "iban": "用户输入的收款人IBAN",
        "currency": "EUR"
    },
    "creditorName": "用户输入的收款人姓名",
    "creditorAgent": "用户输入的收款人代码",
    "creditorAddress": {
        "streetName": "用户输入的街道",
        "buildingNumber": "用户输入的门牌号",
        "townName": "用户输入的城市",
        "postCode": "用户输入的邮编",
        "country": "ES"
    },
    "chargeBearer": "SHAR",
    "remittanceInformationUnstructured": "用户输入的概念"
}
```

## 样式设计

### 1. 表单样式
- **背景**: 浅灰色背景，突出表单区域
- **边框**: 圆角边框，现代化设计
- **间距**: 合理的字段间距和边距

### 2. 输入框样式
- **默认状态**: 浅灰色边框
- **聚焦状态**: 蓝色边框和阴影效果
- **有效状态**: 绿色边框
- **错误状态**: 红色边框和背景

### 3. 按钮样式
- **主要按钮**: 蓝色渐变，用于创建支付
- **次要按钮**: 灰色渐变，用于重置表单
- **悬停效果**: 上移和阴影变化

## 错误处理

### 1. 客户端验证
- 实时字段验证
- 提交前完整验证
- 清晰的错误提示

### 2. 常见错误
- **金额错误**: "La cantidad debe ser un número positivo"
- **IBAN错误**: "IBAN del deudor/acreedor no es válido"
- **必填字段**: "El campo es obligatorio"

### 3. 错误显示
- 弹窗显示所有错误
- 字段高亮显示问题
- 阻止无效提交

## 测试建议

### 1. 功能测试
- 测试所有字段的输入和验证
- 测试重置功能
- 测试不同金额和IBAN组合

### 2. 边界测试
- 测试最大/最小金额
- 测试无效IBAN格式
- 测试空字段提交

### 3. 用户体验测试
- 测试响应式布局
- 测试移动端操作
- 测试错误提示清晰度

## 注意事项

1. **数据安全**: 所有输入数据都会发送到后端API
2. **格式要求**: 严格按照API要求格式化数据
3. **验证规则**: 遵循西班牙银行系统的IBAN规则
4. **用户体验**: 提供清晰的错误提示和操作反馈

## 文件更新

以下文件已更新以支持用户输入功能：

- `templates/index.html`: 添加表单HTML和JavaScript逻辑
- `static/style.css`: 添加表单样式和响应式设计
- `app.py`: 后端API已支持接收用户输入数据
- `RedsysClient.py`: 支付方法已支持自定义数据

现在用户可以完全自定义支付参数，提供更灵活的测试环境！
