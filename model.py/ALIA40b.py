import requests
import json
from collections import defaultdict
from typing import List, Tuple, Dict

# =================================================================
# --- CONFIGURACIÓN ---
# =================================================================

# API ALIA para clasificación
API_KEY_PUBLICAI = "zpka_5c1fd8b611494fc2ae0cad508d939b1e_64cd19f5"
MODEL_URL_PUBLICAI = "https://api.publicai.co/v1/chat/completions"
MODEL_CLASSIFICATION = "BSC-LT/ALIA-40b-instruct_Q8_0"
MODEL_SIMPLIFICATION = "BSC-LT/salamandra-7b-instruct-tools-16k"
MODEL_TRANSLATION_EU = "HiTZ/Latxa-Llama-3.1-8B-Instruct"

# Token para Latxa (euskera)
API_KEY_LATXA = "SabadellHackathon2025"
MODEL_URL_LATXA = "http://hackathon.hitz.eus/v1/chat/completions"

# RoBERTa para verificar complejidad
HF_TOKEN = "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"
HF_ENDPOINT_ROBERTA = "https://dbnv0qwamu3uv944.us-east-1.aws.endpoints.huggingface.cloud/"

# =================================================================
# --- ETAPA 1: CLASIFICACIÓN ---
# =================================================================

def classify_transaction(description: str) -> str:
    """
    Clasifica una transacción usando ALIA-40b.
    Retorna: "Categoría Principal | Sub-Tipo Específico"
    """
    system_prompt = """Eres un motor de clasificación avanzado para transacciones bancarias.

Tu tarea: Analiza la descripción y devuelve SOLO: "Categoría Principal | Sub-Tipo"

**Categorías válidas:**
- Compras: Bienes físicos (ropa, supermercado, electrónicos, libros)
- Servicios: Servicios no tangibles (peluquería, suscripciones, facturas, gimnasio)
- Transporte: Movimiento físico (combustible, taxi, Uber, billetes, mantenimiento)
- Entretenimiento: Ocio y diversión (cine, restaurantes, bares, conciertos, viajes)
- Ingresos: Entrada de dinero (salario, dividendos, reembolsos)
- Otros: Lo que no encaja claramente

**Reglas:**
- Respuesta EXACTA: "Categoría | Sub-tipo"
- Sin explicaciones, sin texto adicional
- Sub-tipo: palabra corta que identifique el tipo específico
- Si es genérico, usa "General" como sub-tipo"""
    
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
        return classification if "|" in classification else "Otros | General"
    except Exception as e:
        print(f"⚠️  Error en clasificación: {e}")
        return "Otros | General"


# =================================================================
# --- ETAPA 2: ANÁLISIS Y AGREGACIÓN ---
# =================================================================

def analyze_transactions(classified_transactions: List[Tuple[str, float]]) -> Dict:
    """
    Procesa transacciones clasificadas y genera estadísticas.
    """
    category_totals = defaultdict(float)
    category_count = defaultdict(int)
    
    for classification, amount in classified_transactions:
        category = classification.split(" | ")[0].strip()
        category_totals[category] += amount
        category_count[category] += 1
    
    # Cálculos financieros
    total_income = max(0, category_totals.get("Ingresos", 0))
    total_expenses = sum(abs(v) for k, v in category_totals.items() if k != "Ingresos" and v < 0)
    
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
        "balance": total_income - total_expenses,
        "category_totals": dict(category_totals),
        "category_count": dict(category_count),
        "top_expense_category": top_expense_category,
        "top_expense_amount": max_expense,
        "top_percentage": top_percentage,
        "transaction_count": len(classified_transactions)
    }


def generate_detailed_report(analysis: Dict) -> str:
    """
    Genera un reporte financiero detallado.
    """
    report = "ANÁLISIS FINANCIERO DETALLADO\n"
    report += "=" * 50 + "\n\n"
    
    report += f"Resumen General:\n"
    report += f"Transacciones procesadas: {analysis['transaction_count']}\n"
    report += f"Ingresos totales: {analysis['total_income']:.2f}€\n"
    report += f"Gastos totales: {analysis['total_expenses']:.2f}€\n"
    report += f"Balance neto: {analysis['balance']:.2f}€\n\n"
    
    if analysis['top_expense_category']:
        report += f"Principal Tendencia de Gasto:\n"
        report += f"Categoría: {analysis['top_expense_category']}\n"
        report += f"Cantidad: {analysis['top_expense_amount']:.2f}€\n"
        report += f"Porcentaje del total: {analysis['top_percentage']:.1f}%\n\n"
    
    report += "Desglose por Categoría:\n"
    sorted_cats = sorted(analysis['category_totals'].items(), 
                        key=lambda x: abs(x[1]), reverse=True)
    for category, total in sorted_cats:
        count = analysis['category_count'].get(category, 0)
        report += f"{category}: {total:+.2f}€ ({count} transacciones)\n"
    
    return report


# =================================================================
# --- ETAPA 3: VERIFICACIÓN DE COMPLEJIDAD CON RoBERTa ---
# =================================================================

def check_text_complexity(text: str) -> float:
    """
    Verifica el nivel de complejidad del texto usando un análisis simple.
    Retorna un score de 0.0 (simple) a 1.0 (complejo).
    
    Análisis basado en:
    - Longitud promedio de palabras
    - Cantidad de palabras técnicas/financieras
    - Longitud de oraciones
    """
    # Palabras técnicas/financieras comunes
    technical_words = [
        'análisis', 'estadísticas', 'ingresos', 'egresos', 'categoría',
        'porcentaje', 'desglose', 'transacciones', 'balance', 'neto',
        'complejidad', 'tendencia', 'presupuestaria', 'cantidad', 'período'
    ]
    
    words = text.lower().split()
    
    if not words:
        return 0.5
    
    # Calcula métricas
    avg_word_length = sum(len(w) for w in words) / len(words)
    technical_ratio = sum(1 for w in words if any(tech in w for tech in technical_words)) / len(words)
    
    # Score: combinación de longitud de palabra y palabras técnicas
    word_length_score = min(avg_word_length / 10, 1.0)  # Normaliza a 0-1
    complexity_score = (word_length_score * 0.5 + technical_ratio * 0.5)
    
    return min(complexity_score, 1.0)


# =================================================================
# --- ETAPA 4: SIMPLIFICACIÓN CON SALAMANDRA ---
# =================================================================

def simplify_text(complex_text: str) -> str:
    """
    Simplifica texto técnico usando Salamandra de PublicAI.
    """
    system_prompt = """Eres un experto en simplificación de textos financieros complejos.

Tu tarea: Reescribe el análisis financiero en lenguaje CLARO y SIMPLE para cualquier persona.

Reglas estrictas:
- Elimina tecnicismos financieros
- Usa palabras comunes y cortas
- Frases de máximo 15 palabras
- Mantén números y datos esenciales
- Resalta lo más importante para el usuario
- Máximo 5-6 líneas
- Resultado: SOLO el texto simplificado, sin introducciones ni explicaciones"""
    
    payload = {
        "model": MODEL_SIMPLIFICATION,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Simplifica este informe:\n\n{complex_text}"}
        ],
        "temperature": 0.3,
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
        print(f"⚠️  Error en simplificación: {e}")
        return complex_text


# =================================================================
# --- ETAPA 5: TRADUCCIÓN CON LATXA (EUSKERA) ---
# =================================================================

def translate_to_basque(text: str) -> str:
    """
    Traduce texto simplificado a Euskera usando Latxa.
    """
    system_prompt = """Eres un traductor experto del español al euskera.

Tu tarea: Traduce el siguiente texto de manera natural y clara.

Reglas:
- Traducción natural y fluida
- Mantén números y valores
- Resultado: SOLO la traducción en euskera, sin explicaciones"""
    
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
        print(f"⚠️  Error en traducción: {e}")
        return text


# =================================================================
# --- FUNCIÓN PRINCIPAL ---
# =================================================================

def main():
    print("\n" + "="*70)
    print("💸 ANALIZADOR FINANCIERO AUTOMATIZADO")
    print("="*70 + "\n")
    
    # Datos de ejemplo
    transactions_data = [
        ("Corte de pelo en peluquería La Barbería", -25.00),
        ("Salario mes de octubre Tech Solutions", 2500.00),
        ("Compra en Mercadona", -85.50),
        ("Abono mensual Netflix", -12.99),
        ("Cena en restaurante El Chef", -55.00),
        ("Recarga de combustible Repsol", -60.00),
        ("Compra de libros Casa del Libro", -30.00),
    ]
    
    # PASO 1: Clasificación
    print("📋 PASO 1: Clasificando transacciones...")
    print("-" * 70)
    classified_results = []
    
    for description, amount in transactions_data:
        classification = classify_transaction(description)
        classified_results.append((classification, amount))
        print(f"  {description:<45} → {classification}")
    
    print()
    
    # PASO 2: Análisis
    print("📊 PASO 2: Analizando datos...")
    print("-" * 70)
    analysis = analyze_transactions(classified_results)
    detailed_report = generate_detailed_report(analysis)
    print(detailed_report)
    
    # PASO 3: Verificar complejidad
    print("🔍 PASO 3: Verificando complejidad del texto...")
    print("-" * 70)
    complexity_score = check_text_complexity(detailed_report)
    print(f"Score de complejidad: {complexity_score:.2f} (0.0=simple, 1.0=complejo)\n")
    
    # PASO 4: Simplificación si es necesario
    simplified_text = detailed_report
    if complexity_score > 0.5:
        print("✏️  PASO 4: Simplificando para público general...")
        print("-" * 70)
        simplified_text = simplify_text(detailed_report)
        print(f"\n{simplified_text}\n")
    else:
        print("✅ PASO 4: El texto ya está suficientemente simple.\n")
    
    # PASO 5: Traducción
    print("🌍 PASO 5: Traduciendo a Euskera (Latxa)...")
    print("-" * 70)
    translated_text = translate_to_basque(simplified_text)
    print(f"\n{translated_text}\n")
    
    print("="*70)
    print("✅ Análisis completado exitosamente")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()