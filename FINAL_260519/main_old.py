from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.lang import Builder

# Importación de nuestros módulos
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
    def build(self):
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # 1. Módulo de Conexión
        self.conexion = ConexionWidget()
        main_layout.add_widget(self.conexion)

        # 2. Contenedor Horizontal para la zona de trabajo
        zona_trabajo = BoxLayout(orientation='horizontal', spacing=10)

        # --- PANEL DE PESTAÑAS ---
        tabs = TabbedPanel(do_default_tab=False, size_hint_x=0.5)

        # --- MONITOR GRÁFICO Y BOTÓN DE GUARDADO ---
        # Creamos un contenedor vertical para el lado derecho
        panel_derecho = BoxLayout(orientation='vertical', size_hint_x=0.5, spacing=5)

        # Instanciamos el monitor gráfico
        self.grafica = MonitorGrafico(size_hint_y=1)
        
        # Creamos la instancia del widget de guardado pasándole la referencia
        self.boton_guardar = GuardarResultadosWidget(grafica_ref=self.grafica)

        # Los añadimos al panel derecho en orden: gráfica arriba, botón abajo
        panel_derecho.add_widget(self.grafica)
        panel_derecho.add_widget(self.boton_guardar)

        # Pestaña 1: Calentamiento
        tab_calentamiento = TabbedPanelItem(text="Calentamiento")
        self.calentamiento = ModoCalentamiento()
        self.calentamiento.conexion_ref = self.conexion
        tab_calentamiento.add_widget(self.calentamiento)

        # Pestaña 2: Lazo Abierto
        tab_open_loop = TabbedPanelItem(text="Lazo Abierto")
        self.open_loop = ModoOpenLoop()
        self.open_loop.conexion_ref = self.conexion
        self.open_loop.grafica_ref = self.grafica
        tab_open_loop.add_widget(self.open_loop)

        # Pestaña 3: Velocity Actions
        tab_velocity = TabbedPanelItem(text="Velocity Actions")
        self.velocity_actions = ModoVelocityActions(conexion_ref=self.conexion, grafica_ref=self.grafica)
        tab_velocity.add_widget(self.velocity_actions)
        
        # Pestaña 4: Velocity ZP
        tab_zp = TabbedPanelItem(text="Velocity ZP")
        self.velocity_zp = ModoVelocityZP(conexion_ref=self.conexion, grafica_ref=self.grafica)
        tab_zp.add_widget(self.velocity_zp)

        # Pestaña 5: Position Actions
        tab_pos = TabbedPanelItem(text="Position Actions")
        self.pos_actions = ModoPositionActions(conexion_ref=self.conexion, grafica_ref=self.grafica)
        tab_pos.add_widget(self.pos_actions)

        # Pestaña 6: Position ZP
        tab_pos_zp = TabbedPanelItem(text="Position ZP")
        self.pos_zp = ModoPositionZP(conexion_ref=self.conexion, grafica_ref=self.grafica)
        tab_pos_zp.add_widget(self.pos_zp)

        tabs.add_widget(tab_calentamiento)
        tabs.add_widget(tab_open_loop)
        tabs.add_widget(tab_velocity)
        tabs.add_widget(tab_zp)
        tabs.add_widget(tab_pos)
        tabs.add_widget(tab_pos_zp) # <--- AÑADIDO

        # Añadimos todo a la zona de trabajo
        zona_trabajo.add_widget(tabs)
        zona_trabajo.add_widget(panel_derecho)
        main_layout.add_widget(zona_trabajo)

        # Estilo visual
        Builder.load_string('''
<BoxLayout>:
    canvas.before:
        Color:
            rgba: 0.1, 0.1, 0.1, 1
        Rectangle:
            pos: self.pos
            size: self.size
''')
        return main_layout

if __name__ == '__main__':
    TesterApp().run()
