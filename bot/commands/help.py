import discord
from discord.ext import commands
from discord import app_commands
from bot.utils.translations import get_translation

class HelpCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(
        name="ayuda",
        description="Muestra todos los comandos disponibles y ayuda"
    )
    async def help_command(self, interaction: discord.Interaction):
        """Show all available commands and help"""
        lang = self.bot.get_user_language(interaction)
        
        embed = discord.Embed(
            title=get_translation("help_title", lang),
            description=get_translation("help_description", lang),
            color=0x0099ff,
            timestamp=discord.utils.utcnow()
        )
        
        # Match commands
        match_commands = [
            "**`/creatematch`** - " + get_translation("help_creatematch", lang),
            "**`/endmatch`** - " + get_translation("help_endmatch", lang),
            "**`/listmatches`** - " + get_translation("help_listmatches", lang)
        ]
        
        embed.add_field(
            name=get_translation("match_commands", lang),
            value="\n".join(match_commands),
            inline=False
        )
        
        # Admin commands  
        admin_commands = [
            "**`/setlogchannel`** - " + get_translation("help_setlogchannel", lang),
            "**`/setchannels`** - " + get_translation("help_setchannels", lang),
            "**`/dmuser`** - " + get_translation("help_dmuser", lang),
            "**`/dmrole`** - " + get_translation("help_dmrole", lang),
            "**`/customembed`** - " + get_translation("help_customembed", lang)
        ]
        
        embed.add_field(
            name=get_translation("admin_commands", lang),
            value="\n".join(admin_commands),
            inline=False
        )
        
        # General commands
        general_commands = [
            "**`/ayuda`** - " + get_translation("help_help", lang)
        ]
        
        embed.add_field(
            name=get_translation("general_commands", lang),
            value="\n".join(general_commands),
            inline=False
        )
        
        # Support info
        embed.add_field(
            name=get_translation("support", lang),
            value=get_translation("support_info", lang),
            inline=False
        )
        
        # Server invite
        embed.add_field(
            name=get_translation("server_invite", lang),
            value="https://discord.gg/5BHpgnG8QP",
            inline=False
        )
        
        embed.set_footer(text=get_translation("help_footer", lang))
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        self.bot.db.log_command('ayuda', interaction.user.id, interaction.guild.id)
