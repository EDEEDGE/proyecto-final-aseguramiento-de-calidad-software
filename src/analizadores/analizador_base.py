import subprocess
import json
import io

def analizar_con_pylint(ruta_archivo: str) -> dict:
    """
    Ejecuta pylint sobre un archivo Python y devuelve:
      - score (calificación /10)
      - mensajes (lista de errores y advertencias)
      - raw (salida cruda)
    Compatible con pylint >= 3.0
    """
    try:
        # Ejecutar pylint en modo JSON (más fácil de parsear)
        resultado = subprocess.run(
            ["pylint", "--output-format=json", "--score=y", "--reports=n", ruta_archivo],
            capture_output=True,
            text=True,
            check=False
        )
    except Exception as e:
        return {"score": None, "mensajes": [], "raw": f"Error ejecutando pylint: {e}"}

    salida = resultado.stdout.strip()
    mensajes = []
    score = None

    # Si pylint devuelve JSON, lo parseamos
    if salida.startswith("["):
        try:
            datos = json.loads(salida)
            for item in datos:
                mensajes.append({
                    "severidad": item.get("type", ""),
                    "linea": item.get("line", 0),
                    "detalle": item.get("message", "")
                })
        except Exception as e:
            mensajes.append({"detalle": f"Error leyendo salida JSON: {e}"})

    # Buscar el score en stderr (pylint lo deja ahí)
    for linea in resultado.stderr.splitlines():
        if "Your code has been rated at" in linea:
            try:
                parte = linea.split("rated at", 1)[1].strip()
                nota = parte.split("/")[0].strip()
                score = float(nota)
            except Exception:
                pass

    return {
        "score": score,
        "mensajes": mensajes,
        "raw": resultado.stdout + "\n" + resultado.stderr
    }
