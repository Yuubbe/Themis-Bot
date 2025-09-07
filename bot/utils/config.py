"""
🏛️ Configuration Manager pour Themis-Bot
Gère le chargement et l'accès aux paramètres de configuration
"""

import json
import os
from typing import Any, Dict

class Config:
    """Gestionnaire de configuration pour Themis-Bot"""
    
    def __init__(self, config_path: str = "data/config.json"):
        self.config_path = config_path
        self._config = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Charge la configuration depuis le fichier JSON"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            else:
                raise FileNotFoundError(f"Fichier de configuration introuvable: {self.config_path}")
        except Exception as e:
            print(f"⚠️ Erreur lors du chargement de la configuration: {e}")
            self._config = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Récupère une valeur de configuration avec notation pointée
        Ex: config.get('bot.token') pour accéder à config['bot']['token']
        """
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Définit une valeur de configuration"""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_config(self) -> None:
        """Sauvegarde la configuration dans le fichier"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Erreur lors de la sauvegarde: {e}")
    
    @property
    def raw_config(self) -> Dict[str, Any]:
        """Retourne la configuration brute"""
        return self._config.copy()
