"""
🏛️ Module d'Administration pour Themis-Bot avec Permissions Automatiques
Commandes slash pour la configuration et gestion du bot avec permissions détaillées
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import logging
import asyncio
from datetime import datetime

class AdminCog(commands.Cog):
    """Module de commandes slash d'administration avec configuration automatique des permissions"""
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
    
    async def _apply_permissions(self, channel, permissions_dict, guild):
        """Applique les permissions détaillées à un canal"""
        for role_name, perms in permissions_dict.items():
            try:
                if role_name == "@everyone":
                    role = guild.default_role
                else:
                    role = discord.utils.get(guild.roles, name=role_name)
                
                if role:
                    overwrites = discord.PermissionOverwrite()
                    for perm_name, value in perms.items():
                        setattr(overwrites, perm_name, value)
                    
                    await channel.set_permissions(role, overwrite=overwrites)
                    await asyncio.sleep(0.2)  # Éviter le rate limiting
                    self.logger.info(f"✅ Permissions appliquées: {role_name} sur {channel.name}")
            except Exception as e:
                self.logger.error(f"❌ Erreur permission {role_name} sur {channel.name}: {e}")

    @app_commands.command(name="setup", description="🏛️ Configuration avancée du serveur avec permissions automatiques")
    @app_commands.default_permissions(administrator=True)
    async def setup_server(self, interaction: discord.Interaction):
        """Configuration complète du serveur avec création de canaux, rôles et permissions automatiques"""
        
        await interaction.response.defer()
        
        guild = interaction.guild
        if guild is None:
            await interaction.edit_original_response(content="❌ Erreur: Impossible d'accéder aux informations du serveur.")
            return
        
        setup_embed = discord.Embed(
            title="🏛️ Configuration Avancée du Royaume de Thémis",
            description="Mise en place de l'infrastructure divine avec permissions automatiques...",
            color=0x9932CC
        )
        
        created_roles = []
        created_channels = []
        created_categories = []
        errors = []
        
        try:
            # 1. Création des rôles de modération hiérarchiques
            setup_embed.add_field(
                name="⚡ Étape 1/4",
                value="Création de la hiérarchie divine...",
                inline=False
            )
            await interaction.edit_original_response(embed=setup_embed)
            
            # Rôles de modération hiérarchiques avec permissions détaillées
            roles_to_create = [
                {
                    "name": "🏛️ Gardien Suprême", 
                    "color": 0x9932CC, 
                    "permissions": discord.Permissions.all(),
                    "description": "Autorité suprême - Tous les pouvoirs"
                },
                {
                    "name": "⚖️ Magistrat", 
                    "color": 0xFF6B35, 
                    "permissions": discord.Permissions(
                        manage_messages=True, kick_members=True, ban_members=True, 
                        manage_channels=True, moderate_members=True, manage_roles=True,
                        view_audit_log=True, manage_nicknames=True
                    ),
                    "description": "Haute modération - Bans, kicks, gestion des canaux"
                },
                {
                    "name": "🛡️ Sentinel", 
                    "color": 0x3498DB, 
                    "permissions": discord.Permissions(
                        manage_messages=True, kick_members=True, moderate_members=True,
                        manage_nicknames=True, view_audit_log=True
                    ),
                    "description": "Modération standard - Messages, kicks, timeouts"
                },
                {
                    "name": "⚔️ Garde Élite", 
                    "color": 0x8B0000, 
                    "permissions": discord.Permissions(
                        manage_messages=True, moderate_members=True, view_audit_log=True
                    ),
                    "description": "Modération messages et timeouts uniquement"
                },
                {
                    "name": "🔍 Inspecteur", 
                    "color": 0x4B0082, 
                    "permissions": discord.Permissions(
                        view_audit_log=True, read_message_history=True
                    ),
                    "description": "Surveillance et rapports - Lecture seule"
                },
                {
                    "name": "📚 Sage", 
                    "color": 0x00FF7F, 
                    "permissions": discord.Permissions(
                        manage_messages=True, send_messages=True, embed_links=True,
                        attach_files=True, use_external_emojis=True
                    ),
                    "description": "Guide communautaire - Aide et support"
                },
                {
                    "name": "🎭 Animateur", 
                    "color": 0xFF1493, 
                    "permissions": discord.Permissions(
                        send_messages=True, embed_links=True, attach_files=True,
                        use_external_emojis=True, create_public_threads=True,
                        manage_threads=True
                    ),
                    "description": "Animation communautaire - Événements et activités"
                },
                {
                    "name": "👑 Citoyen d'Honneur", 
                    "color": 0xFFD700, 
                    "permissions": discord.Permissions(
                        send_messages=True, embed_links=True, attach_files=True,
                        use_external_emojis=True, add_reactions=True
                    ),
                    "description": "Membre de confiance - Privilèges étendus"
                },
                {
                    "name": "🎯 Spécialiste", 
                    "color": 0x32CD32, 
                    "permissions": discord.Permissions(
                        send_messages=True, embed_links=True, attach_files=True
                    ),
                    "description": "Expert dans un domaine spécifique"
                },
                {
                    "name": "🌟 Membre Actif", 
                    "color": 0x87CEEB, 
                    "permissions": discord.Permissions(
                        send_messages=True, attach_files=True, add_reactions=True
                    ),
                    "description": "Membre engagé de la communauté"
                },
                {
                    "name": "🎭 Membre", 
                    "color": 0x95A5A6, 
                    "permissions": discord.Permissions(
                        send_messages=True, read_message_history=True, add_reactions=True
                    ),
                    "description": "Membre standard de la communauté"
                },
                {
                    "name": "👥 Invité", 
                    "color": 0x2F3136, 
                    "permissions": discord.Permissions(
                        send_messages=True, read_message_history=True
                    ),
                    "description": "Accès limité - En observation"
                }
            ]
            
            for role_data in roles_to_create:
                try:
                    role = await guild.create_role(
                        name=role_data["name"],
                        color=discord.Color(role_data["color"]),
                        permissions=role_data["permissions"],
                        reason="Configuration automatique par Themis-Bot"
                    )
                    created_roles.append(role.name)
                    await asyncio.sleep(0.5)  # Éviter les rate limits
                except Exception as e:
                    errors.append(f"Rôle {role_data['name']}: {str(e)}")
            
            # 2. Création des catégories et canaux avec permissions automatiques
            setup_embed.clear_fields()
            setup_embed.add_field(
                name="⚡ Étape 2/4",
                value="Construction de l'architecture divine avec permissions...",
                inline=False
            )
            await interaction.edit_original_response(embed=setup_embed)
            
            # Structure des canaux avec permissions détaillées par rôle
            channel_structure = {
                "🏛️ LE PANTHÉON": {
                    "type": "category",
                    "permissions": {
                        "@everyone": {"view_channel": True, "send_messages": False},
                        "🏛️ Gardien Suprême": {"view_channel": True, "send_messages": True, "manage_messages": True},
                        "⚖️ Magistrat": {"view_channel": True, "send_messages": True, "manage_messages": True}
                    },
                    "channels": [
                        {
                            "name": "📜-règles-sacrées", 
                            "type": "text", 
                            "topic": "Les lois divines qui régissent ce royaume",
                            "permissions": {
                                "@everyone": {"view_channel": True, "send_messages": False, "add_reactions": True},
                                "🏛️ Gardien Suprême": {"send_messages": True, "manage_messages": True},
                                "⚖️ Magistrat": {"send_messages": True, "manage_messages": True},
                                "📚 Sage": {"send_messages": True}
                            }
                        },
                        {
                            "name": "📢-annonces-royales", 
                            "type": "text", 
                            "topic": "Proclamations officielles du royaume",
                            "permissions": {
                                "@everyone": {"view_channel": True, "send_messages": False, "add_reactions": True},
                                "🏛️ Gardien Suprême": {"send_messages": True, "manage_messages": True},
                                "⚖️ Magistrat": {"send_messages": True},
                                "🛡️ Sentinel": {"send_messages": True},
                                "🎭 Animateur": {"send_messages": True}
                            }
                        },
                        {
                            "name": "🎉-événements", 
                            "type": "text", 
                            "topic": "Célébrations et événements communautaires",
                            "permissions": {
                                "@everyone": {"view_channel": True, "send_messages": True, "add_reactions": True},
                                "🎭 Animateur": {"manage_messages": True, "manage_threads": True},
                                "📚 Sage": {"manage_messages": True},
                                "👑 Citoyen d'Honneur": {"create_public_threads": True}
                            }
                        }
                    ]
                },
                "💬 AGORA PUBLIQUE": {
                    "type": "category",
                    "permissions": {
                        "@everyone": {"view_channel": True, "send_messages": True},
                        "👥 Invité": {"view_channel": True, "send_messages": True, "embed_links": False},
                        "🛡️ Sentinel": {"manage_messages": True}
                    },
                    "channels": [
                        {
                            "name": "💬-discussion-générale", 
                            "type": "text", 
                            "topic": "Temple de la parole libre et des échanges",
                            "permissions": {
                                "👥 Invité": {"send_messages": True, "embed_links": False, "attach_files": False},
                                "🎭 Membre": {"send_messages": True, "embed_links": True, "attach_files": True},
                                "🌟 Membre Actif": {"create_public_threads": True},
                                "🎯 Spécialiste": {"manage_messages": True}
                            }
                        },
                        {
                            "name": "🎮-gaming", 
                            "type": "text", 
                            "topic": "Partage tes aventures ludiques",
                            "permissions": {
                                "@everyone": {"send_messages": True, "attach_files": True, "embed_links": True},
                                "🎯 Spécialiste": {"manage_messages": True, "manage_threads": True}
                            }
                        },
                        {
                            "name": "🎨-créations", 
                            "type": "text", 
                            "topic": "Exposition de tes œuvres créatives",
                            "permissions": {
                                "@everyone": {"send_messages": True, "attach_files": True, "embed_links": True},
                                "🎯 Spécialiste": {"manage_messages": True},
                                "👑 Citoyen d'Honneur": {"manage_threads": True}
                            }
                        },
                        {
                            "name": "🍀-détente", 
                            "type": "text", 
                            "topic": "Salon de relaxation et de divertissement",
                            "permissions": {
                                "@everyone": {"send_messages": True, "use_external_emojis": True, "add_reactions": True},
                                "🎭 Animateur": {"manage_messages": True}
                            }
                        }
                    ]
                },
                "🛡️ MODÉRATION": {
                    "type": "category",
                    "permissions": {
                        "@everyone": {"view_channel": False},
                        "🏛️ Gardien Suprême": {"view_channel": True, "send_messages": True, "manage_messages": True},
                        "⚖️ Magistrat": {"view_channel": True, "send_messages": True, "manage_messages": True},
                        "🛡️ Sentinel": {"view_channel": True, "send_messages": True},
                        "⚔️ Garde Élite": {"view_channel": True, "send_messages": True},
                        "🔍 Inspecteur": {"view_channel": True, "send_messages": False}
                    },
                    "channels": [
                        {
                            "name": "🚨-alertes-auto", 
                            "type": "text", 
                            "topic": "Alertes automatiques de modération",
                            "permissions": {
                                "🔍 Inspecteur": {"send_messages": False, "view_channel": True}
                            }
                        },
                        {
                            "name": "📋-rapports", 
                            "type": "text", 
                            "topic": "Rapports de modération et sanctions",
                            "permissions": {
                                "⚔️ Garde Élite": {"send_messages": True, "attach_files": True}
                            }
                        },
                        {
                            "name": "💼-discussion-staff", 
                            "type": "text", 
                            "topic": "Discussions internes de l'équipe"
                        }
                    ]
                },
                "🆘 SANCTUAIRE D'AIDE": {
                    "type": "category",
                    "permissions": {
                        "@everyone": {"view_channel": True, "send_messages": True},
                        "📚 Sage": {"manage_messages": True, "manage_threads": True},
                        "🎯 Spécialiste": {"manage_messages": True}
                    },
                    "channels": [
                        {
                            "name": "❓-support-général", 
                            "type": "text", 
                            "topic": "Demandes d'aide et de conseil",
                            "permissions": {
                                "📚 Sage": {"manage_messages": True, "manage_threads": True},
                                "🎯 Spécialiste": {"manage_messages": True}
                            }
                        },
                        {
                            "name": "🔧-support-technique", 
                            "type": "text", 
                            "topic": "Assistance technique et informatique",
                            "permissions": {
                                "🎯 Spécialiste": {"manage_messages": True, "manage_threads": True, "pin_messages": True}
                            }
                        },
                        {
                            "name": "📚-ressources", 
                            "type": "text", 
                            "topic": "Guides et ressources utiles",
                            "permissions": {
                                "@everyone": {"send_messages": False, "view_channel": True, "add_reactions": True},
                                "📚 Sage": {"send_messages": True, "manage_messages": True},
                                "🎯 Spécialiste": {"send_messages": True}
                            }
                        }
                    ]
                },
                "🔊 SALONS VOCAUX": {
                    "type": "category",
                    "permissions": {
                        "@everyone": {"connect": True, "speak": True},
                        "🛡️ Sentinel": {"mute_members": True, "deafen_members": True, "move_members": True}
                    },
                    "channels": [
                        {
                            "name": "🎤 Amphithéâtre", 
                            "type": "voice", 
                            "user_limit": 0,
                            "permissions": {
                                "@everyone": {"connect": True, "speak": False},
                                "🎭 Animateur": {"speak": True, "priority_speaker": True},
                                "📚 Sage": {"speak": True},
                                "⚖️ Magistrat": {"speak": True, "mute_members": True}
                            }
                        },
                        {
                            "name": "💬 Salon Principal", 
                            "type": "voice", 
                            "user_limit": 10
                        },
                        {
                            "name": "🎮 Gaming", 
                            "type": "voice", 
                            "user_limit": 8,
                            "permissions": {
                                "🎯 Spécialiste": {"priority_speaker": True}
                            }
                        },
                        {
                            "name": "📚 Étude", 
                            "type": "voice", 
                            "user_limit": 6,
                            "permissions": {
                                "@everyone": {"speak": False},
                                "🌟 Membre Actif": {"speak": True},
                                "📚 Sage": {"speak": True, "mute_members": True}
                            }
                        },
                        {
                            "name": "🔒 Privé", 
                            "type": "voice", 
                            "user_limit": 4,
                            "permissions": {
                                "👥 Invité": {"connect": False},
                                "🎭 Membre": {"connect": False},
                                "🌟 Membre Actif": {"connect": True}
                            }
                        }
                    ]
                }
            }
            
            # Créer les catégories et canaux avec leurs permissions automatiques
            for category_name, category_data in channel_structure.items():
                try:
                    # Créer la catégorie
                    category = await guild.create_category(
                        name=category_name,
                        reason="Configuration automatique par Themis-Bot"
                    )
                    created_categories.append(category_name)
                    
                    # Appliquer les permissions de catégorie
                    if "permissions" in category_data:
                        await self._apply_permissions(category, category_data["permissions"], guild)
                    
                    # Créer les canaux dans la catégorie
                    for channel_info in category_data["channels"]:
                        channel = None
                        try:
                            if channel_info["type"] == "text":
                                channel = await guild.create_text_channel(
                                    name=channel_info["name"],
                                    category=category,
                                    topic=channel_info.get("topic", ""),
                                    reason="Configuration automatique par Themis-Bot"
                                )
                            elif channel_info["type"] == "voice":
                                channel = await guild.create_voice_channel(
                                    name=channel_info["name"],
                                    category=category,
                                    user_limit=channel_info.get("user_limit", 0),
                                    reason="Configuration automatique par Themis-Bot"
                                )
                            
                            if channel:
                                created_channels.append(channel.name)
                                
                                # Appliquer les permissions spécifiques du canal
                                if "permissions" in channel_info:
                                    await self._apply_permissions(channel, channel_info["permissions"], guild)
                            
                            await asyncio.sleep(0.3)
                            
                        except Exception as e:
                            errors.append(f"Canal {channel_info['name']}: {str(e)}")
                    
                    await asyncio.sleep(1)  # Pause entre les catégories
                    
                except Exception as e:
                    errors.append(f"Catégorie {category_name}: {str(e)}")
            
            # 3. Configuration des règles et finalisations
            setup_embed.clear_fields()
            setup_embed.add_field(
                name="⚡ Étape 3/4",
                value="Application des lois divines...",
                inline=False
            )
            await interaction.edit_original_response(embed=setup_embed)
            
            # Enregistrer la configuration dans les fichiers
            rules_config = {
                "server_name": guild.name,
                "setup_date": datetime.utcnow().isoformat(),
                "rules": {
                    "📜-règles-sacrées": {
                        "allowed_roles": ["🏛️ Gardien Suprême", "⚖️ Magistrat", "📚 Sage"],
                        "read_only": True,
                        "purpose": "Lois divines du royaume"
                    },
                    "📢-annonces-royales": {
                        "allowed_roles": ["🏛️ Gardien Suprême", "⚖️ Magistrat", "🛡️ Sentinel", "🎭 Animateur"],
                        "read_only": False,
                        "purpose": "Annonces officielles"
                    },
                    "🛡️ MODÉRATION": {
                        "private": True,
                        "staff_only": True,
                        "purpose": "Zone de travail de l'équipe de modération"
                    }
                }
            }
            
            os.makedirs("data", exist_ok=True)
            with open("data/rules.json", "w", encoding="utf-8") as f:
                json.dump(rules_config, f, indent=2, ensure_ascii=False)
            
            # 4. Résumé final
            setup_embed.clear_fields()
            setup_embed.title = "✅ Configuration du Royaume Accomplie"
            setup_embed.description = "🏛️ **Le royaume de Thémis est établi !**"
            setup_embed.color = 0x00FF00
            
            setup_embed.add_field(
                name="👑 Rôles Créés",
                value=f"**{len(created_roles)} rôles hiérarchiques**\n" + 
                      "\n".join([f"• {role}" for role in created_roles[:8]]) +
                      (f"\n... et {len(created_roles)-8} autres" if len(created_roles) > 8 else ""),
                inline=True
            )
            
            setup_embed.add_field(
                name="🏛️ Structure Créée",
                value=f"**{len(created_categories)} catégories**\n" +
                      f"**{len(created_channels)} canaux**\n" +
                      "**Permissions configurées automatiquement**",
                inline=True
            )
            
            setup_embed.add_field(
                name="🔐 Permissions Appliquées",
                value="**Système hiérarchique complet :**\n" +
                      "• 🏛️ Panthéon (lecture seule)\n" +
                      "• 💬 Agora (accès graduel)\n" +
                      "• 🛡️ Modération (staff uniquement)\n" +
                      "• 🆘 Aide (spécialistes)\n" +
                      "• 🔊 Vocal (contrôlé)",
                inline=False
            )
            
            if errors:
                error_text = "\n".join(errors[:5])
                if len(errors) > 5:
                    error_text += f"\n... et {len(errors) - 5} autres erreurs"
                setup_embed.add_field(
                    name="⚠️ Avertissements",
                    value=f"```{error_text}```",
                    inline=False
                )
            
            setup_embed.add_field(
                name="📋 Guide des Permissions",
                value="**Utilisez `/permissions` pour ajuster**\n" +
                      "**Utilisez `/roleinfo` pour analyser**\n" +
                      "**Système automatique configuré !**",
                inline=False
            )
            
            setup_embed.set_footer(text="Themis-Bot • Configuration Avancée Terminée")
            
            await interaction.edit_original_response(embed=setup_embed)
            
            # Log de l'action
            self.logger.info(f"🏛️ {interaction.user} a configuré le serveur {guild.name} avec permissions automatiques")
            
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Erreur de Configuration",
                description=f"**Erreur :** {str(e)}\n\nLa configuration a été interrompue.",
                color=0xFF0000,
                timestamp=datetime.utcnow()
            )
            
            await interaction.edit_original_response(embed=error_embed)
            self.logger.error(f"Erreur lors de la configuration: {e}")

    @app_commands.command(name="permissions", description="🔐 Configure les permissions détaillées d'un canal")
    @app_commands.describe(
        channel="Canal à configurer",
        role="Rôle à modifier",
        permission="Type de permission",
        value="Autoriser (True) ou refuser (False)"
    )
    @app_commands.choices(permission=[
        app_commands.Choice(name="Voir le canal", value="view_channel"),
        app_commands.Choice(name="Envoyer des messages", value="send_messages"),
        app_commands.Choice(name="Gérer les messages", value="manage_messages"),
        app_commands.Choice(name="Liens et médias", value="embed_links"),
        app_commands.Choice(name="Joindre des fichiers", value="attach_files"),
        app_commands.Choice(name="Ajouter des réactions", value="add_reactions"),
        app_commands.Choice(name="Utiliser des émojis externes", value="use_external_emojis"),
        app_commands.Choice(name="Créer des threads", value="create_public_threads"),
        app_commands.Choice(name="Gérer les threads", value="manage_threads"),
        app_commands.Choice(name="Connecter (vocal)", value="connect"),
        app_commands.Choice(name="Parler (vocal)", value="speak"),
        app_commands.Choice(name="Muet vocal", value="mute_members"),
        app_commands.Choice(name="Déafen vocal", value="deafen_members")
    ])
    @app_commands.default_permissions(manage_channels=True)
    async def configure_permissions(
        self, 
        interaction: discord.Interaction, 
        channel: discord.abc.GuildChannel,
        role: discord.Role,
        permission: str,
        value: bool
    ):
        """Configure les permissions détaillées pour un rôle dans un canal"""
        
        try:
            # Créer l'objet PermissionOverwrite
            overwrites = channel.overwrites_for(role)
            setattr(overwrites, permission, value)
            
            await channel.set_permissions(role, overwrite=overwrites)
            
            embed = discord.Embed(
                title="🔐 Permissions Mises à Jour",
                description=f"**Canal:** {channel.mention}\n**Rôle:** {role.mention}",
                color=0x00FF00 if value else 0xFF0000,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="Permission Modifiée",
                value=f"`{permission}`: {'✅ Autorisé' if value else '❌ Refusé'}",
                inline=False
            )
            
            embed.set_footer(text=f"Modifié par {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed)
            
            # Log de l'action
            self.logger.info(f"🔐 {interaction.user} a modifié les permissions de {role.name} dans {channel.name}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la modification des permissions: {e}")
            await interaction.response.send_message(
                f"❌ **Erreur**\nImpossible de modifier les permissions: {str(e)}",
                ephemeral=True
            )

    @app_commands.command(name="roleinfo", description="📋 Affiche les détails et permissions d'un rôle")
    @app_commands.describe(role="Rôle à analyser")
    async def role_info(self, interaction: discord.Interaction, role: discord.Role):
        """Affiche les informations détaillées d'un rôle"""
        
        embed = discord.Embed(
            title=f"📋 Informations du Rôle: {role.name}",
            color=role.color,
            timestamp=datetime.utcnow()
        )
        
        # Informations de base
        embed.add_field(
            name="🆔 Informations Générales",
            value=f"**ID:** `{role.id}`\n"
                  f"**Couleur:** `{role.color}`\n"
                  f"**Position:** `{role.position}`\n"
                  f"**Membres:** `{len(role.members)}`\n"
                  f"**Mentionnable:** {'✅' if role.mentionable else '❌'}\n"
                  f"**Affiché séparément:** {'✅' if role.hoist else '❌'}",
            inline=False
        )
        
        # Permissions importantes
        important_perms = []
        if role.permissions.administrator:
            important_perms.append("👑 Administrateur")
        if role.permissions.manage_guild:
            important_perms.append("🏛️ Gérer le serveur")
        if role.permissions.manage_channels:
            important_perms.append("📝 Gérer les canaux")
        if role.permissions.manage_roles:
            important_perms.append("🔄 Gérer les rôles")
        if role.permissions.ban_members:
            important_perms.append("🔨 Bannir")
        if role.permissions.kick_members:
            important_perms.append("👢 Expulser")
        if role.permissions.moderate_members:
            important_perms.append("⏰ Timeout")
        if role.permissions.manage_messages:
            important_perms.append("🗑️ Gérer les messages")
        
        if important_perms:
            embed.add_field(
                name="⚡ Permissions Importantes",
                value="\n".join(important_perms),
                inline=True
            )
        
        # Membres avec ce rôle (limité à 10)
        if role.members:
            member_list = [member.display_name for member in role.members[:10]]
            if len(role.members) > 10:
                member_list.append(f"... et {len(role.members) - 10} autres")
            
            embed.add_field(
                name="👥 Membres (Top 10)",
                value="\n".join(member_list),
                inline=True
            )
        
        embed.set_footer(text="Themis-Bot • Gestion des Rôles")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="jugement-divin", description="⚖️ RESET COMPLET - Supprime tout et ne laisse qu'un canal de rédemption")
    @app_commands.describe(confirmation="Tapez 'JE CONFIRME LE JUGEMENT DIVIN' pour confirmer")
    @app_commands.default_permissions(administrator=True)
    async def divine_judgment(self, interaction: discord.Interaction, confirmation: str):
        """Commande de reset dramatique du serveur - Supprime tout sauf un canal de rédemption"""
        
        # Vérification de la confirmation
        if confirmation != "JE CONFIRME LE JUGEMENT DIVIN":
            await interaction.response.send_message(
                "❌ **Confirmation Invalide**\n"
                "Pour confirmer cette action destructrice, vous devez taper exactement :\n"
                "```JE CONFIRME LE JUGEMENT DIVIN```\n"
                "⚠️ **ATTENTION:** Cette commande supprime TOUT (rôles, canaux, etc.)",
                ephemeral=True
            )
            return
        
        # Embed de confirmation finale
        warning_embed = discord.Embed(
            title="⚖️ JUGEMENT DIVIN IMMINENT",
            description="🔥 **Dernière chance de reculer !** 🔥\n\n"
                       "Cette action va :\n"
                       "• 🗑️ Supprimer TOUS les canaux\n"
                       "• 👥 Supprimer TOUS les rôles (sauf @everyone)\n"
                       "• 🏛️ Créer uniquement un canal '#rédemption'\n"
                       "• ⚰️ Effacer l'histoire du serveur\n\n"
                       "**Cette action est IRRÉVERSIBLE !**",
            color=0xFF0000,
            timestamp=datetime.utcnow()
        )
        
        warning_embed.add_field(
            name="🔥 Citation Divine",
            value="*« Et Thémis dit : Que la justice s'abatte sur ce royaume corrompu ! »*",
            inline=False
        )
        
        warning_embed.set_footer(text="Vous avez 10 secondes pour arrêter en supprimant cette interaction...")
        
        await interaction.response.send_message(embed=warning_embed)
        
        # Attendre 10 secondes
        await asyncio.sleep(10)
        
        try:
            # Début du jugement divin
            guild = interaction.guild
            if guild is None:
                await interaction.edit_original_response(content="❌ Erreur: Impossible d'accéder au serveur.")
                return
            
            judgment_embed = discord.Embed(
                title="⚖️ LE JUGEMENT DIVIN COMMENCE",
                description="🔥 **Que la purification commence !** 🔥",
                color=0x8B0000,
                timestamp=datetime.utcnow()
            )
            
            await interaction.edit_original_response(embed=judgment_embed)
            
            deleted_channels = 0
            deleted_roles = 0
            errors = []
            
            # 1. Suppression de TOUS les canaux
            judgment_embed.add_field(
                name="🗑️ Phase 1 : Purification des Canaux",
                value="Destruction en cours...",
                inline=False
            )
            await interaction.edit_original_response(embed=judgment_embed)
            
            channels_to_delete = list(guild.channels)
            for channel in channels_to_delete:
                try:
                    await channel.delete(reason="⚖️ Jugement Divin - Purification totale")
                    deleted_channels += 1
                    await asyncio.sleep(0.5)  # Éviter les rate limits
                except Exception as e:
                    errors.append(f"Canal {channel.name}: {str(e)}")
            
            # 2. Suppression de TOUS les rôles (sauf @everyone)
            judgment_embed.clear_fields()
            judgment_embed.add_field(
                name="👥 Phase 2 : Abolition de la Hiérarchie",
                value="Égalisation en cours...",
                inline=False
            )
            await interaction.edit_original_response(embed=judgment_embed)
            
            roles_to_delete = [role for role in guild.roles if role.name != "@everyone"]
            for role in roles_to_delete:
                try:
                    await role.delete(reason="⚖️ Jugement Divin - Abolition des privilèges")
                    deleted_roles += 1
                    await asyncio.sleep(0.5)
                except Exception as e:
                    errors.append(f"Rôle {role.name}: {str(e)}")
            
            # 3. Création du canal de rédemption
            judgment_embed.clear_fields()
            judgment_embed.add_field(
                name="🕊️ Phase 3 : Création de l'Espoir",
                value="Installation du chemin de rédemption...",
                inline=False
            )
            await interaction.edit_original_response(embed=judgment_embed)
            
            # Créer le canal de rédemption
            redemption_channel = await guild.create_text_channel(
                name="rédemption",
                topic="🕊️ Seul canal survivant au Jugement Divin. Ici commence votre rédemption.",
                reason="⚖️ Jugement Divin - Canal de la dernière chance"
            )
            
            # 4. Message final dans le canal de rédemption
            final_embed = discord.Embed(
                title="⚖️ LE JUGEMENT DIVIN EST RENDU",
                description="🔥 **La purification est accomplie** 🔥\n\n"
                           f"📊 **Bilan de la Justice :**\n"
                           f"• 🗑️ Canaux supprimés : `{deleted_channels}`\n"
                           f"• 👥 Rôles abolis : `{deleted_roles}`\n"
                           f"• 🕊️ Canaux de rédemption : `1`\n\n"
                           "🌅 **Nouveau Commencement :**\n"
                           "Ce serveur a été purifié par la justice divine.\n"
                           "Seul ce canal demeure pour permettre la rédemption.\n"
                           "Utilisez `/setup` pour reconstruire un royaume juste.",
                color=0x9932CC,
                timestamp=datetime.utcnow()
            )
            
            final_embed.add_field(
                name="📜 Décret Divin",
                value="*« Que cette destruction serve de leçon. »*\n"
                      "*« De ces cendres renaîtra un royaume plus juste. »*\n"
                      "*« Car telle est la volonté de Thémis. »*",
                inline=False
            )
            
            if errors:
                error_text = "\n".join(errors[:5])
                if len(errors) > 5:
                    error_text += f"\n... et {len(errors) - 5} autres erreurs"
                final_embed.add_field(
                    name="⚠️ Résistances Mineures",
                    value=f"```{error_text}```",
                    inline=False
                )
            
            final_embed.set_footer(text="Themis-Bot • Justice Divine Accomplie")
            
            await redemption_channel.send(embed=final_embed)
            
            # Message de réussite (si le canal original existe encore)
            try:
                success_embed = discord.Embed(
                    title="✅ JUGEMENT DIVIN ACCOMPLI",
                    description=f"🔥 Le serveur a été purifié !\n\n"
                               f"Seul le canal {redemption_channel.mention} demeure.\n"
                               f"La justice divine est rendue.",
                    color=0x00FF00,
                    timestamp=datetime.utcnow()
                )
                await interaction.edit_original_response(embed=success_embed)
            except:
                # Le canal original a probablement été supprimé
                pass
            
            # Log de l'action
            self.logger.warning(f"⚖️ JUGEMENT DIVIN exécuté par {interaction.user} - Serveur {guild.name} purifié")
            
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ ÉCHEC DU JUGEMENT DIVIN",
                description=f"**Erreur :** {str(e)}\n\n"
                           "La justice divine a été entravée.\n"
                           "Vérifiez les permissions du bot.",
                color=0xFF0000,
                timestamp=datetime.utcnow()
            )
            
            try:
                await interaction.edit_original_response(embed=error_embed)
            except:
                # Fallback si l'interaction a expiré
                await interaction.followup.send(embed=error_embed)
            
            self.logger.error(f"Erreur lors du Jugement Divin: {e}")

async def setup(bot):
    """Charge le module d'administration avec permissions automatiques"""
    await bot.add_cog(AdminCog(bot))
