import os
import sys



def get_base_dir():
    """ Devuelve la ruta base, ya sea ejecutando script .py o el .exe empaquetado """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


class ConfigManager:
    def __init__(self, base_assets_path: str = None):
        if base_assets_path is None:
            base_assets_path = os.path.join(get_base_dir(), "assets")
            
        self.assets_path = base_assets_path
        self.config_file = os.path.join(self.assets_path, "config.txt")
        self.global_config = {}
        self.character_config = {}
        
        self._load_global_config()
        self.active_character = self.global_config.get("START_CHAR", "GoldShip")
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
        self._load_character_config()

        # Guardar en el archivo assets/config.txt manteniendo el formato
        if os.path.exists(self.config_file):
            lines = []
            updated = False
            with open(self.config_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("START_CHAR"):
                        lines.append(f"START_CHAR={char_name}\n")
                        updated = True
                    else:
                        lines.append(line)
            
            if not updated:
                lines.append(f"START_CHAR={char_name}\n")

            with open(self.config_file, "w", encoding="utf-8") as f:
                f.writelines(lines)


def load_sleep_time():
    config_path = os.path.join("assets", "config.txt")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("SLEEP_TIME"):
                    try:
                        return int(line.split("=")[1].strip())
                    except ValueError:
                        pass
    return 400  # Valor por defecto si no lo encuentra
