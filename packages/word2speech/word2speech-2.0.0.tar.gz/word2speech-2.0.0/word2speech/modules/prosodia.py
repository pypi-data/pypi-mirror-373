import warnings

# TODO: epitran va a ser deprecada buscar otra librería para tranliteración IPA
warnings.filterwarnings("ignore", module="epitran")
warnings.filterwarnings("ignore", category=SyntaxWarning)

import epitran


class IPAError(SystemExit):
    def __init__(self, message):
        super().__init__(f"error: IPA transliterate: {message}")


def ipa_for_word(word) -> str:
    """Genera la transcripción IPA para una palabra (translitera fonemas -> grafemas)."""
    try:
        epi = epitran.Epitran("spa-Latn")
        ipa = epi.transliterate(word)
        return ipa.strip(), f"IPA generado con epitran para '{word}': {ipa}"
    except Exception as error:
        raise IPAError(f"Error con epitran para '{word}': {error}")


def ssml_for_word(
    word,
    rate="medium",
    pitch="medium",
    volume="medium",
):
    """Genera SSML para una palabra con parámetros de prosodia mejorada."""
    ipa, ipa_log = ipa_for_word(word)

    # Comprobación para ahorrar tokens: tenemos IPA válido y diferente de la palabra, usamos phoneme
    if ipa and ipa != word and len(ipa) > 0:
        return (
            f'<prosody rate="{rate}" pitch="{pitch}" volume="{volume}"><phoneme alphabet="ipa" ph="{ipa}">{word}</phoneme></prosody>',
            ipa_log,
        )
    else:
        return (
            f'<prosody rate="{rate}" pitch="{pitch}" volume="{volume}">{word}</prosody>',
            ipa_log,
        )
