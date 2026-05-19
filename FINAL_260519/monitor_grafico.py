import math
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy_garden.graph import MeshLinePlot, PointPlot
from kivy.properties import ObjectProperty, ListProperty
from utils import abrir_ventana_interactiva

Builder.load_file('monitor_grafico.kv')

class MonitorGrafico(BoxLayout):
    graph = ObjectProperty(None)
    # ### AÑADIDO: Esta es la "matriz" que leerá el botón de guardar
    experiment = ListProperty([]) 

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.plot = MeshLinePlot(color=[0, 0.7, 1, 1])
        self.plot_ref = MeshLinePlot(color=[1, 0, 0, 1])
        self.plot_cursor = PointPlot(color=[1, 1, 0, 1])
        self.plot_cursor.point_size = 5
        self.experiment = [] 
        self.ultimos_datos_recibidos = []
        self.ultima_referencia = 0
        
        # Un pequeño truco: usamos Clock para evitar el error de inicialización
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.vincular_plots())

    def vincular_plots(self):
        if self.graph:
            self.graph.add_plot(self.plot)
            self.graph.add_plot(self.plot_ref)

    def limpiar_grafica(self, x_max=10):
        self.plot.points = []
        self.plot_ref.points = []
        self.plot_cursor.points = []
        self.ids.lbl_punto_x.text = "Tiempo: --- s"
        self.ids.lbl_punto_y.text = "Valor: --- rad/s"
        self.experiment = []
        self.graph.xmin, self.graph.xmax = 0, x_max
        self.graph.ymin, self.graph.ymax = 0, 1
        self.actualizar_marcas()

    def actualizar_datos_completos(self, tiempos, voltajes, salidas, filtrados, ref_val=None):
        self.experiment = list(zip(tiempos, voltajes, salidas, filtrados))
        
        # Dibujamos la señal filtrada
        self.dibujar_lote(list(zip(tiempos, filtrados)))

        # Si nos pasan una referencia, dibujamos la línea horizontal
        if ref_val is not None and tiempos:
            # Creamos dos puntos: uno al inicio (0, ref) y otro al final (t_final, ref)
            self.plot_ref.points = [(0, ref_val), (tiempos[-1], ref_val)]

        # Guardamos los datos en el formato que espera la función de utils (lista de tuplas)
        self.ultimos_datos_recibidos = list(zip(tiempos, filtrados))
        self.ultima_referencia = ref_val

    def actualizar_marcas(self):
        if not self.graph: return
        
        # --- EJE X (Tiempo) ---
        rango_x = self.graph.xmax - self.graph.xmin
        # Ajustamos para tener aprox 10 valores en el eje X
        if rango_x <= 2: self.graph.x_ticks_major = 0.2
        elif rango_x <= 5: self.graph.x_ticks_major = 0.5
        elif rango_x <= 15: self.graph.x_ticks_major = 1
        elif rango_x <= 30: self.graph.x_ticks_major = 2
        else: self.graph.x_ticks_major = 5

        # --- EJE Y (Amplitud) ---
        rango_y = self.graph.ymax - self.graph.ymin
        # Ajustamos para que salgan más etiquetas en el eje Y
        if rango_y <= 1.5: 
            self.graph.y_ticks_major = 0.1  # Salen etiquetas cada 0.1
        elif rango_y <= 5: 
            self.graph.y_ticks_major = 0.5  # Salen etiquetas cada 0.5
        elif rango_y <= 20: 
            self.graph.y_ticks_major = 2    # Salen etiquetas cada 2
        elif rango_y <= 50: 
            self.graph.y_ticks_major = 5    # Salen etiquetas cada 5
        else: 
            self.graph.y_ticks_major = 10   # Salen etiquetas cada 10   

    def añadir_punto(self, x, y):
        self.plot.points.append((x, y))
        cambio = False
        if x > self.graph.xmax:
            self.graph.xmax = x
            cambio = True
        if y > self.graph.ymax:
            self.graph.ymax = math.ceil(y / 5.0) * 5
            cambio = True
        if y < self.graph.ymin:
            self.graph.ymin = math.floor(y / 5.0) * 5
            cambio = True
        if cambio:
            self.actualizar_marcas()

    def dibujar_lote(self, lista_puntos):
        self.plot.points = lista_puntos
        if lista_puntos:
            max_y = max(p[1] for p in lista_puntos)
            min_y = min(p[1] for p in lista_puntos)
            self.graph.ymax = math.ceil(max(1, max_y) / 5.0) * 5
            self.graph.ymin = math.floor(min(0, min_y) / 5.0) * 5
            self.actualizar_marcas()

    def on_touch_down(self, touch):
        if self.graph and self.graph.collide_point(*touch.pos):
            
            # 1. OBTENER EL ÁREA DE DIBUJO REAL (Sincronización exacta)
            # view_pos[0] nos dice cuántos píxeles ocupa el eje Y (el margen izquierdo)
            # view_size[0] nos dice el ancho exacto de la cuadrícula (el área útil)
            x_margen_izquierdo = self.graph.view_pos[0]
            ancho_cuadricula = self.graph.view_size[0]
            
            # 2. CALCULAR POSICIÓN RELATIVA AL ÁREA DE DIBUJO
            # touch.x es la pantalla, self.graph.x + x_margen_izquierdo es donde empieza el 0
            x_pixel_dentro = touch.x - (self.graph.x + x_margen_izquierdo)
            
            # Convertimos a porcentaje (0.0 en el eje Y, 1.0 al final de la cuadrícula)
            porcentaje_x = max(0, min(1, x_pixel_dentro / ancho_cuadricula))
            
            # 3. CONVERTIR A TIEMPO
            rango_tiempo = self.graph.xmax - self.graph.xmin
            x_data = self.graph.xmin + (porcentaje_x * rango_tiempo)
            
            # 4. BÚSQUEDA DEL PUNTO (Usando self.plot)
            puntos = self.plot.points
            if puntos:
                punto_seleccionado = puntos[0]
                min_distancia = abs(puntos[0][0] - x_data)

                for p in puntos:
                    distancia_actual = abs(p[0] - x_data)
                    if distancia_actual < min_distancia:
                        min_distancia = distancia_actual
                        punto_seleccionado = p

                # 5. MOSTRAR CURSOR EN EL PUNTO SELECCIONADO
                if self.plot_cursor not in self.graph.plots:
                    self.graph.add_plot(self.plot_cursor)
                
                # Importante: PointPlot espera una lista de puntos
                self.plot_cursor.points = [punto_seleccionado]
                
                # 6. ACTUALIZAR INTERFAZ
                self.ids.lbl_punto_x.text = f"Tiempo: {punto_seleccionado[0]:.3f} s"
                self.ids.lbl_punto_y.text = f"Salida: {punto_seleccionado[1]:.3f} rad/s"
            
            return True            
        return super().on_touch_down(touch)
    
    def abrir_grafico_externo(self):
        if self.ultimos_datos_recibidos:
            abrir_ventana_interactiva(
                self.ultimos_datos_recibidos, 
                self.ultima_referencia,
                titulo="Análisis de Control Externo"
            )
        else:
            print("Aviso: No hay datos acumulados en el monitor todavía.")