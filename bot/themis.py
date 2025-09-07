"""
🏛️ Themis-Bot - Classe principale
« Il y a une loi que même les dieux ne sauraient briser sans causer la ruine : celle de l'ordre »
"""

import discord
from discord.ext import commands
import logging
import json
import os
from typing import Dict, Any

class ThemisBot(commands.Bot):
    """
    Bot Discord gardien de l'ordre et de la justice
    Incarne l'esprit de Thémis, déesse de la justice divine
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration des intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        
        # Initialisation du bot
        super().__init__(
            command_prefix=config.get('bot.prefix', '!'),
            intents=intents,
            help_command=None,  # On créera notre propre commande help
            case_insensitive=True
        )
        
        # Chargement des règles
        self.rules = self.load_rules()
        
        # Statistiques
        self.stats = {
            'messages_moderated': 0,
            'warnings_issued': 0,
            'redirections': 0
        }
    
    def load_rules(self) -> Dict[str, Any]:
        """Charge les règles de modération"""
        try:
            rules_path = "data/rules.json"
            if os.path.exists(rules_path):
                with open(rules_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.logger.warning(f"Fichier de règles introuvable: {rules_path}")
                return {}
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement des règles: {e}")
            return {}
    
    async def setup_hook(self):
        """Configuration initiale du bot"""
        self.logger.info("⚖️ Configuration de Themis-Bot...")
        
        # Chargement des cogs (modules)
        await self.load_cogs()
        
        # Synchronisation des commandes slash
        try:
            synced = await self.tree.sync()
            self.logger.info(f"📜 {len(synced)} commandes slash synchronisées")
        except Exception as e:
            self.logger.error(f"Erreur lors de la synchronisation: {e}")
    
    async def load_cogs(self):
        """Charge les modules (cogs) du bot"""
        cogs_to_load = [
            'bot.cogs.admin',
            'bot.cogs.help',
            'bot.cogs.utilities',
            'bot.cogs.fun',
            'bot.cogs.security',  # Module de sécurité avec tests IP
            'bot.cogs.tickets'    # Module de tickets et vérification d'identité
        ]
        
        for cog in cogs_to_load:
            try:
                await self.load_extension(cog)
                self.logger.info(f"📚 Module chargé: {cog}")
            except Exception as e:
                self.logger.error(f"❌ Erreur lors du chargement de {cog}: {e}")
    
    async def on_ready(self):
        """Événement déclenché quand le bot est prêt"""
        self.logger.info("🏛️" + "="*50)
        self.logger.info(f"🏛️ Themis-Bot est maintenant en ligne!")
        if self.user:
            self.logger.info(f"🏛️ Connecté en tant que: {self.user.name} (ID: {self.user.id})")
        self.logger.info(f"🏛️ Serveurs: {len(self.guilds)}")
        self.logger.info(f"🏛️ Utilisateurs: {len(set(self.get_all_members()))}")
        self.logger.info("🏛️" + "="*50)
        
        # Définition de l'activité
        activity_text = self.config.get('bot.activity', 'Gardien de l\'ordre 🏛️')
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=activity_text
            ),
            status=discord.Status.online
        )
        
        self.logger.info("⚖️ « La justice est la vérité en action »")
    
    async def on_guild_join(self, guild):
        """Événement lors de l'ajout à un nouveau serveur"""
        self.logger.info(f"🏛️ Themis-Bot a rejoint: {guild.name} (ID: {guild.id})")
        
        # Message de bienvenue dans le canal système
        if guild.system_channel:
            embed = discord.Embed(
                title="🏛️ Themis-Bot - Gardien de l'Ordre",
                description=(
                    "**« Il y a une loi que même les dieux ne sauraient briser sans causer la ruine : celle de l'ordre. »**\n\n"
                    "Salutations ! Je suis Themis-Bot, gardien de l'ordre et de la justice.\n"
                    "Ma mission est de veiller à ce que chaque canal soit utilisé selon sa destination.\n\n"
                    "🔧 Utilisez `!setup` pour configurer les règles de votre serveur.\n"
                    "📋 Utilisez `!help` pour voir toutes mes commandes."
                ),
                color=0x9932CC
            )
            embed.set_thumbnail(url=self.user.avatar.url if self.user and self.user.avatar else None)
            
            try:
                await guild.system_channel.send(embed=embed)
            except discord.Forbidden:
                self.logger.warning(f"Impossible d'envoyer le message de bienvenue dans {guild.name}")
    
    async def on_message(self, message):
        """Traitement des messages pour la modération automatique"""
        # Ignorer les messages du bot et les DM
        if message.author.bot or not message.guild:
            return
        
        # Vérifier si la modération automatique est activée
        if not self.config.get('moderation.auto_delete', True):
            await self.process_commands(message)
            return
        
        # Analyser le message selon les règles
        await self.moderate_message(message)
        
        # Traiter les commandes
        await self.process_commands(message)
    
    async def moderate_message(self, message):
        """Analyse et modère un message selon les règles définies"""
        try:
            channel_name = message.channel.name.lower()
            content = message.content.lower()
            
            # Récupérer les règles pour ce canal
            channel_rules = self.rules.get('channel_rules', {})
            
            for rule_channel, rules in channel_rules.items():
                if rule_channel in channel_name:
                    # Vérifier les mots-clés interdits
                    forbidden = rules.get('forbidden_keywords', [])
                    if any(keyword in content for keyword in forbidden):
                        await self.handle_violation(message, rules, 'forbidden_keyword')
                        return
                    
                    # Vérifier les mots-clés requis (si définis)
                    required = rules.get('required_keywords', [])
                    if required and not any(keyword in content for keyword in required):
                        await self.handle_violation(message, rules, 'missing_keyword')
                        return
                    
                    # Vérifier les restrictions de rôle
                    role_restrictions = rules.get('role_restrictions', [])
                    if role_restrictions:
                        user_roles = [role.name.lower() for role in message.author.roles]
                        if not any(role in user_roles for role in role_restrictions):
                            await self.handle_violation(message, rules, 'role_restriction')
                            return
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la modération: {e}")
    
    async def handle_violation(self, message, rules, violation_type):
        """Gère une violation des règles"""
        try:
            # Supprimer le message offensant
            await message.delete()
            self.stats['messages_moderated'] += 1
            
            # Créer l'embed d'avertissement
            embed = discord.Embed(
                title="⚖️ Violation de l'Ordre Détectée",
                description=rules.get('redirect_message', 'Message inapproprié pour ce canal.'),
                color=0xFF6B6B
            )
            embed.add_field(
                name="🏛️ Rappel de Thémis",
                value="« Chaque canal est un temple, un sanctuaire dédié à une idée, une vérité. »",
                inline=False
            )
            embed.set_footer(text=f"Utilisateur: {message.author.display_name}")
            
            # Envoyer l'avertissement
            warning_msg = await message.channel.send(
                f"{message.author.mention}",
                embed=embed,
                delete_after=30
            )
            
            self.stats['warnings_issued'] += 1
            
            # Log de l'action
            self.logger.info(
                f"⚖️ Message modéré - {message.author} dans #{message.channel.name} "
                f"({violation_type})"
            )
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la gestion de violation: {e}")
    
    async def on_command_error(self, ctx, error):
        """Gestion des erreurs de commandes"""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Vous n'avez pas les permissions nécessaires.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ Je n'ai pas les permissions nécessaires.")
        else:
            self.logger.error(f"Erreur de commande: {error}")
            await ctx.send("❌ Une erreur inattendue s'est produite.")
    
    async def close(self):
        """Fermeture propre du bot"""
        self.logger.info("🏛️ Fermeture de Themis-Bot...")
        await super().close()
