import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from utils.archivos import leer_texto
from analizadores.analizador_base import analizar_con_pylint
from analizadores.analizador_ia import sugerencias_ia

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Agente revisor de codigo")
        self.geometry("1000x700")
        self.minsize(900, 600)
        self.ruta_actual = tk.StringVar(value="(No hay archivo)")

        top = tk.Frame(self, padx=10, pady=10)
        top.pack(fill="x")
        tk.Label(top, text="Archivo:", font=("Segoe UI", 10, "bold")).pack(side="left")
        tk.Label(top, textvariable=self.ruta_actual, fg="#555").pack(side="left", padx=8)
        tk.Button(top, text="Seleccionar .py", command=self.seleccionar_archivo).pack(side="right")

        actions = tk.Frame(self, padx=10, pady=6)
        actions.pack(fill="x")
        tk.Button(actions, text="Analizar con pylint", command=self.analizar).pack(side="left")
        tk.Button(actions, text="Sugerencias IA (Ollama)", command=self.recomendar).pack(side="left", padx=6)
        tk.Button(actions, text="Analizar + IA", command=self.analizar_y_recomendar).pack(side="left")

        body = tk.PanedWindow(self, orient="vertical")
        body.pack(fill="both", expand=True, padx=10, pady=10)

        frame_pylint = tk.LabelFrame(body, text="Resultado Pylint", padx=8, pady=8)
        self.txt_pylint = scrolledtext.ScrolledText(frame_pylint, wrap="word", font=("Consolas", 10))
        self.txt_pylint.pack(fill="both", expand=True)
        body.add(frame_pylint)

        frame_ia = tk.LabelFrame(body, text="Sugerencias IA", padx=8, pady=8)
        self.txt_ia = scrolledtext.ScrolledText(frame_ia, wrap="word", font=("Consolas", 10))
        self.txt_ia.pack(fill="both", expand=True)
        body.add(frame_ia)

    def seleccionar_archivo(self):
        ruta = filedialog.askopenfilename(title="Seleccione archivo de python", filetypes=[("Python", "*.py")])
        if ruta:
            self.ruta_actual.set(ruta)
            self.txt_pylint.delete("1.0", "end")
            self.txt_ia.delete("1.0", "end")

    def _verificar_ruta(self) -> str:
        ruta = self.ruta_actual.get()
        if not ruta or ruta == "(ningun archivo)" or not os.path.exists(ruta):
            messagebox.showerror("Error", "Seleccione un archivo .py")
            return ""
        return ruta

    def analizar(self):
        ruta = self._verificar_ruta()
        if not ruta:
            return
        res = analizar_con_pylint(ruta)
        self.txt_pylint.delete("1.0", "end")
        if res["score"] is not None:
            self.txt_pylint.insert("end", f"Score: {res['score']:.2f}/10\n\n")
        else:
            self.txt_pylint.insert("end", "Score: (no disponible)\n\n")

        if not res["mensajes"]:
            self.txt_pylint.insert("end", "Sin hallazgos importantes\n")
        else:
            self.txt_pylint.insert("end", "Hallazgos:\n")
            for m in res["mensajes"]:
                self.txt_pylint.insert("end", f"- [{m['severidad']}] linea {m['linea']}: {m['detalle']}\n")

    def recomendar(self):
        ruta = self._verificar_ruta()
        if not ruta:
            return
        try:
            codigo = leer_texto(ruta)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        self.txt_ia.delete("1.0", "end")
        self.txt_ia.insert("end", "Consultando modelo Ollama...\n")
        self.update_idletasks()
        resp = sugerencias_ia(codigo)
        self.txt_ia.delete("1.0", "end")
        self.txt_ia.insert("end", resp)

    def analizar_y_recomendar(self):
        self.analizar()
        self.recomendar()

if __name__ == "__main__":
    App().mainloop()
