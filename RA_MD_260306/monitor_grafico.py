import math
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy_garden.graph import MeshLinePlot, PointPlot
from kivy.properties import ObjectProperty, ListProperty, StringProperty
from kivy_garden.graph import LinePlot, PointPlot
from utils import abrir_ventana_interactiva
from guardar import GuardarResultadosWidget

Builder.load_file('monitor_grafico.kv')

class MonitorGrafico(BoxLayout):
    unidad_y = StringProperty("Output") # Valor por defecto
    graph = ObjectProperty(None)
    experiment = ListProperty([]) 

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.plot = LinePlot(color=[0, 0.7, 1, 1], line_width=2) 
        self.plot_ref = LinePlot(color=[1, 0, 0, 1], line_width=2)
        self.plot_cursor = PointPlot(color=[0, 0.5, 0, 1], point_size=6)
        self.experiment = [] 
        self.ultimos_datos_recibidos = []
        self.ultima_referencia = 0
        
        # Un pequeño truco: usamos Clock para evitar el error de inicialización
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.vincular_plots())

    def vincular_plots(self, dt=0):
        if self.ids.graph_id:
            self.graph = self.ids.graph_id
            # Limpiamos para evitar duplicados si pulsas "Ejecutar" varias veces
            self.graph.plots = [] 
            self.graph.add_plot(self.plot)
            self.graph.add_plot(self.plot_ref)
            print("Plots añadidos correctamente")

    # Este método se asegura de que el Graph se actualice al cambiar la propiedad
    def on_unidad_y(self, instance, value):
        self.ids.graph_id.ylabel = value
        self.ids.lbl_punto_y.text = f"Output: --- {value}"

    def limpiar_grafica(self, x_max=10):
        # Intentamos recuperar el link al gráfico si por alguna razón se perdió
        if not self.graph:
            self.graph = self.ids.get('graph_id') # Usa el id exacto que tengas en el .kv

        # Si después de intentar recuperarlo sigue siendo None, abortamos suavemente
        if self.graph is None:
            print("ADVERTENCIA: No se pudo encontrar el objeto gráfico para limpiar.")
            return 

        # Si llegamos aquí, self.graph ya no es None y no habrá crash
        self.plot.points = []
        self.plot_ref.points = []
        self.plot_cursor.points = []
        self.experiment = []
        
        try:
            self.graph.xmin, self.graph.xmax = 0, float(x_max)
            self.graph.ymin, self.graph.ymax = 0, 1
        except:
            pass
            
        self.actualizar_marcas()

    def actualizar_datos_completos(self, tiempos, voltajes, salidas, filtrados, ref_val=None):
        self.experiment = list(zip(tiempos, voltajes, salidas, filtrados))
        
        # 1. Actualizamos la referencia ANTES de dibujar
        self.ultima_referencia = ref_val

        # 2. Ahora dibujar_lote ya lee el valor correcto
        self.dibujar_lote(list(zip(tiempos, filtrados)))

        if ref_val is not None and tiempos:
            self.plot_ref.points = [(t, ref_val) for t in tiempos]
        else:
            self.plot_ref.points = []

        self.ultimos_datos_recibidos = list(zip(tiempos, filtrados))

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
        self.graph.y_ticks_major = rango_y/10 if rango_y > 0 else -rango_y/10

    def _calcular_limites_y(self, valores_y, referencia=None, margen_relativo=0.15):
        if not valores_y:
            return 0, 1

        raw_min = min(valores_y)
        raw_max = max(valores_y)
        rango = raw_max - raw_min or 1

        margen = rango * margen_relativo
        lim_min = raw_min - margen
        lim_max = raw_max + margen

        magnitud = 10 ** math.floor(math.log10(rango))
        paso = magnitud if rango / magnitud < 5 else magnitud * 2

        lim_min = math.floor(lim_min / paso) * paso
        lim_max = math.ceil(lim_max / paso) * paso

        # Solo expandimos si la referencia queda fuera, sin recalcular márgenes
        if referencia is not None:
            if referencia < lim_min:
                lim_min = math.floor(referencia / paso) * paso
            elif referencia > lim_max:
                lim_max = math.ceil(referencia / paso) * paso

        return lim_min, lim_max

    def dibujar_lote(self, lista_puntos):
        self.plot.points = lista_puntos
        if lista_puntos:
            ys = [p[1] for p in lista_puntos]
            self.graph.ymin, self.graph.ymax = self._calcular_limites_y(ys, self.ultima_referencia)
            self.actualizar_marcas()

    def añadir_punto(self, x, y):
        self.plot.points.append((x, y))
        ys = [p[1] for p in self.plot.points]
        nuevo_min, nuevo_max = self._calcular_limites_y(ys, self.ultima_referencia)

        # Histéresis: solo actualiza si el cambio es significativo (>5%)
        rango_actual = self.graph.ymax - self.graph.ymin or 1
        if (abs(nuevo_min - self.graph.ymin) > rango_actual * 0.05 or
                abs(nuevo_max - self.graph.ymax) > rango_actual * 0.05):
            self.graph.ymin, self.graph.ymax = nuevo_min, nuevo_max

        if x > self.graph.xmax:
            self.graph.xmax = x
        self.actualizar_marcas()

    def disparar_guardado(self):
        # 1. Verificamos si tenemos datos en 'experiment' (que ya llenamos en actualizar_datos_completos)
        if not self.experiment:
            print("Error: No data available for saving.")
            return

        try:
            print(f"Abriendo diálogo de guardado para: {self.unidad_y}...")
            
            # 2. Instanciamos el widget de guardado (el que importaste de guardar.py)
            escritor = GuardarResultadosWidget()
            
            # 3. CONEXIÓN CLAVE:
            # Tu script busca: datos = getattr(self.grafica_ref, 'experiment', [])
            # Así que le decimos que su fuente de datos (grafica_ref) es este mismo Monitor.
            escritor.grafica_ref = self
            
            # 4. Ejecutamos la lógica de tu script (el diálogo de Tkinter y la escritura)
            escritor.guardar_txt()
            
        except Exception as e:
            print(f"Error: {e}")

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
                self.ids.lbl_punto_x.text = f"Time: {punto_seleccionado[0]:.3f} s"
                self.ids.lbl_punto_y.text = f"Output: {punto_seleccionado[1]:.3f} {self.unidad_y}"
            
            return True            
        return super().on_touch_down(touch)
    
    def abrir_grafico_externo(self):
        if self.ultimos_datos_recibidos:
            abrir_ventana_interactiva(
                self.ultimos_datos_recibidos, 
                self.ultima_referencia,
                titulo="Control Analysis - Interactive Plot"
            )
        else:
            print("Aviso: No hay datos acumulados en el monitor todavía.")