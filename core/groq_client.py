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
        """ Envía la petición a la API de Groq """
        if not self.is_configured():
            return None

        # Definir el System Prompt
        system_prompt = (
            f"Eres {character_name}, un asistente virtual animado de escritorio. "
            f"Tienes personalidad carismática, alegre y servicial. "
            f"Responde de forma corta, directa, sin rodeos, expresiva y amigable."
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
                temperature=0.7,
                max_tokens=600,
            )
            
            bot_response = completion.choices[0].message.content

            # Guardar la respuesta del bot en la memoria para el siguiente turno
            self.conversation_history.append({"role": "assistant", "content": bot_response})
            
            return bot_response

        except Exception as e:
            # Si la llamada falla, removemos el último mensaje de usuario para no corruptor el flujo
            if self.conversation_history and self.conversation_history[-1]["role"] == "user":
                self.conversation_history.pop()
            return f"Error al procesar la respuesta: {str(e)}"
