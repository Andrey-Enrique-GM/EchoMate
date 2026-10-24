import sys
import os
import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QPushButton, QFrame, QLineEdit, QStackedWidget,
    QCheckBox, QScrollArea
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
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
    """ QTextEdit personalizado oscuro que crece hasta 3 renglones, envía con Enter y pega siempre sin formato """
    def __init__(self, parent_chat=None):
        super().__init__()
        self.parent_chat = parent_chat
        self.setPlaceholderText("Escribe aquí...")
        
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.document().setDocumentMargin(2)
        
        font_metrics = self.fontMetrics()
        self.line_height = font_metrics.lineSpacing()
        
        self.base_height = 36
        self.max_height = (self.line_height * 3) + 10
        
        self.setFixedHeight(self.base_height)
        self.textChanged.connect(self.adjust_input_height)


    def adjust_input_height(self):
        """ Ajusta la altura entre 1 y 3 líneas """
        doc_height = int(self.document().size().height()) + 8
        new_height = max(self.base_height, min(doc_height, self.max_height))
        self.setFixedHeight(new_height)


    def keyPressEvent(self, event):
        """ Enter para enviar, Shift + Enter para salto de línea """
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
                if self.parent_chat:
                    self.parent_chat.send_message()
                return
        super().keyPressEvent(event)


    def insertFromMimeData(self, source):
        """ Intercepta cualquier intento de pegar texto y fuerza el formato plano """
        if source.hasText():
            plain_text = source.text()
            self.textCursor().insertText(plain_text)



class ChatWindow(QWidget):
    # Definir una señal para notificar cambios en los ajustes
    settings_changed = pyqtSignal()

    def __init__(self, parent_window=None, config_manager=None, groq_engine=None):
        super().__init__()
        self.parent_window = parent_window
        self.cfg = config_manager
        self.groq_engine = groq_engine

        # Cargar tamaño persistente desde el ConfigManager
        width = getattr(self.cfg, 'chat_width', 350) if self.cfg else 350
        height = getattr(self.cfg, 'chat_height', 480) if self.cfg else 480
        self.resize(width, height)
        
        # Para el arrastre y redimensionamiento
        self._drag_pos = QPoint()
        self._is_resizing = False
        self._resize_edge = None
        self.setMouseTracking(True) # Detecta los bordes con el mouse

        # Flags: Sin bordes de ventana + Tool (sin barra de tareas) + StaysOnTop
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.Tool | 
            Qt.WindowType.WindowStaysOnTopHint
        )
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.setWindowTitle("EchoMate - Chat")
        
        # Estilos visuales en tono oscuro EchoMate
        self.setStyleSheet("""
            /* Configuración global de texto y fuente para los elementos internos */
            QWidget {
                color: #DCE2EE;
                font-family: 'Segoe UI', system-ui, sans-serif;
                font-size: 13px;
            }

            /* Fondo de la ventana raíz totalmente transparente para las esquinas redondas */
            ChatWindow {
                background-color: transparent;
            }
            
            /* Contenedor principal con esquinas redondeadas y fondo oscuro */
            #main_container {
                background-color: #161922;
                border: 1px solid #232836;
                border-radius: 12px;
            }

            #header_frame {
                background-color: #111319;
                border-bottom: 1px solid #232836;
                border-top-left-radius: 11px;
                border-top-right-radius: 11px;
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
            #chat_scroll {
                background-color: #161922;
                border: none;
            }
            #chat_content {
                background-color: #161922;
            }
            
            /* Estilos de las Burbujas de Chat */
            .user_bubble {
                background-color: #1E40AF;
                color: #FFFFFF;
                border-radius: 8px;
                padding: 8px 12px;
            }
            .bot_bubble {
                background-color: #242938;
                border: 1px solid #2D3446;
                color: #DCE2EE;
                border-radius: 8px;
                padding: 8px 12px;
            }
            .bot_name_label {
                color: #FF5C93;
                font-weight: 600;
                font-size: 11px;
                margin-bottom: 3px;
                margin-left: 4px;
            }
            
            QScrollBar:vertical {
                background: #161922;
                width: 6px;
                margin: 0px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background: #A0AEC0;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: #242938;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
                border: none;
                background: none;
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
                padding: 4px 8px;
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
                padding: 0px 18px;
                font-weight: 600;
                font-size: 13px;
                min-height: 36px;
                max-height: 36px;
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

            QCheckBox {
                color: #DCE2EE;
                font-size: 13px;
                spacing: 8px;
            }
            QCheckBox:disabled {
                color: #64748B;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #32394E;
                border-radius: 4px;
                background-color: #242938;
            }
            QCheckBox::indicator:hover {
                border-color: #3B82F6;
            }
            QCheckBox::indicator:checked {
                background-color: #2575DC;
                border-color: #3B82F6;
            }
            QCheckBox::indicator:disabled {
                background-color: #1A1E29;
                border-color: #262B3A;
            }
            QCheckBox::indicator:checked:disabled {
                background-color: #1D3557;
                border-color: #2A4365;
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

        # Botón de Ajustes y Cerrar
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setProperty("class", "header_icon_btn")
        self.settings_btn.setToolTip("Ajustes")
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

        # Historial cambiado a QScrollArea para permitir bordes redondeados
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setObjectName("chat_scroll")
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.chat_content = QWidget()
        self.chat_content.setObjectName("chat_content")
        self.chat_layout_inner = QVBoxLayout(self.chat_content)
        self.chat_layout_inner.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout_inner.setContentsMargins(10, 10, 10, 10)
        self.chat_layout_inner.setSpacing(10)

        self.chat_scroll.setWidget(self.chat_content)
        chat_layout.addWidget(self.chat_scroll)

        # Obtener el nombre del personaje actual
        char_name = self.parent_window.character.name.lower() if (self.parent_window and hasattr(self.parent_window, 'character')) else "char"

        # Mensajes dinámicos según el personaje activo
        placeholders = {
            "goldship": "¿Qué caos armamos hoy, humano?",
            "mambo": "¿Qué tienes en mente?",
            "tachyon": "¿Qué experimento analizamos hoy?",
            "cafe": "¿Un café para charlar...?",
        }
        default_msg = "Comienza a hablar con tu asistente..."
        
        greeting_text = placeholders.get(char_name, default_msg)

        self.placeholder_label = QLabel(greeting_text)
        self.placeholder_label.setStyleSheet("color: #64748B; font-style: italic;")
        self.chat_layout_inner.addWidget(self.placeholder_label)

        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(10, 0, 10, 0)
        input_layout.setSpacing(8)

        self.input_field = MessageInputEdit(parent_chat=self)
        
        # Inputs dinámicos según el personaje activo
        input_field_placeholders = {
            "goldship": "Escríbeme algo divertido...",
            "mambo": "Escríbeme algo sin prisa...",
            "tachyon": "Escríbeme algo interesante...",
            "cafe": "Escríbeme despacio...",
        }
        default_msg = "Escribe aquí..."
        
        self.input_field.setPlaceholderText(input_field_placeholders.get(char_name, default_msg))
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

        settings_title = QLabel("<b>Ajustes</b>")
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

        self.hide_avatar_checkbox = QCheckBox("Ocultar personaje")
        self.hide_avatar_checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        if self.cfg and hasattr(self.cfg, 'hide_avatar'):
            self.hide_avatar_checkbox.setChecked(self.cfg.hide_avatar)

        self.mute_checkbox = QCheckBox("Silenciar sonidos")
        self.mute_checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        if self.cfg and hasattr(self.cfg, 'mute_sounds'):
            self.mute_checkbox.setChecked(self.cfg.mute_sounds)

        # Si el personaje está oculto, bloquear la opción de silenciar para que permanezca activa
        if self.hide_avatar_checkbox.isChecked():
            self.mute_checkbox.setChecked(True)
            self.mute_checkbox.setEnabled(False)
            self.mute_checkbox.setToolTip("Los sonidos están silenciados automáticamente porque el personaje está oculto")

        self.mute_checkbox.toggled.connect(self.on_mute_toggled)
        self.hide_avatar_checkbox.toggled.connect(self.on_hide_avatar_toggled)

        # Botón para Reiniciar Chat dentro del menú de Ajustes
        clear_chat_btn = QPushButton("🗑 Reiniciar Conversación")
        clear_chat_btn.setObjectName("clear_chat_btn")
        clear_chat_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_chat_btn.clicked.connect(self.clear_chat_context)

        settings_layout.addWidget(settings_title)
        settings_layout.addWidget(key_label)
        settings_layout.addWidget(self.api_key_input)
        settings_layout.addWidget(save_btn)
        settings_layout.addSpacing(5)
        settings_layout.addWidget(self.hide_avatar_checkbox)
        settings_layout.addWidget(self.mute_checkbox)
        settings_layout.addSpacing(5)
        settings_layout.addWidget(clear_chat_btn)
        settings_layout.addStretch()

        self.stack.addWidget(settings_widget)

        main_layout.addWidget(self.stack)
        root_layout.addWidget(main_container)


    def _get_resize_edge(self, pos):
        """ Detecta si el cursor está en un borde para permitir redimensionar la ventana """
        margin = 8
        rect = self.rect()
        x, y = pos.x(), pos.y()
        
        left = x < margin
        right = x > rect.width() - margin
        top = y < margin
        bottom = y > rect.height() - margin
        
        if top and left: return "top_left"
        if top and right: return "top_right"
        if bottom and left: return "bottom_left"
        if bottom and right: return "bottom_right"
        if left: return "left"
        if right: return "right"
        if top: return "top"
        if bottom: return "bottom"
        return None


    def mousePressEvent(self, event):
        """ Inicia el arrastre o el redimensionamiento de la ventana """
        if event.button() == Qt.MouseButton.LeftButton:
            self._resize_edge = self._get_resize_edge(event.pos())
            if self._resize_edge:
                self._is_resizing = True
                self._drag_pos = event.globalPosition().toPoint()
                event.accept()
            else:
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()


    def mouseMoveEvent(self, event):
        """ Maneja el cambio de tamaño o la posición de la ventana """
        # Si se está redimensionando
        if self._is_resizing:
            global_pos = event.globalPosition().toPoint()
            diff = global_pos - self._drag_pos
            self._drag_pos = global_pos
            
            geo = self.geometry()
            if "left" in self._resize_edge:
                geo.setLeft(geo.left() + diff.x())
            if "right" in self._resize_edge:
                geo.setRight(geo.right() + diff.x())
            if "top" in self._resize_edge:
                geo.setTop(geo.top() + diff.y())
            if "bottom" in self._resize_edge:
                geo.setBottom(geo.bottom() + diff.y())
                
            self.setGeometry(geo)
            event.accept()
            return

        # Si se está arrastrando la ventana normalmente
        if event.buttons() == Qt.MouseButton.LeftButton and not self._drag_pos.isNull():
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()


    def mouseReleaseEvent(self, event):
        """ Restablece estados al soltar el clic """
        self._is_resizing = False
        self._resize_edge = None
        super().mouseReleaseEvent(event)


    def keyPressEvent(self, event):
        """ Presionar Escape (Esc) oculta el chat """
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            event.accept()
        else:
            super().keyPressEvent(event)


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
        
        # Limpiar widgets del contenedor de chat
        while self.chat_layout_inner.count():
            item = self.chat_layout_inner.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
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


    def on_mute_toggled(self, checked):
        if self.cfg:
            self.cfg.set_mute_sounds(checked)
        if checked and self.parent_window and hasattr(self.parent_window, 'sound_manager'):
            self.parent_window.sound_manager.stop_all_sounds()

        # Emitir la señal para actualizar el Tray Icon
        self.settings_changed.emit()


    def on_hide_avatar_toggled(self, checked):
        if self.cfg:
            self.cfg.set_hide_avatar(checked)
        
        # Si se oculta el avatar, se silencia obligatoriamente y se deshabilita la casilla
        if checked:
            self.mute_checkbox.setChecked(True)
            self.mute_checkbox.setEnabled(False)
            self.mute_checkbox.setToolTip("Los sonidos están silenciados automáticamente porque el personaje está oculto")
            if self.cfg:
                self.cfg.set_mute_sounds(True)
        else:
            self.mute_checkbox.setEnabled(True)
            self.mute_checkbox.setToolTip("")

        # Ocultar o mostrar la ventana principal del personaje sin cerrar el programa
        if self.parent_window:
            if checked:
                # Desactivar interacción y ocultar
                self.parent_window.hide()
            else:
                self.parent_window.show()
                self.parent_window.update_position() if hasattr(self.parent_window, 'update_position') else None

        # Emitir la señal para actualizar el Tray Icon
        self.settings_changed.emit()


    def send_message(self):
        """ Envía el mensaje ingresado por el usuario """
        text = self.input_field.toPlainText().strip()
        if not text:
            return

        # Elimina el placeholder si existe
        if hasattr(self, 'placeholder_label') and self.placeholder_label:
            self.placeholder_label.deleteLater()
            self.placeholder_label = None

        formatted_user_text = parse_markdown_to_html(text)
        
        # Burbuja del USUARIO (Derecha)
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addStretch()

        bubble = QLabel(formatted_user_text)
        bubble.setProperty("class", "user_bubble")
        bubble.setWordWrap(True)
        row_layout.addWidget(bubble)

        self.chat_layout_inner.addLayout(row_layout)
        
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
        
        # Burbuja del PERSONAJE (Izquierda)
        container_widget = QWidget()
        v_layout = QVBoxLayout(container_widget)
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.setSpacing(2)

        name_lbl = QLabel(character_name)
        name_lbl.setProperty("class", "bot_name_label")
        
        bubble = QLabel(formatted_bot_text)
        bubble.setProperty("class", "bot_bubble")
        bubble.setWordWrap(True)

        v_layout.addWidget(name_lbl)
        v_layout.addWidget(bubble)

        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addWidget(container_widget)
        row_layout.addStretch()

        self.chat_layout_inner.addLayout(row_layout)


    def update_position(self):
        """ Posiciona inteligentemente la ventana de chat evitando que se salga de los límites de la pantalla """
        if self.parent_window:
            pet_geo = self.parent_window.geometry()
            
            # Obtiene la pantalla actual donde está el personaje
            current_screen = self.screen() or self.parent_window.screen()
            screen_geo = current_screen.availableGeometry()
            
            chat_width = self.width()
            chat_height = self.height()
            
            # Lógica Horizontal (X): Intenta izquierda, si no hay espacio, pasa a la derecha
            new_x = pet_geo.x() - chat_width - 10
            if new_x < screen_geo.left():
                # Coloca a la derecha del personaje si a la izquierda no hay espacio
                new_x = pet_geo.x() + pet_geo.width() + 10
                
            # Lógica Vertical (Y): Alinea con el personaje, pero ajustando si se sale arriba o abajo
            new_y = pet_geo.y()
            
            # Si se sale por la parte inferior de la pantalla, subirlo
            if new_y + chat_height > screen_geo.bottom():
                new_y = screen_geo.bottom() - chat_height - 10
                
            # Si se sale por la parte superior de la pantalla, bajarlo
            if new_y < screen_geo.top():
                new_y = screen_geo.top() + 10
                
            self.move(new_x, new_y)


    def showEvent(self, event):
        """ Se ejecuta automáticamente al mostrar la ventana """
        self.update_position()
        super().showEvent(event)
        self.input_field.setFocus()
        self.activateWindow()


    def resizeEvent(self, event):
        """ Detecta cuando el usuario redimensiona la ventana y guarda los valores """
        super().resizeEvent(event)
        if self.cfg:
            self.cfg.set_chat_geometry(self.width(), self.height())


    def closeEvent(self, event):
        """ Asegura guardar el tamaño final justo antes de ocultar o cerrar """
        if self.cfg:
            self.cfg.set_chat_geometry(self.width(), self.height())
        super().closeEvent(event)
        