import serial
import serial.tools.list_ports
import time
from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty

class ConexionSerial(EventDispatcher):
    # Esta propiedad notificará automáticamente a cualquier archivo .kv
    conectado = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ser = None

    def listar_puertos(self):
        puertos = serial.tools.list_ports.comports()
        return [p.device for p in puertos] if puertos else ["No detectado"]

    def conectar(self, puerto):
        try:
            # Ajusta el baudrate según tu código de Arduino
            self.ser = serial.Serial(puerto, 115200, timeout=2)
            time.sleep(2) 
            self.ser.write(b"1\n")
            res = self.ser.readline().decode('utf-8').strip()
            
            if res == "1":
                self.conectado = True
                return True, "Conectado"
            else:
                self.ser.close()
                return False, "Error de Handshake"
        except Exception as e:
            return False, str(e)

    def desconectar(self):
        if self.ser:
            self.ser.close()
        self.conectado = False

    def enviar_datos(self, modo, valor):
        if self.ser and self.conectado:
            try:
                # Enviamos modo y valor con saltos de línea
                cadena = f"{modo}\n{valor}\n".encode('utf-8')
                self.ser.write(cadena)
                print(f"SERIAL: Enviado -> {cadena}")
            except Exception as e:
                print(f"SERIAL ERROR: {e}")