import os
import click
import base64

from watchman_agent_v2.core.config.config_manager import ConfigManager


@click.command()
def generate_key():
    """
    Génère une clé de cryptographie AES-256 et l'enregistre dans le fichier .env.
    """
    config_manager=ConfigManager()
    config_manager.generate_key()
    


if __name__ == "__main__":
    generate_key()
