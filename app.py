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
    window = PetWindow(character)
    window.show()

    # Actualizar la referencia del parent en chat_win si ya existe
    if chat_win:
        chat_win.parent_window = window

    # Actualizar icono y tooltip en la barra de tareas
    update_tray_icon(character)


def update_tray_icon(character):
    """ Actualiza el icono de la bandeja del sistema con el sprite del personaje """
    global tray
    if not tray:
        return

    idle_data = character.get_animation_data("idle")
    full_pixmap = QPixmap(idle_data["path"])

    if not full_pixmap.isNull():
        icon_pixmap = full_pixmap.copy(0, 0, idle_data["frame_width"], idle_data["frame_height"])
        tray.setIcon(QIcon(icon_pixmap))
    
    tray.setToolTip(f"EchoMate - {character.name}")


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
    
    window = PetWindow(character)
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
