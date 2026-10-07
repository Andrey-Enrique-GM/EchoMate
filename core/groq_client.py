import os
try:
    from groq import Groq
except ImportError:
    Groq = None



class GroqEngine:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.client = None
        if api_key and Groq:
            self.init_client(api_key)


    def init_client(self, api_key: str):
        self.api_key = api_key
        if Groq and api_key.strip():
            self.client = Groq(api_key=self.api_key)


    def is_configured(self) -> bool:
        return bool(self.client and self.api_key and self.api_key.strip())


    def get_response(self, user_message: str, character_name: str = "GoldShip") -> str:
        """ Envía la petición a la API de Groq """
        if not self.is_configured():
            return None

        system_prompt = (
            f"Eres {character_name}, un asistente virtual animado de escritorio. "
            f"Responde de forma corta, concisa, expresiva y amigable."
        )

        try:
            completion = self.client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=400,
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Error al procesar la respuesta: {str(e)}"
