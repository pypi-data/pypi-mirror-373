import json
import os.path
from argparse import ArgumentTypeError

from .errors import (
    BitrateError,
    ContourError,
    EmotionError,
    FormatError,
    PitchError,
    SpeedError,
)


class Contour:
    """
    Genera el contructor de entonación con los valores indicados, alrededor
    de la palabra.
        - contour: Puntos de entonación
        - word: Palabra a convertir
    """

    _template = '<prosody contour="{d.contour}">{word}</prosody>'

    def __init__(self, contour):
        if len(contour) > 5:
            raise SystemExit("error: No puede haber más de cinco puntos de entonación")
        contour_list = []
        for point in contour:
            time, pitch = point.split(",")
            try:
                time = int(time)
                pitch = int(pitch)
                contour_list.append(f"({time}%,{pitch:+}%)")
            except ValueError:
                pass

        self.contour = " ".join(contour_list)

    def __format__(self, word):
        return self._template.format(d=self, word=word)


def is_valid_file_word(arg):
    """
    Valida que el argumento de entrada sea una palabra o un fichero
    con la estructura correcta.
    """
    if os.path.isfile(arg):
        with open(arg, encoding="utf-8") as f:
            try:
                words = json.load(f)
                for value in words.values():
                    if not isinstance(value, list):
                        raise ArgumentTypeError("La estructura del fichero es incorrecta.")
                return words
            except json.JSONDecodeError as error:
                raise ArgumentTypeError("El formato del fichero es incorrecto.") from error
    else:
        return arg


def validate_format(fmt, Error=ArgumentTypeError):
    if fmt not in ("mp3", "wav", "ogg"):
        raise Error(f"Opción invalida: '{fmt}' (escoge entre 'mp3', 'wav', 'ogg')")
    return fmt


def validate_speed(speed, Error=ArgumentTypeError):
    try:
        speed = float(speed)
        if not 0.1 <= speed <= 2.0:
            raise Error(f"Opción invalida: {speed} (rango entre 0.1 y 2.0)")
        return speed
    except ValueError:
        raise Error(f"Valor de tipo float inválido: {speed}")


def validate_pitch(pitch, Error=ArgumentTypeError):
    try:
        pitch = int(pitch)
        if not -20 <= pitch <= 20:
            raise Error(f"Opción invalida: {pitch} (rango entre -20 y 20)")
        return pitch
    except ValueError:
        raise Error(f"Valor de tipo int inválido: {pitch}")


def validate_emotion(emotion, Error=ArgumentTypeError):
    if emotion not in ("evil", "good", "neutral"):
        raise Error(f"Opción invalida: '{emotion}' (escoge entre 'evil', 'good', 'neutral')")
    return emotion


def validate_bitrate(bitrate, Error=ArgumentTypeError):
    try:
        bitrate = int(bitrate)
        if not 8000 <= bitrate <= 192000:
            raise Error(f"Opción invalida: {bitrate} (rango entre 8000 y 192000)")
        return bitrate
    except ValueError:
        raise Error(f"Valor de tipo int inválido: {bitrate}")


def validate_contour_point(point, Error=ArgumentTypeError):
    print(point)
    try:
        time, pitch = [int(p) for p in point.split(",")]
        if not 0 <= time <= 100:
            raise Error(f"Porcentaje tiempo invalido: {time} (rango entre 0 y 100)")
        if not -100 <= pitch <= 100:
            raise Error(f"Porcentaje entonación invalido: {pitch} (rango entre -100 y 100)")
        return time, pitch
    except ValueError:
        raise Error(f"Valor de tipo int inválido: {point}")


def validate_config_file(config):
    if "format" in config:
        validate_format(config.get("format"), FormatError)
    if "speed" in config:
        validate_speed(config.get("speed"), SpeedError)
    if "pitch" in config:
        validate_pitch(config.get("pitch"), PitchError)
    if "emotion" in config:
        validate_emotion(config.get("emotion"), EmotionError)
    if "bitrate" in config:
        validate_bitrate(config.get("bitrate"), BitrateError)
    if "contour" in config:
        contour = []
        for point in config.get("contour"):
            contour.append(validate_contour_point(point, ContourError))
        config["contour"] = contour
