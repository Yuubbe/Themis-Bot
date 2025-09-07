# 🏛️ Themis-Bot - Gardien de l'Ordre

*« Il y a une loi que même les dieux ne sauraient briser sans causer la ruine : celle de l'ordre. »*

Un bot Discord modérateur qui maintient l'ordre et la discipline dans les canaux en s'assurant que chaque message est posté dans le bon canal.

## 🎯 Fonctionnalités

- **Surveillance des canaux** : Détecte les messages inappropriés pour le canal
- **Modération automatique** : Supprime et redirige les messages mal placés
- **Système d'avertissements** : Prévient les utilisateurs des infractions
- **Configuration flexible** : Règles personnalisables par serveur
- **Logs détaillés** : Historique des actions de modération

## 🚀 Installation

1. Cloner le repository
2. Installer les dépendances : `pip install -r requirements.txt`
3. Configurer le token dans `config.json`
4. Lancer : `python main.py`

## 📁 Structure

```
Themis-Bot/
├── main.py              # Point d'entrée
├── bot/                 # Code principal du bot
│   ├── __init__.py
│   ├── themis.py        # Classe principale du bot
│   ├── cogs/            # Modules de commandes
│   │   ├── __init__.py
│   │   ├── moderation.py
│   │   └── admin.py
│   └── utils/           # Utilitaires
│       ├── __init__.py
│       ├── config.py
│       ├── database.py
│       └── logger.py
├── data/                # Données et configuration
│   ├── config.json
│   └── rules.json
├── requirements.txt     # Dépendances
└── README.md
```

## ⚖️ La Justice de Thémis

Ce bot incarne l'esprit de Thémis, déesse de la justice divine et de l'ordre naturel.
