from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QRect



class SpriteAnimator:
    def __init__(self, sprite_path: str, total_frames: int, frame_width: int, frame_height: int, columns: int):
        self.full_pixmap = QPixmap(sprite_path)
        self.total_frames = total_frames
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.columns = columns
        self.current_frame = 0

        if self.full_pixmap.isNull():
            print(f"Error cargando: {sprite_path}")


    def get_frame_at(self, frame_idx: int) -> QPixmap:
        """Obtiene un frame específico de la hoja calculando el ancho real según la imagen y los frames."""
        if self.full_pixmap.isNull():
            return QPixmap()

        frame_to_render = frame_idx % self.total_frames
        
        # --- CALCULO DINÁMICO DE ANCHO DE FRAME ---
        # Si la imagen es una tira horizontal, determina el ancho real de cada frame 
        # dividiendo el ancho total de la imagen entre el total de frames de esta animación.
        is_horizontal = self.columns <= 1 and self.full_pixmap.width() > self.frame_width
        
        if is_horizontal and self.total_frames > 0:
            actual_frame_width = self.full_pixmap.width() // self.total_frames
            effective_columns = self.total_frames
        else:
            actual_frame_width = self.frame_width
            effective_columns = self.columns

        col = frame_to_render % effective_columns
        row = frame_to_render // effective_columns

        x = col * actual_frame_width
        y = row * self.frame_height

        return self.full_pixmap.copy(QRect(x, y, actual_frame_width, self.frame_height))


    def get_next_frame(self) -> QPixmap:
        """Avanza al siguiente frame y lo devuelve."""
        pixmap = self.get_frame_at(self.current_frame)
        self.current_frame = (self.current_frame + 1) % self.total_frames
        return pixmap
