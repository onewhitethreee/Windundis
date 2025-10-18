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
            return jsonify({"success": False, "error": "未能获取授权URL"}), 500
    except FileNotFoundError as e:
        print(f"配置文件错误: {e}")
        return jsonify({"success": False, "error": f"配置文件未找到: {str(e)}"}), 500
    except Exception as e:
        print(f"服务器错误: {e}")
        return jsonify({"success": False, "error": f"服务器内部错误: {str(e)}"}), 500

if __name__ == '__main__':
    # 在生产环境中，你需要使用 Gunicorn 或 uWSGI 等 WSGI 服务器
    app.run(debug=True, port=8080) # debug=True 会在代码修改后自动重启服务器，方便开发
