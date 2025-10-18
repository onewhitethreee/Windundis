from flask import Flask, redirect, request, jsonify, render_template
import requests
import json
from flask_cors import CORS
import sys
import os
from datetime import datetime
os.environ['MPLCONFIGDIR'] = os.path.join(os.path.expanduser('~'), '.config', 'matplotlib')
os.makedirs(os.environ['MPLCONFIGDIR'], exist_ok=True)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from RedsysClient import RedsysClient
from model.ALIA40b import analyze_with_charts
from ai_service import ai_service

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
        
        redirect_url = data['redirect_url']
        
        client = RedsysClient(env_filepath='redsys.env')
        
        code = client.extract_code_from_redirect_url(redirect_url)
        print("code", code)
        if not code:
            return jsonify({"success": False, "error": "No se pudo obtener el code de la URL"}), 400
        
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
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        if not data or 'access_token' not in data:
            return jsonify({"success": False, "error": "falta el access_token"}), 400
        
        access_token = data['access_token']
        payment_data = data.get('payment_data', None)  
        
        client = RedsysClient(env_filepath='redsys.env')
        payment_result = client.create_payment_request(access_token, payment_data)
        if payment_result['success']:
            payment_response = payment_result['data']
            
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
                "message": "Pago creado exitosamente, necesita autorización"
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
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        if not data or 'access_token' not in data or 'payment_id' not in data:
            return jsonify({"success": False, "error": "falta el access_token o el payment_id"}), 400
        
        access_token = data['access_token']
        payment_id = data['payment_id']
        
        client = RedsysClient(env_filepath='redsys.env')
        
        status_result = client.check_payment_status(access_token, payment_id)
        
        if status_result['success']:
            return jsonify({
                "success": True,
                "data": status_result['data'],
                "message": "Estado de pago consultado exitosamente"
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

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze_financial_data():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        if not data or 'bank_data' not in data:
            return jsonify({"success": False, "error": "falta el bank_data"}), 400
        
        bank_data = data['bank_data']
        
        result = analyze_with_charts(bank_data)
        
        charts = {}
        for chart_name, chart_path in result['charts'].items():
            if chart_path:
                relative_path = chart_path.replace('static/', '')
                charts[chart_name] = relative_path
        
        return jsonify({
            "success": True,
            "data": {
                "analysis": result['analysis'],
                "profile": result['profile'],
                "charts": charts,
                "detailed_report": result['detailed_report'],
                "simplified_text": result['simplified_text'],
                "translated_text": result['translated_text'],
                "goals": result['goals'],
                "incentives": result['incentives'],
                "transactions": result['transactions']
            },
            "message": "Análisis financiero completado exitosamente"
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error en análisis: {str(e)}"}), 500

@app.route('/api/ai/chat', methods=['POST', 'OPTIONS'])
def ai_chat():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Datos de entrada requeridos"}), 400
        
        user_question = data.get('question', '')
        goal_data = data.get('goal', {})
        
        if not user_question:
            return jsonify({"success": False, "error": "Pregunta requerida"}), 400
        
        if goal_data:
            advice = ai_service.get_goal_advice(
                goal_title=goal_data.get('title', ''),
                goal_description=goal_data.get('description', ''),
                current_amount=goal_data.get('current', 0),
                target_amount=goal_data.get('target', 0),
                user_question=user_question
            )
        else:
            advice = ai_service.get_goal_advice(
                goal_title="Consulta General",
                goal_description="Consulta general sobre finanzas",
                current_amount=0,
                target_amount=0,
                user_question=user_question
            )
        
        return jsonify({
            "success": True,
            "data": {
                "response": advice,
                "timestamp": str(datetime.now())
            },
            "message": "Respuesta AI generada exitosamente"
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error en chat AI: {str(e)}"}), 500

@app.route('/api/ai/analyze-habits', methods=['POST', 'OPTIONS'])
def analyze_financial_habits():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        if not data or 'transactions' not in data:
            return jsonify({"success": False, "error": "Datos de transacciones requeridos"}), 400
        
        transactions_data = data['transactions']
        analysis = ai_service.analyze_financial_habits(transactions_data)
        
        return jsonify({
            "success": True,
            "data": {
                "analysis": analysis,
                "timestamp": str(datetime.now())
            },
            "message": "Análisis de hábitos completado"
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error en análisis de hábitos: {str(e)}"}), 500

@app.route('/api/ai/savings-plan', methods=['POST', 'OPTIONS'])
def create_savings_plan():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Datos requeridos"}), 400
        
        income = data.get('income', 0)
        expenses = data.get('expenses', 0)
        goals = data.get('goals', [])
        
        savings_plan = ai_service.create_savings_plan(income, expenses, goals)
        
        return jsonify({
            "success": True,
            "data": {
                "savings_plan": savings_plan,
                "timestamp": str(datetime.now())
            },
            "message": "Plan de ahorro creado exitosamente"
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error creando plan de ahorro: {str(e)}"}), 500

@app.route('/api/ai/motivation', methods=['POST', 'OPTIONS'])
def get_motivation():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Datos requeridos"}), 400
        
        goal_progress = data.get('progress', 0)
        goal_title = data.get('title', 'Tu meta')
        
        motivation = ai_service.get_motivational_message(goal_progress, goal_title)
        
        return jsonify({
            "success": True,
            "data": {
                "motivation": motivation,
                "timestamp": str(datetime.now())
            },
            "message": "Mensaje motivacional generado"
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error generando motivación: {str(e)}"}), 500

@app.route('/api/ai/subtasks', methods=['POST', 'OPTIONS'])
def divide_task():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        if not data or 'task' not in data:
            return jsonify({"success": False, "error": "Tarea requerida"}), 400
        
        task = data['task']
        subtasks = ai_service.divide_task_into_subtasks(task)
        
        return jsonify({
            "success": True,
            "data": {
                "subtasks": subtasks,
                "timestamp": str(datetime.now())
            },
            "message": "Subtareas generadas exitosamente"
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error dividiendo tarea: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080) 
