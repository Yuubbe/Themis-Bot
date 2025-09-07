"""
🏛️ Logger pour Themis-Bot
Configuration du système de logging avec couleurs et formatage
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logger() -> None:
    """Configure le système de logging pour Themis-Bot"""
    
    # Création du dossier logs s'il n'existe pas
    os.makedirs("logs", exist_ok=True)
    
    # Configuration du logger principal
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Formatter pour les logs
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler pour fichier avec rotation
    file_handler = RotatingFileHandler(
        f"logs/themis_{datetime.now().strftime('%Y%m%d')}.log",
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Handler pour console avec couleurs
    console_handler = logging.StreamHandler()
    console_formatter = ColoredFormatter(
        '%(log_color)s%(asctime)s | %(levelname)8s | %(name)s | %(message)s%(reset)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    
    # Ajout des handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Configuration spécifique pour discord.py
    discord_logger = logging.getLogger('discord')
    discord_logger.setLevel(logging.WARNING)

class ColoredFormatter(logging.Formatter):
    """Formatter avec couleurs pour la console"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Vert
        'WARNING': '\033[33m',    # Jaune
        'ERROR': '\033[31m',      # Rouge
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Ajout de la couleur selon le niveau
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.log_color = log_color
        record.reset = self.COLORS['RESET']
        
        return super().format(record)
