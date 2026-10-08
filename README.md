# EchoMate ✨💬

[![Descargar Ejecutable](https://img.shields.io/badge/Descargar-EchoMate_v1.0_(Windows)-2ea44f?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/Andrey-Enrique-GM/EchoMate/releases/download/v1.0.0/EchoMate_v1.0.zip)

**EchoMate** es un asistente virtual de escritorio e interactivo que trae mascotas y personajes animados directamente a tu pantalla. Combina comportamientos autónomos (caminata independiente, seguimiento de cursor, físicas de arrastre y efectos de sonido) con un **chat inteligente** integrado que le permite conversar, mantener contexto de tus charlas y asistirte en el día a día.

---

## 🚀 Características Principales

* **Mascotas Autónomas de Escritorio:** Animaciones fluidas en tiempo real, físicas de arrastre, movimiento aleatorio y respuestas a interacciones del usuario según la zona del sprite.
* **Chat Integrado con IA:** Conversa directamente con tu mascota a través de una ventana flotante integrada (*Always-On-Top*).
* **Memoria de Conversación:** Mantiene el contexto de las charlas anteriores para ofrecer respuestas coherentes y continuas.
* **Integración Abierta con Groq API:** Funciona utilizando la API gratuita de **Groq**, permitiendo respuestas ultra rápidas con modelos de lenguaje de última generación.
* **Privacidad y Configuración Local:** Tus claves API se almacenan de forma totalmente local en un archivo de entorno `.env` en tu equipo, asegurando la privacidad de tus datos.

---

## 🛠️ ¿Cómo está hecho?

Es una aplicación para PC desarrollada de forma modular en Python, orientada a eventos y procesamiento gráfico/conversacional en tiempo real a través de las siguientes herramientas:

* **Python:** Arquitectura principal, control de lógica de estados (FSM) y gestión de comportamientos del personaje.
* **PyQt6:** Framework gráfico para el renderizado de ventanas transparentes sin bordes, overlay siempre visible (*always-on-top*), temporizadores de animación (*QTimer*) y la interfaz del chat interactivo.
* **Groq SDK & python-dotenv:** Conexión asíncrona con la API de Groq para procesamiento de lenguaje natural y gestión segura de variables de entorno locales.
* **Pygame / Wave:** Reproducción de efectos de sonido y clips de audio asociados a las acciones del personaje sin congelar la interfaz.
* **SpriteSheets:** Procesamiento dinámico de hojas de sprites divididas por cuadrículas para extraer cuadros de animación continuos a diferentes FPS.

---

## 🔑 Configuración de la IA (Groq API Key)

Para habilitar las respuestas inteligentes de tu personaje:

1. Obtén tu clave de API gratuita en [console.groq.com](https://console.groq.com).
2. Abre la ventana de chat en **EchoMate**.
3. Haz clic en el icono de **Ajustes (⚙)** en la esquina superior derecha.
4. Pega tu API Key (`gsk_...`) y haz clic en **Guardar**.
5. ¡Listo! Tu clave quedará guardada en tu archivo `.env` local de forma segura.

---

## 👥 Servicios y Créditos

Este proyecto es una evolución interactiva basada en desarrollos y herramientas open source previo:

* `Desktop Gremlin (C#)`: Proyecto original en el que se inspira la lógica base de mascotas de escritorio. Créditos especiales a **Kritzkingvoid** ([REPOSITORIO](https://github.com/Kritzkingvoid/Desktop_Gremlin)).
* `PyMate`: Proyecto base para **EchoMate**, migración inicial de físicas, renderizado en PyQt6 y animaciones 2D (Sin chat de IA).
* `Sprites y Assets Artísticos`: Todos los derechos de los diseños visuales, expresiones, animaciones y archivos de sonido pertenecientes a los personajes son propiedad de sus respectivos autores y empresas originales. Utilizados bajo fines puramente recreativos, de entretenimiento y desarrollo personal.