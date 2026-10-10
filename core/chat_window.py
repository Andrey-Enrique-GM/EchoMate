import os
import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QPushButton, QFrame, QLineEdit, QStackedWidget
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPixmap



def parse_markdown_to_html(text: str) -> str:
    """ Convierte sintaxis básica de Markdown (**bold**, *italic*, `code`) a HTML """
    # Reemplazar saltos de línea por <br>
    formatted = text.replace('\n', '<br>')
    # Bold **text**
    formatted = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', formatted)
    # Italic *text*
    formatted = re.sub(r'\*(.*?)\*', r'<i>\1</i>', formatted)
    # Inline Code `code`
    formatted = re.sub(r'`(.*?)`', r'<code style="background-color: #2D3446; padding: 2px 4px; border-radius: 4px;">\1</code>', formatted)
    return formatted



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
    def __init__(self, parent_window=None, config_manager=None, groq_engine=None):
        super().__init__()
        self.parent_window = parent_window
        self.cfg = config_manager
        self.groq_engine = groq_engine
        
        # Para el arrastre de ventana sin bordes
        self._drag_pos = QPoint()

        # Flags: Sin bordes de ventana + Tool (sin barra de tareas) + StaysOnTop
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.Tool | 
            Qt.WindowType.WindowStaysOnTopHint
        )
        
        self.setWindowTitle("EchoMate - Chat")
        self.resize(350, 480)
        
        # Estilos visuales en tono oscuro EchoMate
        self.setStyleSheet("""
            QWidget {
                background-color: #161922;
                color: #DCE2EE;
                font-family: 'Segoe UI', system-ui, sans-serif;
                font-size: 13px;
            }
            
            /* Contenedor principal con borde suave para compensar la falta de marco */
            #main_container {
                border: 1px solid #232836;
                border-radius: 8px;
            }

            #header_frame {
                background-color: #111319;
                border-bottom: 1px solid #232836;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 4px 8px;
            }
            #header_title {
                color: #FFFFFF;
                font-weight: 600;
                font-size: 14px;
            }
            .header_icon_btn {
                background-color: transparent;
                border: none;
                color: #A0AEC0;
                font-size: 14px;
                padding: 2px 6px;
            }
            .header_icon_btn:hover {
                color: #FFFFFF;
            }
            #close_btn:hover {
                color: #FF5C93;
            }

            /* Historial */
            #chat_history {
                background-color: #161922;
                border: none;
                padding: 10px;
                line-height: 1.4;
            }
            
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

            /* Entrada y botones */
            QLineEdit {
                background-color: #242938;
                color: #FFFFFF;
                border: 1px solid #32394E;
                border-radius: 6px;
                padding: 6px 10px;
            }
            QLineEdit:focus {
                border: 1px solid #3B82F6;
            }

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

            #send_button, #save_key_btn {
                background-color: #2575DC;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 8px 18px;
                font-weight: 600;
                font-size: 13px;
                min-height: 20px;
            }
            #send_button:hover, #save_key_btn:hover {
                background-color: #3B82F6;
            }
            
            #clear_chat_btn {
                background-color: #242938;
                color: #FF5C93;
                border: 1px solid #32394E;
                border-radius: 8px;
                padding: 8px 14px;
                font-weight: 600;
            }
            #clear_chat_btn:hover {
                background-color: #2D3446;
            }
        """)

        self.init_ui()


    def init_ui(self):
        # Contenedor raíz para aplicar el borde redondeado
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        main_container = QFrame()
        main_container.setObjectName("main_container")
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 10)
        main_layout.setSpacing(8)

        # Cabecera superior (Logo + EchoMate + Ajustes + Cerrar)
        header_frame = QFrame()
        header_frame.setObjectName("header_frame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 6, 10, 6)
        header_layout.setSpacing(8)

        # Logo de EchoMate
        logo_label = QLabel()
        logo_path = os.path.join(os.getcwd(), "echoMate.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                logo_label.setPixmap(pixmap.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        title_label = QLabel("EchoMate")
        title_label.setObjectName("header_title")

        # Botón de Ajustes (⚙) y Cerrar (✕)
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setProperty("class", "header_icon_btn")
        self.settings_btn.setToolTip("Ajustes de IA")
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.clicked.connect(self.toggle_settings)

        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("close_btn")
        self.close_btn.setProperty("class", "header_icon_btn")
        self.close_btn.setToolTip("Cerrar ventana")
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.clicked.connect(self.hide)

        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.settings_btn)
        header_layout.addWidget(self.close_btn)
        main_layout.addWidget(header_frame)

        # Contenedor con StackedWidget para alternar entre Chat y Ajustes
        self.stack = QStackedWidget()

        # CHAT 
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(8)

        self.chat_history = QTextEdit()
        self.chat_history.setObjectName("chat_history")
        self.chat_history.setReadOnly(True)
        self.chat_history.setPlaceholderText("Comienza a hablar con tu asistente...")
        chat_layout.addWidget(self.chat_history)

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
        chat_layout.addWidget(input_container)

        self.stack.addWidget(chat_widget)

        # AJUSTES
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_layout.setContentsMargins(15, 10, 15, 10)
        settings_layout.setSpacing(12)

        settings_title = QLabel("<b>Ajustes de IA</b>")
        settings_title.setStyleSheet("font-size: 15px; color: #FFFFFF;")
        
        key_label = QLabel("Groq API Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("gsk_...")
        
        # Cargar clave existente si está guardada
        if self.cfg and hasattr(self.cfg, 'groq_api_key'):
            self.api_key_input.setText(self.cfg.groq_api_key)

        save_btn = QPushButton("Guardar Clave")
        save_btn.setObjectName("save_key_btn")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self.save_api_key)

        # Botón para Reiniciar Chat dentro del menú de Ajustes
        clear_chat_btn = QPushButton("🗑 Reiniciar Conversación")
        clear_chat_btn.setObjectName("clear_chat_btn")
        clear_chat_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_chat_btn.clicked.connect(self.clear_chat_context)

        settings_layout.addWidget(settings_title)
        settings_layout.addWidget(key_label)
        settings_layout.addWidget(self.api_key_input)
        settings_layout.addWidget(save_btn)
        settings_layout.addSpacing(10)
        settings_layout.addWidget(clear_chat_btn)
        settings_layout.addStretch()

        self.stack.addWidget(settings_widget)

        main_layout.addWidget(self.stack)
        root_layout.addWidget(main_container)


    def mousePressEvent(self, event):
        """ Detecta el clic izquierdo del mouse """
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()


    def mouseMoveEvent(self, event):
        """ Permite arrastrar la ventana """
        if event.buttons() == Qt.MouseButton.LeftButton and not self._drag_pos.isNull():
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()


    def toggle_settings(self):
        """ Alterna entre la pantalla de Chat y la pantalla de Ajustes """
        if self.stack.currentIndex() == 0:
            self.stack.setCurrentIndex(1)
        else:
            self.stack.setCurrentIndex(0)


    def clear_chat_context(self):
        """ Limpia la memoria del chat """
        if self.groq_engine:
            self.groq_engine.clear_history()
        self.chat_history.clear()
        self.stack.setCurrentIndex(0)
        char_name = self.parent_window.character.name if self.parent_window else "EchoMate"
        self.add_bot_response(char_name, "¡Memoria del chat borrada! ¿De qué quieres hablar ahora?")


    def save_api_key(self):
        """ Guarda la clave localmente en el archivo de configuración """
        new_key = self.api_key_input.text().strip()
        if self.cfg:
            self.cfg.set_groq_api_key(new_key)
        if self.groq_engine:
            self.groq_engine.init_client(new_key)
        
        # Volver al chat
        self.stack.setCurrentIndex(0)
        char_name = self.parent_window.character.name if self.parent_window else "EchoMate"
        self.add_bot_response(char_name, "¡Perfecto! Tu clave de Groq ha sido guardada. ¡Ahora sí podemos conversar!")


    def send_message(self):
        """ Envía el mensaje ingresado por el usuario """
        text = self.input_field.toPlainText().strip()
        if not text:
            return

        formatted_user_text = parse_markdown_to_html(text)
        
        # Muestra el mensaje del usuario
        self.chat_history.append(
            f'<div style="margin-bottom: 10px;">'
            f'<span style="color: #4A90E2; font-weight: bold;">You</span><br>'
            f'<span style="color: #DCE2EE;">{formatted_user_text}</span>'
            f'</div>'
        )
        
        self.input_field.clear()
        self.input_field.adjust_input_height()

        char_name = self.parent_window.character.name if self.parent_window else "EchoMate"

        # Verificar si el archivo .env existe o si la clave está vacía
        env_exists = self.cfg.has_env_file if self.cfg else False
        has_key = self.groq_engine and self.groq_engine.is_configured()

        if not env_exists or not has_key:
            tutorial_msg = (
                f"¡Hola! Parece que aún no tienes configurada una **Groq API Key** (no se encontró el archivo `.env`) para habilitar mi inteligencia. 🤖\n\n"
                f"Obtener una es **100% gratis** y te tomará solo 1 minuto:\n"
                f"1. Entra en **console.groq.com** y crea una cuenta.\n"
                f"2. Ve a la sección **API Keys** y haz clic en *Create API Key*.\n"
                f"3. Copia tu clave (empieza con `gsk_...`).\n"
                f"4. Haz clic en el botón de engrane **⚙** arriba a la derecha, pégala y dale a **Guardar**.\n\n"
                f"¡Y listo! Se creará el archivo `.env` automáticamente en la carpeta principal para siempre."
            )
            self.add_bot_response(char_name, tutorial_msg)
        else:
            # Procesa la respuesta con Groq
            response = self.groq_engine.get_response(text, character_name=char_name)
            self.add_bot_response(char_name, response)


    def add_bot_response(self, character_name, text):
        """ Convierte la respuesta Markdown a HTML y la renderiza """
        formatted_bot_text = parse_markdown_to_html(text)
        self.chat_history.append(
            f'<div style="margin-bottom: 10px;">'
            f'<span style="color: #FF5C93; font-weight: bold;">{character_name}</span><br>'
            f'<span style="color: #DCE2EE;">{formatted_bot_text}</span>'
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
