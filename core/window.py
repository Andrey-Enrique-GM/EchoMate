import math
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QCursor
from config import load_sleep_time
from core.sprite_animator import SpriteAnimator
from core.character import Character
from core.auto_walker import AutoWalker
from core.sound_manager import SoundManager



class PetWindow(QWidget):
    def __init__(self, character: Character, target_size: int = 230, fps: int = 35):
        super().__init__()

        self.character = character
        self.target_size = target_size
        self.current_state = None  # Se inicializa en None para permitir que set_state("intro") funcione

        self.sound_manager = SoundManager(self.character.name)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.label = QLabel(self)
        self.label.setFixedSize(self.target_size, self.target_size)
        self.label.setScaledContents(True)
        self.layout.addWidget(self.label)

        self.resize(self.target_size, self.target_size)

        # Animador IDLE permanente
        idle_data = self.character.get_animation_data("idle")
        self.idle_animator = SpriteAnimator(
            sprite_path=idle_data["path"],
            total_frames=idle_data["total_frames"],
            frame_width=idle_data["frame_width"],
            frame_height=idle_data["frame_height"],
            columns=idle_data["columns"]
        )

        # Animador para acciones secundarias
        self.action_animator = None
        self.set_state("intro")

        # Temporizador de renderizado de animación
        interval_ms = int(1000 / fps)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(interval_ms)

        # Configuración del temporizador de inactividad para SLEEP
        self.sleep_timeout_ms = load_sleep_time() * 1000
        self.inactivity_timer = QTimer(self)
        self.inactivity_timer.setSingleShot(True)
        self.inactivity_timer.timeout.connect(self.enter_sleep_state)
        self.reset_inactivity_timer()

        # Configuración de movimiento
        self.is_following = False
        self.follow_timer = QTimer(self)
        self.follow_timer.timeout.connect(self.follow_cursor)
        
        # Parámetros de velocidad constante y radio de detención
        self.speed = 5  # Velocidad de carrera (píxeles por paso)
        self.walk_speed = 0.5  # Velocidad de caminata tranquila (ajustable)
        self.follow_radius = 120.0  # Radio para detenerse antes de tocar el cursor
        
        # Módulo de caminata autónoma con la velocidad de la ventana
        self.auto_walker = AutoWalker(
            self, 
            min_rest_sec=20, 
            max_rest_sec=40, 
            walk_duration_sec=3.5, 
            speed=self.walk_speed
        )

        self.is_dragging = False
        self.has_dragged = False
        self.drag_offset = QPoint()


    def reset_inactivity_timer(self):
        """ Reinicia el contador de inactividad """
        if self.current_state == "sleep":
            self.set_state("idle")
            if hasattr(self, 'auto_walker'):
                self.auto_walker.schedule_next_walk()
        self.inactivity_timer.start(self.sleep_timeout_ms)


    def enter_sleep_state(self):
        """ Activa el estado de descanso profundo (sleep) """
        if not self.is_following and not self.is_dragging:
            self.auto_walker.cancel() # Pausa la caminata autónoma
            self.set_state("sleep")


    def set_state(self, new_state: str):
        """ Cambia el estado de la mascota y reproduce el sonido correspondiente """
        if self.current_state == new_state:
            return
            
        self.current_state = new_state.lower()

        # Reproducir el efecto de sonido (.wav)
        self.sound_manager.play_sound(self.current_state)

        if self.current_state == "idle":
            #self.sound_manager.stop_all_sounds() # Detiene audios largos al volver a idle
            self.action_animator = None
        else:
            anim_data = self.character.get_animation_data(self.current_state)
            if anim_data and anim_data.get("path"):
                self.action_animator = SpriteAnimator(
                    sprite_path=anim_data["path"],
                    total_frames=anim_data["total_frames"],
                    frame_width=anim_data["frame_width"],
                    frame_height=anim_data["frame_height"],
                    columns=anim_data["columns"]
                )


    def play_outro_and_exit(self):
        """Detiene cualquier acción y reproduce la despedida antes de salir."""
        self.is_following = False
        self.follow_timer.stop()
        self.set_state("outro")


    def update_animation(self):
        """ Actualiza la animación de la mascota """
        if self.current_state == "idle":
            pixmap = self.idle_animator.get_next_frame()
        else:
            if self.action_animator:
                pixmap = self.action_animator.get_next_frame()
            else:
                pixmap = self.idle_animator.get_next_frame()
            
            # Finalización de animaciones únicas (intro, outro, click, pat, emote1)
            if self.action_animator and self.action_animator.current_frame == 0:
                if self.current_state == "intro":
                    self.set_state("idle")
                    self.auto_walker.schedule_next_walk()  # Inicia el ciclo del vagabundo autónomo
                    return
                elif self.current_state == "outro":
                    QApplication.quit()  # Cierra la aplicación de inmediato al terminar la animación de despedida
                    return
                elif self.current_state in ["click", "pat", "emote1", "emote2"]:
                    if self.is_following:
                        self.set_state("runidle")
                    elif self.underMouse():
                        self.set_state("hover")
                    else:
                        self.set_state("idle")
                    
                    # Notifica al walker que programe la siguiente acción autónoma
                    self.auto_walker.schedule_next_walk()
                    return

        if pixmap and not pixmap.isNull():
            self.label.setPixmap(pixmap)


    def get_run_direction(self, dx: float, dy: float) -> str:
        """ Determina cuál de las 8 direcciones usar según las deltas dx y dy """
        angle = math.degrees(math.atan2(dy, dx))

        if -22.5 <= angle < 22.5:
            return "runright"
        elif 22.5 <= angle < 67.5:
            return "downright"
        elif 67.5 <= angle < 112.5:
            return "rundown"
        elif 112.5 <= angle < 157.5:
            return "downleft"
        elif angle >= 157.5 or angle < -157.5:
            return "runleft"
        elif -157.5 <= angle < -112.5:
            return "upleft"
        elif -112.5 <= angle < -67.5:
            return "runup"
        elif -67.5 <= angle < -22.5:
            return "upright"

        return "rundown"


    def follow_cursor(self):
        """ Mueve a la mascota y actualiza su animación según la distancia al cursor """
        if not self.is_following or self.current_state in ["intro", "outro"]:
            return

        cursor_pos = QCursor.pos()
        center_pos = self.geometry().center()

        dx = cursor_pos.x() - center_pos.x()
        dy = cursor_pos.y() - center_pos.y()
        distance = math.hypot(dx, dy)

        if distance > self.follow_radius:
            run_anim = self.get_run_direction(dx, dy)
            self.set_state(run_anim)

            step_x = (dx / distance) * self.speed
            step_y = (dy / distance) * self.speed

            new_x = int(self.x() + step_x)
            new_y = int(self.y() + step_y)

            self.move(new_x, new_y)
        else:
            # Al llegar dentro del radio en modo cacería, entra en reposo de carrera (runidle)
            self.set_state("runidle")


    def enterEvent(self, event):
        """ Solo entra a hover si está en idle o runidle puro, evitando interrumpir animaciones activas """
        self.reset_inactivity_timer() # Reinicia el contador con hover
        if not self.is_dragging and self.current_state == "idle" and not self.is_following:
            self.set_state("hover")
        super().enterEvent(event)


    def leaveEvent(self, event):
        """ Solo sale de hover si está en hover puro, evitando interrumpir animaciones activas """
        if not self.is_dragging and self.current_state == "hover" and not self.is_following:
            self.set_state("idle")
        super().leaveEvent(event)


    def mousePressEvent(self, event):
        """ Maneja el clic izquierdo y el clic derecho """
        self.reset_inactivity_timer() # Reinicia el contador con clic
        if self.current_state in ["intro", "outro"]:
            return

        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.has_dragged = False
            # Guarda la posición relativa de la ventana con respecto al cursor
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            
        elif event.button() == Qt.MouseButton.RightButton:
            self.set_state("click")
            event.accept()


    def mouseMoveEvent(self, event):
        """ Maneja el movimiento del personaje cuando se arrastra """
        self.reset_inactivity_timer() # Reinicia el contador con grab
        if self.is_dragging and (event.buttons() & Qt.MouseButton.LeftButton) and not self.is_following:
            delta = event.globalPosition().toPoint() - self.drag_offset
            # Si el cursor se movió más de 3 píxeles, se considera un arrastre real
            if (event.globalPosition().toPoint() - (self.frameGeometry().topLeft() + self.drag_offset)).manhattanLength() > 3:
                self.has_dragged = True
                self.set_state("grab")
            
            self.move(delta)
            event.accept()


    def mouseReleaseEvent(self, event):
        """ Maneja el evento de soltar el clic izquierdo """
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            
            if self.has_dragged:
                if self.underMouse():
                    self.set_state("hover")
                else:
                    self.set_state("idle")
            else:
                # Clic simple en el personaje
                click_x = event.position().x()
                click_y = event.position().y()
                
                left_zone_x = self.width() * 0.35    # Lado izquierdo (mejilla/accesorio)
                right_zone_x = self.width() * 0.65   # Lado derecho (mejilla/accesorio)
                head_zone_y = self.height() * 0.45   # Altura de la cabeza

                if click_x <= left_zone_x and click_y <= head_zone_y:
                    # Cancelar persecución, si estaba activa
                    if self.is_following:
                        self.is_following = False
                        self.follow_timer.stop()
                    # Clic en lado izquierdo, EMOTE1
                    self.set_state("emote1")

                elif click_x >= right_zone_x and click_y <= head_zone_y:
                    # Cancelar persecución, si estaba activa
                    if self.is_following:
                        self.is_following = False
                        self.follow_timer.stop()
                    # Clic en lado derecho, EMOTE3
                    self.set_state("emote3")

                elif click_y <= head_zone_y:
                    # Cancelar persecución, si estaba activa
                    if self.is_following:
                        self.is_following = False
                        self.follow_timer.stop()
                    # Clic en la Cabeza, PAT
                    self.set_state("pat")

                else:
                    # Clic en el Cuerpo, Persecución
                    self.is_following = not self.is_following
                    
                    if self.is_following:
                        # Iniciar persecución y reproducir sonido "run"
                        self.set_state("runidle")
                        self.sound_manager.play_sound("run")
                        self.follow_timer.start(16)
                    else:
                        # Detener persecución y volver a idle
                        self.follow_timer.stop()
                        if self.underMouse():
                            self.set_state("hover")
                        else:
                            self.set_state("idle")
                        
            event.accept()
            
        elif event.button() == Qt.MouseButton.RightButton:
            event.accept()
