"""
🏛️ Module d'Aide pour Themis-Bot
Commande slash d'aide et guide d'utilisation
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging

class HelpCog(commands.Cog):
    """Module de commande d'aide"""
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
    
    @app_commands.command(name="help", description="📖 Affiche l'aide et les commandes disponibles")
    async def help_command(self, interaction: discord.Interaction):
        """Affiche l'aide complète du bot"""
        
        embed = discord.Embed(
            title="🏛️ Guide de Themis-Bot",
            description="*« Il y a une loi que même les dieux ne sauraient briser sans causer la ruine : celle de l'ordre. »*",
            color=0x9932CC
        )
        
        # Commandes de modération
        moderation_commands = [
            "`/warn` - ⚖️ Avertir un utilisateur",
            "`/purge` - 🧹 Supprimer des messages",
            "`/timeout` - ⏰ Mettre en timeout",
            "`/kick` - 👢 Expulser un utilisateur",
            "`/ban` - 🔨 Bannir un utilisateur",
            "`/unban` - 🕊️ Débannir un utilisateur",
            "`/slowmode` - 🐌 Mode lent du canal",
            "`/rules` - 📜 Voir les règles",
            "`/stats` - 📊 Statistiques de modération"
        ]
        
        embed.add_field(
            name="🛡️ Commandes de Modération",
            value="\n".join(moderation_commands),
            inline=False
        )
        
        # Commandes d'administration
        admin_commands = [
            "`/setup` - 🏛️ Configuration initiale",
            "`/configure channel` - ⚙️ Configurer un canal",
            "`/toggle` - 🔄 Activer/Désactiver fonctionnalités",
            "`/prefix` - 🔧 Changer le préfixe",
            "`/reload` - 🔄 Recharger la config",
            "`/info` - 🏛️ Informations du bot"
        ]
        
        embed.add_field(
            name="⚙️ Commandes d'Administration",
            value="\n".join(admin_commands),
            inline=False
        )
        
        # Commandes utilitaires
        utility_commands = [
            "`/userinfo` - 👤 Infos utilisateur",
            "`/serverinfo` - 🏰 Infos du serveur",
            "`/avatar` - 🖼️ Avatar d'un utilisateur",
            "`/ping` - 🏓 Latence du bot"
        ]
        
        embed.add_field(
            name="🔧 Commandes Utilitaires",
            value="\n".join(utility_commands),
            inline=False
        )
        
        # Commandes de divertissement
        fun_commands = [
            "`/quote` - 📜 Citation de Thémis",
            "`/dice` - 🎲 Lancer des dés",
            "`/coinflip` - 🪙 Pile ou face",
            "`/poll` - 📊 Créer un sondage",
            "`/choose` - 🎯 Choix aléatoire",
            "`/8ball` - 🔮 Boule magique"
        ]
        
        embed.add_field(
            name="🎉 Commandes de Divertissement",
            value="\n".join(fun_commands),
            inline=False
        )
        
        # Fonctionnalités automatiques
        embed.add_field(
            name="🤖 Modération Automatique",
            value=(
                "• Surveillance des canaux en temps réel\n"
                "• Redirection des messages mal placés\n"
                "• Respect des règles par canal\n"
                "• Système d'avertissements automatique"
            ),
            inline=False
        )
        
        # Permissions
        embed.add_field(
            name="🔒 Permissions Requises",
            value=(
                "**Modération:** `Manage Messages`, `Moderate Members`\n"
                "**Administration:** `Manage Guild`, `Administrator`"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🏛️ Philosophie de Thémis",
            value="Chaque canal est un temple dédié à une vérité spécifique. Respectez l'ordre !",
            inline=False
        )
        
        embed.set_footer(text="Utilisez les commandes slash (/) pour une expérience optimale")
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    """Charge le module d'aide"""
    await bot.add_cog(HelpCog(bot))
