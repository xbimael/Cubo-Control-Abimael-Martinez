# Sistema de Control de Motor CC (TFG)

Este repositorio contiene el desarrollo completo del software para la monitorización y control de un motor de corriente continua (CC), desarrollado como parte de mi Trabajo de Fin de Grado. El sistema permite la comunicación en tiempo real con un Arduino para la adquisición de datos y la aplicación de diferentes estrategias de control a través de plataformas en Python y MATLAB.

---

## 📂 Estructura del Repositorio

El proyecto está organizado en las siguientes carpetas según el entorno de desarrollo y la tecnología utilizada:

* **`Arduino/aplicacion_AML/`**: Contiene el código fuente (`.ino`) que debe cargarse en la placa Arduino
* **`Version_Python/`**: Aloja las implementaciones de la interfaz gráfica utilizando Python, Kivy y KivyMD:
    * `DCmotor_RA/`: Versión del software en Python para Regulación Automática.
    * `DCmotor_CD/`: Versión del software en Python para Control Digital.
* **`Version_Matlab/`**: Contiene las aplicaciones de escritorio interactivas desarrolladas con **MATLAB App Designer** para el control y análisis del motor:
    * `DCmotor_AML_RA.mlapp`: Aplicación ejecutable en MATLAB para la versión de Regulación Automática.
    * `DCmotor_AML_CD.mlapp`: Aplicación ejecutable en MATLAB para la versión de Control Digital.

---

## 🚀 Cómo Hacerlo Funcionar

### 1. Preparación del Hardware (Arduino)
1. Conecta la placa Arduino a tu ordenador mediante el cable USB.
2. Abre el IDE de Arduino y carga el sketch ubicado en `Arduino/aplicacion_AML/aplicacion_AML.ino`.
3. Selecciona la placa correcta, el puerto COM asignado y realiza el *upload* del código.

### 2. Ejecución de las Aplicaciones de Python
Para ejecutar cualquiera de las dos aplicaciones de Python (`DCmotor_RA` o `DCmotor_CD`) desde el entorno de desarrollo:

1. Asegúrate de tener instalado **Python 3.10+**.
2. Abre la terminal dentro de la carpeta de la versión que quieras lanzar (por ejemplo, `cd Version_Python/DCmotor_RA`).
3. Instala las dependencias requeridas:

### 3. Ejecución de las Aplicaciones de MATLAB

Para abrir y utilizar los archivos `.mlapp`, necesitas disponer de una de las siguientes dos opciones en tu sistema:

#### Opción A: Si dispones de una licencia de MATLAB
1. Abre MATLAB y navega en su explorador de archivos hasta la carpeta `Version_Matlab/`.
2. Haz doble clic sobre la aplicación que desees utilizar (`DCmotor_AML_CD.mlapp` o `DCmotor_AML_RA.mlapp`).
3. Se abrirá el entorno de **App Designer**. Haz clic en el botón **Run** (Ejecutar) en la barra superior para iniciar la interfaz.

#### Opción B: Si NO tienes MATLAB instalado (Mediante MATLAB Runtime)
Para ejecutar las aplicaciones sin necesidad de instalar el software completo ni adquirir una licencia:
1. Es necesario descargar e instalar el **MATLAB Runtime** gratuito desde la web oficial de MathWorks.
2. **Importante:** Debes seleccionar la versión **R2025a (10.0)**, ya que es la versión exacta en la que se han desarrollado estas aplicaciones.
3. Una vez instalado el Runtime, podrás ejecutar el entorno de la aplicación de forma directa en tu sistema.
   ```bash
   pip install -r requirements.txt
