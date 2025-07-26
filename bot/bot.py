import discord
from discord.ext import commands
import asyncio
import os
from datetime import datetime
from bot.utils.database import Database
from bot.utils.scheduler import MatchScheduler
from bot.utils.translations import get_translation
from bot.commands.admin import AdminCommands
from bot.commands.match import MatchCommands
from bot.commands.help import HelpCommands
from bot.commands.advanced import AdvancedCommands

class XSportBSBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        # Initialize database and scheduler
        self.db = Database()
        self.scheduler = MatchScheduler(self)
        
        # Language settings
        self.languages = ['es', 'en', 'pt']  # Spanish primary, English, Portuguese
        self.default_language = 'es'
        
        # Server settings
        self.log_channels = {}
        self.allowed_channels = {}
        
    async def setup_hook(self):
        """Setup hook called when bot is starting"""
        # Add command cogs
        await self.add_cog(AdminCommands(self))
        await self.add_cog(MatchCommands(self))
        await self.add_cog(HelpCommands(self))
        await self.add_cog(AdvancedCommands(self))
        
        # Start scheduler
        self.scheduler.start()
        
        # Start announcement checker
        asyncio.create_task(self.check_scheduled_announcements())
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} commands")
        except Exception as e:
            print(f"Failed to sync commands: {e}")
    
    async def on_ready(self):
        """Called when bot is ready"""
        print(f'{self.user} has connected to Discord!')
        print(f'Bot is ready and serving {len(self.guilds)} guilds')
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="xSportBS Server"
        )
        await self.change_presence(activity=activity)
    
    async def on_guild_join(self, guild):
        """Called when bot joins a new guild"""
        self.db.log_event('guild_join', guild.id, f"Joined guild: {guild.name}")
        print(f"Joined new guild: {guild.name} (ID: {guild.id})")
    
    async def on_guild_remove(self, guild):
        """Called when bot leaves a guild"""
        self.db.log_event('guild_leave', guild.id, f"Left guild: {guild.name}")
        print(f"Left guild: {guild.name} (ID: {guild.id})")
    
    async def on_member_join(self, member):
        """Called when a member joins a guild"""
        self.db.log_member_activity(member.guild.id, member.id, 'join')
        self.db.log_event('member_join', member.guild.id, f"Member joined: {member.display_name}")
    
    async def on_member_remove(self, member):
        """Called when a member leaves a guild"""
        self.db.log_member_activity(member.guild.id, member.id, 'leave')
        self.db.log_event('member_leave', member.guild.id, f"Member left: {member.display_name}")
    
    async def on_message(self, message):
        """Called when a message is sent"""
        if message.author.bot:
            return
        
        # Log member activity
        self.db.log_member_activity(message.guild.id, message.author.id, 'message')
        
        # Process commands if any
        await self.process_commands(message)
    
    async def check_scheduled_announcements(self):
        """Check and send scheduled announcements"""
        while not self.is_closed():
            try:
                pending_announcements = self.db.get_pending_announcements()
                
                for announcement in pending_announcements:
                    announcement_id, guild_id, channel_id, message, schedule_time = announcement
                    
                    guild = self.get_guild(guild_id)
                    if guild:
                        channel = guild.get_channel(channel_id)
                        if channel:
                            embed = discord.Embed(
                                title="📢 Anuncio Programado",
                                description=message,
                                color=0x0099ff,
                                timestamp=datetime.utcnow()
                            )
                            
                            try:
                                await channel.send(embed=embed)
                                self.db.mark_announcement_sent(announcement_id)
                                self.db.log_event('announcement_sent', guild_id, f"Sent scheduled announcement to #{channel.name}")
                            except discord.Forbidden:
                                print(f"No permission to send announcement in {channel.name}")
                            except Exception as e:
                                print(f"Error sending announcement: {e}")
                
                # Check every minute
                await asyncio.sleep(60)
                
            except Exception as e:
                print(f"Error checking announcements: {e}")
                await asyncio.sleep(60)
    
    async def on_message(self, message):
        """Called when a message is sent"""
        if message.author == self.user:
            # Log bot messages in allowed channels
            if message.guild and message.guild.id in self.log_channels:
                log_channel_id = self.log_channels[message.guild.id]
                log_channel = self.get_channel(log_channel_id)
                if log_channel and log_channel != message.channel:
                    embed = discord.Embed(
                        title="Bot Activity",
                        description=f"Bot spoke in {message.channel.mention}",
                        color=0x00ff00,
                        timestamp=datetime.utcnow()
                    )
                    try:
                        await log_channel.send(embed=embed)
                    except:
                        pass
        
        await self.process_commands(message)
    
    def get_user_language(self, interaction):
        """Get user's preferred language from interaction locale"""
        locale = str(interaction.locale)
        if locale.startswith('es'):
            return 'es'
        elif locale.startswith('en'):
            return 'en'
        elif locale.startswith('pt'):
            return 'pt'
        else:
            return self.default_language
    
    async def send_dm_to_role(self, guild, role_id, content, language='es'):
        """Send DM to all members of a role"""
        role = guild.get_role(role_id)
        if not role:
            return 0
        
        sent_count = 0
        for member in role.members:
            try:
                await member.send(content)
                sent_count += 1
                await asyncio.sleep(1)  # Rate limiting
            except:
                continue
        
        return sent_count
    
    def is_admin(self, user, guild):
        """Check if user is admin"""
        member = guild.get_member(user.id)
        if not member:
            return False
        
        return (member.guild_permissions.administrator or 
                member.guild_permissions.manage_guild or
                member.guild_permissions.manage_channels)
    
    def can_use_channel(self, channel_id, guild_id):
        """Check if bot can be used in specific channel"""
        if guild_id not in self.allowed_channels:
            return True
        
        allowed = self.allowed_channels[guild_id]
        return channel_id in allowed if allowed else True
