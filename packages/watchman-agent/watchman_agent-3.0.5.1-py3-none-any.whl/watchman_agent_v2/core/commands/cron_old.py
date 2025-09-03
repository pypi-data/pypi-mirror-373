import logging
import os
import platform
import signal
import subprocess
import sys
import time
import re
from datetime import datetime, timedelta

import click
import psutil
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from watchman_agent_v2.core.utils.launch_detached import launch_detached


@click.group()
def cron():
    """Commandes pour gérer les tâches en arrière plan."""
    pass


# start
def get_executable_name():
    """Retourne le nom de l'exécutable utilisé (agent.exe ou watchman-agent)"""
    return os.path.basename(sys.argv[0])


@click.command()
@click.option('--hour', type=str, required=True, help="L'heure à laquelle démarrer le serveur (0-23).")
@click.option('--minute', type=str, required=True, help="La minute à laquelle démarrer le serveur (0-59).")
@click.option('--day', type=str, required=False, default="*", help="Jour du mois (1-31), '*' pour chaque jour.")
@click.option('--month', type=str, required=False, default="*", help="Mois (1-12), '*' pour chaque mois.")
@click.option('-d', '--detach', is_flag=True, help="Exécution de l'agent en arrière-plan.")
@click.option('--mode',default="local", type=click.Choice(['local', 'network']), help="Mode d'exécution de l'agent", required=False)
def start(hour, minute, day, month, detach,mode):
    """Configure la planification des tâches."""

    # Configuration des logs
    file_path = "watchman_agent_v2/logs/logs.log"
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)
    log_file = file_path
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8"
    )

    executable = get_executable_name()

    def run_agent_on_schedule():
        logging.info(f"🔄 TACHE_EXECUTEE >> {hour}:{minute} (Jour: {day}, Mois: {month})")
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                subprocess.Popen(
                    [executable, "run", "--mode", mode] if mode else [executable, "run"],
                    stdout=f, stderr=subprocess.STDOUT,
                    close_fds=True,
                    start_new_session=True
                )
            logging.info(f"Agent démarré avec succès (logs: {log_file})")
        except Exception as e:
            logging.error(f"❌ Erreur lors du démarrage de l'agent: {e}")

    scheduler = BackgroundScheduler()
    trigger = CronTrigger(hour=hour, minute=minute, day=day, month=month)
    scheduler.add_job(run_agent_on_schedule, trigger=trigger, name="run_agent_on_schedule")

    if detach:
        logging.info("🛠 Démarrage du planificateur en arrière-plan...")

        cmd = [
            executable, "cron", "start",
            "--hour", hour,
            "--minute", minute,
            "--mode", mode
        ]
        if day != "*":
            cmd.extend(["--day", day])
        if month != "*":
            cmd.extend(["--month", month])

        logging.info(f"Commande exécutée : {' '.join(cmd)}")
        print(f"Commande exécutée : {' '.join(cmd)}")

        try:
            launch_detached(cmd, "cron", log_file)
        except Exception as e:
            logging.error(f"❌ Erreur lors de l'exécution de la commande cron: {e}")
        return

    logging.info("🟢 Planificateur en cours d'exécution...")
    scheduler.start()
    logging.info(f"Tâche planifiée pour {hour}:{minute} (Jour: {day}, Mois: {month})")

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logging.info("🛑 Planificateur arrêté.")

    click.echo(f"Tâche cron configurée")


# status
@click.command()
def status():
    """Affiche si le planificateur cron est en cours ou non."""
    pid_file = "watchman_agent_v2/pids/cron.pid"

    # click.echo("État du Planificateur :\n")

    if not os.path.exists(pid_file):
        click.echo("Arrêté.")
        return

    try:
        with open(pid_file, "r") as f:
            pid = int(f.read().strip())

        if psutil.pid_exists(pid):
            click.echo(f"En cours")
        else:
            click.echo("Arrêté")
    except Exception:
        click.echo("Impossible de lire le fichier PID.")


@click.command()
@click.option("--lines", default=30, help="Nombre de lignes à afficher depuis la fin du fichier de log.")
def logs(lines):
    """Affiche les derniers logs du planificateur."""
    log_file = "watchman_agent_v2/logs/logs.log"

    click.echo("Derniers logs :\n")

    if not os.path.exists(log_file):
        click.echo("Aucun fichier de log trouvé.")
        return

    try:
        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
            all_lines = f.readlines()
            for line in all_lines[-lines:]:
                click.echo(line.rstrip())
    except Exception as e:
        click.echo(f"Erreur lors de la lecture des logs : {e}")


# stop
@click.command()
def stop():
    """
    Arrête automatiquement toutes les tâches en arrière-plan (agent, planificateurs, etc.).
    Nettoie également les fichiers PID orphelins.
    """
    pid_dir = "watchman_agent_v2/pids/"

    if not os.path.isdir(pid_dir):
        click.echo("Aucun processus trouvé.")
        return

    pid_files = [f for f in os.listdir(pid_dir) if f.endswith(".pid")]
    running_tasks = {}

    for pid_file in pid_files:
        path = os.path.join(pid_dir, pid_file)
        try:
            with open(path, "r") as f:
                pid = int(f.read().strip())
            if psutil.pid_exists(pid):
                task_name = pid_file.replace(".pid", "")
                running_tasks[task_name] = (pid, path)
            else:
                os.remove(path)
                click.echo(f"Fichier PID orphelin supprimé : {pid_file}")
        except Exception as e:
            click.echo(f"Erreur lors du traitement de {pid_file} : {e}")

    if not running_tasks:
        click.echo("Aucun processus actif trouvé.")
        return

    for name, (pid, path) in running_tasks.items():
        try:
            os.kill(pid, signal.SIGTERM)
            os.remove(path)
            click.echo(f"Tâche '{name}' arrêtée (PID {pid})")
        except Exception as e:
            click.echo(f"Erreur lors de l'arrêt de '{name}' : {e}")


cron.add_command(start)
cron.add_command(status)
cron.add_command(logs)
cron.add_command(stop)

if __name__ == '__main__':
    cron()
