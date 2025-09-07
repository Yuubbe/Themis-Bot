"""
🏛️ Module de Divertissement pour Themis-Bot
Commandes slash pour détendre l'atmosphère du royaume
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
import random
import asyncio
from datetime import datetime

class FunCog(commands.Cog):
    """Module de commandes de divertissement"""
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
    
    @app_commands.command(name="quote", description="📜 Génère une citation de Thémis")
    async def divine_quote(self, interaction: discord.Interaction):
        """Génère une citation inspirante de la déesse Thémis"""
        
        quotes = [
            "« Il y a une loi que même les dieux ne sauraient briser sans causer la ruine : celle de l'ordre. »",
            "« La justice est la vérité en action, et l'ordre est son temple. »",
            "« Chaque canal est un sanctuaire dédié à une vérité spécifique. »",
            "« Prenez garde, car de tels actes ne mènent qu'à la confusion. »",
            "« La confusion est le prélude de votre destruction. »",
            "« Celui qui sème le désordre récolte l'exil. »",
            "« L'ordre doit être préservé, même au prix de l'exil. »",
            "« Les actes les plus graves appellent les sanctions les plus lourdes. »",
            "« Même les plus grands pécheurs peuvent trouver la rédemption. »",
            "« La réflexion précède toujours l'action sage. »",
            "« L'apparence révèle souvent l'âme. »",
            "« Dans le silence naît la sagesse, dans l'ordre prospère la justice. »",
            "« Que ce bannissement serve d'exemple à tous. »",
            "« La parole peut de nouveau couler librement. »",
            "« Thémis veille avec une vigilance parfaite. »"
        ]
        
        selected_quote = random.choice(quotes)
        
        embed = discord.Embed(
            title="📜 Paroles de Thémis",
            description=selected_quote,
            color=0x9932CC
        )
        
        embed.set_footer(text="⚖️ Sagesse divine dispensée par la déesse de la Justice")
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1234567890.png")  # Placeholder
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="dice", description="🎲 Lance des dés")
    @app_commands.describe(
        sides="Nombre de faces du dé (défaut: 6)",
        count="Nombre de dés à lancer (défaut: 1)"
    )
    async def roll_dice(self, interaction: discord.Interaction, sides: int = 6, count: int = 1):
        """Lance des dés avec le nombre de faces spécifié"""
        
        if sides < 2 or sides > 1000:
            await interaction.response.send_message("❌ Le dé doit avoir entre 2 et 1000 faces.", ephemeral=True)
            return
        
        if count < 1 or count > 20:
            await interaction.response.send_message("❌ Vous pouvez lancer entre 1 et 20 dés.", ephemeral=True)
            return
        
        results = [random.randint(1, sides) for _ in range(count)]
        total = sum(results)
        
        embed = discord.Embed(
            title="🎲 Jugement du Hasard",
            description="Les dés de la destinée ont parlé !",
            color=0x32CD32
        )
        
        if count == 1:
            embed.add_field(
                name=f"🎯 Résultat (d{sides})",
                value=f"**{results[0]}**",
                inline=True
            )
        else:
            embed.add_field(
                name=f"🎯 Résultats ({count}d{sides})",
                value=f"{' + '.join(map(str, results))} = **{total}**",
                inline=False
            )
            
            embed.add_field(
                name="📊 Statistiques",
                value=f"Total: **{total}**\nMoyenne: **{total/count:.1f}**",
                inline=True
            )
        
        embed.add_field(
            name="🏛️ Oracle de Thémis",
            value="« Le hasard n'est que l'ordre que nous ne comprenons pas encore »",
            inline=False
        )
        
        embed.set_footer(text=f"Lancé par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="coinflip", description="🪙 Lance une pièce")
    async def flip_coin(self, interaction: discord.Interaction):
        """Lance une pièce de monnaie"""
        
        result = random.choice(["pile", "face"])
        emoji = "🔴" if result == "pile" else "🔵"
        
        embed = discord.Embed(
            title="🪙 Pièce de la Destinée",
            description=f"{emoji} La pièce tombe sur **{result.upper()}** !",
            color=0xFFD700
        )
        
        embed.add_field(
            name="🏛️ Présage de Thémis",
            value="« Dans les choix les plus simples se cachent parfois les plus grandes vérités »",
            inline=False
        )
        
        embed.set_footer(text=f"Lancé par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="poll", description="📊 Crée un sondage")
    @app_commands.describe(
        question="La question du sondage",
        option1="Première option",
        option2="Deuxième option",
        option3="Troisième option (optionnelle)",
        option4="Quatrième option (optionnelle)"
    )
    async def create_poll(self, interaction: discord.Interaction, question: str, option1: str, option2: str, option3: str = None, option4: str = None):
        """Crée un sondage avec réactions"""
        
        options = [option1, option2]
        if option3:
            options.append(option3)
        if option4:
            options.append(option4)
        
        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
        
        embed = discord.Embed(
            title="📊 Consultation Citoyenne",
            description=f"**{question}**",
            color=0x3498DB
        )
        
        for i, option in enumerate(options):
            embed.add_field(
                name=f"{emojis[i]} Option {i+1}",
                value=option,
                inline=False
            )
        
        embed.add_field(
            name="🏛️ Instruction de Thémis",
            value="« Que chaque voix soit entendue dans cette consultation démocratique »",
            inline=False
        )
        
        embed.set_footer(text=f"Sondage créé par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
        
        # Récupérer le message pour ajouter les réactions
        message = await interaction.original_response()
        for i in range(len(options)):
            await message.add_reaction(emojis[i])
    
    @app_commands.command(name="choose", description="🎯 Choix aléatoire entre plusieurs options")
    @app_commands.describe(choices="Options séparées par des virgules")
    async def random_choice(self, interaction: discord.Interaction, choices: str):
        """Fait un choix aléatoire parmi les options données"""
        
        options = [choice.strip() for choice in choices.split(",")]
        
        if len(options) < 2:
            await interaction.response.send_message("❌ Veuillez fournir au moins 2 options séparées par des virgules.", ephemeral=True)
            return
        
        if len(options) > 20:
            await interaction.response.send_message("❌ Maximum 20 options autorisées.", ephemeral=True)
            return
        
        chosen = random.choice(options)
        
        embed = discord.Embed(
            title="🎯 Décision Divine",
            description=f"Parmi toutes les possibilités, Thémis a choisi :",
            color=0xFF6B35
        )
        
        embed.add_field(
            name="✨ Choix de la Destinée",
            value=f"**{chosen}**",
            inline=False
        )
        
        embed.add_field(
            name="📋 Options considérées",
            value=f"{len(options)} possibilités : {', '.join(options)}",
            inline=False
        )
        
        embed.add_field(
            name="🏛️ Sagesse de Thémis",
            value="« Parfois, laisser le destin décider révèle la voie la plus juste »",
            inline=False
        )
        
        embed.set_footer(text=f"Choix demandé par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="8ball", description="🔮 Pose une question à la boule magique")
    @app_commands.describe(question="Ta question pour l'oracle")
    async def magic_8ball(self, interaction: discord.Interaction, question: str):
        """Répond à une question avec la sagesse de la boule magique"""
        
        responses = [
            "🟢 C'est certain.",
            "🟢 Sans aucun doute.",
            "🟢 Oui, absolument.",
            "🟢 Tu peux compter dessus.",
            "🟢 Comme je le vois, oui.",
            "🟢 Il est probable.",
            "🟡 Les perspectives sont bonnes.",
            "🟡 Oui.",
            "🟡 Les signes pointent vers oui.",
            "🟡 Réponse floue, essaie encore.",
            "🟡 Redemande plus tard.",
            "🟡 Mieux vaut ne pas te le dire maintenant.",
            "🟡 Impossible de prédire maintenant.",
            "🟡 Concentre-toi et redemande.",
            "🔴 N'y compte pas.",
            "🔴 Ma réponse est non.",
            "🔴 Mes sources disent non.",
            "🔴 Les perspectives ne sont pas si bonnes.",
            "🔴 Très douteux."
        ]
        
        answer = random.choice(responses)
        
        embed = discord.Embed(
            title="🔮 Oracle de Thémis",
            description=f"**Question :** {question}",
            color=0x9932CC
        )
        
        embed.add_field(
            name="✨ Réponse de l'Oracle",
            value=answer,
            inline=False
        )
        
        embed.add_field(
            name="🏛️ Note de Thémis",
            value="« L'avenir appartient à ceux qui prennent leurs propres décisions »",
            inline=False
        )
        
        embed.set_footer(text=f"Oracle consulté par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    """Charge le module de divertissement"""
    await bot.add_cog(FunCog(bot))
