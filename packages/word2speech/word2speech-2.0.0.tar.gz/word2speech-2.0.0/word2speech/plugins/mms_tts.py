"""
Implementación del modelo TTS de Facebook MMS-TTS
Utilizando la abstracción de la plantilla TTSModel
"""

from io import BytesIO

from ..config import config
from ..models import TTSModel

try:
    import soundfile as sf
    import torch
    from transformers import AutoTokenizer, VitsModel

    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False


class MMSModel(TTSModel):
    """Modelo TTS de Facebook MMS-TTS interfaz unificada."""

    def __init__(self):
        if not DEPS_AVAILABLE:
            raise ImportError("Las dependencias de MMS-TTS no están disponibles. Instalalas con: pip install torch transformers soundfile")

        super().__init__("facebook/mms-tts-spa", "Facebook MMS-TTS Spanish")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._model = None
        self._tokenizer = None

    @property
    def model(self):
        """Lazy load model."""
        if self._model is None:
            self._model = VitsModel.from_pretrained(self.model_id).to(self.device)
        return self._model

    @property
    def tokenizer(self):
        """Lazy load tokenizer."""
        if self._tokenizer is None:
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        return self._tokenizer

    def generate(self, text, **kwargs):
        """Genrar audio usando MMS-TTS"""
        model_config = config.get_model_config(self.model_id)

        speaking_rate = model_config.get("speed", 1.0)
        noise_scale = model_config.get("noise_scale", 0.667)

        if "speed" in kwargs:
            speaking_rate = kwargs["speed"]

        # Configuramos los parámetros en el modelo
        self.model.speaking_rate = speaking_rate
        self.model.noise_scale = noise_scale

        # Tokeniza entradas, genera audio
        inputs = self.tokenizer(text, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            output = self.model(**inputs).waveform
        audio_arr = output.cpu().numpy().squeeze()

        # Guardamos en un buffer y leemos los bytes
        buffer = BytesIO()
        sf.write(buffer, audio_arr, self.model.config.sampling_rate, format="WAV")
        buffer.seek(0)  # Salvaguarda incio del audio·
        audio_bytes = buffer.read()

        return (audio_bytes, "wav", 0, 0)

    def supports(self, feature: str) -> bool:
        """Features soportadas por el modelo"""
        supported_features = {
            "ssml": False,
            "voices": False,
            "speed": True,
            "pitch": False,
            "emotions": False,
            "contour": False,
            "offline": True,
        }
        return supported_features.get(feature, False)
