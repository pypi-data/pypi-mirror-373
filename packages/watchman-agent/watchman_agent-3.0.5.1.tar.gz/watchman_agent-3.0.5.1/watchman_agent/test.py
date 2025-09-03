import asyncio
import binascii
import configparser
import ipaddress
import json
import logging
import os
import threading
import csv
import platform as pt
import time
import subprocess
from pprint import pprint

import platformdirs
import yaml
import getmac
import platform
import socket
from pathlib import Path
import click
import keyring
import requests
from environs import Env
from keyring.errors import NoKeyringError
from pysnmp.hlapi import *
from sqlitedict import SqliteDict
from semver.version import Version as sem_version
from packaging import version as pkg_version
# import pandas as pd
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_info_linux(package_string):
    # Original regular expression pattern
    original_pattern = r'^(.*?)_([^_]+)_([^\s]+)$'

    # Additional pattern to handle strings like "whiptail-0.52.20-1ubuntu1"
    additional_pattern = r'^([^-\s]+)-([\d.]+)-(\S+)$'

    # Pattern for strings like "ncurses-6.1-10.20180224.el8"
    new_pattern = r'^([^-\s]+)-([\d.]+)-([\d.]+)\.([^\s]+)$'

    # Pattern for strings like "ncurses-6.1-10.20180224.el8"
    second_pattern = r'(.*)-(.*)-(.*).(.*)'
    third_pattern = r'\d+(\.\d+)*'

    # Try the original pattern first
    match = re.match(original_pattern, package_string)

    if match:
        name = match.group(1)
        version = match.group(2)
        architecture = match.group(3)
        return {"name": name, "version": version, "arch": architecture}
    else:
        # If the original pattern didn't match, try the additional pattern
        match = re.match(additional_pattern, package_string)

        if match:
            name = match.group(1)
            version = match.group(2)
            architecture = match.group(3)
            return {"name": name, "version": version, "arch": architecture}
        else:
            # If the additional pattern didn't match, try the new pattern
            match = re.match(new_pattern, package_string)

            if match:
                name = match.group(1)
                version = match.group(2)
                release = match.group(3)
                architecture = match.group(4)
                return {"name": name, "version": version, "arch": architecture}
            else:
                # If the new pattern didn't match, try the second pattern
                match = re.match(second_pattern, package_string)

                if match:
                    name = match.group(1)
                    version = match.group(2)
                    release = match.group(3)
                    architecture = match.group(4)
                    return {"name": name, "version": version, "arch": architecture}
                else:
                    return None


def extract_info_windows(package_string):
    try:
        # Essayer de décoder la chaîne hexadécimale
        decoded_string = binascii.unhexlify(package_string[2:]).decode('latin-1')

        # Utilisation d'une expression régulière pour extraire le nom, la version et l'architecture sous Windows
        pattern = r'^(.*?)\s*-\s*(.*?)\s*\((.*?)\)$'
        match = re.match(pattern, decoded_string)

        if match:
            name = match.group(1)
            version = match.group(2)
            architecture = match.group(3)
            return {"name": name, "version": version, "architecture": architecture}
        else:
            return {"name": decoded_string, "version": None, "architecture": None}
    except (binascii.Error, ValueError):
        # La chaîne n'est pas hexadécimale, traiter comme une chaîne normale
        pattern = r'^(.*?)\s*-\s*(.*?)\s*\((.*?)\)$'
        match = re.match(pattern, package_string)

        if match:
            name = match.group(1)
            version = match.group(2)
            architecture = match.group(3)
            return {"name": name, "version": version, "architecture": architecture}
        else:
            return {"name": package_string, "version": None, "architecture": None}


def extract_windows_host_info(input_str):
    # Expression régulière pour extraire l'architecture matérielle (premier mot après "Hardware:")
    hardware_architecture_pattern = r'Hardware:\s(\S+)'

    # Expression régulière pour extraire les informations logicielles
    software_pattern = r'Software:\s(.*?)\sVersion\s(\d+\.\d+).*\(Build\s(\d+)\s.*\)$'

    # Rechercher les correspondances dans la chaîne d'entrée
    hardware_architecture_match = re.search(hardware_architecture_pattern, input_str, re.IGNORECASE)
    software_match = re.search(software_pattern, input_str)

    # Extraire l'architecture matérielle
    hardware_architecture = hardware_architecture_match.group(1).strip() if hardware_architecture_match else None

    # Extraire les informations logicielles
    software_name = software_match.group(1).strip() if software_match else None
    software_version = software_match.group(2).strip() if software_match else None
    software_build = software_match.group(3).strip() if software_match else None

    return {
        "arch": hardware_architecture,
        "os_name": software_name,
        "kernel_version": software_version,
        "build": software_build
    }


def extract_info_macos(package_string):
    # Utilisation d'une expression régulière pour extraire le nom et la version sous macOS
    pattern = r'^(.*?)\s+(\S+)\s*$'
    match = re.match(pattern, package_string)

    if match:
        name = match.group(1)
        version = match.group(2)
        if '(null)' in version:
            version = None
        if '(null)' in name:
            name = None
        return {"name": name, "version": version, "arch": None}
    else:
        return None


linux_version_pattern = re.compile(
    r"^"
    # epoch must start with a digit
    r"(\d+:)?"
    # upstream must start with a digit
    r"\d"
    r"("
    # upstream  can contain only alphanumerics and the characters . + -
    # ~ (full stop, plus, hyphen, tilde)
    r"[A-Za-z0-9\.\+\~\-]+"
    r"|"
    # If there is no debian_revision then hyphens are not allowed in version.
    r"[A-Za-z0-9\.\+\~]+-[A-Za-z0-9\+\.\~]+"
    r")?"
    r"$"
)
irregular_version_pattern = re.compile(r'\d+(\.\d+)*')

def parse_version(text):
    """ Semantic Versioning (SemVer)
     Date-based Versioning
     Alphanumeric or Custom Schemes
     Debian based version parser
     Ubuntu based version parser
     parse version with build:
    """
    if not text:
        return None

    if linux_version_pattern.match(text):
        match = linux_version_pattern.search(text)
        if match:
            version = match.group()
            if ":" in version:
                epoch, _, version = version.partition(":")
                epoch = int(epoch)
            else:
                epoch = 0

            if "-" in version:
                upstream, _, revision = version.rpartition("-")
            else:
                upstream = version
                revision = "0"

            version = upstream
            regex_matched = False

            if 'ubuntu' in version:
                match = irregular_version_pattern.search(version)
                if match:
                    regex_matched = True
                    version = match.group()
            elif 'debian' in version:
                match = irregular_version_pattern.search(version)
                if match:
                    regex_matched = True
                    version = match.group()
            elif 'git' in version:
                match = irregular_version_pattern.search(version)
                if match:
                    regex_matched = True
                    version = match.group()
            elif '-' in version:
                match = irregular_version_pattern.search(version)
                if match:
                    regex_matched = True
                    version = match.group()
            else:
                match = irregular_version_pattern.search(version)
                if match:
                    regex_matched = True
                    version = match.group()

            parsed = None
            if not regex_matched:
                try:
                    parsed = sem_version.parse(version)
                except ValueError:
                    try:
                        parsed = pkg_version.parse(version)
                    except pkg_version.InvalidVersion:
                        parsed = None

            if parsed:
                parsed_split_len = len(str(parsed).split("."))
                if parsed_split_len < 3:
                    version = [str(parsed.major), str(parsed.minor)]
                elif parsed_split_len == 3:
                    try:
                        version = [str(parsed.major), str(parsed.minor), str(parsed.patch)]
                    except AttributeError:
                        version = [str(parsed.major), str(parsed.minor), str(parsed.micro)]
                else:
                    version = parsed

                if isinstance(version, list):
                    version = ".".join(version)
                else:
                    version = version
            else:
                if not regex_matched:
                    print(f'Cannot definitely parse version {text}')
            return version


def snmp_scanner(ip, ports: list = None):
    if ports is None:
        ports = [161]

    open_ports = []

    for port in ports:
        try:
            # Créez un objet socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Fixez un timeout court pour la connexion
            s.settimeout(1)

            # Tentez de se connecter à l'adresse IP et au port donnés
            s.connect((ip, port))
            # Si la connexion réussit, le port est ouvert
            open_ports.append(port)
        except Exception as e:
            print(f'Connexion exception the host must probably filtering the port. Reason: {e}')
    return open_ports



async def get_packages_async(hostname, community, os_name):
    var_bind = '1.3.6.1.2.1.25.6.3.1.2'

    def parse_version_append(ver, res, host):
        ver = parse_version(ver)
        d = {
            "name": pkg_info['name'].replace('"', ",") if '"' in pkg_info['name'] else pkg_info['name'],
            "version": ver,
        }
        res.append(d)

    iterator = await snmp_query_v2(var_bind=var_bind, hostname=hostname, community=community)
    
    result = []
    parsed_values = await parse_snmp_response(iterator, var_bind)
    threads = []
    extract_fnc = extract_info_windows
    if os_name == "linux":
        extract_fnc = extract_info_linux
    else:
        extract_fnc = extract_info_macos

    for value in parsed_values:
        pretty_value = value.prettyPrint()
        pkg_info = extract_fnc(pretty_value)
        if pkg_info:
            thread = threading.Thread(target=parse_version_append,
                                      args=(pkg_info['version'], result, hostname))
            thread.start()
            threads.append(thread)

    for thread in threads:
        thread.join()
    return result


async def get_host_info_async(hostname, community):
    var_binds = {
        'sys_hostname_bind': '1.3.6.1.2.1.1.5.0',
        'sys_descr_bind': '1.3.6.1.2.1.1.1.0',
    }
    result = {}
    for var_bind_name, var_bind_value in var_binds.items():
        iterator = await snmp_get_query_v2(var_bind=var_bind_value, hostname=hostname, community=community)
        parsed_values = await parse_snmp_response(iterator, var_bind_value)
        
        for value in parsed_values:
            value = value.prettyPrint()
            print(  f" host info {value}")
            lower_value = value.lower()
            if var_bind_name == 'sys_hostname_bind':
                result["host_name"] = value
                result["mac"] = getmac.get_mac_address(ip=hostname)
            elif var_bind_name == 'sys_descr_bind':
                if "windows" in lower_value:
                    info = extract_windows_host_info(value)
                    result["os_name"] = info.get("os_name")
                    result["kernel_version"] = info.get("kernel_version")
                    result["arch"] = info.get("arch")
                    result["build"] = info.get("build")
                elif "darwin" in lower_value:
                    partitioned = value.split()
                    if partitioned:
                        result["os_name"] = partitioned[0]
                        result["kernel_version"] = partitioned[2]
                        result["arch"] = partitioned[-1]
                elif "linux" in lower_value:
                    partitioned = value.split()
                    if partitioned:
                        result["os_name"] = partitioned[0]
                        result["kernel_version"] = partitioned[2]
                        result["arch"] = partitioned[-1]
                else:
                    print("Cannot parse unix based host informations.")
    return result


async def parse_snmp_response(iterator, var_bind):
    def sub_thread_iter(bind, var, res, stop):
        oid, value = bind
        if var not in str(oid):
            stop.set()  # Utilisez .set() pour définir la variable de contrôle à True
        else:
            res.append(value)

    def threaded_iterator(indication, status, binds, stop, res, var_b):
        if indication:
            return
        elif status:
            return
        else:
            sub_threads = []
            for bind in binds:
                th = threading.Thread(target=sub_thread_iter, args=(bind, var_b, res, stop))
                th.start()
                if stop.is_set():  # Utilisez .is_set() pour vérifier la variable de contrôle
                    break
                sub_threads.append(th)

            for th in sub_threads:
                th.join()

    result = []
    stop_loop = threading.Event()  # Utilisez un objet Event pour la variable de contrôle
    threads = []
    for error_indication, error_status, error_index, var_binds in iterator:
        thread = threading.Thread(target=threaded_iterator,
                                  args=(error_indication, error_status, var_binds, stop_loop, result, var_bind))
        thread.start()
        if stop_loop.is_set():  # Utilisez .is_set() pour vérifier la variable de contrôle
            break
        threads.append(thread)

    for thread in threads:
        thread.join()
    return result


async def snmp_query_v2(var_bind, hostname, community="public"):
    snmp_engine = SnmpEngine()
    return nextCmd(
        snmp_engine,
        CommunityData(community),
        UdpTransportTarget((hostname, 161), timeout=2.0, retries=0),
        ContextData(),
        ObjectType(ObjectIdentity(var_bind)),
    )


async def snmp_get_query_v2(var_bind, hostname, community="public"):
    snmp_engine = SnmpEngine()
    try:
        return getCmd(
            snmp_engine,
            CommunityData(community),
            UdpTransportTarget((hostname, 161), timeout=2.0, retries=0),
            ContextData(),
            ObjectType(ObjectIdentity(var_bind)),
        )
    except:
        return None


async def snmp_query_v3(var_bind, hostname, username, auth_key, priv_key, auth_protocol=usmHMACSHAAuthProtocol,
                        priv_protocol=usmAesCfb128Protocol):
    snmp_engine = SnmpEngine()
    try:
        return nextCmd(
            snmp_engine,
            UsmUserData(username, auth_key, priv_key, auth_protocol, priv_protocol),
            UdpTransportTarget(hostname),
            ContextData(),
            ObjectType(ObjectIdentity(var_bind)),
        )
    except:
        return None


def scan_up_host_and_append(ip, active_hosts):
    active = is_ip_active(ip=ip, all_active=True)
    if active:
        active_hosts.add(ip)
    return active_hosts


def get_snmp_hosts(network, use_range, range_start, range_end):
    config = Configuration.load(config_file_path=config_file)
    active_hosts = set()
    cidr = config.get_value('network', 'cidr', default=24)
    exempt = config.get_value('network', 'exempt')
    snmp_port = config.get_value('network', 'snmp', 'port', default=161)

    if not snmp_port:
        raise ValueError("The configured snmp port must be provided.")

    if network and use_range:
        if not range_start or not range_end:
            raise ValueError("The network range ip address must be provided.")
        hosts = get_possible_active_hosts_by_range(range_start, range_end, exempt=exempt)
    else:
        hosts = get_possible_active_hosts(ip_address=network, cidr=cidr, exempt=exempt)

    threads = []
    for host in hosts:
        thread = threading.Thread(target=scan_snmp_and_append, args=(host, snmp_port, active_hosts))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
    return active_hosts


async def handle_multi_async_operation(host, community, hosts_report):
    try:
        start = time.perf_counter()
        os_info = await get_host_info_async(host, community)
        end = time.perf_counter()
        if os_info:
            click.echo(f'Getting packages for Host: {host}')
            start = time.perf_counter()
            packages = await get_packages_async(host, community, os_name=os_info.get('os_name').lower())
            end = time.perf_counter()
            hosts_report[host] = {
                "os": os_info,
                "ipv4": host,
                "packages": packages
            }
    except:
        pass



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    hosts={}
    asyncio.run(handle_multi_async_operation('localhost','public',hosts))
    # print(hosts)