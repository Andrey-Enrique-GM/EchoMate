import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QLineEdit, QPushButton
from PyQt6.QtCore import Qt



class ChatWindow(QWidget):
    def __init__(self, parent_window=None):
        super().__init__()
        self.parent_window = parent_window

        # Configuración de ventana independiente
        self.setWindowTitle("EchoMate - Chat")
        self.resize(320, 420)
        
        # Fondo blanco y estilo limpio de chat
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                color: #000000;
                font-family: Segoe UI, sans-serif;
                font-size: 14px;
            }
            QTextEdit {
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                padding: 8px;
                background-color: #FAFAFA;
            }
            QLineEdit {
                border: 1px solid #CCCCCC;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton {
                background-color: #0078D4;
                color: white;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
        """)

        self.init_ui()


    def init_ui(self):
        """ Inicializa la interfaz de usuario del chat """
        layout = QVBoxLayout()

        # Encabezado
        self.label_title = QLabel("<b>EchoMate Chat</b>")
        self.label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_title)

        # Historial de mensajes (cuadro de chat)
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setPlaceholderText("Las conversaciones aparecerán aquí...")
        layout.addWidget(self.chat_history)

        # Entrada de texto y botón enviar
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Escribe un mensaje...")
        self.input_field.returnPressed.connect(self.send_message)
        layout.addWidget(self.input_field)

        self.send_button = QPushButton("Enviar")
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)

        self.setLayout(layout)


    def send_message(self):
        text = self.input_field.text().strip()
        if text:
            self.chat_history.append(f"<b>Tú:</b> {text}")
            self.input_field.clear()


    def update_position(self):
        """ Posiciona la ventana de chat al lado izquierdo del personaje """
        if self.parent_window:
            pet_geo = self.parent_window.geometry()
            # Se coloca a la izquierda con un pequeño margen de 10px
            new_x = pet_geo.x() - self.width() - 10
            new_y = pet_geo.y()
            self.move(new_x, new_y)


    def showEvent(self, event):
        """ Al mostrarse la ventana, actualiza la posición relativa al personaje """
        self.update_position()
        super().showEvent(event)
