import click
import warnings

from watchman_agent_v2.core.utils.log_manager import LogManager
warnings.filterwarnings("ignore")
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from watchman_agent_v2.core.commands import configure, run, generate_key, active_directory, cron


@click.group()
def cli():
    """Agent CLI for network and local system scanning."""
    pass

try:
    cli.add_command(run.run, name="run")
    cli.add_command(cron.cron, name="cron")
    cli.add_command(configure.configure, name="configure")
    cli.add_command(generate_key.generate_key, name="generate-key")
    cli.add_command(active_directory.ad, name="ad")
except Exception as error:
    LogManager.error(f"Une erreur s'est produite {error} ")

if __name__ == "__main__":
    cli()
