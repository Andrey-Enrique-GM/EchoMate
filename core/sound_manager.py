import os
import pygame
from PyQt6.QtCore import QElapsedTimer



class SoundManager:
    def __init__(self, character_name: str, assets_dir: str = "assets"):
        self.character_name = character_name
        self.sounds_dir = os.path.join(assets_dir, "Sounds", character_name)
        
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        self.sounds = {}
        
        # Timer para cooldown de hover
        self.hover_cooldown_timer = QElapsedTimer()
        self.hover_cooldown_timer.start()
        self.hover_cooldown_ms = 1000  # Cooldown de 1 segundo

        self.load_sounds()


    def load_sounds(self):
        """ Escanea la carpeta del personaje y carga todos los archivos .wav """
        if not os.path.exists(self.sounds_dir):
            print(f"[SoundManager] Error: No se encontró la carpeta {self.sounds_dir}")
            return

        for file_name in os.listdir(self.sounds_dir):
            if file_name.lower().endswith(".wav"):
                action_name = os.path.splitext(file_name)[0].lower()
                full_path = os.path.join(self.sounds_dir, file_name)
                try:
                    self.sounds[action_name] = pygame.mixer.Sound(full_path)
                except Exception as e:
                    print(f"[SoundManager] Error al cargar {full_path}: {e}")


    def stop_all_sounds(self):
        """ Detiene inmediatamente cualquier canal de audio que esté sonando """
        if pygame.mixer.get_init():
            pygame.mixer.stop()


    def play_sound(self, sound_name: str):
        """ Reproduce el sonido de una acción si existe """
        sound_key = sound_name.lower()

        if sound_key in self.sounds:
            # Control de cooldown exclusivo para el sonido de hover
            if sound_key == "hover":
                if self.hover_cooldown_timer.elapsed() < self.hover_cooldown_ms:
                    return  # Ignora si aún está dentro del tiempo de espera
                self.hover_cooldown_timer.restart()

            # Detener cualquier audio sonando antes de iniciar el nuevo
            self.stop_all_sounds()
            self.sounds[sound_key].play()
