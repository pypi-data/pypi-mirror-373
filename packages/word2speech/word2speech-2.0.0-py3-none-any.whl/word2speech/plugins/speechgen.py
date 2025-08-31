""" "
Implementación del modelo TTS de speechgen.io
Utilizando la abstracción de la plantilla TTSModel
"""

import requests
from requests.exceptions import HTTPError

from ..config import config
from ..models import TTSModel
from ..modules.utilities import Contour


class SpeechGenModel(TTSModel):
    """Modelo TTS de speechgen.io con interfaz unificada."""

    def __init__(self):
        super().__init__("speechgen.io", "SpeechGen.io")
        self.url = "https://speechgen.io/index.php?r=api/text"

        self.speaker_map = {"female": "Estrella", "male": "Alvaro"}
        self.pitch_map = {"low": -10, "normal": 0, "high": 10}
        self.emotion_map = {"calm": "good", "energetic": "evil", "neutral": "neutral"}

    def generate(self, text, **kwargs):
        """Generar audio utilizando la API de SpeechGen.io."""
        params = self._build_params(text, **kwargs)

        response = self._make_request(params)

        # Manejo de la respuesta de speechgen.io
        if response["status"] == 1:
            if "file" in response and "format" in response:
                file_url = response["file"]
                file_format = response["format"]
                audio = requests.get(file_url).content
                return (audio, file_format, response["cost"], response["balans"])
            else:
                raise HTTPError(f"404 Not Found: {response['error']}")
        else:
            if "login" in response["error"]:
                raise HTTPError(f"401 Unauthorized: {response['error']}")
            else:
                raise HTTPError(f"400 Bad Request: {response['error']}")

    def supports(self, feature):
        """Features soportadas por el modelo"""
        supported_features = {
            "ssml": True,
            "voices": True,
            "speed": True,
            "pitch": True,
            "emotions": True,
            "contour": True,
            "offline": False,
        }
        return supported_features.get(feature, False)

    def _build_params(self, text, **kwargs):
        model_config = config.get_model_config(self.model_id)

        params = {
            "token": config.get_api_key("speechgen"),
            "email": config.get_api_key("speechgen-email"),
            "voice": model_config.get("voice", "Alvaro"),
            "format": "wav",
            "speed": 1.0,
            "pitch": 0,
            "emotion": "neutral",
            "bitrate": 44100,
        }

        # Validamos parámetros obligatorios
        if not params["token"]:
            raise ValueError("Token es obligatorio para SpeechGen API. Para configurarlo: word2speech keys set speechgen TU_TOKEN")
        if not params["email"]:
            raise ValueError("Email es obligatorio para SpeechGen API. Para configurarlo: word2speech keys set speechgen-email TU_EMAIL")

        # Sobreescribimos los parámetros modificados
        if "voice" in kwargs:
            params["voice"] = self.speaker_map.get(kwargs["voice"].lower(), kwargs["voice"])
        if "speed" in kwargs:
            params["speed"] = kwargs["speed"]
        if "pitch" in kwargs:
            try:
                params["pitch"] = int(kwargs["pitch"])
            except ValueError:
                params["pitch"] = self.pitch_map.get(kwargs["pitch"].lower(), 0)
        if "emotion" in kwargs:
            params["emotion"] = self.emotion_map.get(kwargs["emotion"].lower(), params["emotion"])

        # Manejo específico de los puntos de contorno
        if "contour" in kwargs:
            text = format(Contour(kwargs["contour"]), text)

        params["text"] = text
        return params

    def _make_request(self, params):
        """Petición a al API de speechgen.io."""
        response = requests.post(self.url, data=params)
        return response.json()
