import requests
from requests.exceptions import HTTPError


from .utilities import Contour


def send_request(url, data):
    """Devuelve las respuesta en formato JSON de una petición POST."""
    response = requests.post(url, data=data)
    return response.json()


class Word2Speech:
    """
    Clase que se encarga de hacer la petición a la API y obtener el audio
    resultante en formato binario.
    """

    _url = "https://speechgen.io/index.php?r=api/text"

    def __init__(self, config):
        self.config = config

    def convert(self, word):
        if "contour" in self.config:
            word = format(Contour(self.config["contour"]), word)
            del self.config["contour"]
        self.config.update({"text": word})
        response = send_request(self._url, self.config)
        if response["status"] == 1:
            if "file" in response and "format" in response:
                file_url = response["file"]
                file_format = response["format"]
                audio = requests.get(file_url).content
                return (audio, file_format, response["cost"], response["balans"])
            else:
                raise HTTPError(f"404 Not Found: {response['error']}")
        else:
            if "login" in response["error"]:
                raise HTTPError(f"401 Unauthorized: {response['error']}")
            else:
                raise HTTPError(f"400 Bad Request: {response['error']}")
