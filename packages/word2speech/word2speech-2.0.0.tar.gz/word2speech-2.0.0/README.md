# word2speech

Genera audios a partir de palabras (reales o falsas), para el tratamiento de pacientes con dislexia u otras dificultades específicas de aprendizaje.

Un proyecto de Alejandro Varela de Cora.

## Instalación

Se necesita `python>=3.12`, se recomienda utiliza `pipx` para la instalación.

```shell
$ pipx install word2speech
```

## Configuración

Para usar word2speech necesitas configurar:
- **token**: Token de API de speechgen.io
- **email**: Email registrado en speechgen.io
- **voice**: Voz a utilizar (ej: Alvaro)

### Archivo de configuración
Crea `~/.word2speech/config.yml`:
```yaml
token: tu_token_aqui
email: tu_email@domain.com
voice: Alvaro
```

## Inicio rápido

Si no proporcionamos un fichero de configuración mediante el flag `--config`, la aplicación busca automáticamente primero en la configuración local del proyecto `./.word2speech/config.yml` y después en la configuración global del usuario `~/.word2speech/config.yml`.

Si no encuentra ningún archivo, los parámetros obligatorios (token, email, voice) deben proporcionarse por línea de comandos.

```shell
$ word2speech palabra
[17:19:25]: Generando el audio de la palabra "palabra"
[17:19:26]: Audio generado "out.mp3" (coste: 7, saldo: 61705)
```

### Procesamiento por lotes con JSON

Crea un archivo JSON con el siguiente formato:
```json
{
  "palabras": ["abrazo", "bebida", "órganos"],
  "nopalabras": ["babados", "bacela", "plátaco"]
}
```

Luego procésalo:

```shell
$ word2speech data-reduce.json
[17:19:40]: Generando el audio de la palabra "abrazo"
[17:19:40]: Audio generado "palabras/abrazo.mp3" (coste: 0, saldo: 61705)
[17:19:40]: Generando el audio de la palabra "bebida"
[17:19:40]: Audio generado "palabras/bebida.mp3" (coste: 0, saldo: 61705)
[17:19:41]: Generando el audio de la palabra "órganos"
[17:19:41]: Audio generado "palabras/organos.mp3" (coste: 0, saldo: 61705)
[17:19:41]: Generando el audio de la palabra "babados"
[17:19:41]: Audio generado "nopalabras/babados.mp3" (coste: 0, saldo: 61705)
[17:19:41]: Generando el audio de la palabra "bacela"
[17:19:42]: Audio generado "nopalabras/bacela.mp3" (coste: 0, saldo: 61705)
[17:19:42]: Generando el audio de la palabra "plátaco"
[17:19:42]: Audio generado "nopalabras/plataco.mp3" (coste: 0, saldo: 61705)
```

## Uso de subcomandos

`word2speech` tiene disponibles 2 subcomandos, `deletrear` y `prosodia`:

- `deletrear`: Genera el audio de una palabra sílaba por sílaba
  ```shell
  $ word2speech deletrear albaricoque
  [17:29:09]: Generando audio deletreado por sílabas de la palabra "albaricoque"
  [17:29:09]: Texto deletreado: al <break time="250ms"/> ba <break time="250ms"/> ri <break time="250ms"/> co <break time="250ms"/> que
  [17:29:13]: Audio deletreado generado "out_deletreo.mp3" (coste: 95, saldo: 61610)

  # El flag --include-word añade la palabra deletreada al final de audio
  $ word2speech deletrear albaricoque --include-word
  [17:30:51]: Generando audio deletreado por sílabas de la palabra "albaricoque"
  [17:30:51]: Texto deletreado: al <break time="250ms"/> ba <break time="250ms"/> ri <break time="250ms"/> co <break time="250ms"/> que <break time="1s"/> albaricoque
  [17:30:53]: Audio deletreado generado "out_deletreo.mp3" (coste: 124, saldo: 61486)
  ```
- `prosodia`: Genera una versión de la palabra con mayor énfasis en la prosodia de la misma mediante el uso de [SSML](https://www.w3.org/TR/speech-synthesis/) para enriquecer la palabra y la trancripción fonética IPA.
  ```shell
  $ word2speech prosodia albaricoque
  [17:35:20]: IPA generado con epitran para 'albaricoque': albaɾikoke
  [17:35:20]: Generando audio con prosodia mejorada de la palabra "albaricoque"
  [17:35:20]: SSML generado: <prosody rate="medium" pitch="medium" volume="medium"><phoneme alphabet="ipa" ph="albaɾikoke">albaricoque</phoneme></prosody>
  [17:35:21]: Audio con prosodia generado "out_prosodia.mp3" (coste: 125, saldo: 61361)
  ```

## Limitación windows

En Windows debido a la codificación de la consola por defecto pueden surgir problemas a la hora de ejecutar el subcomando `prosodia`, la solución pasa por forzar la codificación `UTF-8`

```cmd
> set PYTHONUTF8=1
```

Podemos establecer la codificación `UTF-8` de forma permanente con:

```cmd
> setx PYTHONUTF8 1
```

> **Nota**: Después de ejecutar `setx`, es necesario reiniciar la terminal (o abrir una nueva) para que el cambio tome efecto.


## Enlaces de interés:

- [Proyecto dislexia](https://github.com/adecora/proyecto-dislexia)
- [speechgen API](https://speechgen.io/es/node/api/)
