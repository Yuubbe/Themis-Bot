# 🚀 Guide Rapide de Déploiement VPS

## Option 1: Script Automatique (Recommandé)

### 1. Connexion au VPS
```bash
ssh root@votre_ip_vps
```

### 2. Téléchargement et exécution du script
```bash
# Télécharger le script
wget https://raw.githubusercontent.com/Yuubbe/Themis-Bot/main/deploy_vps.sh

# Rendre exécutable
chmod +x deploy_vps.sh

# Exécuter en tant que root (il créera l'utilisateur themis)
./deploy_vps.sh
```

### 3. Configuration finale
```bash
# Basculer vers l'utilisateur themis
su - themis
cd Themis-Bot

# Configurer le token Discord
nano .env
# Remplacer: BOT_TOKEN=votre_token_discord_ici

# Démarrer le bot
sudo systemctl start themis-bot

# Vérifier que tout fonctionne
sudo systemctl status themis-bot
```

## Option 2: Installation Manuelle

Suivez le guide détaillé dans `DEPLOIEMENT_VPS.md`

## 🔧 Gestion du Bot

### Commandes essentielles
```bash
# Démarrer
sudo systemctl start themis-bot

# Arrêter  
sudo systemctl stop themis-bot

# Redémarrer
sudo systemctl restart themis-bot

# Voir les logs
sudo journalctl -u themis-bot -f

# Mettre à jour
./update_themis.sh

# Sauvegarder
./backup_themis.sh
```

### Mode Screen (Alternative)
```bash
# Démarrer une session
screen -S themis-bot

# Dans la session
cd ~/Themis-Bot
source .venv/bin/activate  
python3 main.py

# Détacher: Ctrl+A puis D
# Réattacher: screen -r themis-bot
```

## 🆘 Dépannage Rapide

### Bot ne démarre pas
```bash
# Vérifier les logs
sudo journalctl -u themis-bot -n 20

# Tester manuellement
cd ~/Themis-Bot
source .venv/bin/activate
python3 main.py
```

### Réinstaller les dépendances
```bash
cd ~/Themis-Bot
source .venv/bin/activate
pip install --force-reinstall discord.py PyNaCl aiofiles
```

### Vérifier la configuration
```bash
# Vérifier le token
cat .env

# Vérifier les permissions
ls -la .env
ls -la data/
```

## 📊 Monitoring

### Vérifier l'état du service
```bash
sudo systemctl status themis-bot
```

### Voir l'utilisation des ressources
```bash
htop
# Ou
top
```

### Espace disque
```bash
df -h
du -sh ~/Themis-Bot
```

## 🔄 Mise à jour

### Automatique
```bash
./update_themis.sh
```

### Manuelle
```bash
sudo systemctl stop themis-bot
git pull origin main
source .venv/bin/activate
pip install --upgrade discord.py
sudo systemctl start themis-bot
```

---

## ✅ Le bot est maintenant actif 24/7 sur votre VPS ! 🏛️
