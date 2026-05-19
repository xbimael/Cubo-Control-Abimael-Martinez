from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.clock import Clock
import numpy as np
import time
import math
from utils import crear_ecuacion_latex

# Cargamos el diseño KV
Builder.load_file('position_actions.kv')

class ModoPositionActions(BoxLayout):
    conexion_ref = ObjectProperty(None) # Referencia al widget de conexión
    grafica_ref = ObjectProperty(None)  # Referencia al monitor gráfico

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.datos_acumulados = []
        self.tsim_limite = 0
        Clock.schedule_once(self._insertar_ecuacion)

    def _insertar_ecuacion(self, dt):
        # Definimos la fórmula
        formula = r'R(s) = k_p + k_i \cdot \frac{1}{s} + k_d \cdot s'
        widget_latex = crear_ecuacion_latex(formula, altura='100dp')
        self.ids.contenedor_export_latex.add_widget(widget_latex)

    def aplicar_filtro_media_movil(self, datos, ventana=13):
        """Implementa un suavizado básico similar a sgolayfilt."""
        if len(datos) < ventana:
            return datos
        
        datos_suavizados = []
        for i in range(len(datos)):
            if i < ventana:
                # Al principio, usar media de puntos disponibles
                ventana_actual = datos[0:i+1]
            else:
                ventana_actual = datos[i-ventana+1:i+1]
            
            media = sum(ventana_actual) / len(ventana_actual)
            datos_suavizados.append(media)
            
        return datos_suavizados
    
    def ejecutar_position_actions(self, kp, ki, kd, ref, t_sim):
        if not (self.conexion_ref and self.conexion_ref.arduino.ser):
            return
        
        try:
            # Convertir inputs
            tsim = float(t_sim)
            k_p = float(kp)
            k_i = float(ki)
            k_d = float(kd)
            ref_v = float(ref)

            self.referencia_actual = ref_v
            self.tsim_limite = tsim
            self.datos_acumulados = []
            
            # Limpiar gráfica y configurar ejes
            if self.grafica_ref:
                self.grafica_ref.limpiar_grafica(x_max=tsim)

            arduino = self.conexion_ref.arduino
            arduino.ser.reset_input_buffer()
            
            # Protocolo de comunicación (Modo 5)
            # MATLAB envía: Modo, Ref, Tsim, Kp, Kd, Ki
            arduino.ser.write(b"5\n")
            time.sleep(0.05)
            for val in [ref_v, tsim, k_p, k_d, k_i]:
                arduino.ser.write(f"{val}\n".encode())
                time.sleep(0.02)
            
            # Iniciar lectura de datos
            Clock.unschedule(self.leer_datos)
            Clock.schedule_interval(self.leer_datos, 0.005) # 5ms
            
        except ValueError:
            print("Error: Parámetros inválidos")

    def leer_datos(self, dt):
        arduino = self.conexion_ref.arduino
        while arduino.ser.in_waiting >= 3:
            try:
                linea_out = arduino.ser.readline().decode('utf-8').strip()
                linea_time = arduino.ser.readline().decode('utf-8').strip()
                linea_volt = arduino.ser.readline().decode('utf-8').strip()
                
                if not linea_out or not linea_time or not linea_volt:
                    continue
                
                dato_salida = float(linea_out)
                dato_tiempo = float(linea_time)
                dato_volt_raw = float(linea_volt) # <--- CAPTURAMOS EL VOLTAJE
                
                # IMPORTANTE: Guardar los TRES datos para que luego p[2] exista
                self.datos_acumulados.append((dato_tiempo, dato_salida, dato_volt_raw))
                
                if dato_tiempo >= self.tsim_limite:
                    self.finalizar_y_graficar()
                    return False
            except:
                break
        return True

    def finalizar_y_graficar(self):
        # 1. Detener la lectura del reloj
        Clock.unschedule(self.leer_datos)
        
        if self.datos_acumulados:
            # Separamos los datos que fuimos guardando en leer_datos
            # Supongamos que guardaste: (tiempo, salida, tension_raw)
            tiempos = [p[0] for p in self.datos_acumulados]
            salidas = [p[1] for p in self.datos_acumulados]
            
            # Aplicamos la conversión de tensión de tu MATLAB: dato * 12 / 255
            voltajes = [p[2] * 12 / 255 for p in self.datos_acumulados]
            
            # 2. Aplicamos el filtro (el valor 'ventana' según el modo de MATLAB)
            # MATLAB usaba 13 para Velocity y 7 para Position
            ventana = 7 if "Position" in self.__class__.__name__ else 13
            filtrados = self.aplicar_filtro_media_movil(salidas, ventana=ventana)
            
            val_ref = getattr(self, 'referencia_actual', 0.0)

            # 3. LLAMADA CLAVE: Enviamos los 4 vectores al monitor gráfico
            if self.grafica_ref:
                self.grafica_ref.actualizar_datos_completos(
                    tiempos,   # t
                    voltajes,  # v
                    salidas,   # out
                    filtrados,  # filt
                    ref_val=val_ref
                )
        
        print(f"Simulación de {self.__class__.__name__} finalizada.")