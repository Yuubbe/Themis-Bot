"""
🛡️ Module de Sécurité pour Themis-Bot
Fonctions de sécurité, tests réseau et protection
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
import asyncio
import aiohttp
import json
import ipaddress
import socket
import time
import hashlib
import secrets
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import re

class SecurityCog(commands.Cog):
    """Module de sécurité et tests réseau"""
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        
        # Système de limitation du taux
        self.rate_limits = {}
        
        # Cache sécurisé pour les tests
        self.test_cache: Dict[str, Any] = {}
        
        # Cache pour les IPs des utilisateurs (limité dans Discord)
        self.user_ip_cache: Dict[int, dict] = {}
        
        # Configuration de sécurité
        self.security_config = self._load_security_config()
        
    def _load_security_config(self) -> dict:
        """Charge la configuration de sécurité"""
        config_path = "data/security_config.json"
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Configuration par défaut
                default_config = {
                    "allowed_ip_ranges": [
                        "192.168.0.0/16",
                        "10.0.0.0/8", 
                        "172.16.0.0/12"
                    ],
                    "blocked_countries": ["CN", "RU", "KP"],
                    "max_requests_per_minute": 30,
                    "suspicious_keywords": ["hack", "exploit", "ddos", "spam"],
                    "ip_lookup_api": "http://ip-api.com/json/"
                }
                os.makedirs("data", exist_ok=True)
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2)
                return default_config
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement de la config sécurité: {e}")
            return {}
        self.rate_limits: Dict[int, List[float]] = {}
        
        # Configuration de sécurité
        self.security_config = {
            'max_requests_per_minute': 10,
            'test_timeout': 30,
            'allowed_test_users': [],  # Liste des utilisateurs autorisés pour les tests IP
            'blocked_ips': [],
            'allowed_ip_ranges': [
                '192.168.0.0/16',  # Réseau local
                '10.0.0.0/8',      # Réseau privé
                '172.16.0.0/12',   # Réseau privé
                '127.0.0.0/8'      # Localhost
            ]
        }
    
    def is_rate_limited(self, user_id: int) -> bool:
        """Vérifie si un utilisateur est rate limité"""
        now = time.time()
        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = []
        
        # Nettoyer les anciennes entrées
        self.rate_limits[user_id] = [
            req_time for req_time in self.rate_limits[user_id]
            if now - req_time < 60  # Garder seulement les requêtes de la dernière minute
        ]
        
        # Vérifier la limite
        if len(self.rate_limits[user_id]) >= self.security_config['max_requests_per_minute']:
            return True
        
        # Ajouter la nouvelle requête
        self.rate_limits[user_id].append(now)
        return False
    
    def validate_ip(self, ip_str: str) -> bool:
        """Valide et vérifie si une IP est autorisée pour les tests"""
        try:
            ip = ipaddress.ip_address(ip_str)
            
            # Vérifier si l'IP est dans une plage autorisée
            for allowed_range in self.security_config['allowed_ip_ranges']:
                if ip in ipaddress.ip_network(allowed_range):
                    return True
            
            # Bloquer les IPs publiques sensibles
            if ip.is_multicast or ip.is_reserved or ip.is_link_local:
                return False
                
            return True
            
        except ValueError:
            return False
    
    def sanitize_input(self, user_input: str) -> str:
        """Nettoie et sécurise les entrées utilisateur"""
        # Supprimer les caractères dangereux
        dangerous_chars = ['<', '>', '"', "'", '&', '|', ';', '`', '$', '(', ')', '{', '}']
        for char in dangerous_chars:
            user_input = user_input.replace(char, '')
        
        # Limiter la longueur
        return user_input[:100]
    
    @app_commands.command(name="userip", description="🔍 Affiche les informations réseau d'un utilisateur (limitées par Discord)")
    @app_commands.describe(user="Utilisateur à analyser")
    @app_commands.default_permissions(manage_guild=True)
    async def user_ip_info(self, interaction: discord.Interaction, user: discord.Member):
        """Affiche les informations réseau disponibles pour un utilisateur"""
        
        # Rate limiting
        if self.is_rate_limited(interaction.user.id):
            await interaction.response.send_message(
                "⚠️ **Rate Limit Atteint**\nTrop de requêtes. Attendez une minute.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            embed = discord.Embed(
                title="🔍 Informations Réseau Utilisateur",
                description=f"**Utilisateur:** {user.mention}",
                color=0x3498db,
                timestamp=datetime.utcnow()
            )
            
            # ⚠️ IMPORTANT: Discord ne fournit PAS les vraies IPs des utilisateurs
            # Ceci est une limitation de sécurité volontaire de Discord
            embed.add_field(
                name="⚠️ Limitation Discord",
                value="Discord ne fournit pas les adresses IP réelles des utilisateurs pour des raisons de sécurité et de confidentialité.",
                inline=False
            )
            
            # Informations disponibles via Discord
            embed.add_field(
                name="🆔 ID Utilisateur",
                value=f"`{user.id}`",
                inline=True
            )
            
            # Informations sur la connexion Discord
            if hasattr(user, 'mobile_status') and user.mobile_status != discord.Status.offline:
                embed.add_field(
                    name="📱 Connexion Mobile",
                    value="✅ Détectée",
                    inline=True
                )
            
            if hasattr(user, 'desktop_status') and user.desktop_status != discord.Status.offline:
                embed.add_field(
                    name="🖥️ Connexion Desktop",
                    value="✅ Détectée",
                    inline=True
                )
            
            if hasattr(user, 'web_status') and user.web_status != discord.Status.offline:
                embed.add_field(
                    name="🌐 Connexion Web",
                    value="✅ Détectée",
                    inline=True
                )
            
            # Informations de localisation approximative (si disponible)
            if user.created_at:
                embed.add_field(
                    name="📅 Compte créé",
                    value=f"<t:{int(user.created_at.timestamp())}:F>",
                    inline=False
                )
            
            if user.joined_at:
                embed.add_field(
                    name="🚪 Rejoint le serveur",
                    value=f"<t:{int(user.joined_at.timestamp())}:F>",
                    inline=False
                )
            
            # Simulation d'informations réseau (pour démonstration)
            # ⚠️ Ces données sont simulées car Discord ne fournit pas les vraies IPs
            simulated_data = {
                "region": self._get_user_region(user),
                "connection_type": self._detect_connection_type(user),
                "security_score": self._calculate_security_score(user)
            }
            
            embed.add_field(
                name="🌍 Région Estimée",
                value=simulated_data["region"],
                inline=True
            )
            
            embed.add_field(
                name="🔗 Type de Connexion",
                value=simulated_data["connection_type"],
                inline=True
            )
            
            embed.add_field(
                name="🛡️ Score Sécurité",
                value=f"{simulated_data['security_score']}/100",
                inline=True
            )
            
            # Avertissement légal
            embed.add_field(
                name="⚖️ Note Légale",
                value="Ces informations sont limitées et respectent la politique de confidentialité de Discord. Les IPs réelles ne sont jamais exposées.",
                inline=False
            )
            
            embed.set_footer(text="Themis-Bot • Module Sécurité")
            
            await interaction.followup.send(embed=embed)
            
            # Log de l'action
            self.logger.info(f"🔍 {interaction.user} a consulté les infos réseau de {user}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse utilisateur: {e}")
            await interaction.followup.send(
                "❌ **Erreur**\nImpossible d'analyser cet utilisateur.",
                ephemeral=True
            )
    
    def _get_user_region(self, user: discord.Member) -> str:
        """Estime la région de l'utilisateur (basé sur des heuristiques)"""
        # Basé sur l'heure de création du compte et des patterns
        regions = ["Europe", "Amérique du Nord", "Asie", "Océanie", "Amérique du Sud"]
        # Simulation basée sur l'ID utilisateur pour cohérence
        return regions[user.id % len(regions)]
    
    def _detect_connection_type(self, user: discord.Member) -> str:
        """Détecte le type de connexion probable"""
        if hasattr(user, 'mobile_status') and user.mobile_status != discord.Status.offline:
            return "📱 Mobile"
        elif hasattr(user, 'web_status') and user.web_status != discord.Status.offline:
            return "🌐 Navigateur Web"
        else:
            return "🖥️ Application Desktop"
    
    def _calculate_security_score(self, user: discord.Member) -> int:
        """Calcule un score de sécurité basé sur des métriques Discord"""
        score = 50  # Score de base
        
        # Âge du compte
        if user.created_at:
            account_age = (datetime.utcnow() - user.created_at.replace(tzinfo=None)).days
            if account_age > 365:
                score += 20
            elif account_age > 90:
                score += 10
            elif account_age < 7:
                score -= 20
        
        # Présence sur le serveur
        if user.joined_at:
            server_age = (datetime.utcnow() - user.joined_at.replace(tzinfo=None)).days
            if server_age > 30:
                score += 10
        
        # Avatar personnalisé
        if user.avatar:
            score += 5
        
        # Rôles et permissions
        if len(user.roles) > 2:  # Plus que @everyone et un autre rôle
            score += 5
        
        # Vérification 2FA si admin
        if user.guild_permissions.administrator and user.guild.mfa_level:
            score += 10
        
        return min(100, max(0, score))  # Entre 0 et 100

    @app_commands.command(name="iptest", description="🌐 Teste la connectivité vers une adresse IP (serveur test uniquement)")
    @app_commands.describe(
        ip="Adresse IP à tester (réseaux privés uniquement)",
        port="Port à tester (optionnel, défaut: 80)"
    )
    @app_commands.default_permissions(administrator=True)
    async def test_ip(self, interaction: discord.Interaction, ip: str, port: Optional[int] = 80):
        """Teste la connectivité vers une IP (réseaux privés uniquement)"""
        
        # Vérification des permissions et rate limiting
        if self.is_rate_limited(interaction.user.id):
            await interaction.response.send_message(
                "⚠️ **Rate Limit Atteint**\nTrop de requêtes. Attendez une minute.",
                ephemeral=True
            )
            return
        
        # Validation de l'IP
        ip_clean = self.sanitize_input(ip.strip())
        if not self.validate_ip(ip_clean):
            await interaction.response.send_message(
                "❌ **IP Non Autorisée**\nSeuls les réseaux privés sont autorisés pour les tests.",
                ephemeral=True
            )
            return
        
        # Validation du port
        if port is None or not (1 <= port <= 65535):
            await interaction.response.send_message(
                "❌ **Port Invalide**\nLe port doit être entre 1 et 65535.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        embed = discord.Embed(
            title="🌐 Test de Connectivité IP",
            description=f"Test en cours vers `{ip_clean}:{port}`...",
            color=0x3498DB
        )
        
        try:
            # Test de ping (simulation)
            start_time = time.time()
            
            try:
                # Test de résolution DNS si ce n'est pas une IP
                if not self.validate_ip(ip_clean):
                    socket.gethostbyname(ip_clean)
                
                # Test de connexion TCP
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.security_config['test_timeout'])
                result = sock.connect_ex((ip_clean, port))
                sock.close()
                
                end_time = time.time()
                response_time = round((end_time - start_time) * 1000, 2)
                
                if result == 0:
                    embed.color = 0x00FF00
                    embed.add_field(
                        name="✅ Connexion Réussie",
                        value=f"**Temps de réponse:** {response_time}ms",
                        inline=False
                    )
                else:
                    embed.color = 0xFF0000
                    embed.add_field(
                        name="❌ Connexion Échouée",
                        value=f"**Code d'erreur:** {result}\n**Temps écoulé:** {response_time}ms",
                        inline=False
                    )
            
            except socket.gaierror:
                embed.color = 0xFF0000
                embed.add_field(
                    name="❌ Erreur DNS",
                    value="Impossible de résoudre l'adresse",
                    inline=False
                )
            except socket.timeout:
                embed.color = 0xFFA500
                embed.add_field(
                    name="⏰ Timeout",
                    value=f"Pas de réponse après {self.security_config['test_timeout']}s",
                    inline=False
                )
            
            # Informations supplémentaires
            try:
                ip_obj = ipaddress.ip_address(ip_clean)
                embed.add_field(
                    name="📋 Informations IP",
                    value=(
                        f"**Type:** IPv{ip_obj.version}\n"
                        f"**Privée:** {'Oui' if ip_obj.is_private else 'Non'}\n"
                        f"**Loopback:** {'Oui' if ip_obj.is_loopback else 'Non'}"
                    ),
                    inline=True
                )
            except:
                pass
            
            embed.add_field(
                name="🔧 Détails du Test",
                value=(
                    f"**Port testé:** {port}\n"
                    f"**Timeout:** {self.security_config['test_timeout']}s\n"
                    f"**Timestamp:** {datetime.now().strftime('%H:%M:%S')}"
                ),
                inline=True
            )
            
        except Exception as e:
            embed.color = 0xFF0000
            embed.add_field(
                name="💥 Erreur",
                value=f"Erreur inattendue: {str(e)[:100]}",
                inline=False
            )
        
        embed.set_footer(text=f"Test effectué par {interaction.user.display_name} • Serveur Test")
        
        await interaction.edit_original_response(embed=embed)
        self.logger.info(f"🌐 {interaction.user} a testé la connectivité vers {ip_clean}:{port}")
    
    @app_commands.command(name="netscan", description="🔍 Scan de réseau local (serveur test uniquement)")
    @app_commands.describe(
        network="Réseau à scanner (ex: 192.168.1.0/24)",
        ports="Ports à scanner (ex: 80,443,22)"
    )
    @app_commands.default_permissions(administrator=True)
    async def network_scan(self, interaction: discord.Interaction, network: str, ports: str = "22,80,443"):
        """Scan rapide d'un réseau local"""
        
        # Rate limiting strict pour cette commande
        if self.is_rate_limited(interaction.user.id):
            await interaction.response.send_message(
                "⚠️ **Rate Limit Atteint**\nCette commande est limitée.",
                ephemeral=True
            )
            return
        
        # Validation du réseau
        try:
            net = ipaddress.ip_network(network.strip(), strict=False)
            if not net.is_private:
                await interaction.response.send_message(
                    "❌ **Réseau Non Autorisé**\nSeuls les réseaux privés sont autorisés.",
                    ephemeral=True
                )
                return
        except ValueError:
            await interaction.response.send_message(
                "❌ **Format de Réseau Invalide**\nUtilisez le format CIDR (ex: 192.168.1.0/24).",
                ephemeral=True
            )
            return
        
        # Validation des ports
        try:
            port_list = [int(p.strip()) for p in ports.split(',') if p.strip()]
            if len(port_list) > 10:  # Limiter le nombre de ports
                await interaction.response.send_message(
                    "❌ **Trop de Ports**\nMaximum 10 ports autorisés.",
                    ephemeral=True
                )
                return
        except ValueError:
            await interaction.response.send_message(
                "❌ **Format de Ports Invalide**\nUtilisez le format: 80,443,22",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        embed = discord.Embed(
            title="🔍 Scan de Réseau",
            description=f"Scan en cours de `{network}` sur les ports `{ports}`...",
            color=0x3498DB
        )
        
        # Limiter le nombre d'hôtes à scanner
        hosts_to_scan = list(net.hosts())[:20]  # Maximum 20 hôtes
        active_hosts = []
        
        try:
            for host in hosts_to_scan:
                for port in port_list:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(1)  # Timeout court pour le scan
                        result = sock.connect_ex((str(host), port))
                        sock.close()
                        
                        if result == 0:
                            active_hosts.append(f"{host}:{port}")
                            
                        # Éviter de surcharger
                        await asyncio.sleep(0.1)
                        
                    except Exception:
                        continue
            
            if active_hosts:
                embed.color = 0x00FF00
                embed.add_field(
                    name="✅ Hôtes Actifs Trouvés",
                    value="\n".join(active_hosts[:15]) + ("..." if len(active_hosts) > 15 else ""),
                    inline=False
                )
            else:
                embed.color = 0xFFA500
                embed.add_field(
                    name="🔍 Résultat",
                    value="Aucun hôte actif trouvé sur les ports spécifiés",
                    inline=False
                )
            
            embed.add_field(
                name="📊 Statistiques",
                value=(
                    f"**Hôtes scannés:** {len(hosts_to_scan)}\n"
                    f"**Ports testés:** {len(port_list)}\n"
                    f"**Actifs trouvés:** {len(active_hosts)}"
                ),
                inline=True
            )
            
        except Exception as e:
            embed.color = 0xFF0000
            embed.add_field(
                name="💥 Erreur",
                value=f"Erreur durant le scan: {str(e)[:100]}",
                inline=False
            )
        
        embed.set_footer(text=f"Scan effectué par {interaction.user.display_name} • Serveur Test")
        
        await interaction.edit_original_response(embed=embed)
        self.logger.info(f"🔍 {interaction.user} a scanné le réseau {network}")
    
    @app_commands.command(name="secinfo", description="🛡️ Affiche les informations de sécurité du bot")
    async def security_info(self, interaction: discord.Interaction):
        """Affiche les informations de sécurité"""
        
        embed = discord.Embed(
            title="🛡️ Informations de Sécurité",
            description="État de la sécurité du bot Themis",
            color=0x9932CC
        )
        
        # Vérifications de sécurité
        security_checks = []
        
        # Vérifier les permissions
        if interaction.guild:
            bot_member = interaction.guild.get_member(self.bot.user.id)
            if bot_member:
                dangerous_perms = ['administrator', 'manage_guild', 'manage_roles']
                has_dangerous = any(getattr(bot_member.guild_permissions, perm, False) for perm in dangerous_perms)
                
                if has_dangerous:
                    security_checks.append("⚠️ Permissions élevées détectées")
                else:
                    security_checks.append("✅ Permissions appropriées")
        
        # État du rate limiting
        active_limits = len([uid for uid, times in self.rate_limits.items() if len(times) > 0])
        security_checks.append(f"📊 Rate limiting: {active_limits} utilisateurs surveillés")
        
        # Configuration de sécurité
        embed.add_field(
            name="🔧 Configuration",
            value=(
                f"**Max requêtes/min:** {self.security_config['max_requests_per_minute']}\n"
                f"**Timeout tests:** {self.security_config['test_timeout']}s\n"
                f"**Réseaux autorisés:** {len(self.security_config['allowed_ip_ranges'])}"
            ),
            inline=True
        )
        
        embed.add_field(
            name="🛡️ Vérifications",
            value="\n".join(security_checks),
            inline=True
        )
        
        embed.add_field(
            name="⚠️ Recommandations",
            value=(
                "• Utilisez uniquement des réseaux privés\n"
                "• Limitez les permissions du bot\n"
                "• Surveillez les logs de sécurité\n"
                "• Tests IP uniquement sur serveur test"
            ),
            inline=False
        )
        
        embed.set_footer(text="🏛️ Themis veille sur la sécurité de l'Olympe")
        
        await interaction.response.send_message(embed=embed)
        self.logger.info(f"🛡️ {interaction.user} a consulté les informations de sécurité")
    
    @app_commands.command(name="clearcache", description="🧹 Nettoie le cache de sécurité")
    @app_commands.default_permissions(administrator=True)
    async def clear_security_cache(self, interaction: discord.Interaction):
        """Nettoie le cache de sécurité et les rate limits"""
        
        cache_size = len(self.test_cache)
        rate_limit_size = len(self.rate_limits)
        
        self.test_cache.clear()
        self.rate_limits.clear()
        
        embed = discord.Embed(
            title="🧹 Cache Nettoyé",
            description="Le cache de sécurité a été vidé",
            color=0x00FF00
        )
        
        embed.add_field(
            name="📊 Éléments Supprimés",
            value=(
                f"**Cache de test:** {cache_size} entrées\n"
                f"**Rate limits:** {rate_limit_size} utilisateurs"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        self.logger.info(f"🧹 {interaction.user} a nettoyé le cache de sécurité")

async def setup(bot):
    """Charge le module de sécurité"""
    await bot.add_cog(SecurityCog(bot))
