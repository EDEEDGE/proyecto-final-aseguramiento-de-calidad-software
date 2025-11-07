import requests
import subprocess
import json

def modelo_disponible(modelo: str) -> bool:
    try:
        res = subprocess.run(["ollama", "list", "--output", "json"], capture_output=True, text=True)
        data = json.loads(res.stdout)
        nombres = [m["name"] for m in data]
        return modelo in nombres
    except Exception:
        return False

def verificar_sintaxis(codigo: str) -> dict:
    try:
        compile(codigo, "<string>", "exec")
        return {"error": False, "mensaje": "Sintaxis correcta."}
    except SyntaxError as e:
        return {
            "error": True,
            "mensaje": f"Error de sintaxis en la linea {e.lineno}: {e.msg}",
            "linea": e.lineno,
            "detalle": e.text.strip() if e.text else ""
        }

def sugerencias_ia(
    codigo: str,
    modelo_preferido: str = "mistral:7b-instruct",
    alternativo: str = "codellama:7b-instruct",
    temperature: float = 0.2,
    num_predict: int = 400
) -> str:
    sintaxis = verificar_sintaxis(codigo)
    if sintaxis["error"]:
        mensaje_error = (
            "=================== ERROR DE SINTAXIS DETECTADO ===================\n\n"
            f"{sintaxis['mensaje']}\n"
            f"Linea con error: {sintaxis.get('linea', '-')}\n"
            f"Fragmento: {sintaxis.get('detalle', '')}\n\n"
            "=========================================================\n"
            "Corrige el error antes de solicitar el analisis con la IA."
        )
        return mensaje_error

    url = "http://localhost:11434/api/generate"
    if not modelo_disponible(modelo_preferido):
        modelo = alternativo if modelo_disponible(alternativo) else modelo_preferido
    else:
        modelo = modelo_preferido

    prompt = (
        "Eres un analista de codigo experto. Tu tarea es revisar el siguiente codigo en Python "
        "y entregar un informe claro en español. Evita reescribir el codigo, solo analiza y comenta. "
        "Evalua la claridad, estilo, posibles errores y mejoras segun las buenas practicas de programacion.\n\n"
        "Formato de salida:\n"
        "============================================================\n"
        "1. Problemas o errores detectados\n"
        "2. Buenas practicas y puntos positivos\n"
        "3. Recomendaciones o mejoras sugeridas\n"
        "============================================================\n\n"
        f"Codigo a analizar:\n{codigo}"
    )

    payload = {
        "model": modelo,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": num_predict}
    }

    try:
        resp = requests.post(url, json=payload, timeout=180)
        resp.raise_for_status()
        data = resp.json()
        respuesta = data.get("response", "").strip()
        if not respuesta:
            return "(El modelo no devolvio respuesta)"
        return (
            "=================== ANALISIS DE LA IA ===================\n\n"
            f"{respuesta}\n\n"
            "========================================================="
        )
    except requests.exceptions.RequestException as e:
        return (
            f"No se pudo conectar al modelo de Ollama:\n{e}\n\n"
            f"Posibles soluciones:\n"
            f"  - Verificar que Ollama este ejecutandose.\n"
            f"  - Descargar el modelo con: ollama pull {modelo}\n"
        )
