import os

# 1. Forzamos a que Kivy ignore el escalado de Windows
os.environ['KIVY_METRICS_DENSITY'] = '1'
# 2. Evitamos que Windows re-escale la ventana (DPI awareness)
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp

# Componentes de KivyMD
from kivymd.uix.tab import MDTabs, MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

# Importación de tus módulos
from conexion_widget import ConexionWidget
from monitor_grafico import MonitorGrafico
from logic_calentamiento import ModoCalentamiento
from logic_open_loop import ModoOpenLoop
from logic_velocity_actions import ModoVelocityActions
from logic_velocity_zp import ModoVelocityZP
from logic_position_actions import ModoPositionActions
from logic_position_zp import ModoPositionZP
from guardar import GuardarResultadosWidget

class Tab(MDFloatLayout, MDTabsBase):
    '''Clase para el contenido de cada pestaña.'''
    pass

class TesterApp(MDApp):
    def build(self):
        self.title = "DC-Motor Control - Discrete Control"
        # 1. Configuración del Tema Material Design
        self.theme_cls.theme_style = "Light"
        self.color_resaltado = [0.12, 0.43, 0.46, 1]  # #1E6D76
        self.color_borde = [0.24, 0.49, 0.53, 1]      # #3E7E86
        self.color_fondo_suave = [0.87, 0.91, 0.91, 1] # #DFE7E8

        # 2. Contenedor Principal (Usamos MDBoxLayout para sombras y elevación)
        main_layout = MDBoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        # 3. Módulo de Conexión
        self.conexion = ConexionWidget()
        self.conexion.size_hint_y = 0.06
        main_layout.add_widget(self.conexion)

        # 4. Zona de trabajo (Horizontal)
        zona_trabajo = MDBoxLayout(orientation='horizontal', spacing=dp(10))

        # --- PANEL DE PESTAÑAS (MATERIAL DESIGN) ---
        # MDTabs sustituye al TabbedPanel para un look más moderno
        self.tabs = MDTabs(size_hint_x=0.5, 
                           background_color=self.color_resaltado,
                           indicator_color=[1, 1, 1, 1],
                           text_color_active=[1, 1, 1, 1],
                           text_color_normal=[0.87, 0.91, 0.91, 0.7],
                           tab_indicator_height=dp(5))

        # --- CONFIGURACIÓN DE PESTAÑAS ---
        # En MDTabs, cada pestaña se añade con un método específico o vía .kv
        # Por ahora las creamos y las vinculamos
        
        self._añadir_pestana("MOTOR WARM UP", ModoCalentamiento(conexion_ref=self.conexion))
        self._añadir_pestana("OPEN LOOP RESPONSE", ModoOpenLoop(conexion_ref=self.conexion))
        self._añadir_pestana("VELOCITY CONTROL (ACTIONS)", ModoVelocityActions(conexion_ref=self.conexion))
        self._añadir_pestana("VELOCITY CONTROL (ZEROS/POLES)", ModoVelocityZP(conexion_ref=self.conexion))
        self._añadir_pestana("POSITION CONTROL (ACTIONS)", ModoPositionActions(conexion_ref=self.conexion))
        self._añadir_pestana("POSITION CONTROL (ZEROS/POLES)", ModoPositionZP(conexion_ref=self.conexion))

        # Ensamblaje final
        zona_trabajo.add_widget(self.tabs)
        #zona_trabajo.add_widget(panel_derecho)
        main_layout.add_widget(zona_trabajo)

        return main_layout

    def _añadir_pestana(self, titulo, contenido_widget):
        """Método auxiliar para añadir pestañas de forma limpia en MDTabs"""
        class Tab(MDFloatLayout, MDTabsBase):
            '''Clase necesaria para que MDTabs funcione correctamente'''
            pass

        nueva_tab = Tab(title=titulo)
        nueva_tab.add_widget(contenido_widget)
        self.tabs.add_widget(nueva_tab)

    def on_start(self):
        Window.maximize()

if __name__ == '__main__':
    TesterApp().run()