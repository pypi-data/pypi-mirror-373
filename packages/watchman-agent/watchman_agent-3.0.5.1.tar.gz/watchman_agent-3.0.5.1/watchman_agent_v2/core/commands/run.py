import os

import click

from watchman_agent_v2.core.agents.local_agent import LocalAgent
from watchman_agent_v2.core.agents.network_agent import NetworkAgent
from watchman_agent_v2.core.utils.launch_detached import launch_detached
from watchman_agent_v2.core.config.config_manager import ConfigManager


@click.command()
@click.option('--mode', type=click.Choice(['local', 'network']), help="Mode d'exécution de l'agent", required=False)
@click.option('-d', '--detach', is_flag=True, help="Exécution de l'agent en arrière plan")
def run(mode, detach):
    """
    Commande pour lancer l'agent en mode local ou réseau.
    """
    if detach:
        pid_file = os.path.expanduser("~/.watchman_agent.pid")
        log_file = os.path.expanduser("~/watchman_agent_v2.log")
        # Construire la commande à lancer en arrière-plan.
        # On ne passe pas l'option -d au subprocess pour éviter une récursion.
        cmd = ["watchman-agent", "run"]
        if mode:
            cmd.extend(["--mode", mode])
        else:
            # Si le mode n'est pas passé, on peut le récupérer depuis la config ou utiliser 'local' par défaut.
            cmd.extend(["--mode", "local"])
        # with open(log_file, "w") as f:
        #     subprocess.Popen(
        #         cmd,
        #         stdout=f, stderr=subprocess.STDOUT,
        #         close_fds=True,
        #         start_new_session=True  # Détache complètement le processus
        #     )
        # click.echo(f"✅ Processus lancé en arrière-plan (logs: {log_file})")

        launch_detached(cmd, "agent", log_file)
        return  # On quitte pour ne pas exécuter la suite dans ce processus

    if mode is None:
        configManager = ConfigManager()
        config = configManager.config
        mode = config.get('mode', 'local')
        if mode is None:
            mode = 'local'

    if mode == "local":
        agent = LocalAgent()
    else:
        agent = NetworkAgent()
    agent.run()


if __name__ == '__main__':
    run()
