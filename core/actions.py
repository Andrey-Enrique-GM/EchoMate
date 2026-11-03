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
            return "Abriendo GitHub en el navegador, choomba."
        
        elif action_tag == "get_time":
            now = datetime.datetime.now().strftime("%H:%M")
            # Devolvemos el texto formateado para que la app lo use en el chat
            return f"Los relojes del sistema marcan las {now}."
            
    except Exception as e:
        return f"Vaya, hubo un pequeño fallo al ejecutar el comando: {str(e)}"
    
    return None
