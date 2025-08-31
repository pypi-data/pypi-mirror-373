"""
Sistema de gestión de la configuración.
"""

import logging
import os
from pathlib import Path

import yaml

log = logging.getLogger(__name__)


class Config:
    """Clase para manejar la configuración de word2speech."""

    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "config.yml"
        self._config = self._load_config()

    def _get_config_dir(self):
        """Obtiene el directorio de configuración."""
        # Primero buscamos en el directorio de trabajo actual
        local_config = Path.cwd() / ".word2speech"
        if local_config.exists():
            return local_config

        # Usamos la configuración global del usuario
        config_home = os.environ.get("XDG_CONFIG_HOME")
        if config_home:
            return Path(config_home) / "word2speech"
        else:
            return Path.home() / ".word2speech"

    def _load_config(self):
        """Carga la configuración desde un fichero"""
        if not self.config_file.exists():
            return {}

        try:
            with open(self.config_file, "r", encoding="utf8") as fd:
                return yaml.safe_load(fd) or {}
        except Exception as e:
            log.warning(f"Fallo al cargar la configuración: {e}")

    def _save_config(self):
        """Guarda la configuración a un fichero."""
        # Silencia excepción si el directorio ya existe.
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w", encoding="utf8") as fd:
            yaml.safe_dump(self._config, fd, default_flow_style=False)

    def get_model_config(self, model_id):
        """Carga la configuración de un modelo específico."""
        models = self._config.get("models", {})
        return models.get(model_id, {})

    def get_api_key(self, provider):
        """Obtiene la API."""
        keys = self._config.get("keys", {})
        return keys.get(provider)

    def set_api_key(self, provider, key):
        """Configura la clave API."""
        if "keys" not in self._config:
            self._config["keys"] = {}
        self._config["keys"][provider] = key
        self._save_config()

    def list_keys(self):
        """Lista las claves API configuradas"""
        keys = self._config.get("keys", {})
        return {k: (f"{'*' * (len(v) - 4)}{v[-4:]}" if len(v) > 4 else "*" * len(v)) if "email" not in k else v for k, v in keys.items()}


# Instancia global de la configuración
config = Config()
