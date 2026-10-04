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
        """Obtiene un frame específico de la hoja sin alterar el contador interno."""
        if self.full_pixmap.isNull():
            return QPixmap()

        frame_to_render = frame_idx % self.total_frames
        col = frame_to_render % self.columns
        row = frame_to_render // self.columns

        x = col * self.frame_width
        y = row * self.frame_height

        return self.full_pixmap.copy(QRect(x, y, self.frame_width, self.frame_height))


    def get_next_frame(self) -> QPixmap:
        """Avanza al siguiente frame y lo devuelve."""
        pixmap = self.get_frame_at(self.current_frame)
        self.current_frame = (self.current_frame + 1) % self.total_frames
        return pixmap
