import os
import subprocess
import platform
import click


def launch_detached(cmd, task_name, log_file_path):
    """
    Lance une commande en arrière-plan, enregistre le PID et redirige les logs.
    Chaque tâche est identifiée par un nom (task_name), avec son propre fichier PID.
    """

    pid_dir = "watchman_agent_v2/pids/"
    directory = os.path.dirname(pid_dir)
    os.makedirs(directory, exist_ok=True)
    pid_file_path = os.path.join(pid_dir, f"{task_name}.pid")

    def save_pid(pid):
        with open(pid_file_path, "w") as f:
            f.write(str(pid))

    def is_process_running(pid):
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return True

    def check_existing_pid():
        if os.path.exists(pid_file_path):
            try:
                with open(pid_file_path, "r") as f:
                    pid = int(f.read().strip())
                if is_process_running(pid):
                    click.echo(f"⚠️ Une tâche '{task_name}' est déjà en cours (PID {pid})")
                    return True
            except Exception:
                pass
        return False

    if check_existing_pid():
        click.confirm("Souhaitez-vous écraser l'ancien processus ?", abort=True)

    with open(log_file_path, "w") as f:
        kwargs = {
            "stdout": f,
            "stderr": subprocess.STDOUT,
            "close_fds": True
        }
        if platform.system() != "Windows":
            kwargs["start_new_session"] = True

        p = subprocess.Popen(cmd, **kwargs)
        save_pid(p.pid)
        click.echo(f"✅ Processus '{task_name}' lancé (PID {p.pid}, logs: {log_file_path})")



