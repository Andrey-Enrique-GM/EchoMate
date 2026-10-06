import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QPushButton, QFrame
)
from PyQt6.QtCore import Qt



class MessageInputEdit(QTextEdit):
    """ QTextEdit personalizado oscuro que crece hasta 3 renglones y envía con Enter """
    def __init__(self, parent_chat=None):
        super().__init__()
        self.parent_chat = parent_chat
        self.setPlaceholderText("Escribe aquí...")
        
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        font_metrics = self.fontMetrics()
        self.line_height = font_metrics.lineSpacing()
        self.padding = 12 
        
        self.min_height = self.line_height + self.padding
        self.max_height = (self.line_height * 3) + self.padding
        
        self.setFixedHeight(self.min_height)
        self.textChanged.connect(self.adjust_input_height)


    def adjust_input_height(self):
        """ Ajusta la altura entre 1 y 3 líneas """
        doc_height = int(self.document().size().height()) + (self.padding // 2)
        new_height = max(self.min_height, min(doc_height, self.max_height))
        self.setFixedHeight(new_height)


    def keyPressEvent(self, event):
        """ Enter para enviar; Shift + Enter para salto de línea """
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
                if self.parent_chat:
                    self.parent_chat.send_message()
                return
        super().keyPressEvent(event)



class ChatWindow(QWidget):
    def __init__(self, parent_window=None):
        super().__init__()
        self.parent_window = parent_window

        # Flags: Ventana tipo Tool (sin barra de tareas) + StaysOnTop (siempre visible sobre todo)
        self.setWindowFlags(
            Qt.WindowType.Window | 
            Qt.WindowType.Tool | 
            Qt.WindowType.WindowStaysOnTopHint
        )
        
        self.setWindowTitle("EchoMate - Chat")
        self.resize(350, 480)
        
        # Estilos inspirados en Echo
        self.setStyleSheet("""
            QWidget {
                background-color: #161922;
                color: #DCE2EE;
                font-family: 'Segoe UI', system-ui, sans-serif;
                font-size: 13px;
            }
            
            /* Header superior EchoMate */
            #header_frame {
                background-color: #111319;
                border-bottom: 1px solid #232836;
                padding: 4px 8px;
            }
            #header_title {
                color: #FFFFFF;
                font-weight: 600;
                font-size: 14px;
            }

            /* Área de historial de chat */
            #chat_history {
                background-color: #161922;
                border: none;
                padding: 10px;
                line-height: 1.4;
            }
            
            /* Estilo para las barras de desplazamiento */
            QScrollBar:vertical {
                background: #161922;
                width: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #2D3446;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }

            /* Caja de entrada de texto */
            MessageInputEdit {
                background-color: #242938;
                color: #FFFFFF;
                border: 1px solid #32394E;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 13px;
            }
            MessageInputEdit:focus {
                border: 1px solid #3B82F6;
            }

            /* Botón Enviar */
            #send_button {
                background-color: #2575DC;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 8px 18px;
                font-weight: 600;
                font-size: 13px;
                min-height: 20px;
            }
            #send_button:hover {
                background-color: #3B82F6;
            }
            #send_button:pressed {
                background-color: #1D61B8;
            }
        """)

        self.init_ui()


    def init_ui(self):
        """ Configura la interfaz de usuario de la ventana de chat """
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 10)
        main_layout.setSpacing(8)

        # Cabecera superior (EchoMate)
        header_frame = QFrame()
        header_frame.setObjectName("header_frame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(12, 8, 12, 8)

        title_label = QLabel("EchoMate")
        title_label.setObjectName("header_title")

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        main_layout.addWidget(header_frame)

        # Historial de mensajes
        self.chat_history = QTextEdit()
        self.chat_history.setObjectName("chat_history")
        self.chat_history.setReadOnly(True)
        self.chat_history.setPlaceholderText("Comienza a hablar con tu asistente...")
        main_layout.addWidget(self.chat_history)

        # Área inferior de entrada de texto + Botón enviar
        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(10, 0, 10, 0)
        input_layout.setSpacing(8)

        self.input_field = MessageInputEdit(parent_chat=self)
        
        self.send_button = QPushButton("Enviar")
        self.send_button.setObjectName("send_button")
        self.send_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_button.clicked.connect(self.send_message)

        input_layout.addWidget(self.input_field, alignment=Qt.AlignmentFlag.AlignBottom)
        input_layout.addWidget(self.send_button, alignment=Qt.AlignmentFlag.AlignBottom)

        main_layout.addWidget(input_container)
        self.setLayout(main_layout)


    def send_message(self):
        """ Envía el mensaje ingresado por el usuario """
        text = self.input_field.toPlainText().strip()
        if text:
            formatted_text = text.replace('\n', '<br>')
            
            # "You" (usuario)
            self.chat_history.append(
                f'<div style="margin-bottom: 10px;">'
                f'<span style="color: #4A90E2; font-weight: bold;">You</span><br>'
                f'<span style="color: #DCE2EE;">{formatted_text}</span>'
                f'</div>'
            )
            
            self.input_field.clear()
            self.input_field.adjust_input_height()
            self.input_field.setFocus()


    def add_bot_response(self, character_name, text):
        """ Método para agregar respuestas del personaje con el color distintivo de Echo """
        formatted_text = text.replace('\n', '<br>')
        self.chat_history.append(
            f'<div style="margin-bottom: 10px;">'
            f'<span style="color: #FF5C93; font-weight: bold;">{character_name}</span><br>'
            f'<span style="color: #DCE2EE;">{formatted_text}</span>'
            f'</div>'
        )


    def update_position(self):
        """ Posiciona la ventana de chat al lado izquierdo del personaje """
        if self.parent_window:
            pet_geo = self.parent_window.geometry()
            new_x = pet_geo.x() - self.width() - 10
            new_y = pet_geo.y()
            self.move(new_x, new_y)


    def showEvent(self, event):
        """ Se ejecuta automáticamente al mostrar la ventana """
        self.update_position()
        super().showEvent(event)
        self.input_field.setFocus()
        self.activateWindow()
