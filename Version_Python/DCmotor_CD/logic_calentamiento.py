from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import ObjectProperty

# Cargamos su diseño
Builder.load_file('calentamiento.kv')

class ModoCalentamiento(BoxLayout):
    # Aquí guardaremos la referencia al widget de conexión
    conexion_ref = ObjectProperty(None)

    def ejecutar_modo(self, tiempo):
        if self.conexion_ref and self.conexion_ref.arduino.conectado:
            print(f"Enviando Modo 1: {tiempo} segundos")
            # Enviamos el comando al Arduino (Modo 1, Valor tiempo)
            self.conexion_ref.arduino.enviar_datos(1, tiempo)
        else:
            print("Error: Arduino no conectado")