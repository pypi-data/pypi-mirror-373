import json
import unittest
from unittest import mock
from unittest.mock import patch, MagicMock

import paramiko
from paramiko.client import SSHClient
from pysnmp.entity.engine import SnmpEngine

from watchman_agent_v2.core.agents.local_agent import LocalAgent
from watchman_agent_v2.core.protocols.http import HttpProtocol, ProtocolError
import httpx

from watchman_agent_v2.core.protocols.ssh import SSHProtocol
from watchman_agent_v2.core.protocols.wmi_protocol import WMIProtocol


class TestLocalAgent(unittest.TestCase):
    def test_run(self):
        agent = LocalAgent()
        # Tester la méthode run (ici, on attend None car pass)
        self.assertIsNone(agent.run())


class TestHttpProtocolLive(unittest.TestCase):

    def test_collect_info_live(self):
        """Test réel qui récupère les données d'un serveur en cours d'exécution"""
        config = {
            'api_key': 'a1ee56ca-adb3-4223-ab77-7a914af8a7c2',
            'port': 9001,
            'endpoint': '/apps',
            'timeout': 30
        }
        ip = '127.0.0.1'

        http_protocol = HttpProtocol()

        try:
            # Récupération des infos réelles
            result = http_protocol.collect_info(ip, config)

            # Affichage du résultat JSON
            print(json.dumps(result, indent=4))

            # Vérification basique de la réponse
            self.assertIsInstance(result, dict)  # Doit retourner un dictionnaire

        except ProtocolError as e:
            self.fail(f"Erreur lors de la récupération des données : {str(e)}")


class TestSNMPProtocol(unittest.TestCase):

    # Test pour la méthode connect
    def test_connect(self):
        protocol = SNMPProtocol(community="public", ip="127.0.0.1")

        # On patch le moteur SNMP pour simuler une connexion
        with mock.patch.object(SnmpEngine, 'start') as mock_start:
            protocol.connect()
            mock_start.assert_called_once()  # Vérifie que l'engine SNMP a été initialisé
            self.assertIsNotNone(protocol.snmp_engine)  # Vérifie que l'engine SNMP a bien été initialisé
            print("SNMP engine bien initialisé")

    # Test pour collect_info quand tout se passe bien avec une réponse correcte
    def test_collect_info_success(self):
        """Test un appel réussi pour collecter des informations"""
        fake_response = mock.Mock()
        fake_response.status_code = 200
        fake_response.json.return_value = {"data": "success"}
        self.protocol.client.get.return_value = fake_response

        ip = "127.0.0.1"
        config = {'api_key': 'fake_api_key', 'port': 9000}

        result = self.protocol.collect_info(ip, config)

        self.assertEqual(result, {"data": "success"})  # Vérifie que la réponse est correctement formatée

    def test_connect(self):
        """Test que la méthode connect initialise bien le client"""
        with mock.patch.object(httpx, 'Client') as MockClient:
            mock_client = mock.Mock()
            MockClient.return_value = mock_client

            self.protocol.connect()
            MockClient.assert_called_once()  # Vérifie que Client a été initialisé

    def test_disconnect(self):
        """Test que la méthode disconnect ferme correctement la connexion"""
        self.protocol.client = mock.Mock()

        with mock.patch.object(self.protocol.client, 'close') as mock_close:
            self.protocol.disconnect()
            mock_close.assert_called_once()  # Vérifie que la méthode 'close' a été appelée une fois


class TestSSHProtocol(unittest.TestCase):

    def test_collect_info_success(self):
        config = {
            'username': 'Utilisateur',  # Remplacez par votre nom d'utilisateur SSH
            'password': '1622001',  # Remplacez par votre mot de passe SSH
            'port': 22  # Port SSH (par défaut, c'est 22)
        }
        ip = '127.0.0.1'  # Remplacez par l'IP de votre serveur

        ssh_protocol = SSHProtocol()

        # Récupérer les informations réelles du serveur
        result = ssh_protocol.collect_info(ip, config)

        # Afficher le résultat JSON
        print(json.dumps(result, indent=4))


class TestWMIProtocol(unittest.TestCase):

    def test_collect_info_success(self):
        config = {
            'username': 'utilisateur',  # Remplacez par votre nom d'utilisateur SSH
            'password': '1622001',  # Remplacez par votre mot de passe SSH
            'port': 135
        }
        ip = '127.0.0.1'  # Remplacez par l'IP de votre serveur

        wmi_protocol = WMIProtocol()

        # Récupérer les informations réelles du serveur
        result = wmi_protocol.collect_info(ip, config)

        # Afficher le résultat JSON
        print(json.dumps(result, indent=4))


# class TestSNMPProtocol(unittest.TestCase):
#
#     # Test pour la méthode connect
#     def test_connect(self):
#         protocol = SNMPProtocol(community="public", ip="127.0.0.1")
#
#         # On patch le moteur SNMP pour simuler une connexion
#         with mock.patch.object(SnmpEngine, 'start') as mock_start:
#             protocol.connect()
#             mock_start.assert_called_once()  # Vérifie que l'engine SNMP a été initialisé
#             self.assertIsNotNone(protocol.snmp_engine)  # Vérifie que l'engine SNMP a bien été initialisé
#             print("SNMP engine bien initialisé")
#
#     # Test pour collect_info quand tout se passe bien avec une réponse correcte
#     def test_collect_info_success(self):
#         protocol = SNMPProtocol(community="public", ip="127.0.0.1")
#         protocol.snmp_engine = SnmpEngine()  # Simuler l'initialisation de l'engine
#
#         # Simuler la réponse d'une requête SNMP avec un OID simple
#         with mock.patch('your_module.getCmd',
#                         return_value=(None, None, None, [(ObjectIdentity('SNMPv2-MIB', 'sysName', 0), 'TestDevice')])):
#             data = protocol.collect_info()
#             self.assertIsNotNone(data)  # Vérifie que les données ont été récupérées
#             self.assertEqual(data['SNMPv2-MIB::sysName.0'],
#                              'TestDevice')  # Vérifie que les données récupérées sont correctes
#             print("Données récupérées :", data)
#
#     # Test pour collect_info avec une erreur SNMP
#     def test_collect_info_snmp_error(self):
#         protocol = SNMPProtocol(community="public", ip="127.0.0.1")
#         protocol.snmp_engine = SnmpEngine()  # Simuler l'initialisation de l'engine
#
#         # Simuler une erreur de SNMP avec un retour d'erreur dans le getCmd
#         with mock.patch('your_module.getCmd', side_effect=Exception("Erreur SNMP")):
#             result = protocol.collect_info()
#             self.assertIsNone(result)  # Vérifie que la méthode retourne None en cas d'erreur SNMP
#
#     # Test pour collect_info avec une erreur de réponse vide ou incorrecte
#     def test_collect_info_empty_response(self):
#         protocol = SNMPProtocol(community="public", ip="127.0.0.1")
#         protocol.snmp_engine = SnmpEngine()  # Simuler l'initialisation de l'engine
#
#         # Simuler une réponse vide de SNMP (aucune donnée retournée)
#         with mock.patch('your_module.getCmd', return_value=(None, None, None, [])):
#             result = protocol.collect_info()
#             self.assertIsNone(result)  # Vérifie que la méthode retourne None si la réponse est vide ou incorrecte
#
#     # Test pour disconnect
#     def test_disconnect(self):
#         protocol = SNMPProtocol(community="public", ip="127.0.0.1")
#         protocol.snmp_engine = SnmpEngine()  # Simuler l'initialisation de l'engine
#
#         # Simuler la déconnexion
#         with mock.patch.object(protocol.snmp_engine, 'cleanup') as mock_cleanup:
#             protocol.disconnect()
#             mock_cleanup.assert_called_once()  # Vérifie que la méthode cleanup a été appelée
#             self.assertIsNone(protocol.snmp_engine)  # Vérifie que l'engine SNMP a été nettoyé
#             print("SNMP engine bien nettoyé après déconnexion")


if __name__ == '__main__':
    unittest.main()
