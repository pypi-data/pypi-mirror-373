from .mms_tts import MMSModel
from .parler_tts import ParlerModel
from .speechgen import SpeechGenModel


def discover_models():
    """Descubre y registra todos los modelos disponibles."""
    from ..models import registry

    # Registramos el modelo de SpeechGen
    speechgen = SpeechGenModel()
    registry.register(speechgen, aliases=["speechgen", "default"])

    # Registramos Parler-TTS si sus dependencias están disponibles
    try:
        parler = ParlerModel()
        registry.register(parler, aliases=["parler"])
    except ImportError:
        pass

    # Registramos MMS-TTS si sus dependencias están disponibles
    try:
        parler = MMSModel()
        registry.register(parler, aliases=["mms"])
    except ImportError:
        pass


__all__ = ["discover_models", "MMSModel", "ParlerModel", "SpeechGenModel"]
