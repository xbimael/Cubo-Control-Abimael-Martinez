import math
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy_garden.graph import MeshLinePlot
from kivy.properties import ObjectProperty

Builder.load_file('monitor_grafico.kv')

class MonitorGrafico(BoxLayout):
    graph = ObjectProperty(None) # Enlazado desde el .kv

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Solo creamos la línea (plot), la estructura del gráfico ya viene del .kv
        self.plot = MeshLinePlot(color=[0, 0.7, 1, 1])
        # Esperamos un frame para que el gráfico esté listo y añadimos la línea
        self.graph.add_plot(self.plot)

    def limpiar_grafica(self, x_max=10):
        self.plot.points = []
        self.graph.xmin, self.graph.xmax = 0, x_max
        self.graph.ymin, self.graph.ymax = 0, 1
        self.actualizar_marcas()

    def actualizar_marcas(self):
        # Lógica matemática (imposible en .kv)
        self.graph.x_ticks_major = self.graph.xmax / 2
        rango_y = self.graph.ymax - self.graph.ymin
        
        if rango_y <= 1.5: self.graph.y_ticks_major = 0.2
        elif rango_y <= 10: self.graph.y_ticks_major = 2
        elif rango_y <= 50: self.graph.y_ticks_major = 5
        else: self.graph.y_ticks_major = 10

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
        # lista_puntos es [(t1, s1), (t2, s2), ...]
        self.plot.points = lista_puntos
        
        # Ajustamos los ejes una sola vez basándonos en los datos finales
        if lista_puntos:
            max_y = max(p[1] for p in lista_puntos)
            min_y = min(p[1] for p in lista_puntos)
            
            self.graph.ymax = math.ceil(max(1, max_y) / 5.0) * 5
            self.graph.ymin = math.floor(min(0, min_y) / 5.0) * 5
            self.actualizar_marcas()