# PyMate ✨

[![Descargar Ejecutable](https://img.shields.io/badge/Descargar-PyMate_v1.0_(Windows)-2ea44f?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/Andrey-Enrique-GM/PyMate/releases/download/v1.0.0/PyMate_v1.0.zip)

**PyMate** es una aplicación de escritorio interactiva que trae mascotas virtuales animadas directamente a tu pantalla. Las mascotas cuentan con comportamientos autónomos como caminata independiente, seguimiento de cursor, físicas de arrastre, reproducción de efectos de sonido y reacciones a clics e interacciones según la zona del sprite donde el usuario interactúe.

## ¿Cómo está hecho?
Es una aplicación para PC desarrollada de forma modular en Python, orientada a eventos y procesamiento gráfico en tiempo real a través de las siguientes herramientas:
* **Python:** Para la arquitectura principal, el control de la lógica de estados (FSM) y la gestión de comportamientos del personaje.
* **PyQt6:** Utilizado como framework gráfico para el renderizado de ventanas transparentes sin bordes, overlay siempre visible (*always-on-top*), gestión de temporizadores de animación (*QTimer*) y captura de eventos de ratón.
* **Pygame / Wave:** Para la reproducción asíncrona de efectos de sonido y clips de audio asociados a las acciones del personaje sin congelar la interfaz.
* **SpriteSheets:** Procesamiento dinámico de hojas de sprites divididas por cuadrículas para extraer cuadros de animación continuos y fluidos a diferentes fotogramas por segundo (FPS).

## Servicios y Créditos
Este proyecto es una reinterpretación en Python basada en un proyecto original. Se reconoce el trabajo de los creadores de los recursos artísticos y del software base original:
* `Desktop Gremlin (C#)`: Proyecto original en el que está inspirado **PyMate**. Créditos especiales a **Kritzkingvoid** por el diseño conceptual y la lógica base del sistema ([REPOSITORIO](https://github.com/Kritzkingvoid/Desktop_Gremlin)).
* `Sprites y Assets Artísticos`: Todos los derechos de los diseños visuales, expresiones, animaciones y archivos de sonido pertenecientes a los personajes son propiedad de sus respectivos autores y empresas originales. Utilizados bajo fines puramente recreativos, de entretenimiento y desarrollo personal.