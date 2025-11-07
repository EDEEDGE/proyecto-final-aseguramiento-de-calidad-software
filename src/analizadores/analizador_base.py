import subprocess
import json
import re

def analizar_con_pylint(ruta_archivo: str) -> dict:
    try:
        # Ejecutar pylint en modo JSON y texto
        resultado = subprocess.run(
            ["pylint", "--output-format=json", "--score=y", ruta_archivo],
            capture_output=True,
            text=True
        )
    except Exception as e:
        return {"score": None, "mensajes": [], "raw": f"Error ejecutando pylint: {e}"}

    mensajes = []
    score = None

    # Procesar salida JSON (mensajes de advertencia o error)
    salida = resultado.stdout.strip()
    if salida.startswith("["):
        try:
            datos = json.loads(salida)
            for item in datos:
                mensajes.append({
                    "severidad": item.get("type", "").capitalize(),
                    "linea": item.get("line", 0),
                    "detalle": item.get("message", "")
                })
        except Exception as e:
            mensajes.append({"detalle": f"Error leyendo salida JSON: {e}"})

    # Buscar calificación (pylint >=3 ya la envía a stderr)
    texto_busqueda = resultado.stderr + "\n" + resultado.stdout
    match = re.search(r"rated at ([\d\.]+)/10", texto_busqueda)
    if match:
        try:
            score = float(match.group(1))
        except Exception:
            score = None

    # Si no hay score, intentamos obtenerlo con un segundo comando (fallback)
    if score is None:
        try:
            result_text = subprocess.run(
                ["pylint", "--score=y", "--reports=y", ruta_archivo],
                capture_output=True,
                text=True
            )
            match2 = re.search(r"rated at ([\d\.]+)/10", result_text.stdout)
            if match2:
                score = float(match2.group(1))
        except Exception:
            pass

    # Si pylint no devolvió mensajes
    if not mensajes:
        mensajes = [{"detalle": "Código limpio — sin observaciones relevantes."}]

    return {
        "score": score,
        "mensajes": mensajes,
        "raw": resultado.stdout + "\n" + resultado.stderr
    }
