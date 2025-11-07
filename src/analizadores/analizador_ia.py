import requests

def sugerencias_ia(
    codigo: str,
    modelo: str = "mistral:7b-instruct",  # modelo más estable que codellama
    temperature: float = 0.2,
    num_predict: int = 400
) -> str:
    url = "http://localhost:11434/api/generate"

    prompt = (
        "Eres un revisor de código experto. Analiza el siguiente código Python "
        "y devuelve observaciones específicas, concisas y accionables. "
        "Indica posibles bugs, mejoras de legibilidad, uso de excepciones, "
        "y sugerencias PEP8.\n\n"
        f"CÓDIGO:\n{codigo}\n\n"
        "Formato de salida:\n"
        "- Problemas detectados\n"
        "- Buenas prácticas sugeridas\n"
        "- Refactor propuesto (si aplica)"
    )

    payload = {
        "model": modelo,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": num_predict
        }
    }

    try:
        resp = requests.post(url, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "").strip()
    except requests.exceptions.RequestException as e:
        return (
            f"(Aviso) No se pudo conectar con Ollama o el modelo:\n{e}\n\n"
            f"Asegúrate de que:\n"
            f"  - Ollama esté instalado y ejecutando (ollama serve)\n"
            f"  - El modelo '{modelo}' esté descargado (ollama pull {modelo})\n"
        )
