from scipy.signal import savgol_filter
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.clock import Clock
import time
import math
from monitor_grafico import MonitorGrafico

# Cargamos el archivo de diseño
Builder.load_file('open_loop.kv')

class ModoOpenLoop(BoxLayout):
    # Referencias a otros módulos
    conexion_ref = ObjectProperty(None)
    grafica_ref = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.datos_acumulados = [] # Lista para guardar (tiempo, salida)
    
    def ejecutar_open_loop(self, v_input, t_sim, t_sam):
        try:
            v = float(v_input)
            self.referencia_actual = v
            u = v
            tsim = float(t_sim)
            tsam = float(t_sam) * 1000
            
            self.tsim_limite = tsim
            self.tiempo_actual = 0
            self.datos_acumulados = [] # Limpiamos la lista
            self.ids.grafico_ensayo.limpiar_grafica(x_max=tsim)
            
            if self.grafica_ref:
                self.grafica_ref.limpiar_grafica(x_max=tsim)

            if self.conexion_ref and self.conexion_ref.arduino.ser:
                arduino = self.conexion_ref.arduino
                arduino.ser.reset_input_buffer()
                arduino.ser.write(f"2\n{u}\n{tsim}\n{tsam}\n".encode())
                
                # Usamos una frecuencia de lectura MUY alta (1ms) 
                # Solo para leer, sin dibujar, para no perder ni un dato
                Clock.unschedule(self.leer_datos)
                Clock.schedule_interval(self.leer_datos, 0.001)
                
        except ValueError: pass

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
        Clock.unschedule(self.leer_datos)
        
        if self.datos_acumulados:
            tiempos = [p[0] for p in self.datos_acumulados]
            salidas = [p[1] for p in self.datos_acumulados]
            voltajes = [p[2] * 12 / 255 for p in self.datos_acumulados]
            
            try:
                filtrados = savgol_filter(salidas, window_length=13, polyorder=1, mode='interp')
            except Exception as e:
                print(f"Error en filtrado: {e}")
                filtrados = salidas # Fallback por si hay pocos datos
            
            val_ref = getattr(self, 'referencia_actual', 0.0)

            if self.grafica_ref:
                self.grafica_ref.actualizar_datos_completos(
                    tiempos, 
                    voltajes, 
                    salidas, 
                    filtrados,
                    ref_val=val_ref
                )
        
        print(f"Simulación de {self.__class__.__name__} finalizada.")