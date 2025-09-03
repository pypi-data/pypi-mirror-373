import click
import os
from datetime import datetime
from watchman_agent_v2.core.config.config_manager import get_base_dir
class LogManager:
    """
    Classe de gestion des logs qui utilise click pour afficher des messages
    d'information, de succès et d'erreur avec un formatage spécifique,
    et qui les enregistre dans des fichiers datés.
    """
    
    # Dossier par défaut pour les logs
    LOGS_DIR = "/logs"
    
    @staticmethod
    def _write_log(level: str, message: str) -> None:
        """
        Écrit le message dans un fichier de log avec horodatage.
        Crée le dossier de logs si nécessaire.
        
        :param level: Niveau de log (INFO, WARNING, etc.)
        :param message: Message à journaliser
        """
        try:
            LOGS_DIR = get_base_dir() + "/logs"
            # Créer le dossier de logs s'il n'existe pas
            os.makedirs(LogManager.LOGS_DIR, exist_ok=True)
            
            # Générer le nom de fichier basé sur la date actuelle
            date_str = datetime.now().strftime("%Y-%m-%d")
            log_file = os.path.join(LogManager.LOGS_DIR, f"{date_str}.log")
            
            # Formater l'entrée de log avec date/heure
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [{level}] {message}\n"
            
            # Écrire dans le fichier
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
                
        except Exception as e:
            click.echo(click.style(
                f"ERREUR LOG: Impossible d'écrire dans les logs ({str(e)})", 
                fg='red', 
                bold=True
            ))

    @staticmethod
    def info(message: str) -> None:
        LogManager._write_log("INFO", message)
        click.echo(click.style(f"WATCHMAN-INFO: {message}", fg='blue'))
   
    @staticmethod
    def warning(message: str) -> None:
        LogManager._write_log("WARNING", message)
        click.echo(click.style(f"WATCHMAN-WARNING: {message}", fg='yellow'))

    @staticmethod
    def success(message: str) -> None:
        LogManager._write_log("SUCCESS", message)
        click.echo(click.style(f"WATCHMAN-SUCCESS: {message}", fg='green'))

    @staticmethod
    def error(message: str) -> None:
        LogManager._write_log("ERROR", message)
        click.echo(click.style(f"WATCHMAN-ERROR: {message}", fg='red', bold=True))