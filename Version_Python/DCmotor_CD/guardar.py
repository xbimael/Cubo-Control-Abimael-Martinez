import os
import time
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.lang import Builder

Builder.load_file('guardar.kv')
# Intentamos importar tkinter para el diálogo nativo
try:
    import tkinter as tk
    from tkinter import filedialog
    TK_AVAILABLE = True
except ImportError:
    TK_AVAILABLE = False

class GuardarResultadosWidget(BoxLayout):
    grafica_ref = ObjectProperty(None)
    _ultimo_clic = 0  # Para evitar que se abra dos veces

    def guardar_txt(self):
        # --- 1. CONTROL ANTI-REBOTE ---
        ahora = time.time()
        if ahora - self._ultimo_clic < 1.5: # Si pasaron menos de 1.5 seg, ignorar
            return
        self._ultimo_clic = ahora

        # --- 2. VALIDACIÓN DE DATOS ---
        # Buscamos 'experiment' que es la matriz completa [t, v, out, filt]
        datos = getattr(self.grafica_ref, 'experiment', [])
        
        if not datos:
            print("Warning: No data available.")
            return

        # --- 3. OBTENER RUTA (DIÁLOGO) ---
        filepath = ""
        if TK_AVAILABLE:
            root = tk.Tk()
            root.withdraw()
            filepath = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivo de texto", "*.txt")],
                title="Saving results"
            )
            root.destroy()
        else:
            # Fallback si no hay tkinter
            filepath = "datos_experimento.txt"
        
        # --- 4. ESCRITURA ÚNICA ---
        if filepath:
            try:
                with open(filepath, "w") as f:
                    # Guardamos las 4 columnas exactas de MATLAB
                    for fila in datos:
                        # fila es [t, v, out, filt]
                        f.write(f"{fila[0]:.6f} {fila[1]:.6f} {fila[2]:.6f} {fila[3]:.6f}\n")
                print(f"Éxito: Datos guardados en {filepath}")
            except Exception as e:
                print(f"Error al guardar: {e}")