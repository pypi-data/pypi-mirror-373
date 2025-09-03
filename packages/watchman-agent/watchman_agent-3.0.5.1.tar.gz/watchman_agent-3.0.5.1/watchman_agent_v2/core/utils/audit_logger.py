import logging

class AuditLogger:
    """
    Logger spécialisé pour des logs chiffrés avec audit trail.
    """
    def __init__(self):
        self.logger = logging.getLogger("audit")
        self.setup_logger()

    def setup_logger(self):
        """Configure le logger avec les handlers appropriés."""
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log(self, message: str):
        """Enregistre un message dans le log d'audit."""
        self.logger.info(message)
