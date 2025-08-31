"""
Predice la calidad percibida de la voz
"""

import logging
import os
import sys

log = logging.getLogger(__name__)


try:
    import librosa
    import torch

    AUDIO_DEPS_AVAILABLE = True
except ImportError:
    AUDIO_DEPS_AVAILABLE = False
    log.warning("La dependencias para módulo de análisis de audio no está disponibles. Instalar con pipx word2speech[analysis]")


class AudioAnalyzer:
    """
    Predice el índice MOS (Mean Opinion Score):
    Medida de 1 a 5 que refleja qué tan natural o inteligible suena un audio, según percepción humana.
    """

    def __init__(self):
        if not AUDIO_DEPS_AVAILABLE:
            raise ImportError("La dependencias para módulo de análisis de audio no está disponibles. Instalar con pipx word2speech[analysis]")

    def analyze_file(self, audio_path):
        try:
            wave, sr = librosa.load(audio_path, sr=None, mono=True)

            # Silenciamos la salida de SpeechMOS
            stdout, stderr = sys.stdout, sys.stderr
            sys.stdout = open(os.devnull, "w")
            sys.stderr = open(os.devnull, "w")

            predictor = torch.hub.load("tarepan/SpeechMOS:v1.2.0", "utmos22_strong", trust_repo=True)
            score = predictor(torch.from_numpy(wave).unsqueeze(0), sr)

            sys.stdout, sys.stderr = stdout, stderr

            return score.item()
        except Exception as e:
            log.error(f"Error analizando {audio_path}: {e}")
            return 0.0
