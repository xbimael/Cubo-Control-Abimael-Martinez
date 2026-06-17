import os
import sys
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import OneLineListItem
from kivy.properties import ObjectProperty 
from serial_manager import ConexionSerial
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu

def resource_path(path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), path)

Builder.load_file(resource_path("conexion.kv"))

class ConexionWidget(BoxLayout):
    # Definimos la propiedad al nivel de clase
    arduino = ObjectProperty(None)

    def __init__(self, **kwargs):
        # Primero creamos el objeto arduino
        self.arduino = ConexionSerial()
        # Luego ejecutamos el init de la interfaz
        super().__init__(**kwargs)
        self.menu = None # Variable para guardar el menú

    def abrir_menu_puertos(self, boton):
        items = self.actualizar_puertos()
        
        # Obtenemos la instancia de la app actual
        app = MDApp.get_running_app() 
        
        self.menu = MDDropdownMenu(
            caller=boton,
            items=items,
            width_mult=4,
            background_color=app.color_fondo_suave, # Ahora 'app' sí existe
            radius=[10, 10, 10, 10]
        )
        self.menu.open()

    def seleccionar_puerto(self, puerto):
        # Actualizamos el texto del botón (que ahora actúa como spinner)
        self.ids.selector_puerto.text = puerto
        if self.menu:
            self.menu.dismiss()

    def actualizar_puertos(self):
        puertos = self.arduino.listar_puertos()
        
        # Si no hay puertos, creamos una lista con un aviso
        if not puertos:
            puertos = ["No ports found"]

        # IMPORTANTE: Esto debe devolver una LISTA DE DICCIONARIOS
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": str(p),
                "on_release": lambda x=str(p): self.seleccionar_puerto(x),
            } for p in puertos
        ]
        return menu_items

    def gestionar_conexion(self, puerto):
        if not self.arduino.conectado:
            exito, mensaje = self.arduino.conectar(puerto)
            if not exito:
                print(f"[SERIAL] Fallo al abrir el puerto {puerto}.")
        else:
            self.arduino.desconectar()

