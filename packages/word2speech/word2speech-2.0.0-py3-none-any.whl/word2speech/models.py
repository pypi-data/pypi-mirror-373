"""
Unifica la inferencia y el registro de los modelos TTS
"""

import abc
import logging

log = logging.getLogger(__name__)


class TTSModel(abc.ABC):
    """Plantilla para todos los modelos TTS."""

    def __init__(self, model_id, name):
        self.model_id = model_id
        self.name = name or model_id

    @abc.abstractmethod
    def generate(self, text, **kwargs):
        """
        Genera audio de texto.

        Returns:
            Tuple de (audio_bytes, format, cost, balans)
        """
        pass

    @abc.abstractmethod
    def supports(self, feature):
        """Comprobar si el modelo admite una función específica"""
        pass

    def __str__(self):
        return f"{self.name} ({self.model_id})"


class TTSRegistry:
    """Registro de los modelos TTS."""

    def __init__(self):
        self._models = {}
        self._aliases = {}

    def register(self, model, aliases):
        """Registra un modelo TTS."""
        self._models[model.model_id] = model
        if aliases:
            for alias in aliases:
                self._aliases[alias] = model.model_id
        log.debug(f"Modelo TTS regitrado: {model}")

    def get(self, model_id):
        """Obtiene un modelo por ID o alias."""
        actual_id = self._aliases.get(model_id, model_id)
        return self._models.get(actual_id)

    def list_models(self):
        """Lista todos los modelos registrados."""
        return list(self._models.values())

    def list_model_ids(self):
        """Lista todos los IDs de los modelos"""
        return list(self._models.keys())


# Instancia global del regsitro de modelos
registry = TTSRegistry()
