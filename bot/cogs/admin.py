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
                name="⚡ Étape 1/3",
                value="Création de la hiérarchie divine...",
                inline=False
            )
            await interaction.edit_original_response(embed=setup_embed)
            
            # Rôles de modération hiérarchiques avec permissions détaillées
            roles_to_create = [
                {
                    "name": "🏛️ Gardien Suprême", 
                    "color": 0x9932CC, 
                    "permissions": discord.Permissions.all()
                },
                {
                    "name": "⚖️ Magistrat", 
                    "color": 0xFF6B35, 
                    "permissions": discord.Permissions(
                        manage_messages=True, kick_members=True, ban_members=True, 
                        manage_channels=True, moderate_members=True, manage_roles=True,
                        view_audit_log=True, manage_nicknames=True
                    )
                },
                {
                    "name": "🛡️ Sentinel", 
                    "color": 0x3498DB, 
                    "permissions": discord.Permissions(
                        manage_messages=True, kick_members=True, moderate_members=True,
                        manage_nicknames=True, view_audit_log=True
                    )
                },
                {
                    "name": "⚔️ Garde Élite", 
                    "color": 0x8B0000, 
                    "permissions": discord.Permissions(
                        manage_messages=True, moderate_members=True, view_audit_log=True
                    )
                },
                {
                    "name": "🔍 Inspecteur", 
                    "color": 0x4B0082, 
                    "permissions": discord.Permissions(
                        view_audit_log=True, read_message_history=True
                    )
                },
                {
                    "name": "📚 Sage", 
                    "color": 0x00FF7F, 
                    "permissions": discord.Permissions(
                        manage_messages=True, send_messages=True, embed_links=True,
                        attach_files=True, use_external_emojis=True
                    )
                },
                {
                    "name": "🎭 Animateur", 
                    "color": 0xFF1493, 
                    "permissions": discord.Permissions(
                        send_messages=True, embed_links=True, attach_files=True,
                        use_external_emojis=True, create_public_threads=True,
                        manage_threads=True
                    )
                },
                {
                    "name": "🎯 Spécialiste", 
                    "color": 0x32CD32, 
                    "permissions": discord.Permissions(
                        send_messages=True, embed_links=True, attach_files=True
                    )
                },
                {
                    "name": "� VIP", 
                    "color": 0xFF00FF, 
                    "permissions": discord.Permissions(
                        send_messages=True, embed_links=True, attach_files=True,
                        use_external_emojis=True, add_reactions=True, priority_speaker=True
                    )
                },
                {
                    "name": "🌟 Membre Actif", 
                    "color": 0x87CEEB, 
                    "permissions": discord.Permissions(
                        send_messages=True, attach_files=True, add_reactions=True
                    )
                },
                {
                    "name": "�👑 Citoyen d'Honneur", 
                    "color": 0xFFD700, 
                    "permissions": discord.Permissions(
                        send_messages=True, embed_links=True, attach_files=True,
                        use_external_emojis=True, add_reactions=True
                    )
                },
                {
                    "name": "🎭 Citoyen", 
                    "color": 0x95A5A6, 
                    "permissions": discord.Permissions(
                        send_messages=True, read_message_history=True, add_reactions=True,
                        connect=True, speak=True
                    )
                },
                {
                    "name": "🎫 En Attente", 
                    "color": 0x2F3136, 
                    "permissions": discord.Permissions(
                        read_message_history=True, view_channel=True
                    )
                },
                {
                    "name": "⚠️ Banni Temporaire", 
                    "color": 0x000000, 
                    "permissions": discord.Permissions()
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
                name="⚡ Étape 2/3",
                value="Construction de l'architecture divine avec permissions...",
                inline=False
            )
            await interaction.edit_original_response(embed=setup_embed)
            
            # Structure des canaux avec permissions détaillées par rôle
            channel_structure = {
                "📋 INFORMATIONS": {
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
                                "🎭 Citoyen": {"view_channel": True, "send_messages": False, "add_reactions": True},
                                "� En Attente": {"view_channel": False},
                                "�🏛️ Gardien Suprême": {"send_messages": True, "manage_messages": True},
                                "⚖️ Magistrat": {"send_messages": True, "manage_messages": True},
                                "📚 Sage": {"send_messages": True}
                            }
                        },
                        {
                            "name": "📢-annonces-royales", 
                            "type": "text", 
                            "topic": "Proclamations officielles du royaume",
                            "permissions": {
                                "🎭 Citoyen": {"view_channel": True, "send_messages": False, "add_reactions": True},
                                "� En Attente": {"view_channel": False},
                                "�🏛️ Gardien Suprême": {"send_messages": True, "manage_messages": True},
                                "⚖️ Magistrat": {"send_messages": True},
                                "🛡️ Sentinel": {"send_messages": True},
                                "🎭 Animateur": {"send_messages": True}
                            }
                        },
                        {
                            "name": "ℹ️-guide-serveur", 
                            "type": "text", 
                            "topic": "Guide d'utilisation du serveur et de ses fonctionnalités",
                            "permissions": {
                                "🎭 Citoyen": {"view_channel": True, "send_messages": False, "add_reactions": True},
                                "🎫 En Attente": {"view_channel": True, "send_messages": False},
                                "📚 Sage": {"send_messages": True, "manage_messages": True}
                            }
                        }
                    ]
                },
                "🎫 VÉRIFICATION D'IDENTITÉ": {
                    "type": "category",
                    "permissions": {
                        "@everyone": {"view_channel": True, "send_messages": True},
                        "🎭 Citoyen": {"view_channel": False},  # Les citoyens vérifiés n'ont plus besoin de cette zone
                        "🏛️ Gardien Suprême": {"view_channel": True, "send_messages": True, "manage_messages": True},
                        "⚖️ Magistrat": {"view_channel": True, "send_messages": True, "manage_messages": True},
                        "🛡️ Sentinel": {"view_channel": True, "send_messages": True, "manage_messages": True}
                    },
                    "channels": [
                        {
                            "name": "🎫-créer-ticket", 
                            "type": "text", 
                            "topic": "Créez votre ticket pour vérifier votre identité",
                            "permissions": {
                                "@everyone": {"view_channel": True, "send_messages": True},
                                "🎭 Citoyen": {"view_channel": False}
                            }
                        },
                        {
                            "name": "�-guide-vérification", 
                            "type": "text", 
                            "topic": "Guide complet pour la vérification d'identité",
                            "permissions": {
                                "@everyone": {"view_channel": True, "send_messages": False},
                                "🎭 Citoyen": {"view_channel": False}
                            }
                        }
                    ]
                },
                "�💬 AGORA PUBLIQUE": {
                    "type": "category",
                    "permissions": {
                        "🎭 Citoyen": {"view_channel": True, "send_messages": True},
                        "🎫 En Attente": {"view_channel": False},
                        "🛡️ Sentinel": {"manage_messages": True}
                    },
                    "channels": [
                        {
                            "name": "💬-discussion-générale", 
                            "type": "text", 
                            "topic": "Temple de la parole libre et des échanges",
                            "permissions": {
                                "🎭 Citoyen": {"send_messages": True, "embed_links": True, "attach_files": True},
                                "👑 Citoyen d'Honneur": {"create_public_threads": True, "manage_threads": True},
                                "🌟 Membre Actif": {"create_public_threads": True}
                            }
                        },
                        {
                            "name": "🎮-gaming", 
                            "type": "text", 
                            "topic": "Partage tes aventures ludiques et organise des parties",
                            "permissions": {
                                "🎭 Citoyen": {"send_messages": True, "attach_files": True, "embed_links": True}
                            }
                        },
                        {
                            "name": "🎨-créations", 
                            "type": "text", 
                            "topic": "Partage tes créations artistiques et projets",
                            "permissions": {
                                "🎭 Citoyen": {"send_messages": True, "attach_files": True, "embed_links": True}
                            }
                        },
                        {
                            "name": "📰-actualités", 
                            "type": "text", 
                            "topic": "Discussions sur l'actualité et les événements",
                            "permissions": {
                                "🎭 Citoyen": {"send_messages": True, "embed_links": True},
                                "📚 Sage": {"manage_messages": True}
                            }
                        }
                    ]
                },
                "🔊 SALONS VOCAUX": {
                    "type": "category",
                    "permissions": {
                        "🎭 Citoyen": {"view_channel": True, "connect": True, "speak": True},
                        "🎫 En Attente": {"view_channel": False},
                        "💎 VIP": {"priority_speaker": True},
                        "🛡️ Sentinel": {"move_members": True, "mute_members": True}
                    },
                    "channels": [
                        {
                            "name": "🔊 Hall Principal", 
                            "type": "voice", 
                            "user_limit": 0,  # Pas de limite
                            "permissions": {
                                "🎭 Citoyen": {"connect": True, "speak": True},
                                "💎 VIP": {"priority_speaker": True}
                            }
                        },
                        {
                            "name": "🎮 Gaming Lounge", 
                            "type": "voice", 
                            "user_limit": 10,
                            "permissions": {
                                "🎭 Citoyen": {"connect": True, "speak": True, "use_voice_activation": True}
                            }
                        },
                        {
                            "name": "📚 Salle d'Étude", 
                            "type": "voice", 
                            "user_limit": 6,
                            "permissions": {
                                "🎭 Citoyen": {"connect": True, "speak": True},
                                "📚 Sage": {"priority_speaker": True}
                            }
                        },
                        {
                            "name": "🎵 Musique & Détente", 
                            "type": "voice", 
                            "user_limit": 8,
                            "permissions": {
                                "🎭 Citoyen": {"connect": True, "speak": True, "use_voice_activation": True}
                            }
                        },
                        {
                            "name": "💼 Réunion Privée", 
                            "type": "voice", 
                            "user_limit": 4,
                            "permissions": {
                                "🎭 Citoyen": {"connect": True, "speak": True},
                                "🎯 Spécialiste": {"priority_speaker": True}
                            }
                        }
                    ]
                },
                "👑 ZONE VIP": {
                    "type": "category",
                    "permissions": {
                        "@everyone": {"view_channel": False},
                        "💎 VIP": {"view_channel": True, "send_messages": True, "connect": True, "speak": True},
                        "👑 Citoyen d'Honneur": {"view_channel": True, "send_messages": True, "connect": True},
                        "🏛️ Gardien Suprême": {"view_channel": True, "send_messages": True},
                        "⚖️ Magistrat": {"view_channel": True, "send_messages": True}
                    },
                    "channels": [
                        {
                            "name": "💎-salon-vip", 
                            "type": "text", 
                            "topic": "Salon exclusif pour les membres VIP",
                            "permissions": {
                                "💎 VIP": {"send_messages": True, "embed_links": True, "attach_files": True}
                            }
                        },
                        {
                            "name": "👑 Salon Royal", 
                            "type": "voice", 
                            "user_limit": 6,
                            "permissions": {
                                "💎 VIP": {"connect": True, "speak": True, "priority_speaker": True}
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
                        "🛡️ Sentinel": {"view_channel": True, "send_messages": True}
                    },
                    "channels": [
                        {
                            "name": "📋-rapports", 
                            "type": "text", 
                            "topic": "Rapports de modération et sanctions",
                            "permissions": {
                                "🔍 Inspecteur": {"view_channel": True, "send_messages": True}
                            }
                        },
                        {
                            "name": "💼-discussion-staff", 
                            "type": "text", 
                            "topic": "Discussions internes de l'équipe"
                        },
                        {
                            "name": "📊-logs-serveur", 
                            "type": "text", 
                            "topic": "Logs automatiques des actions du serveur",
                            "permissions": {
                                "@everyone": {"send_messages": False}
                            }
                        },
                        {
                            "name": "🎫-logs-tickets", 
                            "type": "text", 
                            "topic": "Historique des tickets de vérification d'identité",
                            "permissions": {
                                "@everyone": {"send_messages": False}
                            }
                        },
                        {
                            "name": "🛡️ Bureau Modération", 
                            "type": "voice", 
                            "user_limit": 5,
                            "permissions": {
                                "🔍 Inspecteur": {"connect": True, "speak": True}
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
            
            # 3. Résumé final
            setup_embed.clear_fields()
            setup_embed.title = "✅ Configuration du Royaume Accomplie"
            setup_embed.description = "🏛️ **Le royaume de Thémis est établi avec permissions automatiques !**"
            setup_embed.color = 0x00FF00
            
            setup_embed.add_field(
                name="👑 Rôles Créés",
                value=f"**{len(created_roles)} rôles hiérarchiques**\n" + 
                      "\n".join([f"• {role}" for role in created_roles]),
                inline=True
            )
            
            setup_embed.add_field(
                name="🏛️ Structure Créée",
                value=f"**{len(created_categories)} catégories**\n" +
                      f"**{len(created_channels)} canaux**\n" +
                      "**✅ Permissions configurées automatiquement**",
                inline=True
            )
            
            setup_embed.add_field(
                name="🔐 Permissions Appliquées Automatiquement",
                value="**📜 Règles :** Lecture seule pour tous, écriture pour staff\n" +
                      "**📢 Annonces :** Lecture pour tous, écriture pour modération\n" +
                      "**💬 Discussion :** Accès graduel selon les rôles\n" +
                      "**🛡️ Modération :** Staff uniquement\n" +
                      "**Chaque rôle a ses permissions spécifiques !**",
                inline=False
            )
            
            if errors:
                error_text = "\n".join(errors[:3])
                if len(errors) > 3:
                    error_text += f"\n... et {len(errors) - 3} autres erreurs"
                setup_embed.add_field(
                    name="⚠️ Avertissements",
                    value=f"```{error_text}```",
                    inline=False
                )
            
            setup_embed.set_footer(text="Themis-Bot • Configuration avec Permissions Automatiques")
            
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

async def setup(bot):
    """Charge le module d'administration avec permissions automatiques"""
    await bot.add_cog(AdminCog(bot))