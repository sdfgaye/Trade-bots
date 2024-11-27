import logging
import os
from datetime import datetime
from omegaconf import DictConfig

def get_logger(name: str = None, cfg: DictConfig = None):
    """
    Configure and return a logger object.

    Parameters:
    - name (str): Nom optionnel pour le logger (module ou script).
    - cfg (DictConfig): Configuration Hydra (logging).

    Returns:
    - logging.Logger: Logger configuré.
    """
    # Extraire les paramètres depuis la configuration
    log_dir = os.path.abspath(cfg.logging.log_dir if cfg and "logging" in cfg else "logs")
    log_level = getattr(logging, cfg.logging.level.upper(), logging.INFO) if cfg and "logging" in cfg else logging.INFO
    handlers = cfg.logging.handlers if cfg and "logging" in cfg and "handlers" in cfg.logging else ["console"]
    
    # Créer le dossier de logs si nécessaire
    os.makedirs(log_dir, exist_ok=True)

    # Générer un nom de fichier avec millisecondes
    LOG_FILE = f"{datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')[:-3]}.log"
    LOG_FILE_PATH = os.path.join(log_dir, LOG_FILE)

    # Configurer le logger
    logger = logging.getLogger(name)

    if logger.hasHandlers():
        logger.handlers.clear()
        
    logger.setLevel(log_level)

    # File handler
    if "file" in handlers:
        file_handler = logging.FileHandler(LOG_FILE_PATH)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "[%(asctime)s] %(lineno)d %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Console handler
    if "console" in handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger
