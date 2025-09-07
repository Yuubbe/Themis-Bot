#!/bin/bash

# 🏛️ Script de Déploiement Automatique Themis-Bot
# Pour VPS Debian 12

echo "🏛️ Déploiement de Themis-Bot sur VPS Debian 12"
echo "=============================================="

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier si on est root
if [[ $EUID -eq 0 ]]; then
   log_warning "Ce script ne doit pas être exécuté en tant que root"
   log_info "Créons d'abord un utilisateur dédié..."
   
   # Créer utilisateur themis s'il n'existe pas
   if ! id "themis" &>/dev/null; then
       adduser themis
       usermod -aG sudo themis
       log_success "Utilisateur 'themis' créé"
   else
       log_info "Utilisateur 'themis' existe déjà"
   fi
   
   log_info "Basculer vers l'utilisateur themis et relancer le script"
   exit 1
fi

# Mise à jour du système
log_info "Mise à jour du système..."
sudo apt update && sudo apt upgrade -y

# Installation des dépendances système
log_info "Installation des dépendances système..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    build-essential \
    libffi-dev \
    libssl-dev \
    libopus0 \
    libopus-dev \
    curl \
    wget \
    htop \
    nano \
    screen \
    tmux \
    ufw

log_success "Dépendances système installées"

# Vérifier version Python
PYTHON_VERSION=$(python3 --version)
log_info "Version Python: $PYTHON_VERSION"

# Aller dans le dossier home
cd ~

# Cloner le repository si il n'existe pas
if [ ! -d "Themis-Bot" ]; then
    log_info "Clonage du repository Themis-Bot..."
    git clone https://github.com/Yuubbe/Themis-Bot.git
    log_success "Repository cloné"
else
    log_info "Repository déjà présent, mise à jour..."
    cd Themis-Bot
    git pull origin main
    cd ~
fi

# Entrer dans le dossier
cd Themis-Bot

# Créer environnement virtuel
if [ ! -d ".venv" ]; then
    log_info "Création de l'environnement virtuel..."
    python3 -m venv .venv
    log_success "Environnement virtuel créé"
fi

# Activer l'environnement virtuel
log_info "Activation de l'environnement virtuel..."
source .venv/bin/activate

# Mettre à jour pip
log_info "Mise à jour de pip..."
pip install --upgrade pip

# Installer les dépendances Python
log_info "Installation des dépendances Python..."
pip install discord.py python-dotenv PyNaCl aiofiles colorlog aiohttp

log_success "Dépendances Python installées"

# Créer les dossiers nécessaires
log_info "Création des dossiers de données..."
mkdir -p data/tickets data/identity_photos logs
chmod 755 data
chmod 700 data/identity_photos

# Créer le fichier .env si il n'existe pas
if [ ! -f ".env" ]; then
    log_info "Création du fichier .env..."
    cat > .env << EOF
BOT_TOKEN=votre_token_discord_ici
BOT_PREFIX=!
BOT_ACTIVITY=Gardien de l'ordre 🏛️
EOF
    chmod 600 .env
    log_warning "⚠️  IMPORTANT: Editez le fichier .env avec votre token Discord !"
    log_info "nano .env"
else
    log_info "Fichier .env déjà présent"
fi

# Créer le script de lancement
log_info "Création du script de lancement..."
cat > start_themis.sh << 'EOF'
#!/bin/bash
cd /home/themis/Themis-Bot
source .venv/bin/activate
python3 main.py
EOF
chmod +x start_themis.sh

# Créer le service systemd
log_info "Configuration du service systemd..."
sudo tee /etc/systemd/system/themis-bot.service > /dev/null << EOF
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
EOF

# Recharger systemd et activer le service
sudo systemctl daemon-reload
sudo systemctl enable themis-bot

log_success "Service systemd configuré"

# Créer script de mise à jour
log_info "Création du script de mise à jour..."
cat > update_themis.sh << 'EOF'
#!/bin/bash
cd /home/themis/Themis-Bot

echo "🔄 Arrêt du service..."
sudo systemctl stop themis-bot

echo "💾 Sauvegarde de la configuration..."
cp .env .env.backup
cp -r data data_backup_$(date +%Y%m%d_%H%M%S)

echo "⬇️  Mise à jour du code..."
git pull origin main

echo "📦 Mise à jour des dépendances..."
source .venv/bin/activate
pip install --upgrade discord.py python-dotenv PyNaCl aiofiles colorlog aiohttp

echo "🚀 Redémarrage du service..."
sudo systemctl start themis-bot

echo "✅ Themis-Bot mis à jour et redémarré"
sudo systemctl status themis-bot
EOF
chmod +x update_themis.sh

# Créer script de sauvegarde
log_info "Création du script de sauvegarde..."
mkdir -p backups
cat > backup_themis.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/themis/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

echo "💾 Création de la sauvegarde..."
tar -czf $BACKUP_DIR/themis_data_$DATE.tar.gz -C /home/themis/Themis-Bot data .env

# Garder seulement les 7 dernières sauvegardes
find $BACKUP_DIR -name "themis_data_*.tar.gz" -mtime +7 -delete

echo "✅ Sauvegarde créée: themis_data_$DATE.tar.gz"
ls -lh $BACKUP_DIR/themis_data_$DATE.tar.gz
EOF
chmod +x backup_themis.sh

# Configuration du firewall basique
log_info "Configuration du firewall..."
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

log_success "Firewall configuré"

# Affichage final
echo ""
echo "🎉 DÉPLOIEMENT TERMINÉ !"
echo "======================"
echo ""
log_success "Themis-Bot est installé et configuré"
echo ""
echo "📋 PROCHAINES ÉTAPES:"
echo ""
echo "1️⃣  Configurez votre token Discord:"
echo "   nano .env"
echo ""
echo "2️⃣  Démarrez le bot:"
echo "   sudo systemctl start themis-bot"
echo ""
echo "3️⃣  Vérifiez le statut:"
echo "   sudo systemctl status themis-bot"
echo ""
echo "4️⃣  Voir les logs:"
echo "   sudo journalctl -u themis-bot -f"
echo ""
echo "🔧 COMMANDES UTILES:"
echo "   ./update_themis.sh     - Mettre à jour le bot"
echo "   ./backup_themis.sh     - Sauvegarder les données"
echo "   screen -S themis       - Lancer en mode screen"
echo ""
echo "🏛️ Que la justice règne ! ⚖️"
