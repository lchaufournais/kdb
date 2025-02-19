import os
import re
import requests
from nicegui import ui
from logging_utils import log_message, ConsoleColor, trace

OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://ollama:11434/v1/llama")

OLLAMA_API_KEY_REGEX = r'^sk(?:-proj)?-[A-Za-z0-9_-]+$'

class OpenAIClient:
    def __init__(self):
        self.api_key = None

    def set_api_key(self, key: str):
        """Set the Ollama API key with regex validation."""
        try:
            if not re.match(OLLAMA_API_KEY_REGEX, key):
                ui.notify("Invalid Ollama API key format.", color="red", position="top")
                return
            self.api_key = key
            ui.notify("API key set successfully!", color="green", position="top")
            log_message("API key validated and set.", session_id="GLOBAL")
        except Exception as e:
            log_message(f"Error in set_api_key: {e}", level="error", session_id="GLOBAL")
            ui.notify("Failed to set API key.", color="red", position="top")

    def get_response(prompt: str) -> str:
        """Appeler l'API Ollama pour obtenir une réponse à partir du prompt."""
        try:
            headers = {'Content-Type': 'application/json'}
            payload = {'prompt': prompt, 'model': 'llama2'}

            response = requests.post(OLLAMA_API_URL, json=payload, headers=headers)

            if response.status_code == 200:
                return response.json().get('response', '').strip()
            else:
                print(f"Erreur de l'API Ollama : {response.status_code}")
                return ""
        except Exception as e:
            print(f"Erreur lors de l'appel à l'API Ollama : {e}")
            return ""