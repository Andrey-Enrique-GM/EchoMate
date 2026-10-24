import sys
import os
from config import ConfigManager
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap
from core.character import Character
from core.window import PetWindow
from core.chat_window import ChatWindow
from core.groq_client import GroqEngine



# Variables globales para gestionar la ventana e icono activo
window = None
chat_win = None
tray = None

# Cargar la configuración y la clave desde .env
cfg = ConfigManager()
groq_engine = GroqEngine(api_key=cfg.groq_api_key)


def toggle_chat():
    """ Abre o cierra/oculta la ventana de chat al lado del personaje """
    global chat_win, window, cfg, groq_engine
    if chat_win is None:
        chat_win = ChatWindow(
            parent_window=window, 
            config_manager=cfg, 
            groq_engine=groq_engine
        )
        # Conectar la señal de chat_window con el refresh del tray de app.py
        chat_win.settings_changed.connect(refresh_tray)
    
    if chat_win.isVisible():
        chat_win.hide()
    else:
        chat_win.show()


def switch_character(app, new_char_name):
    """ Cambia el personaje activo y actualiza la ventana """
    global window, tray, cfg, chat_win

    if window and window.character.name.lower() == new_char_name.lower():
        return

    # Guardar la selección en el archivo de config
    cfg.set_active_character(new_char_name)

    # Detener y cerrar la ventana previa
    if window:
        window.auto_walker.cancel()
        window.close()

    # Instanciar el nuevo personaje
    character = Character(character_name=new_char_name)
    window = PetWindow(character, config_manager=cfg)
    if not cfg.hide_avatar:
        window.show()

    # Actualizar la referencia del parent en chat_win si ya existe
    if chat_win:
        chat_win.parent_window = window

    # Actualizar icono y tooltip en la barra de tareas
    update_tray_icon(character)


def update_tray_icon(character=None):
    """ Actualiza el icono de la bandeja del sistema según el estado (normal, muted, hidden) """
    global tray, cfg, window
    if not tray:
        return

    char_name = character.name if character else (window.character.name if window else "EchoMate")

    # Evaluar estados estrictos
    if getattr(cfg, 'hide_avatar', False):
        icon_filename = "echomate_hidden.png"
        status_text = "Oculto"
    elif getattr(cfg, 'mute_sounds', False):
        icon_filename = "echomate_muted.png"
        status_text = "Silenciado"
    else:
        icon_filename = "echomate_normal.png"
        status_text = "Activo"

    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_dir, "assets", "Tray", icon_filename)
    
    if os.path.exists(icon_path):
        tray.setIcon(QIcon(icon_path))
    
    tray.setToolTip(f"EchoMate - {char_name} ({status_text})")


def refresh_tray():
    """ Función para la actualización del ícono y tooltip del Tray según config """
    global tray, window
    if not tray:
        return
    current_char = window.character if (window and hasattr(window, 'character')) else None
    update_tray_icon(current_char)


def setup_tray_menu(app):
    """ Crea el menú contextual exclusivo para el Tray Icon """
    global window
    menu = QMenu()

    # Acción superior para Abrir/Cerrar el Chat
    chat_action = menu.addAction("Chat")
    chat_action.triggered.connect(toggle_chat)

    menu.addSeparator()

    # Submenú de selección de personajes en assets/SpriteSheet
    char_submenu = menu.addMenu("Cambiar personaje")
    spritesheet_dir = os.path.join("assets", "SpriteSheet")
    
    if os.path.exists(spritesheet_dir):
        available_chars = [
            d for d in os.listdir(spritesheet_dir) 
            if os.path.isdir(os.path.join(spritesheet_dir, d))
        ]
        
        for char_name in available_chars:
            action = char_submenu.addAction(char_name)
            action.triggered.connect(
                lambda checked, name=char_name: switch_character(app, name)
            )

    menu.addSeparator()

    # Acción de cierre con animación outro
    close_action = menu.addAction("Cerrar")
    close_action.triggered.connect(lambda: window.play_outro_and_exit())

    return menu


def main():
    global window, tray, cfg
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    cfg = ConfigManager()
    character = Character(character_name=cfg.active_character)
    groq_engine = GroqEngine(api_key=cfg.groq_api_key)
    
    window = PetWindow(character, config_manager=cfg)
    if not cfg.hide_avatar:
        window.show()

    # Tray Icon
    tray = QSystemTrayIcon(app)
    update_tray_icon(character)

    # El menú vive solo en el Tray Icon
    tray_menu = setup_tray_menu(app)
    tray.setContextMenu(tray_menu)
    tray.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
