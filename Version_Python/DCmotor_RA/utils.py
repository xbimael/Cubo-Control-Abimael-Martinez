import matplotlib
matplotlib.use('Agg')  # Renderizado en memoria (evita ventanas emergentes)
import matplotlib.pyplot as plt
from io import BytesIO
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image as KivyImage

def crear_ecuacion_latex(texto_latex, altura='100dp'):
    """
    Genera un widget de Imagen de Kivy a partir de código LaTeX.
    Renderizado en blanco con fondo transparente.
    """
    # 1. Crear figura de Matplotlib
    fig = plt.figure(figsize=(6, 1.5), dpi=120)
    fig.patch.set_alpha(0) # Fondo transparente
    
    # 2. Renderizar el texto
    plt.text(0.5, 0.5, f"${texto_latex}$", 
             fontsize=22, color='black',
             ha='center', va='center')
    plt.axis('off')

    # 3. Guardar en un buffer de memoria
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1, transparent=True)
    plt.close(fig) # Liberar memoria
    buf.seek(0)
    
    # 4. Convertir a textura de Kivy y retornar el Widget
    textura = CoreImage(buf, ext='png').texture
    return KivyImage(texture=textura, size_hint_y=None, height=altura)

def abrir_ventana_interactiva(datos_acumulados, referencia, titulo="Análisis de Datos"):    
    # Cambiamos el motor a interactivo
    matplotlib.use('TkAgg', force=True) 
    import matplotlib.pyplot as plt 

    if not datos_acumulados:
        print("No data")
        return

    # Extraemos los datos
    tiempos, salidas = zip(*datos_acumulados)
    
    plt.figure(titulo, figsize=(9, 5))

    # 1. SALIDA: 
    plt.plot(tiempos, salidas, 'b', markersize=3, label='Output (Filt)')
    
    # 2. ENTRADA/REFERENCIA: Puntos rojos discretos alineados con el tiempo
    if referencia is not None:
        # Creamos un vector de la referencia con el mismo tiempo que la salida
        referencia_vector = [referencia] * len(tiempos)
        plt.plot(tiempos, referencia_vector, 'r', markersize=2, label='Reference')

    # Configuración de ejes (Estilo MATLAB)
    plt.xlabel('t(s)')
    plt.ylabel(r'$\omega$ (rad/s)')
    
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    
    plt.show() 
    
    # Volvemos a 'Agg' para evitar conflictos con el renderizado de Kivy
    matplotlib.use('Agg', force=True)