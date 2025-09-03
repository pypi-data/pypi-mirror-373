import logging
import os
import platform
import subprocess
import sys
import click
import re
from datetime import datetime



@click.group()
def cron():
    """Commandes pour gérer les tâches planifiées."""
    pass

def get_executable_name():
    """Retourne le chemin absolu de l'exécutable"""
    return os.path.abspath(sys.argv[0])

def get_agent_log_path():
    """Retourne le chemin absolu des logs de l'application"""
    log_path = os.path.abspath("watchman_agent_v2/logs/logs.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    return log_path

def register_system_cron(hour, minute, day, month, command):
    """Enregistre la tâche dans le système de planification"""
    system = platform.system()
    job_name = "WatchmanAgent"
    agent_log = get_agent_log_path()
    
    # Validation des paramètres
    if not re.match(r'^\d{1,2}$', hour) or int(hour) > 23:
        raise ValueError("Heure invalide (0-23)")
    if not re.match(r'^\d{1,2}$', minute) or int(minute) > 59:
        raise ValueError("Minute invalide (0-59)")
    
    try:
        if system in ['Linux', 'Darwin']:
            # Formatage de l'expression cron avec redirection des logs
            cron_expr = f"{minute} {hour} {day} {month} * {command} >> {agent_log} 2>&1"
            
            # Ajout à la crontab
            subprocess.run(
                f'(crontab -l | grep -v "# {job_name}"; echo "{cron_expr} # {job_name}") | crontab -',
                shell=True,
                check=True
            )
            return f"Tâche cron configurée: {cron_expr}"

        elif system == 'Windows':
            time_str = f"{int(hour):02d}:{int(minute):02d}"
            
            # Commande avec redirection pour Windows
            full_cmd = f'cmd /c "{command} >> \"{agent_log}\" 2>&1"'
            
            # Suppression de l'ancienne tâche
            subprocess.run(
                f'schtasks /Delete /TN "{job_name}" /F',
                shell=True,
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL
            )
            
            # Configurer selon le type de planification
            if day == '*' and month == '*':
                cmd = f'schtasks /Create /TN "{job_name}" /TR "{full_cmd}" /SC DAILY /ST {time_str} /F'
            elif day != '*' and month == '*':
                cmd = f'schtasks /Create /TN "{job_name}" /TR "{full_cmd}" /SC MONTHLY /D {day} /ST {time_str} /F'
            else:
                months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
                month_name = months[int(month)-1] if month != '*' else '*'
                cmd = f'schtasks /Create /TN "{job_name}" /TR "{full_cmd}" /SC ONCE /SD 01/{month}/{datetime.now().year} /ST {time_str} /F'
            
            subprocess.run(cmd, shell=True, check=True)
            return f"Tâche Windows configurée: {cmd}"

        else:
            raise NotImplementedError("Système non supporté")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Erreur de configuration: {e}")

def setup_cron_logging():
    """Configure la journalisation pour les opérations cron"""
    log_path = os.path.abspath("watchman_agent_v2/logs/cron.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8"
    )
    return log_path


def unregister_system_cron():
    """Supprime la tâche du système"""
    system = platform.system()
    job_name = "WatchmanAgent"
    
    try:
        if system in ['Linux', 'Darwin']:
            subprocess.run(
                f'(crontab -l | grep -v "# {job_name}") | crontab -',
                shell=True,
                check=True
            )
            return "Tâche cron supprimée"
            
        elif system == 'Windows':
            subprocess.run(
                f'schtasks /Delete /TN "{job_name}" /F',
                shell=True,
                check=True
            )
            return "Tâche Windows supprimée"
            
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Erreur de suppression: {e}")

def check_system_cron():
    """Vérifie si la tâche existe"""
    system = platform.system()
    job_name = "WatchmanAgent"
    
    try:
        if system in ['Linux', 'Darwin']:
            result = subprocess.run(
                'crontab -l',
                shell=True,
                capture_output=True,
                text=True
            )
            return f"# {job_name}" in result.stdout
            
        elif system == 'Windows':
            result = subprocess.run(
                f'schtasks /Query /TN "{job_name}"',
                shell=True,
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL
            )
            return result.returncode == 0
            
    except Exception:
        return False


@click.command()
@click.option('--hour', type=str, required=True, help="Heure (0-23)")
@click.option('--minute', type=str, required=True, help="Minute (0-59)")
@click.option('--day', type=str, default="*", help="Jour du mois (1-31), '*' par défaut")
@click.option('--month', type=str, default="*", help="Mois (1-12), '*' par défaut")
@click.option('--mode', default="local", type=click.Choice(['local', 'network']), help="Mode d'exécution")
def start(hour, minute, day, month, mode):
    """Configure la tâche planifiée dans le système"""
    setup_cron_logging()
    
    try:
        executable = get_executable_name()
        
        # Commande de base sans redirection
        base_cmd = f'{executable} run --mode {mode}' if mode != "local" else f'{executable} run'
        
        result = register_system_cron(hour, minute, day, month, base_cmd)
        logging.info(result)
        click.echo(result)
        
    except Exception as e:
        logging.error(f"❌ Erreur: {str(e)}")
        click.echo(f"Erreur: {str(e)}", err=True)


@click.command()
def status():
    """Affiche l'état de la tâche planifiée"""
    try:
        if check_system_cron():
            click.echo("En cours")
        else:
            click.echo("Arrêté")
    except Exception as e:
        click.echo(f"Erreur: {str(e)}", err=True)

@click.command()
@click.option("--lines", default=30, help="Nombre de lignes à afficher")
def logs(lines):
    """Affiche les logs de configuration"""
    log_file = "watchman_agent_v2/logs/logs.log"
    
    if not os.path.exists(log_file):
        click.echo("Aucun log disponible")
        return

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read().splitlines()[-lines:]
            click.echo("\n".join(content))
    except Exception as e:
        click.echo(f"Erreur de lecture: {str(e)}", err=True)

@click.command()
def stop():
    """Supprime la tâche planifiée"""
    log_file = setup_cron_logging()
    
    try:
        result = unregister_system_cron()
        logging.info(result)
        click.echo(result)
    except Exception as e:
        logging.error(f"❌ Erreur: {str(e)}")
        click.echo(f"Erreur: {str(e)}", err=True)

cron.add_command(start)
cron.add_command(status)
cron.add_command(logs)
cron.add_command(stop)

if __name__ == '__main__':
    cron()