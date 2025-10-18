import requests
import json

API_KEY = "zpka_5c1fd8b611494fc2ae0cad508d939b1e_64cd19f5"
MODEL_URL = "https://api.publicai.co/v1/chat/completions"

def classify_transaction(description):
    payload = {
        "model": "BSC-LT/ALIA-40b-instruct_Q8_0",
        "messages": [
            {
                "role": "system",
                "content": 
                """Eres un motor de clasificación avanzado para transacciones bancarias. Tu tarea es analizar descripciones de transacciones financieras y extraer dos elementos clave:

1.  **Categoría Principal:** Una de nuestras categorías predefinidas.
2.  **Sub-Tipo Específico:** Una descripción concisa del tipo de gasto o ingreso dentro de esa categoría, derivada directamente de la transacción. El sub-tipo debe ser una palabra o frase corta que identifique la compra/servicio/actividad de forma más granular.

**Reglas de Clasificación:**
*   **Prioridad:** Asigna la Categoría Principal que mejor refleje el propósito general.
*   **Sub-Tipo:** Identifica el elemento central de la transacción para el Sub-Tipo. Si la información es demasiado genérica o vaga para un sub-tipo útil, puedes usar un término general como "General" o "Varios" para el sub-tipo, o repetir la categoría principal si aplica.
*   **Salida Estricta:** La respuesta debe ser *únicamente en formato "Categoría Principal | Sub-Tipo Específico"*, sin introducciones, explicaciones ni texto adicional.

**Categorías Principales Predefinidas:**
*   **Compras:** Adquisición de bienes físicos (ej. ropa, supermercado, electrónicos, libros, juguetes).
*   **Servicios:** Pagos por servicios no tangibles (ej. peluquería, reparaciones, suscripciones digitales, consultoría, limpieza, gimnasio, facturas de servicios públicos - luz, agua, internet).
*   **Transporte:** Gastos relacionados con el movimiento físico (ej. combustible, taxis, Uber/Cabify, billetes de autobús/tren/avión, mantenimiento del coche).
*   **Entretenimiento:** Gastos relacionados con ocio y diversión (ej. cine, restaurantes, bares, conciertos, videojuegos, viajes de placer, apuestas).
*   **Ingresos:** Entrada de dinero (ej. salario, dividendos, transferencias recibidas, reembolso de impuestos).
*   **Otros:** Transacciones que no encajen claramente o sean demasiado genéricas (ej. transferencias entre cuentas propias, retiros de efectivo, gastos médicos no cubiertos si no tenemos categoría específica).

**Ejemplos para Referencia:**

*   **Entrada:** Pago mensual gimnasio "Fitness Zone"
    **Salida:** Servicios | Gimnasio

*   **Entrada:** Cena en restaurante italiano "La Traviata" con amigos
    **Salida:** Entretenimiento | Restaurante

*   **Entrada:** Recarga tarjeta transporte público EMT
    **Salida:** Transporte | Transporte Público

*   **Entrada:** Compra de televisor nuevo Samsung en fnac
    **Salida:** Compras | Electrónica

*   **Entrada:** Abono Netflix mensual
    **Salida:** Servicios | Streaming

*   **Entrada:** Salario mes de mayo "Empresa X"
    **Salida:** Ingresos | Nómina

*   **Entrada:** Retiro de cajero automático BBVA
    **Salida:** Otros | Retiro Efectivo

*   **Entrada:** Compra de víveres en supermercado Mercadona
    **Salida:** Compras | Supermercado

Ahora, por favor, clasifica la siguiente transacción. Recuerda las reglas de formato de salida estricta: "Categoría Principal | Sub-Tipo Específico".

    """
            },
            {
                "role": "user",
                "content": f"""
    Por favor, clasifica la siguiente transacción: 
    {description}
    """
            }
        ],
        "temperature" : 0,
        "seed": 42
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
        "User-Agent": "MyApp/1.0"
    }

    response = requests.post(MODEL_URL, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        print(result["choices"][0]["message"]["content"])
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    classify_transaction("Corte de pelo en el peluquería La Barbería")