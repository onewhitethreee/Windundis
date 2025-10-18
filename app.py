from flask import Flask, redirect, request, jsonify, render_template
import requests
import json
from flask_cors import CORS
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from RedsysClient import RedsysClient

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:8080", "http://127.0.0.1:8080"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
}) 



@app.route('/')
def index():
    """Ruta de la página principal"""
    return render_template('index.html')

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        client = RedsysClient(env_filepath='redsys.env')
        
        redirect_url = client.get_authorization_redirect_url()
        
        if redirect_url:
            return jsonify({
                "success": True, 
                "redirect_url": redirect_url,
                "message": "URL de autorización obtenida exitosamente"
            }), 200
        else:
            return jsonify({"success": False, "error": "No se pudo obtener la URL de autorización"}), 500
    except FileNotFoundError as e:
        return jsonify({"success": False, "error": f"Archivo de configuración no encontrado: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": f"Error interno: {str(e)}"}), 500

@app.route('/api/token', methods=['POST', 'OPTIONS'])
def get_token():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        if not data or 'redirect_url' not in data:
            return jsonify({"success": False, "error": "缺少redirect_url参数"}), 400
        
        redirect_url = data['redirect_url']
        
        client = RedsysClient(env_filepath='redsys.env')
        
        # 从重定向URL中提取code
        code = client.extract_code_from_redirect_url(redirect_url)
        
        if not code:
            return jsonify({"success": False, "error": "无法从URL中提取code参数"}), 400
        
        # 使用code获取access token
        token_result = client.get_access_token(code)
        if token_result['success']:
            return jsonify({
                "success": True,
                "data": token_result['data'],
                "message": "access token obtenido exitosamente"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": token_result['error'],
                "details": token_result.get('response_text', '')
            }), 500
            
    except FileNotFoundError as e:
        return jsonify({"success": False, "error": f"Archivo de configuración no encontrado: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": f"Error interno: {str(e)}"}), 500

@app.route('/api/payment/create', methods=['POST', 'OPTIONS'])
def create_payment():
    """创建支付请求，需要用户同意"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        if not data or 'access_token' not in data:
            return jsonify({"success": False, "error": "缺少access_token参数"}), 400
        
        access_token = data['access_token']
        payment_data = data.get('payment_data', None)  # 可选的支付数据
        
        client = RedsysClient(env_filepath='redsys.env')
        print("data", data)
        # 创建支付请求
        payment_result = client.create_payment_request(access_token, payment_data)
        print("payment_result", payment_result)
        if payment_result['success']:
            payment_response = payment_result['data']
            
            # 提取用户同意URL
            sca_redirect_url = None
            if '_links' in payment_response and 'scaRedirect' in payment_response['_links']:
                sca_redirect_url = payment_response['_links']['scaRedirect']['href']
            
            return jsonify({
                "success": True,
                "data": {
                    "payment_id": payment_response.get('paymentId'),
                    "transaction_status": payment_response.get('transactionStatus'),
                    "sca_redirect_url": sca_redirect_url,
                    "links": payment_response.get('_links', {}),
                    "request_id": payment_result.get('request_id')
                },
                "message": "支付请求创建成功，需要用户同意"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": payment_result['error'],
                "details": payment_result.get('response_text', '')
            }), 500
            
    except FileNotFoundError as e:
        return jsonify({"success": False, "error": f"Archivo de configuración no encontrado: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": f"Error interno: {str(e)}"}), 500

@app.route('/api/payment/status', methods=['POST', 'OPTIONS'])
def check_payment_status():
    """检查支付状态"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        if not data or 'access_token' not in data or 'payment_id' not in data:
            return jsonify({"success": False, "error": "缺少access_token或payment_id参数"}), 400
        
        access_token = data['access_token']
        payment_id = data['payment_id']
        
        client = RedsysClient(env_filepath='redsys.env')
        
        # 检查支付状态
        status_result = client.check_payment_status(access_token, payment_id)
        
        if status_result['success']:
            return jsonify({
                "success": True,
                "data": status_result['data'],
                "message": "支付状态查询成功"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": status_result['error'],
                "details": status_result.get('response_text', '')
            }), 500
            
    except FileNotFoundError as e:
        return jsonify({"success": False, "error": f"Archivo de configuración no encontrado: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": f"Error interno: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080) 
