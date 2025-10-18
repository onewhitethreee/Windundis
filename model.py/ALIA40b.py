import requests
import json
from collections import defaultdict
from typing import List, Tuple, Dict
from datetime import datetime
import re

# =================================================================
# --- CONFIGURACIÓN ---
# =================================================================

API_KEY_PUBLICAI = "zpka_5c1fd8b611494fc2ae0cad508d939b1e_64cd19f5"
MODEL_URL_PUBLICAI = "https://api.publicai.co/v1/chat/completions"
MODEL_CLASSIFICATION = "BSC-LT/ALIA-40b-instruct_Q8_0"
MODEL_SIMPLIFICATION = "BSC-LT/salamandra-7b-instruct-tools-16k"
MODEL_TRANSLATION_EU = "HiTZ/Latxa-Llama-3.1-8B-Instruct"

API_KEY_LATXA = "SabadellHackathon2025"
MODEL_URL_LATXA = "http://hackathon.hitz.eus/v1/chat/completions"

# =================================================================
# --- HEURÍSTICAS DE CLASIFICACIÓN (PRE-CLASIFICACIÓN) ---
# =================================================================

KEYWORD_RULES = {
    "Comida | Supermercado": ["carrefour", "mercadona", "lidl", "aldi", "día", "eroski", "super"],
    "Comida | Restaurante": ["restaurante", "pizzería", "burger", "sushi", "asador", "grill", "taberna"],
    "Comida | Bar/Café": ["café", "bar", "caffe", "coffee", "terraza", "pub"],
    "Comida | Delivery": ["deliveroo", "just eat", "uber eats", "glovo", "pedidos"],
    "Transporte | Combustible": ["repsol", "cepsa", "esso", "gasolina", "gasoil", "combustible"],
    "Transporte | Taxi/Uber": ["uber", "cabify", "bolt", "taxi"],
    "Transporte | Transporte público": ["renfe", "autobús", "metro", "transporte", "ave"],
    "Servicios | Suscripción streaming": ["netflix", "spotify", "hbo", "prime video", "disney+", "twitch"],
    "Servicios | Internet/Telefonía": ["vodafone", "movistar", "orange", "telefónica", "jazztel", "internet"],
    "Servicios | Peluquería": ["peluquería", "barbería", "salón", "corte de pelo"],
    "Servicios | Facturas": ["factura", "recibo", "suministro", "agua", "luz", "gas", "eléctrico"],
    "Servicios | Gimnasio": ["gimnasio", "gym", "fitness", "deporte", "pilates", "yoga"],
    "Servicios | Reparaciones": ["reparación", "mecánico", "técnico", "mantenimiento", "arreglo"],
    "Compras | Ropa": ["decathlon", "zara", "h&m", "mango", "pull&bear", "ropa", "calzado"],
    "Compras | Electrónica": ["mediamarkt", "fnac", "pccomponentes", "electrónica", "móvil", "ordenador"],
    "Compras | Libros": ["casa del libro", "amazon", "librería", "libro"],
    "Compras | Hogar": ["ikea", "carrefour home", "muebles", "hogar"],
    "Ocio | Cine/Entretenimiento": ["cine", "yelmo", "cinesa", "películas"],
    "Ocio | Conciertos": ["ticketmaster", "concierto", "festival", "música en vivo"],
    "Ocio | Viajes": ["booking", "airbnb", "expedia", "despegar", "viaje", "hotel"],
    "Ocio | Deportes": ["deporte", "entradas", "pase"],
}

def pre_classify_by_keywords(description: str) -> str:
    """
    Pre-clasifica por palabras clave antes de llamar a la API.
    Retorna clasificación si coincide, None si no.
    """
    desc_lower = description.lower()
    
    for classification, keywords in KEYWORD_RULES.items():
        for keyword in keywords:
            if keyword in desc_lower:
                return classification
    
    return None


# =================================================================
# --- ETAPA 0: PARSING DE TRANSACCIONES BANCARIAS ---
# =================================================================

def parse_bank_transactions(bank_data: Dict) -> List[Tuple[str, float, str]]:
    """
    Extrae transacciones del formato bancario JSON.
    Normaliza signos: ingresos (+), gastos (−).
    """
    transactions = []
    
    if "transactions" not in bank_data or "booked" not in bank_data["transactions"]:
        return transactions
    
    for txn in bank_data["transactions"]["booked"]:
        try:
            amount_str = txn.get("transactionAmount", {}).get("amount", "0")
            amount = float(amount_str)
            booking_date = txn.get("bookingDate", "")
            
            description = ""
            
            if "creditorName" in txn and txn["creditorName"]:
                description = f"{txn['creditorName']}"
            elif "debtorName" in txn and txn["debtorName"]:
                description = f"{txn['debtorName']}"
            else:
                description = txn.get("remittanceInformationUnstructured", "Transacción bancaria")
            
            # Limpieza de caracteres especiales
            description = description.replace("&W", "").replace("&N", "").replace("&A", "")
            description = description.replace("/DB/", " ").replace("/CB/", " ").replace("/TXT/", "")
            description = re.sub(r'\s+', ' ', description).strip()
            
            transactions.append((description, amount, booking_date))
            
        except Exception as e:
            print(f"Error procesando transacción: {e}")
            continue
    
    return transactions


# =================================================================
# --- ETAPA 1: CLASIFICACIÓN MEJORADA ---
# =================================================================

def classify_transaction(description: str, amount: float, date: str) -> str:
    """
    Clasifica transacción con:
    1. Pre-clasificación por keywords
    2. Contexto de monto y fecha en prompt
    3. Validación estricta de formato
    """
    
    # Intenta pre-clasificación
    pre_class = pre_classify_by_keywords(description)
    if pre_class:
        return pre_class
    
    # Contexto para el modelo
    amount_sign = "ingreso" if amount >= 0 else "gasto"
    
    system_prompt = f"""Eres un clasificador de transacciones EXACTO.

Contexto: Esta es una transacción de {amount_sign} de {abs(amount):.2f}€ el {date}.

RESPONDE EXACTAMENTE CON UNO DE ESTOS FORMATOS:

INGRESOS | Salario
INGRESOS | Dividendos
INGRESOS | Reembolso
INGRESOS | Transferencia recibida

COMIDA | Supermercado
COMIDA | Restaurante
COMIDA | Bar/Café
COMIDA | Delivery

TRANSPORTE | Combustible
TRANSPORTE | Taxi/Uber
TRANSPORTE | Transporte público
TRANSPORTE | Mantenimiento vehículo

OCIO | Cine/Entretenimiento
OCIO | Viajes
OCIO | Conciertos
OCIO | Deportes

SERVICIOS | Peluquería
SERVICIOS | Suscripción streaming
SERVICIOS | Internet/Telefonía
SERVICIOS | Facturas
SERVICIOS | Gimnasio
SERVICIOS | Reparaciones

COMPRAS | Ropa
COMPRAS | Electrónica
COMPRAS | Libros
COMPRAS | Hogar

BANCA | Comisión
BANCA | Intereses

Si no estás seguro: Sin identificar | General

SOLO EL FORMATO "Categoría | Sub-tipo". NADA MÁS."""
    
    payload = {
        "model": MODEL_CLASSIFICATION,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Clasifica: {description}"}
        ],
        "temperature": 0.0,
        "seed": 42
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY_PUBLICAI}",
        "User-Agent": "FinanceExpert/1.0"
    }
    
    try:
        response = requests.post(MODEL_URL_PUBLICAI, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        classification = result["choices"][0]["message"]["content"].strip()
        
        # Validar formato
        if "|" not in classification:
            return "Sin identificar | General"
        
        parts = classification.split("|")
        if len(parts) != 2:
            return "Sin identificar | General"
        
        category = parts[0].strip().upper()
        subtype = parts[1].strip()
        
        valid_categories = ["INGRESOS", "COMIDA", "TRANSPORTE", "OCIO", "SERVICIOS", "COMPRAS", "BANCA", "SIN IDENTIFICAR"]
        
        if category not in valid_categories:
            return "Sin identificar | General"
        
        if category == "SIN IDENTIFICAR":
            return "Sin identificar | General"
        
        return f"{category.capitalize()} | {subtype}"
        
    except Exception as e:
        print(f"Error en clasificación: {e}")
        return "Sin identificar | General"


# =================================================================
# --- ETAPA 2: ANÁLISIS Y AGREGACIÓN ---
# =================================================================

def analyze_transactions(classified_transactions: List[Tuple[str, float, str]]) -> Dict:
    """
    Procesa transacciones y genera estadísticas.
    Normaliza ingresos (+) y gastos (−).
    """
    category_totals = defaultdict(float)
    category_count = defaultdict(int)
    date_range = {"start": None, "end": None}
    all_amounts = []
    
    for classification, amount, date_str in classified_transactions:
        category = classification.split(" | ")[0].strip()
        category_totals[category] += amount
        category_count[category] += 1
        all_amounts.append(amount)
        
        if date_str:
            if not date_range["start"] or date_str < date_range["start"]:
                date_range["start"] = date_str
            if not date_range["end"] or date_str > date_range["end"]:
                date_range["end"] = date_str
    
    # Ingresos son positivos, gastos son negativos
    total_income = sum(v for v in category_totals.values() if v > 0)
    total_expenses = sum(abs(v) for v in category_totals.values() if v < 0)
    balance = total_income - total_expenses
    
    # Volatilidad del gasto
    expenses_list = [abs(v) for k, v in category_totals.items() if k != "Ingresos" and v < 0]
    expense_volatility = 0
    if len(expenses_list) > 1:
        mean_expense = sum(expenses_list) / len(expenses_list)
        variance = sum((x - mean_expense) ** 2 for x in expenses_list) / len(expenses_list)
        expense_volatility = variance ** 0.5  # Desviación estándar
    
    # Categoría con mayor gasto
    top_expense_category = ""
    max_expense = 0
    for cat, total in category_totals.items():
        if cat != "Ingresos" and abs(total) > max_expense:
            max_expense = abs(total)
            top_expense_category = cat
    
    top_percentage = (max_expense / total_expenses * 100) if total_expenses > 0 else 0
    
    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "balance": balance,
        "category_totals": dict(category_totals),
        "category_count": dict(category_count),
        "top_expense_category": top_expense_category,
        "top_expense_amount": max_expense,
        "top_percentage": top_percentage,
        "transaction_count": len(classified_transactions),
        "date_range": date_range,
        "expense_volatility": expense_volatility
    }


def generate_detailed_report(analysis: Dict) -> str:
    """
    Genera reporte financiero técnico.
    Mantiene números y fechas exactas.
    """
    report = "ANÁLISIS FINANCIERO DETALLADO\n"
    report += "=" * 60 + "\n\n"
    
    if analysis["date_range"]["start"]:
        report += f"Período: {analysis['date_range']['start']} a {analysis['date_range']['end']}\n"
    
    report += f"Transacciones: {analysis['transaction_count']}\n"
    report += f"Ingresos: +{analysis['total_income']:.2f}€\n"
    report += f"Gastos: -{analysis['total_expenses']:.2f}€\n"
    report += f"Balance: {analysis['balance']:+.2f}€\n"
    report += f"Volatilidad de gasto: {analysis['expense_volatility']:.2f}€\n\n"
    
    if analysis['top_expense_category']:
        report += f"Mayor categoría de gasto: {analysis['top_expense_category']} (−{analysis['top_expense_amount']:.2f}€, {analysis['top_percentage']:.1f}%)\n\n"
    
    report += "Gastos por categoría:\n"
    sorted_cats = sorted(analysis['category_totals'].items(), 
                        key=lambda x: abs(x[1]), reverse=True)
    for category, total in sorted_cats:
        count = analysis['category_count'].get(category, 0)
        sign = "+" if total >= 0 else "−"
        report += f"{category}: {sign}{abs(total):.2f}€ ({count} trans.)\n"
    
    return report


# =================================================================
# --- ETAPA 3: ANÁLISIS DE PERFIL AVANZADO ---
# =================================================================

def analyze_financial_profile(analysis: Dict) -> Dict:
    """
    Análisis avanzado del perfil con nuevas métricas.
    """
    total_income = analysis["total_income"]
    total_expenses = analysis["total_expenses"]
    balance = analysis["balance"]
    category_totals = analysis["category_totals"]
    expense_volatility = analysis["expense_volatility"]
    
    if total_income > 0:
        expense_ratio = (total_expenses / total_income) * 100
    else:
        expense_ratio = 0
    
    # Ratios 50-30-20
    ideal_essentials = total_income * 0.50
    ideal_discretionary = total_income * 0.30
    ideal_savings = total_income * 0.20
    
    # Gastos reales por tipo
    essentials = abs(category_totals.get("Comida", 0)) + abs(category_totals.get("Servicios", 0)) + abs(category_totals.get("Banca", 0))
    discretionary = abs(category_totals.get("Ocio", 0)) + abs(category_totals.get("Compras", 0))
    transportation = abs(category_totals.get("Transporte", 0))
    actual_savings = balance if balance > 0 else 0
    
    # Ratio de dependencia (si hay ingresos variables)
    income_dependency = "Ingresos fijos" if total_income > 0 else "Sin ingresos"
    
    # Índice de ahorro constante
    savings_consistency = "Alto" if expense_volatility < 50 else "Medio" if expense_volatility < 150 else "Bajo"
    
    # Clasificación avanzada de perfil
    profile_type = classify_advanced_profile(total_income, balance, expense_ratio, 
                                             expense_volatility, category_totals)
    
    recommendations = []
    alerts = []
    
    if total_expenses > total_income and total_income > 0:
        alerts.append("Estás gastando más de lo que ingresas")
    
    if essentials > ideal_essentials and total_income > 0:
        overrun = essentials - ideal_essentials
        recommendations.append(f"Reduce gastos esenciales {overrun:.2f}€ negociando servicios.")
    
    if discretionary > ideal_discretionary and total_income > 0:
        overrun = discretionary - ideal_discretionary
        recommendations.append(f"Reduce ocio y compras {overrun:.2f}€ para equilibrar.")
    
    if expense_volatility > 150:
        recommendations.append(f"Tu gasto es muy variable ({expense_volatility:.2f}€). Intenta estabilizarlo.")
    
    if actual_savings < ideal_savings and total_income > 0 and balance >= 0:
        shortfall = ideal_savings - actual_savings
        recommendations.append(f"Intenta ahorrar {shortfall:.2f}€ más congelando pequeños gastos.")
    
    return {
        "expense_ratio": expense_ratio,
        "ideal_essentials": ideal_essentials,
        "ideal_discretionary": ideal_discretionary,
        "ideal_savings": ideal_savings,
        "actual_essentials": essentials,
        "actual_discretionary": discretionary,
        "actual_transportation": transportation,
        "actual_savings": actual_savings,
        "recommendations": recommendations,
        "alerts": alerts,
        "profile_type": profile_type,
        "income_dependency": income_dependency,
        "savings_consistency": savings_consistency,
        "expense_volatility": expense_volatility
    }


def classify_advanced_profile(total_income: float, balance: float, expense_ratio: float, 
                              volatility: float, category_totals: Dict) -> str:
    """
    Clasificación avanzada de perfiles.
    """
    if total_income == 0:
        return "Sin ingresos"
    
    savings_ratio = balance / total_income
    discretionary = abs(category_totals.get("Ocio", 0)) + abs(category_totals.get("Compras", 0))
    discretionary_ratio = discretionary / total_income if total_income > 0 else 0
    
    # Lógica de clasificación
    if balance < 0:
        return "Gasto excesivo"
    elif savings_ratio > 0.25 and volatility < 50:
        return "Ahorrador constante"
    elif savings_ratio > 0.20:
        return "Ahorrador"
    elif savings_ratio > 0.10 and volatility < 100:
        return "Equilibrado prudente"
    elif savings_ratio > 0.10:
        return "Equilibrado"
    elif discretionary_ratio > 0.20 and volatility > 150:
        return "Impulsivo"
    elif savings_ratio > 0:
        return "Conservador"
    else:
        return "Sin ahorros"


# =================================================================
# --- ETAPA 4: VERIFICACIÓN DE COMPLEJIDAD ---
# =================================================================

def check_text_complexity(text: str) -> float:
    """
    Verifica complejidad del texto.
    """
    technical_words = ['análisis', 'estadísticas', 'ingresos', 'egresos', 'categoría',
                       'porcentaje', 'desglose', 'transacciones', 'balance', 'neto',
                       'tendencia', 'presupuestaria', 'período', 'volatilidad']
    
    words = text.lower().split()
    if not words:
        return 0.5
    
    avg_word_length = sum(len(w) for w in words) / len(words)
    technical_ratio = sum(1 for w in words if any(tech in w for tech in technical_words)) / len(words)
    
    complexity_score = (min(avg_word_length / 10, 1.0) * 0.5 + technical_ratio * 0.5)
    return min(complexity_score, 1.0)


# =================================================================
# --- ETAPA 5: SIMPLIFICACIÓN NARRATIVA MEJORADA ---
# =================================================================

def simplify_text(complex_text: str) -> str:
    """
    Convierte análisis en explicación conversacional.
    Mantiene números y fechas exactas.
    """
    system_prompt = """Eres un asesor financiero personal que explica el estado de cuentas.

Tu tarea: Transforma el análisis en una EXPLICACIÓN CONVERSACIONAL natural.

REGLAS CRÍTICAS:
- No inventes cifras ni categorías. Mantén TODOS los números y fechas exactas del texto original.
- Cero aproximaciones: si dice 1959.62€, escribe 1959.62€
- Tono informal, cercano, como hablando con un amigo
- Estructura narrativa: cuenta una historia, no enumeres datos
- Usa "has gastado", "has recibido", "tu saldo"
- 1-2 párrafos máximo, frases completas naturales
- Destaca lo importante de forma natural en la conversación

Ejemplo correcto:
"Durante este período recibiste 2500€ exactos y gastaste 540.38€. Lo que más destaca es que tu gasto principal fue −317.49€ en categorías varias. Tu saldo final es muy positivo: 1959.62€, así que vas muy bien."

SOLO la explicación, sin encabezados, sin formato especial, sin emojis."""
    
    payload = {
        "model": MODEL_SIMPLIFICATION,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Explica mi situación financiera exactamente:\n\n{complex_text}"}
        ],
        "temperature": 0.5,
        "seed": 42
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY_PUBLICAI}",
        "User-Agent": "FinanceExpert/1.0"
    }
    
    try:
        response = requests.post(MODEL_URL_PUBLICAI, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        result = response.json()
        simplified = result["choices"][0]["message"]["content"].strip()
        return simplified
    except Exception as e:
        print(f"Error en simplificación: {e}")
        return complex_text


# =================================================================
# --- ETAPA 6: TRADUCCIÓN A EUSKERA ---
# =================================================================

def translate_to_basque(text: str) -> str:
    """
    Traduce a Euskera usando Latxa.
    """
    system_prompt = """Eres traductor experto español-euskera.
Tu tarea: Traduce el texto manteniendo números y estructura.
SOLO la traducción, sin explicaciones."""
    
    payload = {
        "model": MODEL_TRANSLATION_EU,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Traduce al euskera:\n\n{text}"}
        ]
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY_LATXA}",
        "User-Agent": "FinanceExpert/1.0"
    }
    
    try:
        response = requests.post(MODEL_URL_LATXA, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        result = response.json()
        translation = result["choices"][0]["message"]["content"].strip()
        return translation
    except Exception as e:
        print(f"Error en traducción: {e}")
        return text


# =================================================================
# --- GENERACIÓN DE METAS E INCENTIVOS AVANZADOS ---
# =================================================================

def generate_personalized_goals(profile: Dict, analysis: Dict) -> List[str]:
    """
    Metas personalizadas según el perfil avanzado.
    """
    goals = []
    
    goals.append("META 1: Ajusta tu presupuesto al ratio 50-30-20")
    goals.append(f"  Essentials (50%): {profile['ideal_essentials']:.2f}€ vs {profile['actual_essentials']:.2f}€ (actual)")
    goals.append(f"  Ocio (30%): {profile['ideal_discretionary']:.2f}€ vs {profile['actual_discretionary']:.2f}€ (actual)")
    goals.append(f"  Ahorros (20%): {profile['ideal_savings']:.2f}€ vs {profile['actual_savings']:.2f}€ (actual)")
    
    if profile["profile_type"] == "Ahorrador constante":
        goals.append("\nMETA 2: Optimiza tu disciplina")
        goals.append("  Tu consistencia es excepcional. Considera invertir parte de tus ahorros.")
    elif profile["profile_type"] == "Ahorrador":
        goals.append("\nMETA 2: Mantén la disciplina")
        goals.append("  Vas muy bien. Intenta aumentar inversiones a largo plazo.")
    elif profile["profile_type"] == "Equilibrado prudente":
        goals.append("\nMETA 2: Estabiliza tu gasto")
        goals.append("  Equilibrio perfecto. Continúa monitoreando mensualmente.")
    elif profile["profile_type"] == "Impulsivo":
        goals.append("\nMETA 2: Controla impulsos de gasto")
        goals.append("  Tu gasto es muy variable. Establece presupuestos mensuales estrictos.")
    elif profile["profile_type"] == "Gasto excesivo":
        goals.append("\nMETA 2: Reduce gastos inmediatamente")
        goals.append("  Estás en números rojos. Acciones urgentes necesarias.")
    else:
        goals.append("\nMETA 2: Aumenta capacidad de ahorro")
        goals.append("  Reduce gastos no esenciales gradualmente.")
    
    if analysis["top_expense_category"]:
        category = analysis["top_expense_category"]
        amount = analysis["top_expense_amount"]
        reduction = amount * 0.15
        goals.append(f"\nMETA 3: Controla gastos en {category}")
        goals.append(f"  Intenta reducir {reduction:.2f}€ (15%) en esta categoría.")
    
    return goals


def generate_incentives(profile: Dict) -> List[str]:
    """
    Incentivos personalizados según perfil avanzado.
    """
    incentives = []
    
    if profile["profile_type"] == "Ahorrador constante":
        incentives.append("PERFIL: Ahorrador Constante - Nivel VIP")
        incentives.append("  Acceso a cuentas premium con 3.5% APY")
        incentives.append("  Asesor financiero personal gratuito")
        incentives.append("  Programa de inversión automática")
        incentives.append("  Descuento 5% en seguros y productos financieros")
    
    elif profile["profile_type"] == "Ahorrador":
        incentives.append("PERFIL: Ahorrador - Nivel Premium")
        incentives.append("  Acceso a fondos de inversión con comisiones reducidas")
        incentives.append("  Cashback 2% en todas las compras")
        incentives.append("  Créditos a tasa especial (hasta 2.5%)")
    
    elif profile["profile_type"] == "Equilibrado prudente":
        incentives.append("PERFIL: Equilibrado Prudente - Nivel Oro")
        incentives.append("  Créditos preferenciales (hasta 3% interés)")
        incentives.append("  Programa de puntos en cada transacción")
        incentives.append("  Bonificación 75€ si mantienes patrón 3 meses")
        incentives.append("  Acceso a eventos de educación financiera")
    
    elif profile["profile_type"] == "Impulsivo":
        incentives.append("PERFIL: Impulsivo - Plan de Control")
        incentives.append("  App premium de control de gastos 3 meses gratis")
        incentives.append("  Alertas automáticas cuando se acerca a límites")
        incentives.append("  Asesoría financiera gratuita 1 mes")
        incentives.append("  Recompensa 150€ si estabilizas gasto 30 días")
    
    elif profile["profile_type"] == "Gasto excesivo":
        incentives.append("PERFIL: Gasto Excesivo - Plan de Rescate")
        incentives.append("  Sesión de asesoramiento financiero urgente GRATIS")
        incentives.append("  App de control premium 6 meses gratis")
        incentives.append("  Plan de consolidación de deudas personalizado")
        incentives.append("  Recompensa 200€ si reduces gasto 20% en próximo mes")
    
    else:
        incentives.append("PERFIL: Conservador - Plan Desarrollo")
        incentives.append("  Cuenta de ahorro con 1.5% APY")
        incentives.append("  Bono 25€ si alcanzas 500€ de ahorro")
        incentives.append("  Tutoriales de educación financiera premium")
    
    return incentives


# =================================================================
# --- FUNCIÓN PRINCIPAL ---
# =================================================================

def main():
    print("\n" + "="*70)
    print("ANALIZADOR FINANCIERO - FORMATO BANCARIO v2.0")
    print("="*70 + "\n")
    
    bank_data = {
        "account": {"iban": "ES6200810602620003333338", "currency": "EUR"},
        "transactions": {"booked": [
            {"transactionId": "TXN001", "bookingDate": "2025-02-01", "transactionAmount": {"currency": "EUR", "amount": "2500.00"}, "remittanceInformationUnstructured": "Salario mensual"},
            {"transactionId": "TXN002", "bookingDate": "2025-02-01", "transactionAmount": {"currency": "EUR", "amount": "-2.40"}, "remittanceInformationUnstructured": "Comisión bancaria"},
            {"transactionId": "TXN003", "bookingDate": "2025-02-02", "transactionAmount": {"currency": "EUR", "amount": "-45.50"}, "creditorName": "Carrefour", "remittanceInformationUnstructured": "Supermercado"},
            {"transactionId": "TXN004", "bookingDate": "2025-02-02", "transactionAmount": {"currency": "EUR", "amount": "-25.00"}, "creditorName": "La Barba Peluquería", "remittanceInformationUnstructured": "Servicio"},
            {"transactionId": "TXN005", "bookingDate": "2025-02-03", "transactionAmount": {"currency": "EUR", "amount": "-55.00"}, "creditorName": "Restaurante El Chef", "remittanceInformationUnstructured": "Restaurante"},
            {"transactionId": "TXN006", "bookingDate": "2025-02-03", "transactionAmount": {"currency": "EUR", "amount": "-60.00"}, "creditorName": "Repsol", "remittanceInformationUnstructured": "Combustible"},
            {"transactionId": "TXN007", "bookingDate": "2025-02-04", "transactionAmount": {"currency": "EUR", "amount": "-12.99"}, "creditorName": "Netflix", "remittanceInformationUnstructured": "Suscripción"},
            {"transactionId": "TXN008", "bookingDate": "2025-02-05", "transactionAmount": {"currency": "EUR", "amount": "-89.99"}, "creditorName": "Decathlon", "remittanceInformationUnstructured": "Ropa deportiva"},
            {"transactionId": "TXN009", "bookingDate": "2025-02-05", "transactionAmount": {"currency": "EUR", "amount": "-35.00"}, "creditorName": "Vodafone", "remittanceInformationUnstructured": "Factura teléfono"},
            {"transactionId": "TXN010", "bookingDate": "2025-02-06", "transactionAmount": {"currency": "EUR", "amount": "-42.00"}, "creditorName": "Cines Yelmo", "remittanceInformationUnstructured": "Cine"},
            {"transactionId": "TXN011", "bookingDate": "2025-02-07", "transactionAmount": {"currency": "EUR", "amount": "-150.00"}, "creditorName": "Travel Booking", "remittanceInformationUnstructured": "Viaje"},
            {"transactionId": "TXN012", "bookingDate": "2025-02-07", "transactionAmount": {"currency": "EUR", "amount": "-22.50"}, "creditorName": "Café Central", "remittanceInformationUnstructured": "Café"},
        ]}
    }
    
    print("PASO 1: Extrayendo transacciones bancarias...")
    print("-" * 70)
    transactions = parse_bank_transactions(bank_data)
    print(f"Transacciones extraídas: {len(transactions)}\n")
    
    print("PASO 2: Clasificando transacciones...")
    print("-" * 70)
    classified_results = []
    
    for description, amount, date in transactions:
        classification = classify_transaction(description, amount, date)
        classified_results.append((classification, amount, date))
        print(f"  {description:<40} -> {classification}")
    
    print()
    
    print("PASO 3: Analizando datos financieros...")
    print("-" * 70)
    analysis = analyze_transactions(classified_results)
    detailed_report = generate_detailed_report(analysis)
    print(detailed_report)
    
    print("PASO 4: Verificando complejidad del informe...")
    print("-" * 70)
    complexity_score = check_text_complexity(detailed_report)
    print(f"Score de complejidad: {complexity_score:.2f}\n")
    
    print("PASO 5: Explicación conversacional...")
    print("-" * 70)
    simplified_text = simplify_text(detailed_report)
    print(f"\n{simplified_text}\n")
    
    print("PASO 6: Traducción a Euskera...")
    print("-" * 70)
    translated_text = translate_to_basque(simplified_text)
    print(f"\n{translated_text}\n")
    
    # AHORA: Análisis de perfil y personalización (después de traducción)
    print("="*70)
    print("ANÁLISIS DE PERFIL Y RECOMENDACIONES PERSONALIZADAS")
    print("="*70 + "\n")
    
    print("PASO 7: Analizando tu perfil financiero...")
    print("-" * 70)
    profile = analyze_financial_profile(analysis)
    
    print(f"Perfil detectado: {profile['profile_type']}")
    print(f"Ratio de gastos: {profile['expense_ratio']:.1f}%")
    print(f"Volatilidad de gasto: {profile['expense_volatility']:.2f}€")
    print(f"Consistencia de ahorro: {profile['savings_consistency']}")
    print(f"Dependencia de ingresos: {profile['income_dependency']}\n")
    
    print(f"Ratio 50-30-20 (Ideal vs Real):")
    print(f"  Essentials (50%): {profile['ideal_essentials']:.2f}€ vs {profile['actual_essentials']:.2f}€")
    print(f"  Ocio (30%): {profile['ideal_discretionary']:.2f}€ vs {profile['actual_discretionary']:.2f}€")
    print(f"  Ahorros (20%): {profile['ideal_savings']:.2f}€ vs {profile['actual_savings']:.2f}€")
    
    if profile["alerts"]:
        print(f"\nAlertas:")
        for alert in profile["alerts"]:
            print(f"  ⚠️ {alert}")
    
    if profile["recommendations"]:
        print(f"\nRecomendaciones:")
        for rec in profile["recommendations"]:
            print(f"  💡 {rec}")
    
    print()
    
    print("PASO 8: Metas personalizadas para ti...")
    print("-" * 70)
    goals = generate_personalized_goals(profile, analysis)
    for goal in goals:
        print(goal)
    
    print()
    
    print("PASO 9: Ofertas e incentivos disponibles...")
    print("-" * 70)
    incentives = generate_incentives(profile)
    for incentive in incentives:
        print(incentive)
    
    print()
    print("="*70)
    print("Análisis completado exitosamente")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()