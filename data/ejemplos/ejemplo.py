import os, json

def procesar_datos(ruta):
    f = open(ruta, "r")
    data = json.load(f)
    total = 0
    for k in data:
        total += data[k]
    return total

if