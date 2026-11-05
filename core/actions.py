import webbrowser
import os
import datetime
import subprocess



def run_system_command(action_tag):
    """ Ejecuta acciones locales de forma asíncrona y retorna un mensaje si es necesario """
    action_tag = action_tag.lower().strip()
    
    try:
        if action_tag == "open_browser":
            webbrowser.open("https://www.google.com")
            return "¡Hecho! Acabo de abrir el navegador web en tu pantalla."
        
        elif action_tag == "open_notepad":
            subprocess.Popen(["notepad.exe"])
            return "Abriendo el Bloc de notas, ¡listo para tus apuntes!"
        
        elif action_tag == "open_github":
            webbrowser.open("https://github.com")
            return "Abriendo GitHub en el navegador."
        
        elif action_tag == "open_discord":
            # Intenta abrir la app de escritorio de Discord en Windows, si no, abre la versión web
            discord_path = os.path.expanduser(r"~\AppData\Local\Discord\app-*")
            try:
                # O forma estándar mediante protocolo de Windows o comando start
                os.startfile("discord://")
            except:
                webbrowser.open("https://discord.com/app")
            return "Conectando canales... Abriendo Discord en un segundo."

        elif action_tag == "open_spotify":
            try:
                os.startfile("spotify://")
            except:
                webbrowser.open("https://open.spotify.com")
            return "¡Ponle ritmo! Abriendo Spotify."

        elif action_tag == "open_steam":
            try:
                os.startfile("steam://")
            except:
                subprocess.Popen(["C:\\Program Files (x86)\\Steam\\steam.exe"])
            return "Cargando biblioteca... Abriendo Steam."

        elif action_tag == "open_gmail":
            webbrowser.open("https://mail.google.com")
            return "Abriendo tu bandeja de entrada en Gmail."

        elif action_tag == "open_vscode":
            try:
                # Abre Visual Studio Code usando el comando de consola global 'code'
                subprocess.Popen(["code"], shell=True)
            except:
                pass
            return "Iniciando entorno de desarrollo... Abriendo VS Code."

        elif action_tag == "get_time":
            now = datetime.datetime.now().strftime("%H:%M")
            # Devuelve el texto formateado para que la app lo use en el chat
            return f"Los relojes del sistema marcan las {now}."
            
    except Exception as e:
        return f"Vaya, hubo un pequeño fallo al ejecutar el comando: {str(e)}"
    
    return None
