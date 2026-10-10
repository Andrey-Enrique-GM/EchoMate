import os
import sys
from dotenv import load_dotenv, set_key

# Cargar variables del entorno desde .env al iniciar la aplicación
load_dotenv()



def get_base_dir():
    """ Devuelve la ruta base real, ya sea ejecutando script.py o el .exe empaquetado """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

# Cargar explícitamente el .env desde la ruta base absoluta
env_path = os.path.join(get_base_dir(), ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)



class ConfigManager:
    def __init__(self, base_assets_path: str = None):
        if base_assets_path is None:
            base_assets_path = os.path.join(get_base_dir(), "assets")
            
        self.assets_path = base_assets_path
        self.config_file = os.path.join(self.assets_path, "config.txt")
        self.env_path = os.path.join(get_base_dir(), ".env")
        
        self.global_config = {}
        self.character_config = {}
        
        self._load_global_config()
        self.active_character = self.global_config.get("START_CHAR", "GoldShip")
        
        # Verificar si el archivo .env existe físicamente
        self.has_env_file = os.path.exists(self.env_path)
        
        # Leer la API Key del entorno
        self.groq_api_key = os.getenv("GROQ_API_KEY", "")
        
        self._load_character_config()


    def _parse_txt(self, file_path: str) -> dict:
        data = {}
        if not os.path.exists(file_path):
            return data
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    data[key.strip()] = value.strip()
        return data


    def _load_global_config(self):
        self.global_config = self._parse_txt(self.config_file)


    def _load_character_config(self):
        char_path = os.path.join(self.assets_path, "SpriteSheet", self.active_character, "config.txt")
        self.character_config = self._parse_txt(char_path)


    def get_sprite_path(self, animation_name: str = "idle") -> str:
        return os.path.join(self.assets_path, "SpriteSheet", self.active_character, f"{animation_name}.png")


    def set_active_character(self, char_name: str):
        """ Actualiza la variable en memoria y sobreescribe START_CHAR en assets/config.txt """
        self.active_character = char_name
        self.global_config["START_CHAR"] = char_name
        
        if os.path.exists(self.config_file):
            lines = []
            updated = False
            with open(self.config_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("START_CHAR"):
                        lines.append(f"START_CHAR={char_name}\n")
                        updated = True
                    else:
                        lines.append(line if line.endswith('\n') else line + '\n')
            
            if not updated:
                lines.append(f"START_CHAR={char_name}\n")

            with open(self.config_file, "w", encoding="utf-8") as f:
                f.writelines(lines)
                
        self._load_character_config()


    def set_groq_api_key(self, api_key: str):
        """ Crea o actualiza el archivo .env con el formato GROQ_API_KEY='...' en la ruta principal """
        self.groq_api_key = api_key
        
        # Asegurar que el archivo .env exista o se cree en la ruta base
        if not os.path.exists(self.env_path):
            with open(self.env_path, "w", encoding="utf-8") as f:
                f.write(f"GROQ_API_KEY='{api_key}'\n")
        else:
            set_key(self.env_path, "GROQ_API_KEY", f"'{api_key}'")
            
        self.has_env_file = True


def load_sleep_time():
    config_path = os.path.join(get_base_dir(), "assets", "config.txt")
    
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("SLEEP_TIME"):
                    try:
                        # Se obtiene solo el valor numérico antes de cualquier caracter extraño
                        val_str = line.split("=")[1].strip()
                        return int(''.join(filter(str.isdigit, val_str)))
                    except (ValueError, IndexError):
                        pass
    return 400  # Valor por defecto si no lo encuentra
