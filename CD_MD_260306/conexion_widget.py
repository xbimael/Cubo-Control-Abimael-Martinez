from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import ObjectProperty # <--- IMPORTANTE
from serial_manager import ConexionSerial

# Nota: Es mejor cargar el archivo DESPUÉS de definir la clase 
# o dentro de la misma, pero vamos a asegurar la propiedad primero.

class ConexionWidget(BoxLayout):
    # Definimos la propiedad al nivel de clase
    arduino = ObjectProperty(None)

    def __init__(self, **kwargs):
        # Primero creamos el objeto arduino
        self.arduino = ConexionSerial()
        # Luego ejecutamos el init de la interfaz
        super().__init__(**kwargs)

    def actualizar_puertos(self):
        self.ids.selector_puerto.values = self.arduino.listar_puertos()

    def gestionar_conexion(self, puerto):
        if not self.arduino.conectado:
            exito, mensaje = self.arduino.conectar(puerto)
            if not exito:
                print(f"[SERIAL] Fallo al abrir el puerto {puerto}.")
        else:
            self.arduino.desconectar()

# Cargamos el KV al final del archivo
Builder.load_file('conexion.kv')