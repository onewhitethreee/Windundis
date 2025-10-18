from flask import Flask, request, jsonify, render_template
import requests
import json
from flask_cors import CORS 

app = Flask(__name__)
CORS(app) 


BASE_BANK_API_URL = "https://your-bank-api.com/v1" # 假设的银行 API 基础 URL
API_KEY = "your_super_secret_api_key" # 你的 API 密钥

# --- 辅助函数：调用银行 API ---
def call_bank_api(endpoint, method="GET", data=None):
    url = f"{BASE_BANK_API_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {API_KEY}", # 根据你的 API 认证方式调整
        "Content-Type": "application/json"
    }

    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=data)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            return {"error": f"Unsupported HTTP method: {method}"}, 400

        response.raise_for_status()
        return response.json(), 200
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else 500
        try:
            error_details = e.response.json()
        except json.JSONDecodeError:
            error_details = {"message": e.response.text}
        return {"error": f"API call failed (HTTP Error {status_code}): {e}", "details": error_details}, status_code
    except requests.exceptions.RequestException as e:
        return {"error": f"API call failed (Network Error): {e}"}, 500
    except json.JSONDecodeError:
        return {"error": f"API returned non-JSON response: {response.text}"}, 500
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}, 500

# --- Flask 路由 (API 端点) ---

@app.route('/')
def index():
    """首页路由"""
    return render_template('index.html')

@app.route('/api/accounts/<customer_id>', methods=['GET'])
def get_account_data(customer_id):
    if not customer_id:
        return jsonify({"error": "Customer ID is required."}), 400
    
    # 调用银行 API
    result, status = call_bank_api(f"/accounts/{customer_id}")
    return jsonify(result), status

@app.route('/api/transfer', methods=['POST'])
def handle_transfer():
    data = request.get_json()
    sender_account_id = data.get("sender_account_id")
    recipient_account_id = data.get("recipient_account_id")
    amount = data.get("amount")
    description = data.get("description", "")

    if not all([sender_account_id, recipient_account_id, amount]):
        return jsonify({"error": "Missing required fields for transfer."}), 400
    if not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({"error": "Invalid amount for transfer."}), 400

    transfer_payload = {
        "sender_account_id": sender_account_id,
        "recipient_account_id": recipient_account_id,
        "amount": amount,
        "currency": "USD", # 假设货币
        "description": description
    }
    
    # 调用银行 API
    result, status = call_bank_api("/transactions/transfer", method="POST", data=transfer_payload)
    return jsonify(result), status

@app.route('/api/purchase', methods=['POST'])
def handle_purchase():
    data = request.get_json()
    customer_account_id = data.get("account_id")
    merchant_id = data.get("merchant_id")
    item_name = data.get("item_name")
    price = data.get("amount")

    if not all([customer_account_id, merchant_id, item_name, price]):
        return jsonify({"error": "Missing required fields for purchase."}), 400
    if not isinstance(price, (int, float)) or price <= 0:
        return jsonify({"error": "Invalid price for purchase."}), 400
    
    purchase_payload = {
        "account_id": customer_account_id,
        "merchant_id": merchant_id,
        "item_name": item_name,
        "amount": price,
        "currency": "USD" # 假设货币
    }

    # 调用银行 API
    result, status = call_bank_api("/purchases", method="POST", data=purchase_payload)
    return jsonify(result), status

if __name__ == '__main__':
    # 在生产环境中，你需要使用 Gunicorn 或 uWSGI 等 WSGI 服务器
    app.run(debug=True, port=8080) # debug=True 会在代码修改后自动重启服务器，方便开发
