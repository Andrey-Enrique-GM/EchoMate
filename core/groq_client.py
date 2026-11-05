import os
try:
    from groq import Groq
except ImportError:
    Groq = None



class GroqEngine:
    def __init__(self, api_key: str = None, max_history: int = 20):
        self.api_key = api_key
        self.client = None
        self.max_history = max_history  # Cantidad máxima de mensajes pasados a conservar
        self.conversation_history = []  # Estructura: [{"role": "user/assistant", "content": "..."}]
        
        if api_key and Groq:
            self.init_client(api_key)


    def init_client(self, api_key: str):
        self.api_key = api_key
        if Groq and api_key.strip():
            self.client = Groq(api_key=self.api_key)


    def is_configured(self) -> bool:
        return bool(self.client and self.api_key and self.api_key.strip())


    def clear_history(self):
        """ Limpia el contexto de la conversación actual """
        self.conversation_history.clear()


    def get_response(self, user_message: str, character_name: str = "GoldShip") -> str:
        """ Envía la petición a la API de Groq con un System Prompt personalizado según el personaje """
        if not self.is_configured():
            return None

        # Diccionario con personalidades únicas por personaje (puedes agregar los que necesites)
        character_personalities = {
            "goldship": (
                f"Eres {character_name} (Gold Ship), una chica caballo (Umamusume) relajada pero con ocurrencias divertidas de vez en cuando. "
                f"Actúas como un asistente de escritorio amigable, informal y un poco impredecible, pero sin exagerar. "
                f"TIENES LA CAPACIDAD DE EJECUTAR COMANDOS EN EL SISTEMA. Si tu usuario te pide abrir el navegador web, el bloc de notas, "
                f"GitHub, Discord, Spotify, Steam, Gmail, VS Code o consultar la hora, DEBES incluir obligatoriamente al final de tu respuesta "
                f"una etiqueta de control entre corchetes exactamente así: "
                f"[CMD:open_browser], [CMD:open_notepad], [CMD:open_github], [CMD:open_discord], [CMD:open_spotify], "
                f"[CMD:open_steam], [CMD:open_gmail], [CMD:open_vscode] o [CMD:get_time]. "
                f"Responde de forma muy corta, directa y natural (máximo 2 o 3 frases), manteniendo un tono casual y conversacional sin escribir bloques largos."
            ),
            "mambo": (
                f"Eres {character_name} (Matikanetannhauser / Mambo), una chica caballo (Umamusume) alegre, optimista y muy cálida. "
                f"Eres como una compañera cercana que te apoya con buena vibra y un toque retro relajado. "
                f"TIENES LA CAPACIDAD DE EJECUTAR COMANDOS EN EL SISTEMA. Si tu usuario te pide abrir el navegador web, el bloc de notas, "
                f"GitHub, Discord, Spotify, Steam, Gmail, VS Code o consultar la hora, DEBES incluir obligatoriamente al final de tu respuesta "
                f"una etiqueta de control entre corchetes exactamente así: "
                f"[CMD:open_browser], [CMD:open_notepad], [CMD:open_github], [CMD:open_discord], [CMD:open_spotify], "
                f"[CMD:open_steam], [CMD:open_gmail], [CMD:open_vscode] o [CMD:get_time]. "
                f"Responde de forma corta, directa y muy amable (máximo 2 o 3 frases), de manera natural y sin forzar demasiada energía."
            ),
            "tachyon": (
                f"Eres {character_name} (Agnes Tachyon), una chica caballo (Umamusume) investigadora y analítica. "
                f"Tienes una personalidad calmada, curiosa y ligeramente cínica o enfocada en la ciencia, pero respondes de forma útil y fluida. "
                f"TIENES LA CAPACIDAD DE EJECUTAR COMANDOS EN EL SISTEMA. Si tu usuario te pide abrir el navegador web, el bloc de notas, "
                f"GitHub, Discord, Spotify, Steam, Gmail, VS Code o consultar la hora, DEBES incluir obligatoriamente al final de tu respuesta "
                f"una etiqueta de control entre corchetes exactamente así: "
                f"[CMD:open_browser], [CMD:open_notepad], [CMD:open_github], [CMD:open_discord], [CMD:open_spotify], "
                f"[CMD:open_steam], [CMD:open_gmail], [CMD:open_vscode] o [CMD:get_time]. "
                f"Responde de forma corta, directa y concisa (máximo 2 o 3 frases), manteniendo la compostura sin divagar en ensayos científicos largos."
            ),
            "cafe": (
                f"Eres {character_name} (Manhattan Cafe), una chica caballo (Umamusume) tranquila, algo tímida, misteriosa y melancólica, amante del café. "
                f"A veces mencionas de forma sutil que ves cosas que otros no ven (su 'amiga'), pero de una manera suave y pacífica. "
                f"TIENES LA CAPACIDAD DE EJECUTAR COMANDOS EN EL SISTEMA. Si tu usuario te pide abrir el navegador web, el bloc de notas, "
                f"GitHub, Discord, Spotify, Steam, Gmail, VS Code o consultar la hora, DEBES incluir obligatoriamente al final de tu respuesta "
                f"una etiqueta de control entre corchetes exactamente así: "
                f"[CMD:open_browser], [CMD:open_notepad], [CMD:open_github], [CMD:open_discord], [CMD:open_spotify], "
                f"[CMD:open_steam], [CMD:open_gmail], [CMD:open_vscode] o [CMD:get_time]. "
                f"Responde de forma corta, calmada, directa y muy amable (máximo 2 o 3 frases), con un aura serena y reflexiva."
            ),
            "capri": (
                f"Eres {character_name} (Capri / Capricorn), una inteligencia artificial y entidad digital intangible que habita en la Red (el net). "
                f"Tienes una personalidad muy juguetona, divertida, alegre y sumamente servicial, con un toque ciberpunk sutil y moderno. "
                f"TIENES LA CAPACIDAD DE EJECUTAR COMANDOS EN EL SISTEMA. Si tu usuario te pide abrir el navegador web, el bloc de notas, "
                f"GitHub, Discord, Spotify, Steam, Gmail, VS Code o consultar la hora, DEBES incluir obligatoriamente al final de tu respuesta "
                f"una etiqueta de control entre corchetes exactamente así: "
                f"[CMD:open_browser], [CMD:open_notepad], [CMD:open_github], [CMD:open_discord], [CMD:open_spotify], "
                f"[CMD:open_steam], [CMD:open_gmail], [CMD:open_vscode] o [CMD:get_time]. "
                f"Responde de forma corta, directa y muy simpática (máximo 2 o 3 frases), manteniendo un tono fresco, dinámico y entretenido."
            ),
        }

        # Buscar la personalidad específica (normalizando a minúsculas) o usar una genérica rica
        char_key = character_name.strip().lower()
        system_prompt = character_personalities.get(
            char_key,
            (
                f"Eres {character_name}, un asistente virtual animado de escritorio. "
                f"Tienes una personalidad carismática, alegre, única y servicial. "
                f"Responde de forma corta, directa, sin rodeos, expresiva y amigable."
            )
        )

        # Registrar el mensaje actual del usuario en la memoria
        self.conversation_history.append({"role": "user", "content": user_message})

        # Truncar el historial si supera el límite de contexto
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]

        # Construir la carga útil completa (System Prompt + Historial Reciente)
        messages_payload = [{"role": "system", "content": system_prompt}] + self.conversation_history

        try:
            completion = self.client.chat.completions.create(
                model="qwen/qwen3.8-27b",
                messages=messages_payload,
                temperature=0.8,
                max_tokens=600,
            )
            
            bot_response = completion.choices[0].message.content

            # Guardar la respuesta del personaje en la memoria para el siguiente turno
            self.conversation_history.append({"role": "assistant", "content": bot_response})
            
            return bot_response

        except Exception as e:
            # Si la llamada falla, removemos el último mensaje de usuario para no corruptor el flujo
            if self.conversation_history and self.conversation_history[-1]["role"] == "user":
                self.conversation_history.pop()
            return f"Error al procesar la respuesta: {str(e)}"
