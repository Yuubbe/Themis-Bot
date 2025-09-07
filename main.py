"""
🏛️ Themis-Bot - Gardien de l'Ordre
Point d'entrée principal du bot Discord
"""

import asyncio
import logging
from bot.themis import ThemisBot
from bot.utils.config import Config
from bot.utils.logger import setup_logger

async def main():
    """Fonction principale pour démarrer Themis-Bot"""
    
    # Configuration du logger
    setup_logger()
    logger = logging.getLogger(__name__)
    
    # Chargement de la configuration
    config = Config()
    
    logger.info("🏛️ Initialisation de Themis-Bot...")
    logger.info("« La justice est la vérité en action » - Victor Hugo")
    
    # Création et démarrage du bot
    bot = ThemisBot(config)
    
    try:
        await bot.start(config.get('bot.token'))
    except KeyboardInterrupt:
        logger.info("⚖️ Arrêt demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"💥 Erreur fatale: {e}")
    finally:
        await bot.close()
        logger.info("🏛️ Themis-Bot s'est retiré dans l'Olympe")

if __name__ == "__main__":
    asyncio.run(main())
