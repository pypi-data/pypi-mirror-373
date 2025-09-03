from abc import ABC
import platform
import csv
import json
import subprocess
import socket
import uuid
import sys
from typing import List, Dict, Optional, Tuple
import psutil

from watchman_agent_v2.core.config.config_manager import ConfigManager

class ManageHost(ABC):
    def __init__(self):
        self.config=ConfigManager()
        
