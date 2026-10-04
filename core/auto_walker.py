import math
import random
from PyQt6.QtCore import QObject, QTimer
from PyQt6.QtGui import QGuiApplication



class AutoWalker(QObject):
    def __init__(self, window, min_rest_sec: int = 20, max_rest_sec: int = 40, walk_duration_sec: float = 3.5, speed: float = 0.5):
        super().__init__()
        self.window = window
        self.min_rest = min_rest_sec
        self.max_rest = max_rest_sec
        self.walk_duration_ms = int(walk_duration_sec * 1000)
        
        # Velocidad en píxeles por paso (modificable en window.py)
        self.speed = speed

        # Temporizadores
        self.rest_timer = QTimer(self)
        self.rest_timer.setSingleShot(True)
        self.rest_timer.timeout.connect(self.trigger_random_action) # Decidir acción por probabilidad

        self.walk_timer = QTimer(self)
        self.walk_timer.timeout.connect(self._step)

        self.duration_timer = QTimer(self)
        self.duration_timer.setSingleShot(True)
        self.duration_timer.timeout.connect(self.stop_walk)

        self.dx = 0.0
        self.dy = 0.0
        self.pos_x = 0.0
        self.pos_y = 0.0
        self.is_walking = False


    def get_walk_direction(self, dx: float, dy: float) -> str:
        """ Determina la animación de caminata según el ángulo de dirección en 4 ejes """
        angle = math.degrees(math.atan2(dy, dx))

        if -45 <= angle < 45:
            return "walkright"
        elif 45 <= angle < 135:
            return "walkdown"
        elif angle >= 135 or angle < -135:
            return "walkleft"
        else:
            return "walkup"


    def schedule_next_walk(self):
        """ Programa el próximo evento si no se está caminando o arrastrando """
        if not self.is_walking and not self.rest_timer.isActive():
            wait_time_ms = random.randint(self.min_rest * 1000, self.max_rest * 1000)
            self.rest_timer.start(wait_time_ms)


    def trigger_random_action(self):
        """ Elige aleatoriamente entre caminar o hacer uno de los 3 emotes según sus probabilidades """
        # Permitimos cambiar de estado si está en "idle" o en el bucle continuo de "emote3"
        valid_states = ["idle", "emote3"]
        if self.window.current_state not in valid_states or self.window.is_following or self.window.is_dragging:
            self.schedule_next_walk()
            return

        # Lista de acciones y sus pesos de probabilidad (Caminar: 2, Emotes: 1 cada uno)
        actions = ["walk", "emote1", "emote2", "emote3"]
        weights = [2, 1, 1, 1]

        chosen_action = random.choices(actions, weights=weights, k=1)[0]

        if chosen_action == "walk":
            self.start_walk()
        else:
            # Ejecuta el emote elegido
            self.window.set_state(chosen_action)
            # Si es emote3 (bucle), programa el temporizador para que en el futuro decida la siguiente acción
            if chosen_action == "emote3":
                self.schedule_next_walk()


    def start_walk(self):
        """ Calcula una dirección aleatoria, asigna la animación y comienza a caminar """
        angle = random.uniform(0, 2 * math.pi)
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed

        # Posición flotante actual
        self.pos_x = float(self.window.x())
        self.pos_y = float(self.window.y())

        # Validar límites de pantalla
        screen_geo = QGuiApplication.primaryScreen().geometry()
        future_x = self.pos_x + (self.dx * (self.walk_duration_ms / 16))
        future_y = self.pos_y + (self.dy * (self.walk_duration_ms / 16))

        if future_x < 0 or future_x + self.window.width() > screen_geo.width():
            self.dx *= -1
        if future_y < 0 or future_y + self.window.height() > screen_geo.height():
            self.dy *= -1

        # Asignar la animación de caminata según la dirección calculada
        walk_state = self.get_walk_direction(self.dx, self.dy)
        self.window.set_state(walk_state)

        self.is_walking = True
        self.walk_timer.start(16)
        self.duration_timer.start(self.walk_duration_ms)


    def _step(self):
        """ Aplica un paso de movimiento """
        if not self.is_walking:
            return

        if self.window.is_dragging or self.window.is_following or self.window.current_state in ["intro", "outro", "grab", "click"]:
            self.stop_walk()
            return

        self.pos_x += self.dx
        self.pos_y += self.dy
        self.window.move(int(self.pos_x), int(self.pos_y))


    def stop_walk(self):
        """ Detiene el movimiento y restablece la animación """
        self.is_walking = False
        self.walk_timer.stop()
        self.duration_timer.stop()

        if self.window.current_state not in ["intro", "outro", "grab", "click"] and not self.window.is_following:
            self.window.set_state("idle")

        self.schedule_next_walk()


    def cancel(self):
        """ Cancela temporizadores """
        self.is_walking = False
        self.rest_timer.stop()
        self.walk_timer.stop()
        self.duration_timer.stop()
        