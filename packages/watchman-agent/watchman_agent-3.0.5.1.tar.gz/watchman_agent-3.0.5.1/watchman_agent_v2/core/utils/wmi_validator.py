from impacket.dcerpc.v5.dcomrt import DCOMConnection
from impacket.dcerpc.v5.dcom.wmi import CLSID_WbemLevel1Login, IWbemLevel1Login
from impacket.dcerpc.v5.dtypes import NULL
import socket
import logging

class WMICredentialValidator:
    def __init__(self, timeout=10):
        self.timeout = timeout
        self.logger = logging.getLogger('wmi_validator')

    def validate(self, domain, username, password, client_ip):
        """Valide des credentials WMI contre une machine cible"""
        try:
            return self._attempt_wmi_connection(
                domain=domain,
                username=username,
                password=password,
                target=client_ip
            )
        except socket.error as e:
            self.logger.error(f"Erreur réseau : {str(e)}")
            return False
        except Exception as e:
            self.logger.debug(f"Erreur d'authentification : {str(e)}")
            return False

    def _attempt_wmi_connection(self, domain, username, password, target):
        """Tente une connexion WMI via DCOM avec timeout"""
        dcom = None
        try:
            dcom = DCOMConnection(
                target,
                username=username,
                password=password,
                domain=domain,
                oxidResolver=True,
                timeout=self.timeout,
                doKerberos=False
            )

            # Tente d'accéder au namespace root/cimv2
            iInterface = dcom.CoCreateInstanceEx(CLSID_WbemLevel1Login)
            iWbemLevel1Login = IWbemLevel1Login(iInterface)
            iWbemLevel1Login.NTLMLogin('root\\cimv2', NULL, NULL)
            
            # Nettoyage propre
            iWbemLevel1Login.RemRelease()
            dcom.disconnect()
            return True

        except Exception as e:
            if dcom:
                dcom.disconnect()
            raise e