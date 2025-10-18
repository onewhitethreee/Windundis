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

@app.route('/dashboard')
def dashboard():
    """Ruta del dashboard después del login exitoso"""
    return render_template('dashboard.html')

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
                "message": "Token获取成功"
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

if __name__ == '__main__':
    app.run(debug=True, port=8080) 
