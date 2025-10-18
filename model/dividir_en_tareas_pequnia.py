import requests

API_KEY = "zpka_5c1fd8b611494fc2ae0cad508d939b1e_64cd19f5"
MODEL_URL = "https://api.publicai.co/v1/chat/completions"
def dividir_en_tareas_pequnia(tarea):
    payload = {
        "model": "BSC-LT/salamandra-7b-instruct-tools-16k",
        "messages": [
            {
                "role": "system",
                "content": "Por favor, divide la tarea en subtareas más pequeñas que sean fáciles de completar. Cada subtarea debe ser específica y decirme por dónde empezar. Este es el nombre de la tarea: "
            },
            {
                "role": "user",
                "content": tarea
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

    response = requests.post(MODEL_URL, headers=headers, json=payload, verify=False)

    if response.status_code == 200:
        result = response.json()
        print(result["choices"][0]["message"]["content"])
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    dividir_en_tareas_pequnia("Reducir Gastos Viajes")