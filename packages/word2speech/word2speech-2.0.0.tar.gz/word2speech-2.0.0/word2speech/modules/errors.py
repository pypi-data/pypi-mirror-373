"""
Definimos errores personalizados para la valdación del fichero de configuración.
"""


class ConfigError(SystemExit):
    _type = ""

    def __init__(self, message):
        super().__init__(f'error: config file: argumento "{self._type}": {message}')


class FormatError(ConfigError):
    _type = "format"


class SpeedError(ConfigError):
    _type = "speed"


class PitchError(ConfigError):
    _type = "pitch"


class EmotionError(ConfigError):
    _type = "emotion"


class BitrateError(ConfigError):
    _type = "bitrate"


class ContourError(ConfigError):
    _type = "contour"
