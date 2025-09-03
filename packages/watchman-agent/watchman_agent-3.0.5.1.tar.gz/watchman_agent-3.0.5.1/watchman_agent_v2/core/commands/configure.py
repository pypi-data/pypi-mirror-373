import click
import yaml

from watchman_agent_v2.core.config.config_manager import ConfigManager
from watchman_agent_v2.core.config.settings.network_config import NetworkConfig, extract_ips_from_file, is_valid_ip
from watchman_agent_v2.core.config.settings.api_config import APIConfig
from watchman_agent_v2.core.config.settings.protocols_config import ProtocolsConfig
from watchman_agent_v2.core.config.settings.mode_config import ModeConfig


@click.group()
def configure():
    """Commandes pour configurer l'agent."""
    pass


# network @click.command() @click.option('--mode', type=click.Choice(['cidr', 'ip_list', 'plage', 'ldap']),
# help="Mode de géneration d'adresse ip") @click.option('--cidr', type=int, help="CIDR à utiliser en mode cidr")
# @click.option('--start-address', type=str, help="L'adresse de debut à utiliser en cas de mode plage")
# @click.option('--end-address', type=str, help="CIDR à utiliser") @click.option('--network-address', type=str,
# help="Addresse réseau à utiliser") @click.option('--inclusions', type=str, help="Adresses IP à inclure (séparées
# par des virgules) en mode ip list uniquement") @click.option('--exclusions', type=str, help="Adresses IP à exclure
# (séparées par des virgules) à utiliser dans tous les modes ") def network(mode, cidr, start_address, end_address,
# network_address, inclusions, exclusions): """Configure le réseau."""
#
#     config = NetworkConfig()
#     config.set_network(mode, cidr, start_address, end_address, network_address, inclusions, exclusions)
#     click.echo("Configuration réseau mise à jour.")

# @click.command()
# @click.option('--mode', type=click.Choice(['cidr', 'ip_list', 'plage', 'ldap']), help="Mode de génération d'adresse IP")
# @click.option('--cidr', type=int, help="CIDR à utiliser en mode cidr")
# @click.option('--start-address', type=str, help="L'adresse de début à utiliser en mode plage")
# @click.option('--end-address', type=str, help="L'adresse de fin à utiliser en mode plage")
# @click.option('--network-address', type=str, help="Adresse réseau à utiliser")
# @click.option('--inclusions', type=str, help="Adresses IP à inclure (séparées par des virgules) en mode ip_list "
#                                              "uniquement")
# @click.option('--inclusions-file', type=click.Path(exists=True), help="Fichier .txt ou .csv contenant les IP à inclure")
# @click.option('--exclusions', type=str, help="Adresses IP à exclure (séparées par des virgules)")
# def network(mode, cidr, start_address, end_address, network_address, inclusions, inclusions_file, exclusions):
#     """Configure le réseau."""
#     all_inclusions = []
#
#     # 1. Lire les IP depuis le fichier si fourni
#     if inclusions_file:
#         try:
#             with open(inclusions_file, 'r', encoding='utf-8') as f:
#                 for line in f:
#                     line = line.strip()
#                     if not line or line.startswith("#"):
#                         continue  # Ignore les lignes vides ou les commentaires
#                     if ',' in line:
#                         all_inclusions.extend([ip.strip() for ip in line.split(',') if ip.strip()])
#                     else:
#                         all_inclusions.append(line)
#         except Exception as e:
#             click.echo(f"❌ Erreur lors de la lecture du fichier {inclusions_file}: {e}")
#             return
#
#     # 2. Ajouter les IP depuis l'option en ligne de commande
#     if inclusions:
#         all_inclusions.extend([ip.strip() for ip in inclusions.split(',') if ip.strip()])
#
#     # 3. Joindre la liste finale en chaîne (séparateur virgule)
#     inclusions_str = ",".join(all_inclusions) if all_inclusions else None
#
#     config = NetworkConfig()
#     config.set_network(mode, cidr, start_address, end_address, network_address, inclusions_str, exclusions)
#     click.echo("Configuration réseau mise à jour.")


@click.command()
@click.option('--mode', type=click.Choice(['cidr', 'ip_list', 'plage', 'ldap']), help="Mode de génération d'adresse IP")
@click.option('--cidr', type=int, help="CIDR à utiliser en mode cidr")
@click.option('--start-address', type=str, help="L'adresse de début à utiliser en mode plage")
@click.option('--end-address', type=str, help="L'adresse de fin à utiliser en mode plage")
@click.option('--network-address', type=str, help="Adresse réseau à utiliser")
@click.option('--inclusions', type=str,
              help="Adresses IP à inclure (séparées par des virgules) en mode ip_list uniquement")
@click.option('--inclusions-file', type=click.Path(exists=True), help="Fichier .txt ou .csv contenant les IP à inclure")
@click.option('--ip-column', type=str, help="Nom de la colonne contenant les IP dans le fichier CSV")
@click.option('--exclusions', type=str, help="Adresses IP à exclure (séparées par des virgules)")
def network(mode, cidr, start_address, end_address, network_address, inclusions, inclusions_file, ip_column,
            exclusions):
    """Configure le réseau."""
    all_inclusions = []

    # 1. Lire les IP depuis le fichier si fourni
    if inclusions_file:
        try:
            ips_from_file = extract_ips_from_file(inclusions_file, ip_column)
            all_inclusions.extend(ips_from_file)
        except Exception as e:
            click.echo(f"{e}")
            return

    # 2. Ajouter les IP depuis l'option en ligne de commande
    if inclusions:
        all_inclusions.extend([ip.strip() for ip in inclusions.split(',') if ip.strip() and is_valid_ip(ip.strip())])

    # 3. Supprimer doublons éventuels
    all_inclusions = list(dict.fromkeys(all_inclusions))

    config = NetworkConfig()
    config.set_network(mode, cidr, start_address, end_address, network_address, all_inclusions, exclusions)
    click.echo("✅ Configuration réseau mise à jour.")


# api
@click.command()
@click.option('--client-id', type=str, required=True, help="Client ID de l'API")
@click.option('--client-secret', type=str, required=True, help="Client Secret de l'API")
def api_auth(client_id, client_secret):
    """Configure les clés API."""
    config = APIConfig()
    config.set_api_keys(client_id, client_secret)
    click.echo("Clés API mises à jour.")


# mode
@configure.command()
@click.argument('mode', type=click.Choice(['local', 'network']), required=False)
def mode(mode):
    """Configure ou affiche le mode actuel."""
    config = ModeConfig()

    if mode:
        config.set_mode(mode)
        click.echo(f"Mode modifié avec succès : {mode}")
    else:
        click.echo(f"Mode actuel : {config.get_mode()}")


# display
@click.command()
def show():
    """Affiche la configuration complète de l'utilisateur."""
    config_manager = ConfigManager()
    config = config_manager.config

    # Déchiffrer la clé API pour affichage
    if "api" in config and "client_secret" in config["api"]:
        api_config = APIConfig()
        config["api"]["client_secret"] = api_config.get_api_keys()["client_secret"]

    click.echo(yaml.dump(config, default_flow_style=False, allow_unicode=True))


# export
# @click.command()
# @click.option('--activate', type=click.BOOL, help="Activé le mode export", )
# @click.option('--path', type=str, help="Le dossier dans lequel l'export sera sauvegardé")
# @click.option('--file-name', type=str, help="Nom du fichier")
# def export(activate, path, file_name):
#     """Configure l'export"""
#     config = ExportConfig()
#     config.set_export(activate, path, file_name)
#     click.echo("Configuration export mise à jour.")


# # log
# @click.command()
# @click.option('--mode', type=click.Choice(['DEBUG', 'INFO', 'ERROR']), help="Mode 'DEBUG', 'INFO','ERROR' ")
# def log(mode):
#     """Configure le mode de log."""
#     config = LogConfig()
#     config.set_log(mode)
#     click.echo("Configuration de log mise à jour.")


# Protocoles 
# protocoles 
@configure.group()
def protocols():
    """Configure protocoles"""
    pass


def common_protocol_options(func):
    @click.option('--client-ip',
                  type=click.STRING,
                  help="Adresse IP spécifique pour l'override")
    @click.option('--enabled/--disabled',
                  default=True,
                  help="Activer/désactiver le protocole")
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


#specifics commandes configs

# SNMP
@protocols.command()
@click.option('--client-ip',
              type=click.STRING,
              help="Adresse IP spécifique pour l'override")
@click.option('--enabled/--disabled',
              default=True,
              help="Activer/désactiver le protocole")
@click.option('--community', help="Communauté SNMP")
@click.option('--port',
              type=int,
              default=161,
              help="Port SNMP")
@click.option('--version',
              type=click.Choice(['1', '2c', '3']),
              default='2c',
              help="Version du protocole")
def snmp(client_ip, enabled, community, port, version):
    """Configure SNMP dans un contexte réseau"""
    snmp_config = {}
    if community:
        snmp_config['community'] = community
    if port:
        snmp_config['port'] = port
    if version:
        snmp_config['version'] = version

    if enabled is not None:
        snmp_config['enabled'] = enabled

    ProtocolsConfig().set_protocols(client_ip=client_ip, protocol='snmp', proto_config=snmp_config)
    click.echo(f"SNMP configuré pour le réseau ")


# HTTP
@protocols.command()
@click.option('--client-ip',
              type=click.STRING,
              help="Adresse IP spécifique pour l'override")
@click.option('--enabled/--disabled',
              default=True,
              help="Activer/désactiver le protocole")
@click.option('--api-key', help="Clé de l'api du serveur")
@click.option('--port',
              type=int,
              help="Port HTTP du serveur http watchman")
def http(client_ip, enabled, api_key, port):
    """Configure HTTP dans un contexte réseau"""
    http_config = {}
    if api_key:
        http_config['api_key'] = api_key
    if port:
        http_config['port'] = port
    if enabled is not None:
        http_config['enabled'] = enabled

    ProtocolsConfig().set_protocols(client_ip=client_ip, protocol='http', proto_config=http_config)
    click.echo(f"HTTP configuré pour le réseau ")


# WMI
@protocols.command()
@click.option('--client-ip',
              type=click.STRING,
              help="Adresse IP spécifique pour l'override")
@click.option('--enabled/--disabled',
              default=True,
              help="Activer/désactiver le protocole")
@click.option('--domain',
              help="Domaine Windows")
@click.option('--username',
              prompt=True,
              help="Utilisateur du domaine")
@click.option('--password', prompt=True, help="Mot de passe")
def wmi(client_ip, enabled, domain, username, password):
    """Configure l'accès WMI pour l'inventaire Windows"""
    config = ConfigManager()
    wmi_config = {"domain": domain, "username": config.encrypt(username), "password": config.encrypt(password),
                  "enabled": enabled}
    ProtocolsConfig().set_protocols(client_ip=client_ip, protocol='wmi', proto_config=wmi_config)
    click.echo(f"Accès WMI {'global' if not client_ip else 'pour ' + client_ip} configuré")


# SSH
@protocols.command()
@click.option('--client-ip',
              type=click.STRING,
              help="Adresse IP spécifique pour l'override")
@click.option('--enabled/--disabled',
              default=True,
              help="Activer/désactiver le protocole")
@click.option('--username',
              help="Nom d'utilisateur")
@click.option('--password', help="Mot de passe du ssh")
@click.option('--key-path', help="Path de la clé ssh en cas d'authentification par ")
@click.option('--passphrase', help="Passphrase au cas où votre clé est protegé par une passphrase")
@click.option('--port',
              help="Port à utiliser pour SSH")
def ssh(client_ip, enabled, username, password, key_path, passphrase, port):
    """Configure l'accès SSH pour l'inventaire Windows"""
    config = ConfigManager()
    ssh_config = {"port": port, "username": config.encrypt(username) if username is not None else None,
                  "password": config.encrypt(password) if password is not None else None,
                  "key_path": config.encrypt(key_path) if key_path is not None else None,
                  "passphrase": config.encrypt(passphrase) if passphrase is not None else None, "enabled": enabled}
    ProtocolsConfig().set_protocols(client_ip=client_ip, protocol='ssh', proto_config=ssh_config)
    click.echo(f"Accès SSH {'global' if not client_ip else 'pour ' + client_ip} configuré")


# Ajouter les commandes au groupe configure
configure.add_command(network)
configure.add_command(api_auth)
configure.add_command(show)

if __name__ == '__main__':
    configure()
