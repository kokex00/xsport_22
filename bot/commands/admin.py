import discord
from discord.ext import commands
from discord import app_commands
from bot.utils.translations import get_translation
from datetime import datetime
import asyncio

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(
        name="setlogchannel",
        description="Set the channel for bot activity logs"
    )
    @app_commands.describe(channel="The channel to log bot activities")
    async def set_log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Set log channel for bot activities"""
        if not self.bot.is_admin(interaction.user, interaction.guild):
            lang = self.bot.get_user_language(interaction)
            embed = discord.Embed(
                title=get_translation("error", lang),
                description=get_translation("admin_only", lang),
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        self.bot.log_channels[interaction.guild.id] = channel.id
        lang = self.bot.get_user_language(interaction)
        
        embed = discord.Embed(
            title=get_translation("success", lang),
            description=get_translation("log_channel_set", lang).format(channel=channel.mention),
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        
        await interaction.response.send_message(embed=embed)
        self.bot.db.log_command('setlogchannel', interaction.user.id, interaction.guild.id)
    
    @app_commands.command(
        name="setchannels",
        description="Set allowed channels for bot usage"
    )
    @app_commands.describe(channels="Channels where bot can be used (space separated IDs)")
    async def set_channels(self, interaction: discord.Interaction, channels: str):
        """Set allowed channels for bot usage"""
        if not self.bot.is_admin(interaction.user, interaction.guild):
            lang = self.bot.get_user_language(interaction)
            embed = discord.Embed(
                title=get_translation("error", lang),
                description=get_translation("admin_only", lang),
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            channel_ids = [int(ch.strip()) for ch in channels.split()]
            self.bot.allowed_channels[interaction.guild.id] = channel_ids
            
            lang = self.bot.get_user_language(interaction)
            channel_mentions = []
            for ch_id in channel_ids:
                channel = self.bot.get_channel(ch_id)
                if channel:
                    channel_mentions.append(channel.mention)
            
            embed = discord.Embed(
                title=get_translation("success", lang),
                description=get_translation("channels_set", lang).format(
                    channels=", ".join(channel_mentions)
                ),
                color=0x00ff00,
                timestamp=datetime.utcnow()
            )
            
            await interaction.response.send_message(embed=embed)
            self.bot.db.log_command('setchannels', interaction.user.id, interaction.guild.id)
            
        except ValueError:
            lang = self.bot.get_user_language(interaction)
            embed = discord.Embed(
                title=get_translation("error", lang),
                description=get_translation("invalid_channel_ids", lang),
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(
        name="dmuser",
        description="Send a direct message to a specific user"
    )
    @app_commands.describe(
        user="The user to send the DM to",
        message="The message to send"
    )
    async def dm_user(self, interaction: discord.Interaction, user: discord.Member, message: str):
        """Send DM to specific user"""
        if not self.bot.is_admin(interaction.user, interaction.guild):
            lang = self.bot.get_user_language(interaction)
            embed = discord.Embed(
                title=get_translation("error", lang),
                description=get_translation("admin_only", lang),
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        lang = self.bot.get_user_language(interaction)
        
        try:
            await user.send(message)
            
            embed = discord.Embed(
                title=get_translation("success", lang),
                description=get_translation("dm_sent", lang).format(user=user.mention),
                color=0x00ff00,
                timestamp=datetime.utcnow()
            )
            
            await interaction.response.send_message(embed=embed)
            self.bot.db.log_command('dmuser', interaction.user.id, interaction.guild.id)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title=get_translation("error", lang),
                description=get_translation("dm_failed", lang),
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(
        name="dmrole",
        description="Send a direct message to all members of a role"
    )
    @app_commands.describe(
        role="The role to send DMs to",
        message="The message to send"
    )
    async def dm_role(self, interaction: discord.Interaction, role: discord.Role, message: str):
        """Send DM to all members of a role"""
        if not self.bot.is_admin(interaction.user, interaction.guild):
            lang = self.bot.get_user_language(interaction)
            embed = discord.Embed(
                title=get_translation("error", lang),
                description=get_translation("admin_only", lang),
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        lang = self.bot.get_user_language(interaction)
        
        await interaction.response.defer()
        
        sent_count = await self.bot.send_dm_to_role(interaction.guild, role.id, message, lang)
        
        embed = discord.Embed(
            title=get_translation("success", lang),
            description=get_translation("role_dm_sent", lang).format(
                count=sent_count,
                role=role.mention
            ),
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        
        await interaction.followup.send(embed=embed)
        self.bot.db.log_command('dmrole', interaction.user.id, interaction.guild.id)
    
    @app_commands.command(
        name="customembed",
        description="Send a custom embed with optional image"
    )
    @app_commands.describe(
        title="Embed title",
        description="Embed description",
        color="Embed color (hex format, e.g., #ff0000)",
        image="Image attachment"
    )
    async def custom_embed(
        self, 
        interaction: discord.Interaction, 
        title: str, 
        description: str, 
        color: str = "#0099ff",
        image: discord.Attachment = None
    ):
        """Send custom embed with optional image"""
        if not self.bot.is_admin(interaction.user, interaction.guild):
            lang = self.bot.get_user_language(interaction)
            embed = discord.Embed(
                title=get_translation("error", lang),
                description=get_translation("admin_only", lang),
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Parse color
            if color.startswith('#'):
                color_int = int(color[1:], 16)
            else:
                color_int = int(color, 16)
        except ValueError:
            color_int = 0x0099ff
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=color_int,
            timestamp=datetime.utcnow()
        )
        
        if image:
            # Validate image type
            if image.content_type and image.content_type.startswith('image/'):
                embed.set_image(url=image.url)
            else:
                lang = self.bot.get_user_language(interaction)
                error_embed = discord.Embed(
                    title=get_translation("error", lang),
                    description=get_translation("invalid_image", lang),
                    color=0xff0000
                )
                await interaction.response.send_message(embed=error_embed, ephemeral=True)
                return
        
        await interaction.response.send_message(embed=embed)
        self.bot.db.log_command('customembed', interaction.user.id, interaction.guild.id)
