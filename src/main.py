import os
from utils.archivos import leer_texto
from analizadores.analizador_base import analizar_con_pylint
from analizadores.analizador_ia import sugerencias_ia

#menu
def imprimir_resumen_pylint(res):
    print("\nAnálisis estatico (pylint)")
    if res["score"] is not None:
        print(f"Score: {res['score']:.2f}/10")
    else:
        print("Score: (no disponible)")
    if not res["mensajes"]:
        print("No se encontraron hallazgos importantes")
    else:
        print("Hallazgos:")
        for m in res["mensajes"][:20]:
            print(f"     - [{m['severidad']}] línea {m['linea']}: {m['detalle']}")
        if len(res["mensajes"]) > 20:
            print(f"     ... y {len(res['mensajes'])-20} más.")

def main():
    print("\nAgente revisor de codigo")
    ruta = input("Ruta del archivo .py a analizar (ej: data/ejemplos/ejemplo.py): ").strip()
    if not os.path.exists(ruta):
        print("Archivo no encontrado...")
        return

    codigo = leer_texto(ruta)

    #realiza el analisis estatico
    res_pylint = analizar_con_pylint(ruta)
    imprimir_resumen_pylint(res_pylint)

    #Sugerencias con Ollama
    print("\nSugerencias de IA utilizando modelo Ollama")
    sugerencias = sugerencias_ia(codigo, modelo="codellama:7b-instruct")
    print(sugerencias)

if __name__ == "__main__":
    main()
