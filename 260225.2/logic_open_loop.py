from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.clock import Clock

# Cargamos el archivo de diseño
Builder.load_file('open_loop.kv')

class ModoOpenLoop(BoxLayout):
    # Referencias a otros módulos
    conexion_ref = ObjectProperty(None)
    grafica_ref = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.datos_acumulados = [] # Lista para guardar (tiempo, salida)

    def ejecutar_open_loop(self, v_input, t_sim):
        try:
            v = float(v_input)
            u = v * 255 / 12
            tsim = float(t_sim)
            
            self.tsim_limite = tsim
            self.tiempo_actual = 0
            self.datos_acumulados = [] # Limpiamos la lista
            
            if self.grafica_ref:
                self.grafica_ref.limpiar_grafica(x_max=tsim)

            if self.conexion_ref and self.conexion_ref.arduino.ser:
                arduino = self.conexion_ref.arduino
                arduino.ser.reset_input_buffer()
                arduino.ser.write(f"2\n{u}\n{tsim}\n".encode())
                
                # Usamos una frecuencia de lectura MUY alta (1ms) 
                # Solo para leer, sin dibujar, para no perder ni un dato
                Clock.unschedule(self.leer_datos)
                Clock.schedule_interval(self.leer_datos, 0.001)
                
        except ValueError: pass

    def leer_datos(self, dt):
        arduino = self.conexion_ref.arduino
        
        while arduino.ser.in_waiting >= 3:
            try:
                linea = arduino.ser.readline().decode('utf-8').strip()
                if not linea: continue
                
                dato_salida = float(linea)
                dato_tiempo = float(arduino.ser.readline().decode('utf-8').strip())
                dato_tension = float(arduino.ser.readline().decode('utf-8').strip())

                # EN VEZ DE GRAFICAR, GUARDAMOS
                self.datos_acumulados.append((dato_tiempo, dato_salida))
                self.tiempo_actual = dato_tiempo
                
                if self.tiempo_actual >= self.tsim_limite:
                    self.finalizar_y_graficar() # Llamamos a la función de dibujo
                    return False
            except:
                break
        return True

    def finalizar_y_graficar(self):
        print(f"Simulación terminada. Puntos capturados: {len(self.datos_acumulados)}")
        if self.grafica_ref:
            # Enviamos todos los puntos de golpe a la gráfica
            self.grafica_ref.dibujar_lote(self.datos_acumulados)
        
        return True