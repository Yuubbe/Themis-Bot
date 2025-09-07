"""
🏛️ Module de Modération pour Themis-Bot
Commandes slash pour la gestion de l'ordre et de la discipline
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from typing import Optional
from datetime import timedelta

class ModerationCog(commands.Cog):
    """Module de commandes slash de modération"""
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
    
    @app_commands.command(name="warn", description="⚖️ Avertit un utilisateur pour violation des règles")
    @app_commands.describe(
        member="L'utilisateur à avertir",
        reason="La raison de l'avertissement"
    )
    @app_commands.default_permissions(manage_messages=True)
    async def warn_user(self, interaction: discord.Interaction, member: discord.Member, reason: str = "Violation de l'ordre"):
        """Avertit un utilisateur pour violation des règles"""
        
        embed = discord.Embed(
            title="⚖️ Avertissement Officiel",
            description=f"**{member.mention}** a reçu un avertissement.",
            color=0xFFA500
        )
        embed.add_field(name="📋 Raison", value=reason, inline=False)
        embed.add_field(
            name="🏛️ Rappel de Thémis", 
            value="« Prenez garde, car de tels actes ne mènent qu'à la confusion »",
            inline=False
        )
        embed.set_footer(text=f"Modérateur: {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
        self.logger.info(f"⚖️ {interaction.user} a averti {member} pour: {reason}")
    
    @app_commands.command(name="purge", description="🧹 Supprime un nombre de messages dans le canal")
    @app_commands.describe(amount="Nombre de messages à supprimer (max 100)")
    @app_commands.default_permissions(manage_messages=True)
    async def purge_messages(self, interaction: discord.Interaction, amount: int = 10):
        """Supprime un nombre de messages dans le canal"""
        
        if amount > 100:
            await interaction.response.send_message("❌ Je ne peux pas supprimer plus de 100 messages à la fois.", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        
        embed = discord.Embed(
            title="🧹 Purification du Temple",
            description=f"**{len(deleted)} messages** ont été purifiés de ce sanctuaire.",
            color=0x9932CC
        )
        embed.set_footer(text="L'ordre est restauré")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        self.logger.info(f"🧹 {interaction.user} a purgé {len(deleted)} messages dans #{interaction.channel.name}")
    
    @app_commands.command(name="timeout", description="⏰ Met un utilisateur en timeout pour réflexion")
    @app_commands.describe(
        member="L'utilisateur à mettre en timeout",
        duration="Durée en minutes (max 1440 = 24h)",
        reason="Raison du timeout"
    )
    @app_commands.default_permissions(moderate_members=True)
    async def timeout_user(self, interaction: discord.Interaction, member: discord.Member, duration: int = 5, reason: str = "Perturbation de l'ordre"):
        """Met un utilisateur en timeout"""
        
        if duration > 1440:
            await interaction.response.send_message("❌ La durée maximale est de 1440 minutes (24h).", ephemeral=True)
            return
        
        timeout_duration = timedelta(minutes=duration)
        
        try:
            await member.timeout(timeout_duration, reason=reason)
            
            embed = discord.Embed(
                title="⏰ Temps de Réflexion",
                description=f"**{member.mention}** doit méditer sur ses actes.",
                color=0xFF6B6B
            )
            embed.add_field(name="⏱️ Durée", value=f"{duration} minutes", inline=True)
            embed.add_field(name="📋 Raison", value=reason, inline=False)
            
            await interaction.response.send_message(embed=embed)
            self.logger.info(f"⏰ {interaction.user} a mis {member} en timeout pour {duration}min: {reason}")
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ Je n'ai pas les permissions pour mettre cet utilisateur en timeout.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur lors du timeout: {e}", ephemeral=True)
    
    @app_commands.command(name="rules", description="📜 Affiche les règles du serveur")
    async def show_rules(self, interaction: discord.Interaction):
        """Affiche les règles du serveur"""
        
        embed = discord.Embed(
            title="📜 Les Lois de l'Ordre",
            description="« Il y a une loi que même les dieux ne sauraient briser sans causer la ruine : celle de l'ordre. »",
            color=0x9932CC
        )
        
        embed.add_field(
            name="🏛️ Principe Fondamental",
            value="Chaque canal est un temple dédié à une vérité spécifique.",
            inline=False
        )
        
        # Règles par canal
        channel_rules = self.bot.rules.get('channel_rules', {})
        for channel, rules in channel_rules.items():
            redirect_msg = rules.get('redirect_message', 'Respectez la destination de ce canal.')
            embed.add_field(
                name=f"#{channel}",
                value=redirect_msg,
                inline=True
            )
        
        embed.set_footer(text="La sagesse de Thémis guide nos actions")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="stats", description="📊 Affiche les statistiques de modération")
    @app_commands.default_permissions(manage_guild=True)
    async def moderation_stats(self, interaction: discord.Interaction):
        """Affiche les statistiques de modération"""
        
        embed = discord.Embed(
            title="📊 Statistiques de Modération",
            description="Rapport sur l'état de l'ordre dans ce royaume",
            color=0x32CD32
        )
        
        embed.add_field(
            name="📝 Messages Modérés",
            value=f"{self.bot.stats['messages_moderated']}",
            inline=True
        )
        embed.add_field(
            name="⚠️ Avertissements",
            value=f"{self.bot.stats['warnings_issued']}",
            inline=True
        )
        embed.add_field(
            name="🔄 Redirections",
            value=f"{self.bot.stats['redirections']}",
            inline=True
        )
        
        embed.set_footer(text="L'ordre prévaut grâce à la vigilance")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    """Charge le module de modération"""
    await bot.add_cog(ModerationCog(bot))
