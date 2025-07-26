import discord
from discord.ext import commands
from discord import app_commands
from bot.utils.translations import get_translation
from datetime import datetime, timedelta
import calendar
import asyncio

class MatchCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_matches = {}
    
    @app_commands.command(
        name="creatematch",
        description="Create a new match with teams, date, time and image"
    )
    @app_commands.describe(
        team1="First team mention or name",
        team2="Second team mention or name", 
        day="Day of the month (1-31)",
        hour="Hour (0-23)",
        minute="Minute (0-59)",
        image="Match image from your device"
    )
    async def create_match(
        self,
        interaction: discord.Interaction,
        team1: str,
        team2: str,
        day: int,
        hour: int,
        minute: int,
        image: discord.Attachment = None
    ):
        """Create a new match"""
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
        
        # Validate date/time inputs
        if not (1 <= day <= 31):
            embed = discord.Embed(
                title=get_translation("error", lang),
                description=get_translation("invalid_day", lang),
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if not (0 <= hour <= 23):
            embed = discord.Embed(
                title=get_translation("error", lang),
                description=get_translation("invalid_hour", lang),
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if not (0 <= minute <= 59):
            embed = discord.Embed(
                title=get_translation("error", lang),
                description=get_translation("invalid_minute", lang),
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Create match datetime (current month/year)
        now = datetime.now()
        try:
            match_date = datetime(now.year, now.month, day, hour, minute)
            
            # If date is in the past, assume next month
            if match_date < now:
                if now.month == 12:
                    match_date = datetime(now.year + 1, 1, day, hour, minute)
                else:
                    match_date = datetime(now.year, now.month + 1, day, hour, minute)
        
        except ValueError:
            embed = discord.Embed(
                title=get_translation("error", lang),
                description=get_translation("invalid_date", lang),
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Generate match ID
        match_id = len(self.active_matches) + 1
        
        # Create match embed
        embed = discord.Embed(
            title=get_translation("match_created", lang),
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        
        # Format time based on language
        if lang == 'en':
            time_str = match_date.strftime("%B %d, %Y at %H:%M GMT")
        elif lang == 'pt':
            time_str = match_date.strftime("%d de %B, %Y às %H:%M (Portugal)")
        else:  # Spanish
            months_es = {
                1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
                5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
                9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
            }
            month_name = months_es[match_date.month]
            time_str = f"{match_date.day} de {month_name}, {match_date.year} a las {match_date.strftime('%H:%M')} (España)"
        
        embed.add_field(
            name=get_translation("teams", lang),
            value=f"🔴 {team1}\n🔵 {team2}",
            inline=False
        )
        
        embed.add_field(
            name=get_translation("match_time", lang),
            value=time_str,
            inline=False
        )
        
        embed.add_field(
            name=get_translation("match_id", lang),
            value=f"#{match_id}",
            inline=True
        )
        
        # Add image if provided
        if image and image.content_type and image.content_type.startswith('image/'):
            embed.set_image(url=image.url)
        
        # Store match info
        self.active_matches[match_id] = {
            'team1': team1,
            'team2': team2,
            'datetime': match_date,
            'guild_id': interaction.guild.id,
            'channel_id': interaction.channel.id,
            'creator_id': interaction.user.id,
            'lang': lang
        }
        
        # Schedule reminders (10 and 3 minutes before)
        reminder_10 = match_date - timedelta(minutes=10)
        reminder_3 = match_date - timedelta(minutes=3)
        
        if reminder_10 > datetime.now():
            self.bot.scheduler.schedule_reminder(match_id, reminder_10, 10, lang)
        
        if reminder_3 > datetime.now():
            self.bot.scheduler.schedule_reminder(match_id, reminder_3, 3, lang)
        
        await interaction.response.send_message(embed=embed)
        
        # Send DM to mentioned teams/users
        await self._send_match_dm(interaction.guild, team1, team2, embed, lang)
        
        self.bot.db.log_command('creatematch', interaction.user.id, interaction.guild.id)
    
    @app_commands.command(
        name="endmatch",
        description="End an active match"
    )
    @app_commands.describe(match_id="The ID of the match to end")
    async def end_match(self, interaction: discord.Interaction, match_id: int):
        """End an active match"""
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
        
        if match_id not in self.active_matches:
            embed = discord.Embed(
                title=get_translation("error", lang),
                description=get_translation("match_not_found", lang),
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        match_info = self.active_matches[match_id]
        del self.active_matches[match_id]
        
        embed = discord.Embed(
            title=get_translation("match_ended", lang),
            description=get_translation("match_ended_desc", lang).format(
                team1=match_info['team1'],
                team2=match_info['team2'],
                match_id=match_id
            ),
            color=0xff9900,
            timestamp=datetime.utcnow()
        )
        
        await interaction.response.send_message(embed=embed)
        self.bot.db.log_command('endmatch', interaction.user.id, interaction.guild.id)
    
    @app_commands.command(
        name="listmatches",
        description="List all active matches"
    )
    async def list_matches(self, interaction: discord.Interaction):
        """List all active matches"""
        lang = self.bot.get_user_language(interaction)
        
        if not self.active_matches:
            embed = discord.Embed(
                title=get_translation("active_matches", lang),
                description=get_translation("no_active_matches", lang),
                color=0x0099ff
            )
            await interaction.response.send_message(embed=embed)
            return
        
        embed = discord.Embed(
            title=get_translation("active_matches", lang),
            color=0x0099ff,
            timestamp=datetime.utcnow()
        )
        
        for match_id, match_info in self.active_matches.items():
            match_date = match_info['datetime']
            
            # Format time based on language
            if lang == 'en':
                time_str = match_date.strftime("%B %d at %H:%M GMT")
            elif lang == 'pt':
                time_str = match_date.strftime("%d de %B às %H:%M")
            else:  # Spanish
                months_es = {
                    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
                    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
                    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
                }
                month_name = months_es[match_date.month]
                time_str = f"{match_date.day} de {month_name} a las {match_date.strftime('%H:%M')}"
            
            embed.add_field(
                name=f"#{match_id} - {match_info['team1']} vs {match_info['team2']}",
                value=time_str,
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
        self.bot.db.log_command('listmatches', interaction.user.id, interaction.guild.id)
    
    async def _send_match_dm(self, guild, team1, team2, embed, language):
        """Send DM notifications to mentioned teams/users"""
        teams = [team1, team2]
        
        # Create a modified embed for DM with converted mentions
        dm_embed = discord.Embed(
            title=embed.title,
            color=embed.color,
            timestamp=embed.timestamp
        )
        
        # Convert mentions to text for DM
        team1_text = await self._convert_mention_to_text(guild, team1)
        team2_text = await self._convert_mention_to_text(guild, team2)
        
        # Add fields with converted text
        for field in embed.fields:
            if field.name and "teams" in field.name.lower():
                dm_embed.add_field(
                    name=field.name,
                    value=f"🔴 {team1_text}\n🔵 {team2_text}",
                    inline=field.inline
                )
            else:
                dm_embed.add_field(
                    name=field.name,
                    value=field.value,
                    inline=field.inline
                )
        
        # Copy image if exists
        if embed.image:
            dm_embed.set_image(url=embed.image.url)
        
        for team in teams:
            # Check if it's a role mention (<@&role_id>)
            if team.startswith('<@&') and team.endswith('>'):
                try:
                    role_id = int(team[3:-1])
                    role = guild.get_role(role_id)
                    if role:
                        # Send DM to all members of the role
                        for member in role.members:
                            try:
                                await member.send(embed=dm_embed)
                                await asyncio.sleep(1)  # Rate limiting
                            except:
                                continue
                except ValueError:
                    continue
            
            # Check if it's a user mention (<@user_id>)
            elif team.startswith('<@') and team.endswith('>'):
                try:
                    user_id = int(team[2:-1])
                    user = guild.get_member(user_id)
                    if user:
                        try:
                            await user.send(embed=dm_embed)
                        except:
                            continue
                except ValueError:
                    continue
    
    async def _convert_mention_to_text(self, guild, mention_text):
        """Convert mention to readable text"""
        # Check if it's a role mention (<@&role_id>)
        if mention_text.startswith('<@&') and mention_text.endswith('>'):
            try:
                role_id = int(mention_text[3:-1])
                role = guild.get_role(role_id)
                if role:
                    return f"@{role.name}"
            except ValueError:
                pass
        
        # Check if it's a user mention (<@user_id>)
        elif mention_text.startswith('<@') and mention_text.endswith('>'):
            try:
                user_id = int(mention_text[2:-1])
                user = guild.get_member(user_id)
                if user:
                    return f"@{user.display_name}"
            except ValueError:
                pass
        
        # Return original text if not a mention
        return mention_text
