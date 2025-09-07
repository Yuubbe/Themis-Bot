# 🚀 Déploiement Themis-Bot sur VPS Debian 12

## 📋 Prérequis et Installation

### 1. Connexion au VPS
```bash
ssh root@votre_ip_vps
# ou
ssh utilisateur@votre_ip_vps
```

### 2. Mise à jour du système
```bash
sudo apt update && sudo apt upgrade -y
```

### 3. Installation de Python 3.11+ et outils nécessaires
```bash
# Installation Python et pip
sudo apt install python3 python3-pip python3-venv python3-dev -y

# Installation Git
sudo apt install git -y

# Installation des outils système nécessaires
sudo apt install curl wget htop nano screen tmux -y

# Vérifier la version Python
python3 --version
```

### 4. Installation des dépendances système pour PyNaCl
```bash
# Dépendances pour compilation PyNaCl
sudo apt install build-essential libffi-dev libssl-dev -y

# Dépendances audio pour discord.py voice
sudo apt install libopus0 libopus-dev -y
```

## 📁 Déploiement du Bot

### 1. Créer un utilisateur dédié (Recommandé)
```bash
# Créer utilisateur themis
sudo adduser themis

# Ajouter aux groupes nécessaires
sudo usermod -aG sudo themis

# Se connecter avec le nouvel utilisateur
su - themis
```

### 2. Cloner le repository
```bash
# Se placer dans le dossier home
cd ~

# Cloner le repository
git clone https://github.com/Yuubbe/Themis-Bot.git

# Entrer dans le dossier
cd Themis-Bot
```

### 3. Configuration de l'environnement virtuel
```bash
# Créer l'environnement virtuel
python3 -m venv .venv

# Activer l'environnement
source .venv/bin/activate

# Mettre à jour pip
pip install --upgrade pip

# Installer les dépendances
pip install discord.py python-dotenv PyNaCl aiofiles colorlog aiohttp
```

### 4. Configuration des fichiers
```bash
# Créer le fichier .env
nano .env
```

**Contenu du fichier .env :**
```env
BOT_TOKEN=votre_token_discord_ici
BOT_PREFIX=!
BOT_ACTIVITY=Gardien de l'ordre 🏛️
```

```bash
# Créer les dossiers nécessaires
mkdir -p data/tickets data/identity_photos logs

# Permissions appropriées
chmod 755 data
chmod 700 data/identity_photos
```

## 🔧 Configuration Avancée

### 1. Créer un script de lancement
```bash
nano start_themis.sh
```

**Contenu du script :**
```bash
#!/bin/bash
cd /home/themis/Themis-Bot
source .venv/bin/activate
python3 main.py
```

```bash
# Rendre le script exécutable
chmod +x start_themis.sh
```

### 2. Configuration avec systemd (Service système)
```bash
sudo nano /etc/systemd/system/themis-bot.service
```

**Contenu du service :**
```ini
[Unit]
Description=Themis Discord Bot
After=network.target

[Service]
Type=simple
User=themis
WorkingDirectory=/home/themis/Themis-Bot
Environment=PATH=/home/themis/Themis-Bot/.venv/bin
ExecStart=/home/themis/Themis-Bot/.venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Recharger systemd
sudo systemctl daemon-reload

# Activer le service au démarrage
sudo systemctl enable themis-bot

# Démarrer le service
sudo systemctl start themis-bot

# Vérifier le statut
sudo systemctl status themis-bot
```

## 📊 Gestion et Monitoring

### 1. Commandes de gestion du service
```bash
# Démarrer le bot
sudo systemctl start themis-bot

# Arrêter le bot
sudo systemctl stop themis-bot

# Redémarrer le bot
sudo systemctl restart themis-bot

# Voir les logs
sudo journalctl -u themis-bot -f

# Voir les logs des dernières 24h
sudo journalctl -u themis-bot --since "24 hours ago"
```

### 2. Alternative avec Screen (Plus simple)
```bash
# Démarrer une session screen
screen -S themis-bot

# Dans la session screen
cd ~/Themis-Bot
source .venv/bin/activate
python3 main.py

# Détacher la session : Ctrl+A puis D
# Réattacher : screen -r themis-bot
```

### 3. Monitoring avec htop
```bash
# Installer htop si pas déjà fait
sudo apt install htop -y

# Surveiller les processus
htop
```

## 🔐 Sécurité et Maintenance

### 1. Configuration du firewall
```bash
# Installer ufw
sudo apt install ufw -y

# Configuration basique
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

# Activer le firewall
sudo ufw enable
```

### 2. Script de mise à jour automatique
```bash
nano update_themis.sh
```

**Contenu :**
```bash
#!/bin/bash
cd /home/themis/Themis-Bot

# Arrêter le service
sudo systemctl stop themis-bot

# Sauvegarder la configuration
cp .env .env.backup
cp -r data data_backup

# Mettre à jour le code
git pull origin main

# Réinstaller les dépendances si nécessaire
source .venv/bin/activate
pip install --upgrade discord.py python-dotenv PyNaCl aiofiles colorlog aiohttp

# Redémarrer le service
sudo systemctl start themis-bot

echo "✅ Themis-Bot mis à jour et redémarré"
```

```bash
chmod +x update_themis.sh
```

### 3. Sauvegarde automatique
```bash
nano backup_themis.sh
```

**Contenu :**
```bash
#!/bin/bash
BACKUP_DIR="/home/themis/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Sauvegarder les données
tar -czf $BACKUP_DIR/themis_data_$DATE.tar.gz -C /home/themis/Themis-Bot data

# Garder seulement les 7 dernières sauvegardes
find $BACKUP_DIR -name "themis_data_*.tar.gz" -mtime +7 -delete

echo "✅ Sauvegarde créée: themis_data_$DATE.tar.gz"
```

```bash
chmod +x backup_themis.sh

# Ajouter à crontab pour sauvegarde quotidienne
crontab -e
# Ajouter cette ligne :
0 2 * * * /home/themis/backup_themis.sh
```

## 🔍 Dépannage

### 1. Vérifier les logs
```bash
# Logs du service
sudo journalctl -u themis-bot -n 50

# Logs en temps réel
sudo journalctl -u themis-bot -f

# Logs d'erreurs seulement
sudo journalctl -u themis-bot -p err
```

### 2. Tester manuellement
```bash
cd ~/Themis-Bot
source .venv/bin/activate
python3 main.py
```

### 3. Vérifier les permissions
```bash
ls -la data/
ls -la .env
```

### 4. Problèmes courants

**Bot ne démarre pas :**
- Vérifier le token dans `.env`
- Vérifier les permissions des fichiers
- Vérifier l'installation des dépendances

**PyNaCl ne s'installe pas :**
```bash
sudo apt install build-essential libffi-dev libssl-dev python3-dev -y
pip install --upgrade pip setuptools wheel
pip install PyNaCl
```

**Problème de permissions :**
```bash
sudo chown -R themis:themis /home/themis/Themis-Bot
chmod -R 755 /home/themis/Themis-Bot
chmod 600 /home/themis/Themis-Bot/.env
```

## 📋 Checklist de Déploiement

- [ ] VPS Debian 12 opérationnel
- [ ] Python 3.11+ installé
- [ ] Git installé
- [ ] Utilisateur `themis` créé
- [ ] Repository cloné
- [ ] Environnement virtuel créé
- [ ] Dépendances installées
- [ ] Fichier `.env` configuré avec le token
- [ ] Service systemd configuré
- [ ] Bot démarré et fonctionnel
- [ ] Logs vérifiés
- [ ] Sauvegarde configurée
- [ ] Firewall configuré

## 🚀 Commandes de Déploiement Rapide

```bash
# Tout en une fois (à adapter selon vos besoins)
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git build-essential libffi-dev libssl-dev libopus0 libopus-dev -y
sudo adduser themis
su - themis
git clone https://github.com/Yuubbe/Themis-Bot.git
cd Themis-Bot
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install discord.py python-dotenv PyNaCl aiofiles colorlog aiohttp
# Configurer .env avec votre token
# Puis configurer le service systemd
```

---

## 🏛️ Themis-Bot est maintenant déployé et opérationnel 24/7 ! ⚖️
