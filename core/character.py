import os



class Character:
    def __init__(self, character_name: str, base_assets_path: str = "assets"):
        self.name = character_name
        self.char_dir = os.path.join(base_assets_path, "SpriteSheet", character_name)
        self.config_data = {}
        self.available_animations = {}

        self._load_character_config()
        self._scan_animations()


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


    def _load_character_config(self):
        config_path = os.path.join(self.char_dir, "config.txt")
        self.config_data = self._parse_txt(config_path)


    def _scan_animations(self):
        """Detecta todos los archivos .png presentes en la carpeta del personaje."""
        if not os.path.exists(self.char_dir):
            return
        
        for file in os.listdir(self.char_dir):
            if file.lower().endswith(".png"):
                anim_name = os.path.splitext(file)[0].lower()
                self.available_animations[anim_name] = os.path.join(self.char_dir, file)


    def get_animation_data(self, state_name: str) -> dict:
        """
        Retorna la ruta y parámetros de la animación.
        Si la animación no existe para este personaje, hace fallback a 'idle'.
        """
        state_key = state_name.lower()

        # Fallback a 'idle' si el estado solicitado no existe en la carpeta
        if state_key not in self.available_animations:
            print(f"[Warning] '{state_name}' no existe para {self.name}. Usando fallback 'idle'.")
            state_key = "idle"

        sprite_path = self.available_animations[state_key]

        # Extrae los parámetros de la config con valores por defecto seguros
        frame_width = int(self.config_data.get("WIDTH", 350))
        frame_height = int(self.config_data.get("HEIGHT", 350))
        columns = int(self.config_data.get("COLUMN", 10))
        
        # El total de frames se busca por la clave en mayúsculas (ej. IDLE, GRAB, PAT, etc.)
        config_key = state_name.upper()
        total_frames = int(self.config_data.get(config_key, 340 if state_key == "idle" else 30))

        return {
            "path": sprite_path,
            "total_frames": total_frames,
            "frame_width": frame_width,
            "frame_height": frame_height,
            "columns": columns
        }
        