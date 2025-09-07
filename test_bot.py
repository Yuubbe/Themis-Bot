"""
🏛️ Tests basiques pour Themis-Bot
Vérifications de fonctionnement
"""

import asyncio
import logging
import sys
import os

# Ajouter le chemin du projet
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_imports():
    """Test des imports principaux"""
    try:
        print("📚 Test des imports...")
        
        from bot.utils.config import Config
        print("✅ Config importé")
        
        from bot.utils.logger import setup_logger
        print("✅ Logger importé")
        
        # Note: discord.py sera testé après installation
        print("✅ Tous les imports de base réussis")
        return True
        
    except Exception as e:
        print(f"❌ Erreur d'import: {e}")
        return False

async def test_config():
    """Test de la configuration"""
    try:
        print("\n⚙️ Test de la configuration...")
        
        from bot.utils.config import Config
        config = Config()
        
        # Test de lecture
        prefix = config.get('bot.prefix', '!')
        print(f"✅ Préfixe: {prefix}")
        
        # Test de modification
        config.set('test.value', 'hello')
        assert config.get('test.value') == 'hello'
        print("✅ Configuration fonctionnelle")
        return True
        
    except Exception as e:
        print(f"❌ Erreur de config: {e}")
        return False

async def test_logger():
    """Test du système de logging"""
    try:
        print("\n📝 Test du logger...")
        
        from bot.utils.logger import setup_logger
        setup_logger()
        
        logger = logging.getLogger("test")
        logger.info("Test de log")
        print("✅ Logger configuré")
        return True
        
    except Exception as e:
        print(f"❌ Erreur de logger: {e}")
        return False

async def main():
    """Tests principaux"""
    print("🏛️ Tests Themis-Bot")
    print("=" * 30)
    
    tests = [
        test_imports,
        test_config,
        test_logger
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ Test échoué: {e}")
    
    print(f"\n📊 Résultats: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés!")
        print("🚀 Vous pouvez maintenant configurer votre token et lancer le bot!")
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez la configuration.")

if __name__ == "__main__":
    asyncio.run(main())
