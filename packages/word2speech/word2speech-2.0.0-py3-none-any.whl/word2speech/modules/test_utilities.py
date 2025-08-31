import pytest

from .utilities import (
    Contour,
    validate_bitrate,
    validate_contour_point,
    validate_emotion,
    validate_format,
    validate_pitch,
    validate_speed,
)


class CustomError(Exception):
    pass


def test_entonacion_succeed():
    contour = Contour(("10, 80", "30,100", "60,-10"))
    assert format(contour, "Palabra") == '<prosody contour="(10%,+80%) (30%,+100%) (60%,-10%)">Palabra</prosody>'


def test_entonacion_fail():
    with pytest.raises(SystemExit) as exec_info:
        Contour([(10, 80), (30, 100), (60, -10), (65, -20), (70, 0), (80, 15)])

    assert exec_info.type is SystemExit
    assert exec_info.value.args[0] == "error: No puede haber más de cinco puntos de entonación"


def test_validate_format_success():
    fmt = validate_format("mp3")
    assert fmt == "mp3"


def test_validate_format_fail():
    with pytest.raises(CustomError) as exec_info:
        fmt = "mp5"
        validate_format(fmt, CustomError)
    assert exec_info.type is CustomError
    assert exec_info.value.args[0] == f"Opción invalida: '{fmt}' (escoge entre 'mp3', 'wav', 'ogg')"


def test_validate_speed_success():
    speed = validate_speed(1.0)
    assert speed == 1.0


def test_validate_speed_fail():
    with pytest.raises(CustomError) as exec_info:
        speed = "uno"
        validate_speed(speed, CustomError)
    assert exec_info.type is CustomError
    assert exec_info.value.args[0] == f"Valor de tipo float inválido: {speed}"
    with pytest.raises(CustomError) as exec_info:
        speed = 5.0
        validate_speed(speed, CustomError)
    assert exec_info.type is CustomError
    assert exec_info.value.args[0] == f"Opción invalida: {speed} (rango entre 0.1 y 2.0)"


def test_validate_pitch_success():
    pitch = validate_pitch(0)
    assert pitch == 0


def test_validate_pitch_fail():
    with pytest.raises(CustomError) as exec_info:
        pitch = "cero"
        validate_pitch(pitch, CustomError)
    assert exec_info.type is CustomError
    assert exec_info.value.args[0] == f"Valor de tipo int inválido: {pitch}"
    with pytest.raises(CustomError) as exec_info:
        pitch = 25
        validate_pitch(pitch, CustomError)
    assert exec_info.type is CustomError
    assert exec_info.value.args[0] == f"Opción invalida: {pitch} (rango entre -20 y 20)"


def test_validate_emotion_success():
    emotion = validate_emotion("good")
    assert emotion == "good"


def test_validate_emotion_fail():
    with pytest.raises(CustomError) as exec_info:
        emotion = "bad"
        validate_emotion(emotion, CustomError)
    assert exec_info.type is CustomError
    assert exec_info.value.args[0] == f"Opción invalida: '{emotion}' (escoge entre 'evil', 'good', 'neutral')"


def test_validate_bitrate_success():
    bitrate = validate_bitrate(48000)
    assert bitrate == 48000


def test_validate_bitrate_fail():
    with pytest.raises(CustomError) as exec_info:
        bitrate = "doscientos"
        validate_bitrate(bitrate, CustomError)
    assert exec_info.type is CustomError
    assert exec_info.value.args[0] == f"Valor de tipo int inválido: {bitrate}"
    with pytest.raises(CustomError) as exec_info:
        bitrate = 200_000
        validate_bitrate(bitrate, CustomError)
    assert exec_info.type is CustomError
    assert exec_info.value.args[0] == f"Opción invalida: {bitrate} (rango entre 8000 y 192000)"


def test_validate_contour_point_success():
    point = validate_contour_point("10,80")
    assert point == (10, 80)


def test_validate_contour_point_fail():
    with pytest.raises(CustomError) as exec_info:
        point = "diez,veinte"
        validate_contour_point(point, CustomError)
    assert exec_info.type is CustomError
    assert exec_info.value.args[0] == f"Valor de tipo int inválido: {point}"
    with pytest.raises(CustomError) as exec_info:
        point = "110,80"
        validate_contour_point(point, CustomError)
    assert exec_info.type is CustomError
    assert exec_info.value.args[0] == "Porcentaje tiempo invalido: 110 (rango entre 0 y 100)"
    with pytest.raises(CustomError) as exec_info:
        point = "10,180"
        validate_contour_point(point, CustomError)
    assert exec_info.type is CustomError
    assert exec_info.value.args[0] == "Porcentaje entonación invalido: 180 (rango entre -100 y 100)"
