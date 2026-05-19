from kivy.app import App
from kivy.core.window import Window
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
import matplotlib
matplotlib.use('Agg') # Renderizado en memoria, sin ventana externa
import matplotlib.pyplot as plt
from io import BytesIO
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image as KivyImage

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

class TesterApp(App):
    # Definición de colores para la interfaz
    VERDE = [0.1, 0.7, 0.2, 1]
    AZUL = [0, 0.7, 1, 1]
    NARANJA = [1, 0.6, 0.1, 1]
    LILA = [0.6, 0.4, 0.8, 1]

    def build(self):
        # 1. Contenedor Principal (Estilo definido en .kv)
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # 2. Módulo de Conexión
        self.conexion = ConexionWidget()
        main_layout.add_widget(self.conexion)

        # 3. Contenedor Horizontal para la zona de trabajo
        zona_trabajo = BoxLayout(orientation='horizontal', spacing=10)

        # --- PANEL DE PESTAÑAS ---
        tabs = TabbedPanel(do_default_tab=False, size_hint_x=0.5)

        # --- MONITOR GRÁFICO Y BOTÓN DE GUARDADO ---
        panel_derecho = BoxLayout(orientation='vertical', size_hint_x=0.5, spacing=5)

        # Instancias
        self.grafica = MonitorGrafico(size_hint_y=1)
        self.boton_guardar = GuardarResultadosWidget(grafica_ref=self.grafica)

        panel_derecho.add_widget(self.grafica)
        panel_derecho.add_widget(self.boton_guardar)

        # --- CONFIGURACIÓN DE PESTAÑAS ---
        
        # Pestaña 1: Calentamiento
        tab_calentamiento = TabbedPanelItem(text="WARM UP")
        self.calentamiento = ModoCalentamiento()
        self.calentamiento.conexion_ref = self.conexion
        tab_calentamiento.add_widget(self.calentamiento)

        # Pestaña 2: Lazo Abierto
        tab_open_loop = TabbedPanelItem(text="OPEN LOOP")
        self.open_loop = ModoOpenLoop()
        self.open_loop.conexion_ref = self.conexion
        self.open_loop.grafica_ref = self.grafica
        tab_open_loop.add_widget(self.open_loop)

        # Pestañas con paso de parámetros por constructor
        tab_velocity = TabbedPanelItem(text="VELOCITY ACTIONS")
        self.velocity_actions = ModoVelocityActions(conexion_ref=self.conexion, grafica_ref=self.grafica)
        tab_velocity.add_widget(self.velocity_actions)
        
        tab_zp = TabbedPanelItem(text="VELOCITY ZP")
        self.velocity_zp = ModoVelocityZP(conexion_ref=self.conexion, grafica_ref=self.grafica)
        tab_zp.add_widget(self.velocity_zp)

        tab_pos = TabbedPanelItem(text="POSITION ACTIONS")
        self.pos_actions = ModoPositionActions(conexion_ref=self.conexion, grafica_ref=self.grafica)
        tab_pos.add_widget(self.pos_actions)

        tab_pos_zp = TabbedPanelItem(text="POSITION ZP")
        self.pos_zp = ModoPositionZP(conexion_ref=self.conexion, grafica_ref=self.grafica)
        tab_pos_zp.add_widget(self.pos_zp)

        # Agregar pestañas al panel
        tabs.add_widget(tab_calentamiento)
        tabs.add_widget(tab_open_loop)
        tabs.add_widget(tab_velocity)
        tabs.add_widget(tab_zp)
        tabs.add_widget(tab_pos)
        tabs.add_widget(tab_pos_zp)

        # Ensamblaje final
        zona_trabajo.add_widget(tabs)
        zona_trabajo.add_widget(panel_derecho)
        main_layout.add_widget(zona_trabajo)

        return main_layout
    
    def on_start(self):
        Window.maximize()

    def crear_ecuacion_latex(texto_latex, altura='80dp'):
        # Crear figura pequeña y transparente
        fig = plt.figure(figsize=(5, 1.2), dpi=120)
        fig.patch.set_alpha(0)
        
        # Renderizar en BLANCO para que destaque en el fondo oscuro
        plt.text(0.5, 0.5, f"${texto_latex}$", 
                fontsize=20, color='white', 
                ha='center', va='center')
        plt.axis('off')

        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1, transparent=True)
        plt.close(fig)
        buf.seek(0)
        
        textura = CoreImage(buf, ext='png').texture
        return KivyImage(texture=textura, size_hint_y=None, height=altura)
    
if __name__ == '__main__':
    TesterApp().run()