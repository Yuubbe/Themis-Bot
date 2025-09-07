import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import json
import aiofiles
from datetime import datetime
import uuid
import os
from typing import Optional, Union

class TicketSystem(commands.Cog):
    """Système complet de tickets et vérification d'identité pour Themis-Bot"""
    
    def __init__(self, bot):
        self.bot = bot
        self.tickets_dir = "data/tickets/"
        self.tickets_data = {}
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Créer les dossiers nécessaires"""
        os.makedirs(self.tickets_dir, exist_ok=True)
        os.makedirs("data/identity_photos/", exist_ok=True)
        
    async def cog_load(self):
        """Charger les données des tickets au démarrage"""
        await self.load_tickets_data()
        
    async def load_tickets_data(self):
        """Charger les données des tickets depuis le fichier"""
        try:
            async with aiofiles.open("data/tickets_data.json", "r", encoding="utf-8") as f:
                content = await f.read()
                self.tickets_data = json.loads(content)
        except FileNotFoundError:
            self.tickets_data = {"active_tickets": {}, "verification_queue": {}}
            await self.save_tickets_data()
            
    async def save_tickets_data(self):
        """Sauvegarder les données des tickets"""
        try:
            async with aiofiles.open("data/tickets_data.json", "w", encoding="utf-8") as f:
                await f.write(json.dumps(self.tickets_data, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"Erreur sauvegarde tickets: {e}")

    @app_commands.command(name="ticket", description="🎫 Créer un ticket de vérification d'identité")
    @app_commands.describe(
        raison="Motif de votre demande de vérification",
        age="Votre âge (obligatoire pour la vérification)"
    )
    async def create_ticket(self, interaction: discord.Interaction, raison: str = "Vérification d'identité", age: Optional[int] = None):
        """Créer un nouveau ticket de vérification"""
        
        # Vérifications de sécurité
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur !", ephemeral=True)
            return
            
        if not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message("❌ Erreur de type d'utilisateur !", ephemeral=True)
            return
        
        # Vérifier si l'utilisateur a déjà un ticket actif
        user_id = str(interaction.user.id)
        if user_id in self.tickets_data.get("active_tickets", {}):
            await interaction.response.send_message(
                "❌ Vous avez déjà un ticket actif ! Fermez-le avant d'en créer un nouveau.",
                ephemeral=True
            )
            return
            
        # Vérifier si l'utilisateur est déjà vérifié
        citoyen_role = discord.utils.get(interaction.guild.roles, name="🎭 Citoyen")
        if citoyen_role and citoyen_role in interaction.user.roles:
            await interaction.response.send_message(
                "✅ Vous êtes déjà vérifié en tant que citoyen !",
                ephemeral=True
            )
            return
            
        # Vérifier l'âge si fourni
        if age is not None and age < 13:
            await interaction.response.send_message(
                "❌ Vous devez avoir au moins 13 ans pour rejoindre ce serveur Discord.",
                ephemeral=True
            )
            return
            
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Générer un ID unique pour le ticket
            ticket_id = str(uuid.uuid4())[:8]
            
            # Créer le canal de ticket
            guild = interaction.guild
            
            # Permissions pour le canal de ticket
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(
                    view_channel=True, send_messages=True, attach_files=True,
                    read_message_history=True
                ),
                self.bot.user: discord.PermissionOverwrite(
                    view_channel=True, send_messages=True, manage_messages=True
                )
            }
            
            # Ajouter les permissions pour les modérateurs
            for role_name in ["🏛️ Gardien Suprême", "⚖️ Magistrat", "🛡️ Sentinel"]:
                role = discord.utils.get(guild.roles, name=role_name)
                if role:
                    overwrites[role] = discord.PermissionOverwrite(
                        view_channel=True, send_messages=True, manage_messages=True
                    )
            
            # Trouver ou créer la catégorie tickets
            category = discord.utils.get(guild.categories, name="🎫 TICKETS")
            if not category:
                category = await guild.create_category(
                    "🎫 TICKETS",
                    overwrites={
                        guild.default_role: discord.PermissionOverwrite(view_channel=False)
                    }
                )
            
            # Créer le canal
            channel = await guild.create_text_channel(
                f"ticket-{interaction.user.name}-{ticket_id}",
                category=category,
                overwrites=overwrites,
                topic=f"Ticket de vérification pour {interaction.user.display_name}"
            )
            
            # Créer l'embed d'accueil du ticket
            welcome_embed = discord.Embed(
                title="🎫 Nouveau Ticket de Vérification",
                description=f"**Bienvenue {interaction.user.mention} !**\n\nVotre ticket a été créé avec succès.",
                color=0x3498DB,
                timestamp=datetime.utcnow()
            )
            
            welcome_embed.add_field(
                name="📋 Informations du ticket",
                value=f"**ID:** `{ticket_id}`\n**Motif:** {raison}\n**Âge déclaré:** {age if age else 'Non précisé'}",
                inline=False
            )
            
            welcome_embed.add_field(
                name="📸 Processus de vérification",
                value=(
                    "**Étapes à suivre :**\n"
                    "1️⃣ Envoyez une photo de votre pièce d'identité\n"
                    "2️⃣ **IMPORTANT:** Masquez TOUT sauf votre âge/date de naissance\n"
                    "3️⃣ Attendez la validation par un modérateur\n"
                    "4️⃣ Recevez votre rôle 'Citoyen' une fois approuvé"
                ),
                inline=False
            )
            
            welcome_embed.add_field(
                name="⚠️ Règles importantes",
                value=(
                    "• Ne montrez QUE votre âge sur la pièce d'identité\n"
                    "• Masquez nom, adresse, numéro, photo, etc.\n"
                    "• Photo claire et lisible obligatoire\n"
                    "• Respectez les modérateurs\n"
                    "• Un seul ticket par personne"
                ),
                inline=False
            )
            
            welcome_embed.set_footer(
                text="Utilisez les boutons ci-dessous pour interagir avec votre ticket"
            )
            
            # Créer les boutons d'interaction
            view = TicketView(self.bot, ticket_id, user_id)
            
            message = await channel.send(embed=welcome_embed, view=view)
            
            # Enregistrer les données du ticket
            self.tickets_data.setdefault("active_tickets", {})[user_id] = {
                "ticket_id": ticket_id,
                "channel_id": channel.id,
                "user_id": interaction.user.id,
                "created_at": datetime.utcnow().isoformat(),
                "reason": raison,
                "age": age,
                "status": "en_attente",
                "welcome_message_id": message.id
            }
            
            await self.save_tickets_data()
            
            # Log dans le canal de logs si disponible
            logs_channel = discord.utils.get(guild.text_channels, name="🎫-logs-tickets")
            if logs_channel and isinstance(logs_channel, discord.TextChannel):
                log_embed = discord.Embed(
                    title="📝 Nouveau Ticket Créé",
                    color=0x00FF00,
                    timestamp=datetime.utcnow()
                )
                log_embed.add_field(name="Utilisateur", value=f"{interaction.user.mention} ({interaction.user.id})", inline=True)
                log_embed.add_field(name="Canal", value=channel.mention, inline=True)
                log_embed.add_field(name="ID Ticket", value=f"`{ticket_id}`", inline=True)
                log_embed.add_field(name="Motif", value=raison, inline=False)
                
                await logs_channel.send(embed=log_embed)
            
            await interaction.followup.send(
                f"✅ Votre ticket a été créé ! Rendez-vous dans {channel.mention}",
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.followup.send(
                f"❌ Erreur lors de la création du ticket : {str(e)}",
                ephemeral=True
            )

    @app_commands.command(name="verify-identity", description="🔍 Valider l'identité d'un utilisateur (Staff uniquement)")
    @app_commands.describe(
        user="Utilisateur à vérifier",
        approved="Approuver ou rejeter la vérification"
    )
    async def verify_identity(self, interaction: discord.Interaction, user: discord.Member, approved: bool):
        """Valider ou rejeter une vérification d'identité"""
        
        # Vérifications de sécurité
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans un serveur !", ephemeral=True)
            return
            
        if not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message("❌ Erreur de type d'utilisateur !", ephemeral=True)
            return
        
        # Vérifier les permissions
        required_roles = ["🏛️ Gardien Suprême", "⚖️ Magistrat", "🛡️ Sentinel"]
        if not any(role.name in required_roles for role in interaction.user.roles):
            await interaction.response.send_message(
                "❌ Vous n'avez pas les permissions pour effectuer cette action !",
                ephemeral=True
            )
            return
            
        user_id = str(user.id)
        
        # Vérifier si l'utilisateur a un ticket actif
        if user_id not in self.tickets_data.get("active_tickets", {}):
            await interaction.response.send_message(
                f"❌ {user.mention} n'a pas de ticket actif !",
                ephemeral=True
            )
            return
            
        await interaction.response.defer()
        
        try:
            ticket_info = self.tickets_data["active_tickets"][user_id]
            
            if approved:
                # Approuver la vérification
                citoyen_role = discord.utils.get(interaction.guild.roles, name="🎭 Citoyen")
                en_attente_role = discord.utils.get(interaction.guild.roles, name="🎫 En Attente")
                
                if citoyen_role:
                    await user.add_roles(citoyen_role, reason=f"Vérification approuvée par {interaction.user}")
                    
                if en_attente_role and en_attente_role in user.roles:
                    await user.remove_roles(en_attente_role, reason="Vérification réussie")
                
                # Envoyer un message de confirmation dans le ticket
                channel = self.bot.get_channel(ticket_info["channel_id"])
                if channel:
                    success_embed = discord.Embed(
                        title="✅ Vérification Approuvée !",
                        description=f"Félicitations {user.mention} ! Votre identité a été vérifiée avec succès.",
                        color=0x00FF00,
                        timestamp=datetime.utcnow()
                    )
                    success_embed.add_field(
                        name="🎭 Nouveau statut",
                        value="Vous êtes maintenant un **Citoyen** vérifié !\nVous avez accès à tous les canaux du serveur.",
                        inline=False
                    )
                    success_embed.add_field(
                        name="📋 Prochaines étapes",
                        value="• Lisez les règles dans <#rules-channel>\n• Présentez-vous si vous le souhaitez\n• Profitez de votre séjour !",
                        inline=False
                    )
                    success_embed.set_footer(text=f"Vérifié par {interaction.user.display_name}")
                    
                    await channel.send(embed=success_embed)
                    await asyncio.sleep(10)  # Laisser le temps de lire
                    
                    # Fermer le ticket automatiquement après approbation
                    await self.close_ticket_internal(channel, interaction.user, "Vérification réussie - fermeture automatique")
                
                result_msg = f"✅ Vérification de {user.mention} **approuvée** avec succès !"
                
            else:
                # Rejeter la vérification
                channel = self.bot.get_channel(ticket_info["channel_id"])
                if channel:
                    reject_embed = discord.Embed(
                        title="❌ Vérification Rejetée",
                        description=f"Désolé {user.mention}, votre vérification a été rejetée.",
                        color=0xFF0000,
                        timestamp=datetime.utcnow()
                    )
                    reject_embed.add_field(
                        name="🔄 Que faire maintenant ?",
                        value=(
                            "• Vérifiez que votre photo est claire\n"
                            "• Assurez-vous que seul votre âge est visible\n"
                            "• Contactez un modérateur pour plus d'informations\n"
                            "• Vous pouvez soumettre une nouvelle photo"
                        ),
                        inline=False
                    )
                    reject_embed.set_footer(text=f"Rejeté par {interaction.user.display_name}")
                    
                    await channel.send(embed=reject_embed)
                
                result_msg = f"❌ Vérification de {user.mention} **rejetée**."
            
            # Log de l'action
            if interaction.guild:
                logs_channel = discord.utils.get(interaction.guild.text_channels, name="🎫-logs-tickets")
                if logs_channel and isinstance(logs_channel, discord.TextChannel):
                    log_embed = discord.Embed(
                        title="🔍 Vérification Traitée",
                        color=0x00FF00 if approved else 0xFF0000,
                        timestamp=datetime.utcnow()
                    )
                    log_embed.add_field(name="Utilisateur", value=f"{user.mention} ({user.id})", inline=True)
                    log_embed.add_field(name="Modérateur", value=f"{interaction.user.mention}", inline=True)
                    log_embed.add_field(name="Résultat", value="✅ Approuvé" if approved else "❌ Rejeté", inline=True)
                    log_embed.add_field(name="Ticket ID", value=f"`{ticket_info['ticket_id']}`", inline=False)
                    
                    await logs_channel.send(embed=log_embed)
            
            await interaction.followup.send(result_msg)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur lors de la vérification : {str(e)}")

    async def close_ticket_internal(self, channel, closer, reason="Ticket fermé"):
        """Fonction interne pour fermer un ticket"""
        try:
            # Trouver l'utilisateur du ticket
            user_id = None
            for uid, ticket_info in self.tickets_data.get("active_tickets", {}).items():
                if ticket_info["channel_id"] == channel.id:
                    user_id = uid
                    break
                    
            if user_id:
                # Créer un transcript du ticket
                transcript = await self.create_transcript(channel)
                
                # Sauvegarder le transcript
                transcript_path = f"{self.tickets_dir}transcript_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                async with aiofiles.open(transcript_path, "w", encoding="utf-8") as f:
                    await f.write(transcript)
                
                # Envoyer le transcript aux logs
                logs_channel = discord.utils.get(channel.guild.channels, name="🎫-logs-tickets")
                if logs_channel:
                    close_embed = discord.Embed(
                        title="🔒 Ticket Fermé",
                        color=0xFF9900,
                        timestamp=datetime.utcnow()
                    )
                    close_embed.add_field(name="Utilisateur", value=f"<@{user_id}>", inline=True)
                    close_embed.add_field(name="Fermé par", value=closer.mention, inline=True)
                    close_embed.add_field(name="Raison", value=reason, inline=False)
                    
                    try:
                        with open(transcript_path, "rb") as f:
                            transcript_file = discord.File(f, filename=f"transcript_{user_id}.txt")
                            await logs_channel.send(embed=close_embed, file=transcript_file)
                    except:
                        await logs_channel.send(embed=close_embed)
                
                # Supprimer des données actives
                if user_id in self.tickets_data.get("active_tickets", {}):
                    del self.tickets_data["active_tickets"][user_id]
                    await self.save_tickets_data()
            
            # Supprimer le canal
            await channel.delete(reason=reason)
            
        except Exception as e:
            print(f"Erreur fermeture ticket: {e}")

    async def create_transcript(self, channel):
        """Créer un transcript du canal"""
        transcript = f"=== TRANSCRIPT DU TICKET ===\n"
        transcript += f"Canal: #{channel.name}\n"
        transcript += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        transcript += f"=" * 50 + "\n\n"
        
        try:
            async for message in channel.history(limit=None, oldest_first=True):
                timestamp = message.created_at.strftime('%Y-%m-%d %H:%M:%S')
                author = f"{message.author.display_name} ({message.author.id})"
                content = message.content or "[Message sans contenu]"
                
                transcript += f"[{timestamp}] {author}: {content}\n"
                
                if message.attachments:
                    for attachment in message.attachments:
                        transcript += f"  📎 Pièce jointe: {attachment.filename} ({attachment.url})\n"
                
                if message.embeds:
                    for embed in message.embeds:
                        transcript += f"  📋 Embed: {embed.title or 'Sans titre'}\n"
                        
        except Exception as e:
            transcript += f"\nErreur lors de la création du transcript: {e}\n"
            
        return transcript

class TicketView(discord.ui.View):
    """Vue avec boutons pour interagir avec les tickets"""
    
    def __init__(self, bot, ticket_id, user_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.ticket_id = ticket_id
        self.user_id = user_id
        
    @discord.ui.button(label="📸 J'ai envoyé ma photo", style=discord.ButtonStyle.green, emoji="📸")
    async def photo_sent(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌ Seul le créateur du ticket peut utiliser ce bouton !", ephemeral=True)
            return
            
        embed = discord.Embed(
            title="📸 Photo reçue !",
            description="Merci ! Un modérateur va examiner votre photo sous peu.",
            color=0xFFA500
        )
        embed.add_field(
            name="⏳ En attente",
            value="Un membre du staff va vérifier votre document d'identité. Patientez svp.",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
        
        # Notifier les modérateurs
        if interaction.guild:
            for role_name in ["🏛️ Gardien Suprême", "⚖️ Magistrat", "🛡️ Sentinel"]:
                role = discord.utils.get(interaction.guild.roles, name=role_name)
                if role:
                    await interaction.followup.send(
                        f"🔔 {role.mention} - Nouvelle photo d'identité à vérifier dans ce ticket !",
                        ephemeral=False
                    )
                    break
    
    @discord.ui.button(label="🔒 Fermer le ticket", style=discord.ButtonStyle.red, emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Vérifier les permissions
        if str(interaction.user.id) != self.user_id:
            required_roles = ["🏛️ Gardien Suprême", "⚖️ Magistrat", "🛡️ Sentinel"]
            # Vérifier que c'est un membre et qu'il a les bonnes permissions
            if not isinstance(interaction.user, discord.Member) or not any(role.name in required_roles for role in interaction.user.roles):
                await interaction.response.send_message("❌ Vous n'avez pas les permissions pour fermer ce ticket !", ephemeral=True)
                return
        
        await interaction.response.send_message("🔒 Fermeture du ticket en cours...", ephemeral=True)
        
        ticket_system = self.bot.get_cog('TicketSystem')
        if ticket_system:
            await ticket_system.close_ticket_internal(
                interaction.channel, 
                interaction.user, 
                f"Fermé par {interaction.user.display_name}"
            )
    
    @discord.ui.button(label="❓ Aide", style=discord.ButtonStyle.secondary, emoji="❓")
    async def help_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        help_embed = discord.Embed(
            title="❓ Aide - Vérification d'Identité",
            description="Guide pour réussir votre vérification",
            color=0x3498DB
        )
        
        help_embed.add_field(
            name="📋 Documents acceptés",
            value="• Carte d'identité\n• Passeport\n• Permis de conduire\n• Carte étudiante (avec âge)",
            inline=True
        )
        
        help_embed.add_field(
            name="✅ Comment masquer les infos",
            value="• Utilisez du papier/post-it\n• Éditez numériquement\n• Utilisez un marqueur noir\n• Laissez SEULEMENT l'âge visible",
            inline=True
        )
        
        help_embed.add_field(
            name="❌ Erreurs communes",
            value="• Photo floue\n• Informations personnelles visibles\n• Document non officiel\n• Âge non visible",
            inline=False
        )
        
        await interaction.response.send_message(embed=help_embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
