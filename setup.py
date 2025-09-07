"""
🏛️ Script de démarrage rapide pour Themis-Bot
Aide à la configuration initiale et au test du bot
"""

import os
import json

def create_startup_guide():
    """Crée un guide de démarrage"""
    
    guide = """
🏛️ GUIDE DE DÉMARRAGE THEMIS-BOT
================================

1. 📝 CONFIGURATION DU TOKEN
   - Allez sur https://discord.com/developers/applications
   - Créez une nouvelle application
   - Section "Bot" -> Reset Token
   - Copiez le token dans data/config.json

2. 🔧 PERMISSIONS REQUISES
   Le bot a besoin des permissions suivantes:
   - Send Messages
   - Manage Messages
   - Read Message History
   - Embed Links
   - Use Slash Commands
   - Moderate Members (pour timeout)

3. 🔗 INVITATION DU BOT
   URL d'invitation avec permissions:
   https://discord.com/api/oauth2/authorize?client_id=VOTRE_CLIENT_ID&permissions=1099780067329&scope=bot

4. ⚙️ COMMANDES PRINCIPALES
   !setup         - Configuration initiale
   !configure     - Configurer un canal
   !rules         - Afficher les règles
   !warn          - Avertir un utilisateur
   !purge         - Nettoyer des messages
   !stats         - Statistiques

5. 🚀 DÉMARRAGE
   python main.py

6. 📋 VÉRIFICATIONS
   - Le bot apparaît en ligne
   - Réagit aux commandes
   - Modère automatiquement
   
Que la justice de Thémis guide vos pas ! ⚖️
"""
    
    with open("SETUP_GUIDE.txt", "w", encoding="utf-8") as f:
        f.write(guide)
    
    print("📋 Guide de démarrage créé: SETUP_GUIDE.txt")

def check_config():
    """Vérifie la configuration"""
    config_path = "data/config.json"
    
    if not os.path.exists(config_path):
        print("❌ Fichier de configuration manquant!")
        return False
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    token = config.get('bot', {}).get('token', '')
    
    if token == 'VOTRE_TOKEN_BOT_ICI':
        print("⚠️ Token du bot non configuré!")
        print("Modifiez le fichier data/config.json")
        return False
    
    print("✅ Configuration semble correcte")
    return True

def main():
    """Menu principal de configuration"""
    print("🏛️ Assistant de Configuration Themis-Bot")
    print("=" * 40)
    
    while True:
        print("\n📋 Options disponibles:")
        print("1. Créer le guide de démarrage")
        print("2. Vérifier la configuration")
        print("3. Tester la connexion (TODO)")
        print("4. Quitter")
        
        choice = input("\n🎯 Votre choix (1-4): ").strip()
        
        if choice == "1":
            create_startup_guide()
        elif choice == "2":
            check_config()
        elif choice == "3":
            print("🚧 Test de connexion non implémenté")
        elif choice == "4":
            print("⚖️ Que Thémis vous protège!")
            break
        else:
            print("❌ Choix invalide")

if __name__ == "__main__":
    main()
