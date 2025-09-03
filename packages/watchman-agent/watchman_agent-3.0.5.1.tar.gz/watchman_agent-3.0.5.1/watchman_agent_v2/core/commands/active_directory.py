import click

from watchman_agent_v2.core.ad.Ad_assets import AdAssets
from watchman_agent_v2.core.ad.Ad_users import AdUsers
from watchman_agent_v2.core.ad.configure import AdConfig
from watchman_agent_v2.core.agents.local_agent import LocalAgent
from watchman_agent_v2.core.agents.network_agent import NetworkAgent
from watchman_agent_v2.core.config.config_manager import ConfigManager

@click.group()
def ad():
    """
    Interagir avec l'active directory
    """
    pass
@ad.command()
def users():
    
    agent = AdUsers()
    agent.run()
    
@ad.command()
def devices():
    
    agent = AdAssets()
    agent.run()
    

@ad.command()
@click.option('-s', '--ldap-server', 
              type=click.STRING,
              help="Adresse du serveur LDAP. Exemple : ldap://192.168.1.10 ou ldaps://192.168.1.10")
@click.option('-p', '--ldap-port',
              help="Port du serveur LDAP (par défaut : 389 pour LDAP, 636 pour LDAPS)")
@click.option('-b', '--ldap-search-base',
              help="Base de recherche LDAP (Base DN), au format : DC=exemple,DC=com")
@click.option('-g', '--ldap-group',
              help="Nom distingué (DN) complet du groupe à rechercher. Exemple : CN=Admins,OU=Groupes,DC=exemple,DC=com")
@click.option('-u', '--username',
              help="Nom d'utilisateur au format DOMAINE\\utilisateur. Exemple : ENTREPRISE\\jdoe")
@click.option('-d', '--domain',
              help="Nom complet du domaine Active Directory. Exemple : entreprise.local")
def configure(ldap_server, ldap_port, ldap_search_base, ldap_group, username,domain):
    password = None
    if username:  # Si username est fourni, demander le password en prompt
        password = click.prompt("Mot de passe", hide_input=True, confirmation_prompt=True)
    
    ad_config = AdConfig()
    ad_config.set_ad_keys(ldap_server, ldap_port, ldap_search_base, ldap_group,domain)
    
    if username and password:
        ad_config.set_ad_user_key(username, password)

    click.echo(" AD information configurée avec succès")
    
    