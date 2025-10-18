import requests
import json
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialAIService:

    
    def __init__(self):
        self.api_key_publicai = "zpka_5c1fd8b611494fc2ae0cad508d939b1e_64cd19f5"
        self.model_url_publicai = "https://api.publicai.co/v1/chat/completions"
        
        self.model_salamandra = "BSC-LT/salamandra-7b-instruct-tools-16k"
        self.model_alia = "BSC-LT/ALIA-40b-instruct_Q8_0"
        
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key_publicai}",
            "User-Agent": "FinancialAssistant/1.0"
        }
    
    def _make_api_request(self, messages: List[Dict], model: str, temperature: float = 0.7) -> Optional[str]:

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "seed": 42
        }
        
        try:
            response = requests.post(
                self.model_url_publicai, 
                headers=self.headers, 
                json=payload, 
                verify=False,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"Error in API request: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"API request exception: {str(e)}")
            return None
    
    def get_goal_advice(self, goal_title: str, goal_description: str, current_amount: float, 
                       target_amount: float, user_question: str) -> str:

        progress_percentage = (current_amount / target_amount * 100) if target_amount > 0 else 0
        remaining_amount = target_amount - current_amount
        
        system_prompt = f"""Eres un asesor financiero experto. Tu tarea es ayudar al usuario a alcanzar sus metas financieras.

Información de la meta:
- Título: {goal_title}
- Descripción: {goal_description}
- Progreso actual: {current_amount:.2f}€ de {target_amount:.2f}€ ({progress_percentage:.1f}%)
- Cantidad restante: {remaining_amount:.2f}€

Proporciona consejos prácticos, específicos y motivadores. Sé conciso pero útil."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ]
        
        response = self._make_api_request(messages, self.model_salamandra, temperature=0.7)
        
        if response:
            return response
        else:
            return "Lo siento, no pude procesar tu consulta en este momento. Por favor, inténtalo de nuevo."
    
    def analyze_financial_habits(self, transactions_data: Dict) -> str:

        system_prompt = """Eres un analista financiero experto. Analiza los datos de transacciones del usuario y proporciona insights sobre sus hábitos financieros.

Identifica:
1. Patrones de gasto
2. Oportunidades de ahorro
3. Áreas de mejora
4. Recomendaciones específicas

Sé constructivo y motivador en tus sugerencias."""

        user_prompt = f"""Analiza estos datos financieros y dame recomendaciones:

Datos de transacciones:
{json.dumps(transactions_data, indent=2, ensure_ascii=False)}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self._make_api_request(messages, self.model_alia, temperature=0.5)
        
        if response:
            return response
        else:
            return "No pude analizar tus datos financieros en este momento. Por favor, inténtalo más tarde."
    
    def create_savings_plan(self, income: float, expenses: float, goals: List[Dict]) -> str:
 
        balance = income - expenses
        savings_rate = (balance / income * 100) if income > 0 else 0
        
        system_prompt = f"""Eres un planificador financiero experto. Crea un plan de ahorro personalizado basado en la situación financiera del usuario.

Situación actual:
- Ingresos mensuales: {income:.2f}€
- Gastos mensuales: {expenses:.2f}€
- Balance disponible: {balance:.2f}€
- Tasa de ahorro actual: {savings_rate:.1f}%

Proporciona un plan detallado y realista para alcanzar las metas financieras."""

        goals_text = "\n".join([f"- {goal.get('title', 'Meta')}: {goal.get('target', 0):.2f}€" for goal in goals])
        
        user_prompt = f"""Crea un plan de ahorro para estas metas:
{goals_text}

Incluye:
1. Estrategia de ahorro mensual
2. Priorización de metas
3. Consejos para optimizar gastos
4. Timeline realista"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self._make_api_request(messages, self.model_salamandra, temperature=0.6)
        
        if response:
            return response
        else:
            return "No pude crear tu plan de ahorro en este momento. Por favor, inténtalo más tarde."
    
    def get_motivational_message(self, goal_progress: float, goal_title: str) -> str:

        if goal_progress >= 100:
            achievement_level = "completado"
        elif goal_progress >= 75:
            achievement_level = "casi completado"
        elif goal_progress >= 50:
            achievement_level = "a mitad de camino"
        elif goal_progress >= 25:
            achievement_level = "empezando bien"
        else:
            achievement_level = "recién comenzado"
        
        system_prompt = f"""Eres un coach motivacional especializado en finanzas personales. 

El usuario ha {achievement_level} su meta "{goal_title}" con un {goal_progress:.1f}% de progreso.

Proporciona un mensaje motivacional, específico y alentador. Incluye consejos prácticos para continuar o celebrar el logro."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Motívame para continuar con mi meta: {goal_title}"}
        ]
        
        response = self._make_api_request(messages, self.model_salamandra, temperature=0.8)
        
        if response:
            return response
        else:
            return f"¡Excelente progreso en tu meta '{goal_title}'! Sigue así."
    
    def divide_task_into_subtasks(self, task: str) -> str:

        system_prompt = """Eres un experto en gestión de proyectos y planificación financiera. 

Tu tarea es dividir una meta financiera en subtareas más pequeñas y manejables. Cada subtarea debe ser:
1. Específica y clara
2. Accionable
3. Con un timeline realista
4. Con indicadores de progreso

Proporciona una lista estructurada y práctica."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Divide esta meta financiera en subtareas: {task}"}
        ]
        
        response = self._make_api_request(messages, self.model_salamandra, temperature=0.5)
        
        if response:
            return response
        else:
            return f"Para la meta '{task}', te sugiero empezar por definir un presupuesto específico y establecer fechas límite claras."

    def generate_task_suggestions(self, user_description: str, financial_situation: dict = None) -> str:

        system_prompt = """Eres un asesor financiero experto especializado en crear metas financieras personalizadas.

Tu tarea es analizar la descripción del usuario y generar sugerencias de tareas financieras específicas y realistas.

Para cada sugerencia, incluye:
1. Título claro y motivador
2. Descripción detallada
3. Meta monetaria realista
4. Plazo sugerido
5. Prioridad (alta/media/baja)
6. Estrategia específica

Proporciona 3-5 sugerencias variadas y útiles."""

        context = ""
        if financial_situation:
            context = f"""
Situación financiera actual:
- Ingresos: {financial_situation.get('income', 'No especificado')}€
- Gastos: {financial_situation.get('expenses', 'No especificado')}€
- Balance: {financial_situation.get('balance', 'No especificado')}€
"""

        user_prompt = f"""Basándote en esta descripción del usuario, genera sugerencias de tareas financieras:

{context}

Descripción del usuario: {user_description}

Proporciona sugerencias específicas y accionables."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self._make_api_request(messages, self.model_salamandra, temperature=0.7)
        
        if response:
            return response
        else:
            return f"Basándome en tu descripción '{user_description}', te sugiero crear metas específicas como: ahorro de emergencia, reducción de gastos, o inversión a largo plazo."

    def create_smart_goal(self, goal_type: str, user_context: str, financial_data: dict = None) -> dict:

        system_prompt = f"""Eres un experto en planificación financiera. Crea una meta financiera específica basada en el tipo y contexto proporcionados.

Tipo de meta: {goal_type}
Contexto del usuario: {user_context}

Genera una meta completa con:
- Título motivador
- Descripción clara
- Meta monetaria realista
- Plazo apropiado
- Prioridad
- Estrategia específica

Responde en formato JSON con las siguientes claves:
title, description, target, deadline, priority, strategy"""

        context = ""
        if financial_data:
            context = f" Situación financiera: Ingresos {financial_data.get('income', 0)}€, Gastos {financial_data.get('expenses', 0)}€"

        user_prompt = f"Crea una meta financiera para: {goal_type}. Contexto: {user_context}.{context}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self._make_api_request(messages, self.model_salamandra, temperature=0.6)
        
        if response:
            try:
                import json
                return json.loads(response)
            except:
                return {
                    "title": f"Meta de {goal_type}",
                    "description": response[:200] + "..." if len(response) > 200 else response,
                    "target": 1000,
                    "deadline": "6 meses",
                    "priority": "medium",
                    "strategy": "Define tu estrategia personalizada basada en tus necesidades."
                }
        else:
            return {
                "title": f"Meta de {goal_type}",
                "description": f"Meta personalizada para {goal_type}",
                "target": 1000,
                "deadline": "6 meses",
                "priority": "medium",
                "strategy": "Define tu estrategia personalizada."
            }


ai_service = FinancialAIService()
