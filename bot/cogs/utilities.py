"""
🔧 Module Utilitaires pour Themis-Bot
Commandes slash d'information et d'utilité
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from datetime import datetime
from typing import Optional

class UtilitiesCog(commands.Cog):
    """Module de commandes slash utilitaires"""
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
    
    @app_commands.command(name="userinfo", description="👤 Affiche les informations d'un utilisateur")
    @app_commands.describe(user="L'utilisateur à examiner (optionnel)")
    async def userinfo(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        """Affiche les informations détaillées d'un utilisateur"""
        
        # Si aucun utilisateur spécifié, utiliser l'auteur de la commande
        target_user = user or interaction.user
        
        # Vérifier que c'est bien un membre du serveur
        if not isinstance(target_user, discord.Member):
            await interaction.response.send_message("❌ Utilisateur non trouvé sur ce serveur.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"👤 Profil de {target_user.display_name}",
            color=target_user.color if target_user.color != discord.Color.default() else 0x3498DB
        )
        
        # Avatar
        embed.set_thumbnail(url=target_user.display_avatar.url)
        
        # Informations de base
        embed.add_field(
            name="🏷️ Identité",
            value=(
                f"**Nom:** {target_user.name}\n"
                f"**Surnom:** {target_user.display_name}\n"
                f"**ID:** {target_user.id}\n"
                f"**Bot:** {'Oui' if target_user.bot else 'Non'}"
            ),
            inline=True
        )
        
        # Dates importantes
        created_at = target_user.created_at.strftime("%d/%m/%Y à %H:%M")
        joined_at = target_user.joined_at.strftime("%d/%m/%Y à %H:%M") if target_user.joined_at else "Inconnue"
        
        embed.add_field(
            name="📅 Dates",
            value=(
                f"**Création:** {created_at}\n"
                f"**Arrivée:** {joined_at}"
            ),
            inline=True
        )
        
        # Statut et activité
        status_emoji = {
            'online': '🟢',
            'idle': '🟡', 
            'dnd': '🔴',
            'offline': '⚫'
        }
        
        status_text = f"{status_emoji.get(str(target_user.status), '❓')} {str(target_user.status).title()}"
        activity_text = "Aucune"
        
        if target_user.activity:
            if target_user.activity.type == discord.ActivityType.playing:
                activity_text = f"🎮 {target_user.activity.name}"
            elif target_user.activity.type == discord.ActivityType.listening:
                activity_text = f"🎵 {target_user.activity.name}"
            elif target_user.activity.type == discord.ActivityType.watching:
                activity_text = f"📺 {target_user.activity.name}"
            else:
                activity_text = f"✨ {target_user.activity.name}"
        
        embed.add_field(
            name="🎭 Activité",
            value=(
                f"**Statut:** {status_text}\n"
                f"**Activité:** {activity_text}"
            ),
            inline=False
        )
        
        # Rôles (limiter à 10 rôles pour éviter les messages trop longs)
        roles = [role.mention for role in target_user.roles[1:]]  # Exclure @everyone
        if len(roles) > 10:
            roles_text = ", ".join(roles[:10]) + f"... (+{len(roles)-10})"
        elif roles:
            roles_text = ", ".join(roles)
        else:
            roles_text = "Aucun rôle"
        
        embed.add_field(
            name=f"🎭 Rôles ({len(target_user.roles)-1})",
            value=roles_text,
            inline=False
        )
        
        # Permissions notables
        perms = target_user.guild_permissions
        notable_perms = []
        
        perm_names = {
            'administrator': '👑 Administrateur',
            'manage_guild': '⚙️ Gérer le serveur',
            'manage_channels': '📺 Gérer les canaux',
            'manage_roles': '🎭 Gérer les rôles',
            'ban_members': '🔨 Bannir',
            'kick_members': '👢 Expulser',
            'manage_messages': '📝 Gérer les messages',
            'moderate_members': '🔇 Modérer les membres'
        }
        
        for perm, emoji_name in perm_names.items():
            if getattr(perms, perm, False):
                notable_perms.append(emoji_name)
        
        if notable_perms:
            embed.add_field(
                name="🛡️ Permissions Notables",
                value=", ".join(notable_perms),
                inline=False
            )
        
        embed.set_footer(text=f"Examiné par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
        self.logger.info(f"👤 {interaction.user} a consulté le profil de {target_user}")
    
    @app_commands.command(name="serverinfo", description="🏛️ Affiche les informations du serveur")
    async def serverinfo(self, interaction: discord.Interaction):
        """Affiche les informations détaillées du serveur"""
        
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message("❌ Erreur: Impossible d'accéder aux informations du serveur.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"🏛️ {guild.name}",
            description=guild.description or "Aucune description",
            color=0x9932CC
        )
        
        # Icône du serveur
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        # Propriétaire
        owner_text = f"{guild.owner.mention} ({guild.owner})" if guild.owner else "Inconnu"
        
        # Informations générales
        embed.add_field(
            name="📋 Informations Générales",
            value=(
                f"**Propriétaire:** {owner_text}\n"
                f"**Créé le:** {guild.created_at.strftime('%d/%m/%Y')}\n"
                f"**ID:** {guild.id}\n"
                f"**Région:** {guild.preferred_locale}"
            ),
            inline=True
        )
        
        # Statistiques
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        embed.add_field(
            name="📊 Statistiques",
            value=(
                f"**Membres:** {guild.member_count}\n"
                f"**Rôles:** {len(guild.roles)}\n"
                f"**Canaux:** {text_channels + voice_channels}\n"
                f"**Catégories:** {categories}"
            ),
            inline=True
        )
        
        # Détail des canaux
        embed.add_field(
            name="📺 Canaux",
            value=(
                f"💬 Texte: {text_channels}\n"
                f"🔊 Vocal: {voice_channels}\n"
                f"📁 Catégories: {categories}"
            ),
            inline=True
        )
        
        # Niveau de vérification
        verification_levels = {
            discord.VerificationLevel.none: "🔓 Aucune",
            discord.VerificationLevel.low: "🔒 Faible", 
            discord.VerificationLevel.medium: "🔐 Moyenne",
            discord.VerificationLevel.high: "🛡️ Élevée",
            discord.VerificationLevel.highest: "👑 Maximale"
        }
        
        # Fonctionnalités
        features = []
        feature_names = {
            'VERIFIED': '✅ Vérifié',
            'PARTNERED': '🤝 Partenaire',
            'COMMUNITY': '🌟 Communauté',
            'DISCOVERABLE': '🔍 Découvrable',
            'WELCOMESCREEN_ENABLED': '👋 Écran d\'accueil',
            'BANNER': '🎨 Bannière',
            'VANITY_URL': '🔗 URL personnalisée'
        }
        
        for feature in guild.features:
            if feature in feature_names:
                features.append(feature_names[feature])
        
        embed.add_field(
            name="🔐 Sécurité",
            value=(
                f"**Vérification:** {verification_levels.get(guild.verification_level, 'Inconnue')}\n"
                f"**Filtre explicit:** {guild.explicit_content_filter.name.title()}"
            ),
            inline=False
        )
        
        if features:
            embed.add_field(
                name="✨ Fonctionnalités",
                value=", ".join(features),
                inline=False
            )
        
        # Boost
        if guild.premium_tier > 0:
            embed.add_field(
                name="🚀 Nitro Boost",
                value=(
                    f"**Niveau:** {guild.premium_tier}\n"
                    f"**Boosts:** {guild.premium_subscription_count}"
                ),
                inline=True
            )
        
        embed.set_footer(text=f"Consulté par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
        self.logger.info(f"🏛️ {interaction.user} a consulté les infos du serveur {guild.name}")
    
    @app_commands.command(name="ping", description="🏓 Affiche la latence du bot")
    async def ping(self, interaction: discord.Interaction):
        """Affiche la latence du bot"""
        
        # Calculer la latence avant de répondre
        latency = round(self.bot.latency * 1000)
        
        embed = discord.Embed(
            title="🏓 Pong !",
            color=0x00FF00 if latency < 100 else 0xFFA500 if latency < 200 else 0xFF0000
        )
        
        embed.add_field(
            name="📡 Latence WebSocket",
            value=f"**{latency}ms**",
            inline=True
        )
        
        # Déterminer la qualité de la connexion
        if latency < 50:
            quality = "🟢 Excellente"
        elif latency < 100:
            quality = "🟡 Bonne"
        elif latency < 200:
            quality = "🟠 Correcte"
        else:
            quality = "🔴 Lente"
        
        embed.add_field(
            name="📶 Qualité",
            value=quality,
            inline=True
        )
        
        embed.set_footer(text="Que la vitesse de Hermès soit avec nous !")
        
        await interaction.response.send_message(embed=embed)
        self.logger.info(f"🏓 {interaction.user} a testé la latence ({latency}ms)")
    
    @app_commands.command(name="avatar", description="🖼️ Affiche l'avatar d'un utilisateur")
    @app_commands.describe(user="L'utilisateur dont afficher l'avatar (optionnel)")
    async def avatar(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        """Affiche l'avatar d'un utilisateur en haute résolution"""
        
        # Si aucun utilisateur spécifié, utiliser l'auteur
        target_user = user or interaction.user
        
        # Vérifier que c'est bien un membre du serveur
        if not isinstance(target_user, discord.Member):
            await interaction.response.send_message("❌ Utilisateur non trouvé sur ce serveur.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"🖼️ Avatar de {target_user.display_name}",
            color=target_user.color if target_user.color != discord.Color.default() else 0x3498DB
        )
        
        # Avatar en haute résolution
        avatar_url = target_user.display_avatar.url
        embed.set_image(url=avatar_url)
        
        # Liens de téléchargement
        embed.add_field(
            name="📥 Télécharger",
            value=(
                f"[PNG]({target_user.display_avatar.with_format('png').url}) | "
                f"[JPG]({target_user.display_avatar.with_format('jpg').url}) | "
                f"[WEBP]({target_user.display_avatar.with_format('webp').url})"
            ),
            inline=False
        )
        
        embed.set_footer(text=f"Demandé par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
        self.logger.info(f"🖼️ {interaction.user} a consulté l'avatar de {target_user}")

async def setup(bot):
    """Charge le module utilitaires"""
    await bot.add_cog(UtilitiesCog(bot))
