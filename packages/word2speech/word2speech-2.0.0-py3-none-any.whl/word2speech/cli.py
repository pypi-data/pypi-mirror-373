#!/usr/bin/env python
"""
Herramienta de Generación de Audio Adaptativo mediante TTS para la mejora de la
conciencia en dificultades específicas del aprendizaje.
"""

import logging
import sys
from pathlib import Path

import click

from .config import config
from .models import registry
from .plugins import discover_models

log = logging.getLogger(__name__)


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Mostrar version")
@click.option("--verbose", "-v", is_flag=True, help="Verbose logging")
@click.pass_context
def cli(ctx, version, verbose):
    """word2speech: Herramienta CLI para el manejo de modelos TTS."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s] %(levelname)s: %(message)s", force=True)
    else:
        logging.basicConfig(level=logging.INFO, format="[%(asctime)s]: %(message)s", datefmt="%H:%M:%S", force=True)

    # Registra todos los modelos disponibles
    discover_models()

    if version:
        click.echo("word2speech version 1.0.3")
        return

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.argument("text")
@click.option("-m", "--model", default="speechgen.io", help="Modelo TTS a usar (default: speechgen.io)")
@click.option("-o", "--output", default="out", help="Nombre del archivo de salida")
@click.option("--voice", help="Voz: male/female o nombre específico (p.ej., 'Alvaro')")
@click.option("--speed", type=float, help="Velocidad del habla: 0.1-2.0 (default: 1.0)")
@click.option("--pitch", help="Tono: low/normal/high or -20 to 20 (default: 0)")
@click.option("--emotion", help="Emoción: calm/energetic/neutral (default: neutral)")
@click.option("--contour", "-c", multiple=True, metavar="tiempo,tono", help="Detalle de entonación. %tiempo  duración (0 a 100), %tono entonación (-100 a 100)")
def speak(text, model, output, voice, speed, pitch, emotion, contour):
    """
    Generar voz a partir de texto usando modelos TTS.

    \b
    Ejemplos:
        word2speech speak "hola mundo"
        word2speech speak "hola" --voice female --speed 1.2 --emotion calm

    \b
    Para listar los modelos:
        word2speech models
    """
    tts_model = registry.get(model)
    if not tts_model:
        click.echo(f"Moldelo '{model}' no encontrado.", err=True)
        click.echo("Usa 'word2speech models' para ver los modelos disponibles.", err=True)
        sys.exit(1)

    options = {}
    if voice:
        options["voice"] = voice
    if speed:
        options["speed"] = speed
    if pitch:
        options["pitch"] = pitch
    if emotion:
        options["emotion"] = emotion
    if contour:
        options["contour"] = contour

    try:
        log.info(f'Generando audio para: "{text}"')
        audio, file_format, cost, balance = tts_model.generate(text, **options)

        output_file = f"{output}.{file_format}"
        with open(output_file, "wb") as f:
            f.write(audio)

        log.info(f'Audio generado "{output_file}" (coste: {cost}, saldo: {balance})')

    except Exception as e:
        click.echo(f"Error generando audio: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("word")
@click.option("-m", "--model", default="speechgen.io", help="Modelo TTS a usar (default: speechgen.io)")
@click.option("-o", "--output", default="out_spell", help="Nombre del archivo de salida")
@click.option("--pause", default=250, help="Pausa entre sílabas (ms)")
@click.option("--include-word", is_flag=True, help="Incluir palabra completa al final")
def spell(word, model, output, pause, include_word):
    """Deletrea una palabra sílaba a sílaba"""
    tts_model = registry.get(model)
    if not tts_model:
        click.echo(f"Moldelo '{model}' no encontrado.", err=True)
        click.echo("Usa 'word2speech models' para ver los modelos disponibles.", err=True)
        sys.exit(1)

    if not tts_model.supports("ssml"):
        click.echo(f"El modelo '{model}' no soporta deletreo (requiere SSML)", err=True)
        sys.exit(1)

    from .modules.deletrear import spell_word

    try:
        spelled_text = spell_word(word, pause)
        if include_word:
            spelled_text += f'<break time="1s" /> {word}'

        log.info(f'Generando deletreo de sílabas: "{word}"')
        log.info(f"Texto deletreado: {spelled_text}")

        audio, file_format, cost, balance = tts_model.generate(spelled_text)
        output_file = f"{output}.{file_format}"

        with open(output_file, "wb") as f:
            f.write(audio)

        log.info(f'Audio deletreado generado "{output_file}" (coste: {cost}, saldo: {balance})')

    except Exception as e:
        click.echo(f"Error generando audio deletreado: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("word")
@click.option("-m", "--model", default="speechgen.io", help="Modelo TTS a usar (default: speechgen.io)")
@click.option("-o", "--output", default="out_prosody", help="Nombre del archivo de salida")
@click.option("--rate", default="medium", help="Velocidad del habla")
@click.option("--pitch-level", default="medium", help="Nivel de tono")
@click.option("--volume", default="medium", help="Nivel de volumen")
def prosody(word, model, output, rate, pitch_level, volume):
    """Genera voz con prosodia mejorada usando SSML y IPA"""
    tts_model = registry.get(model)
    if not tts_model:
        click.echo(f"Moldelo '{model}' no encontrado.", err=True)
        click.echo("Usa 'word2speech models' para ver los modelos disponibles.", err=True)
        sys.exit(1)

    if not tts_model.supports("ssml"):
        click.echo(f"El modelo '{model}' no soporta prosodia mejorada (requiere SSML)", err=True)
        sys.exit(1)

    from .modules.prosodia import ssml_for_word

    try:
        ssml_text, ssml_log = ssml_for_word(word, rate=rate, pitch=pitch_level, volume=volume)

        if ssml_log:
            log.info(ssml_log)
        log.info(f'Generando audio enriquecido con prosodia: "{word}"')
        log.info(f"SSML: {ssml_text}")

        audio, file_format, cost, balance = tts_model.generate(ssml_text)
        output_file = f"{output}.{file_format}"

        with open(output_file, "wb") as f:
            f.write(audio)

        log.info(f'Audio prosódico generado "{output_file}" (coste: {cost}, saldo: {balance})')

    except Exception as e:
        click.echo(f"Error generando audio prosódico: {e}", err=True)
        sys.exit(1)


@cli.command()
def models():
    """Lista los models TTS disponibles o muestra información detallada de un modelo."""
    available_models = registry.list_models()
    if not available_models:
        click.echo("No hay modelos TTS disponibles.")
        return

    # Lista todos los modelos diponibles:
    click.echo("Modelos TTS disponibles:\n")

    for model in available_models:
        aliases = ", ".join(k for k, v in registry._aliases.items() if v is model.model_id)

        if aliases:
            click.echo(f"{model.model_id} ({aliases})")
        else:
            click.echo(f"{model.model_id}")

        # Extras por modelo
        capabilities = [
            ("Soporte SSML", "ssml"),
            ("Múltiples voces", "voices"),
            ("Puntos de contorno", "contour"),
            ("Offline", "offline"),
        ]
        for desc, feature in capabilities:
            status = "✅" if model.supports(feature) else "❌"
            click.echo(f"  {status} {desc}")

        # Ejemplos de uso
        if model.model_id == "speechgen.io":
            click.echo('  Uso: word2speech speak "text" --voice Alvaro --emotion good')
            click.echo("  Setup: word2speech keys set speechgen TU_TOKEN")
            click.echo("  Setup: word2speech keys set speechgen-email TU_EMAIL")
        elif "parler" in model.model_id.lower():
            click.echo(f'  Uso: word2speech speak "text" -m {model.model_id} --voice female --emotion calm')
        elif "mms" in model.model_id.lower():
            click.echo(f'  Uso: word2speech speak "text" -m {model.model_id} --speed 1.2')

        click.echo("")


@cli.group()
def keys():
    """Manejo de las APIs para los modelos TTS."""
    pass


@keys.command("set")
@click.argument("provider")
@click.argument("key")
def keys_set(provider, key):
    """
    Configura la clave API.

    \b
    Para SpeechGen.io, es necesario:
      word2speech keys set speechgen TU_TOKEN
      word2speech keys set speechgen-email TU_EMAIL
    """
    config.set_api_key(provider, key)
    click.echo(f"Establecida clave API para: {provider}")

    if provider == "speechgen":
        click.echo("No olvides configurar también tu email:")
        click.echo("  word2speech keys set speechgen-email TU_EMAIL")
    elif provider == "speechgen-email":
        click.echo("No olvides configurar también tu token:")
        click.echo("  word2speech keys set speechgen TU_TOKEN")


@keys.command("list")
def keys_list():
    """Lista las claves API configuradas."""
    keys_dict = config.list_keys()
    if not keys_dict:
        click.echo("No hay claves API configuradas.")
        return

    click.echo("Claves API configuradas:")
    for provider, masked_key in keys_dict.items():
        click.echo(f"  {provider}: {masked_key}")


@cli.command()
@click.argument("json_file", type=click.Path(exists=True))
@click.option("-m", "--model", default="speechgen.io", help="Modelo TTS a usar (default: speechgen.io)")
@click.option("--voice", help="Voz: male/female o nombre específico (p.ej., 'Alvaro')")
@click.option("--speed", type=float, help="Velocidad del habla: 0.1-2.0 (default: 1.0)")
@click.option("--pitch", help="Tono: low/normal/high or -20 to 20 (default: 0)")
@click.option("--emotion", help="Emoción: calm/energetic/neutral (default: neutral)")
@click.option("--contour", "-c", multiple=True, metavar="tiempo,tono", help="Detalle de entonación. %tiempo duración (0 a 100), %tono entonación (-100 a 100)")
def batch(json_file, model, voice, speed, pitch, emotion, contour):
    """
    Genera audio de palabras/pseudoplabras de un fichero JSON.

    \b
    Formato del fichero:
    {
        <directorio>: [
            [<nombre del fichero>, <texto>]
            ...
        ]
        ...
    }
    """
    import json

    tts_model = registry.get(model)
    if not tts_model:
        click.echo(f"Moldelo '{model}' no encontrado.", err=True)
        click.echo("Usa 'word2speech models' para ver los modelos disponibles.", err=True)
        sys.exit(1)

    options = {}
    if voice:
        options["voice"] = voice
    if speed:
        options["speed"] = speed
    if pitch:
        options["pitch"] = pitch
    if emotion:
        options["emotion"] = emotion
    if contour:
        options["contour"] = contour

    # Leemos el fichero
    with open(json_file, "r", encoding="utf8") as fd:
        data = json.load(fd)

    for category, word_list in data.items():
        # No lanza excepción si el directorio ya existe
        Path(category).mkdir(parents=True, exist_ok=True)

        for filename, word in word_list:
            try:
                log.info(f'Generando audio para: "{word}"')

                audio, file_format, cost, balance = tts_model.generate(word, **options)
                output_file = f"{category}/{filename}.{file_format}"

                with open(output_file, "wb") as f:
                    f.write(audio)

                log.info(f'Audio generado "{output_file}" (coste: {cost}, saldo: {balance})')

            except Exception as e:
                click.echo(f"Error generando audio para: {e}", err=True)


@cli.command()
@click.argument("path", nargs=1, required=True)
@click.option("--verbose", "-v", is_flag=True, help="Verbose información a nivel fichero")
def analyze(path, verbose):
    """
    Analyze predice el índice MOS de los audios.

    \b
    Ejemplos:
      word2speech analyze speechgen/          # Analiza directorio
      word2speech analyze mms/
      word2speech analyze audio.wav           # Analiza archivo de audio
      word2speech analyze speechgen/audio.wav
    """
    from glob import glob

    from .analysis import AudioAnalyzer

    analyze = AudioAnalyzer()
    path_obj = Path(path)

    if not Path(path).exists():
        click.echo(f"El PATH no es existe:{path}", err=True)
        sys.exit(1)

    results = []

    # Si es una archivo
    if path_obj.is_file():
        if not path.lower().endswith(".wav"):
            click.echo(f"El archivo debe ser en formato WAV: {path}", err=True)
            sys.exit(1)

        report = analyze.analyze_file(path)
        results.append((path, report))

    # Si es un directorio
    elif path_obj.is_dir():
        audio_files = glob(f"{path}/*.wav")
        if not audio_files:
            click.echo(f"No hat archivos WAV para evaluar: {path}", err=True)
            sys.exit(1)

        for audio_file in audio_files:
            report = analyze.analyze_file(audio_file)
            results.append((audio_file, report))

    else:
        click.echo(f"El PATH deber ser un archivo o directorio: {path}", err=True)
        sys.exit(1)

    # Media de metrica
    performance = sum(map(lambda row: row[1], results)) / len(results)

    if len(results) == 1:
        click.echo(f"El audio analizado obtiene una puntuación total de: {performance:.4f}")
    else:
        click.echo(f"Los {len(results)} audios analizados obtiene una puntuación total de: {performance:.4f}")

    if verbose:
        click.echo("")
        for file, perf in results:
            click.echo(f"{file}: {perf}")


@cli.command()
def cheat():
    """Guía rápida de opciones comunes."""
    click.echo("Word2Speech Guía Rápida")
    click.echo("═" * 23)

    click.echo("\n Inicio:")
    click.echo('   word2speech speak "text"                    # Audio básico')
    click.echo("   word2speech keys set speechgen YOUR_TOKEN   # Setup API")
    click.echo('   word2speech batch "data.json"               # Audio por lotes')

    click.echo("\n Opciones universales (funcionan en TODOS los modelos):")
    click.echo("    --speed 0.1-2.0      -m model_name       -o filename")

    click.echo("\n Otras options (sólo funcionan con ALGUNOS modelos):")
    click.echo("   --voice female/male/name            # ✅ speechgen, parler  ❌ mms")
    click.echo("   --pitch low/normal/high/-20-20      # ✅ speechgen, parler  ❌ mms")
    click.echo("   --emotion calm/energetic/neutral    # ✅ speechgen, parler  ❌ mms")
    click.echo("   --countour tiempo,tono              # ✅ speechgen          ❌ parler, mms")

    click.echo("\n Descubrir modelos:")
    click.echo("   word2speech models   # Lista todos los modelos")

    click.echo("\n Analizar modelos:")
    click.echo("   word2speech analyze audio.wav   # Analiza un audio")
    click.echo("   word2speech analyze mms/        # Analiza un directorio")


if __name__ == "__main__":
    cli()
