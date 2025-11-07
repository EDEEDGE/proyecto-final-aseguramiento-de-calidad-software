import os

def leer_texto(ruta: str) -> str:
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No existe el archivo: {ruta}")
    with open(ruta, "r", encoding="utf-8") as f:
        return f.read()
