import discord
from discord.ext import commands
from discord import app_commands
from bot.utils.translations import get_translation
from datetime import datetime, timedelta
import asyncio

class AdvancedCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.match_votes = {}  # Store ongoing votes
    
    @app_commands.command(
        name="recordresult",
        description="Record match result and update team statistics"
    )
    @app_commands.describe(
        match_id="ID of the match",
        team1_score="Score of team 1",
        team2_score="Score of team 2"
    )
    async def record_result(
        self,
        interaction: discord.Interaction,
        match_id: int,
        team1_score: int,
        team2_score: int
    ):
        """Record match result"""
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
        
        # Get match info
        match_commands_cog = self.bot.get_cog('MatchCommands')
        if not match_commands_cog or match_id not in match_commands_cog.active_matches:
            embed = discord.Embed(
                title=get_translation("error", lang),
                description=get_translation("match_not_found", lang),
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        match_info = match_commands_cog.active_matches[match_id]
        
        # Convert mentions to team names
        team1_name = await self._extract_team_name(interaction.guild, match_info['team1'])
        team2_name = await self._extract_team_name(interaction.guild, match_info['team2'])
        
        # Save result to database
        self.bot.db.save_match_result(
            match_id, 
            interaction.guild.id, 
            team1_name, 
            team2_name, 
            team1_score, 
            team2_score, 
            match_info['datetime']
        )
        
        # Create result embed
        embed = discord.Embed(
            title=get_translation("match_result_recorded", lang),
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        
        # Determine winner and display
        if team1_score > team2_score:
            winner = team1_name
            embed.add_field(name="🏆 " + get_translation("winner", lang), value=winner, inline=False)
        elif team2_score > team1_score:
            winner = team2_name
            embed.add_field(name="🏆 " + get_translation("winner", lang), value=winner, inline=False)
        else:
            embed.add_field(name="🤝 " + get_translation("result", lang), value=get_translation("draw", lang), inline=False)
        
        embed.add_field(
            name=get_translation("final_score", lang),
            value=f"{team1_name} {team1_score} - {team2_score} {team2_name}",
            inline=False
        )
        
        # Remove match from active matches
        del match_commands_cog.active_matches[match_id]
        
        await interaction.response.send_message(embed=embed)
        self.bot.db.log_command('recordresult', interaction.user.id, interaction.guild.id)
    
    @app_commands.command(
        name="teamstats",
        description="Show team statistics and rankings"
    )
    @app_commands.describe(team_name="Specific team name (optional)")
    async def team_stats(self, interaction: discord.Interaction, team_name: str = None):
        """Show team statistics"""
        lang = self.bot.get_user_language(interaction)
        
        # Get team stats from database
        stats = self.bot.db.get_team_stats(interaction.guild.id, team_name)
        
        if not stats:
            embed = discord.Embed(
                title=get_translation("error", lang),
                description=get_translation("no_team_stats", lang),
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            return
        
        embed = discord.Embed(
            title=get_translation("team_statistics", lang),
            color=0x0099ff,
            timestamp=datetime.utcnow()
        )
        
        if team_name:
            # Show specific team stats
            team_data = stats[0]
            embed.add_field(name=get_translation("team", lang), value=team_data[0], inline=False)
            embed.add_field(name=get_translation("points", lang), value=str(team_data[1]), inline=True)
            embed.add_field(name=get_translation("wins", lang), value=str(team_data[2]), inline=True)
            embed.add_field(name=get_translation("losses", lang), value=str(team_data[3]), inline=True)
            embed.add_field(name=get_translation("draws", lang), value=str(team_data[4]), inline=True)
        else:
            # Show rankings
            embed.description = get_translation("team_rankings", lang)
            
            for i, team_data in enumerate(stats[:10], 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                embed.add_field(
                    name=f"{medal} {team_data[0]}",
                    value=f"{get_translation('points', lang)}: {team_data[1]} | {get_translation('wins', lang)}: {team_data[2]} | {get_translation('losses', lang)}: {team_data[3]} | {get_translation('draws', lang)}: {team_data[4]}",
                    inline=False
                )
        
        await interaction.response.send_message(embed=embed)
        self.bot.db.log_command('teamstats', interaction.user.id, interaction.guild.id)
    
    @app_commands.command(
        name="matchhistory",
        description="Show recent match results"
    )
    @app_commands.describe(limit="Number of matches to show (max 20)")
    async def match_history(self, interaction: discord.Interaction, limit: int = 10):
        """Show match history"""
        lang = self.bot.get_user_language(interaction)
        
        if limit > 20:
            limit = 20
        
        results = self.bot.db.get_match_results(interaction.guild.id, limit)
        
        if not results:
            embed = discord.Embed(
                title=get_translation("error", lang),
                description=get_translation("no_match_history", lang),
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            return
        
        embed = discord.Embed(
            title=get_translation("match_history", lang),
            color=0x0099ff,
            timestamp=datetime.utcnow()
        )
        
        for result in results:
            team1, team2, score1, score2, winner, match_date = result
            
            if winner == 'draw':
                result_text = f"🤝 {get_translation('draw', lang)}"
            else:
                result_text = f"🏆 {winner}"
            
            embed.add_field(
                name=f"{team1} {score1} - {score2} {team2}",
                value=f"{result_text}\n📅 {match_date}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
        self.bot.db.log_command('matchhistory', interaction.user.id, interaction.guild.id)
    
    @app_commands.command(
        name="createtournament",
        description="Create a new tournament"
    )
    @app_commands.describe(
        name="Tournament name",
        start_day="Start day (1-31)",
        end_day="End day (1-31)"
    )
    async def create_tournament(
        self,
        interaction: discord.Interaction,
        name: str,
        start_day: int,
        end_day: int
    ):
        """Create a tournament"""
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
        
        # Validate dates
        if not (1 <= start_day <= 31) or not (1 <= end_day <= 31):
            embed = discord.Embed(
                title=get_translation("error", lang),
                description=get_translation("invalid_date", lang),
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Create tournament dates
        now = datetime.now()
        start_date = datetime(now.year, now.month, start_day)
        end_date = datetime(now.year, now.month, end_day)
        
        if start_date < now:
            start_date = start_date.replace(month=now.month + 1 if now.month < 12 else 1, year=now.year + 1 if now.month == 12 else now.year)
            end_date = end_date.replace(month=now.month + 1 if now.month < 12 else 1, year=now.year + 1 if now.month == 12 else now.year)
        
        # Save tournament
        tournament_id = self.bot.db.create_tournament(
            interaction.guild.id,
            name,
            start_date,
            end_date,
            interaction.user.id
        )
        
        embed = discord.Embed(
            title=get_translation("tournament_created", lang),
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name=get_translation("tournament_name", lang), value=name, inline=False)
        embed.add_field(name=get_translation("tournament_id", lang), value=f"#{tournament_id}", inline=True)
        embed.add_field(name=get_translation("start_date", lang), value=start_date.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name=get_translation("end_date", lang), value=end_date.strftime("%d/%m/%Y"), inline=True)
        
        await interaction.response.send_message(embed=embed)
        self.bot.db.log_command('createtournament', interaction.user.id, interaction.guild.id)
    
    @app_commands.command(
        name="tournaments",
        description="Show active tournaments"
    )
    async def list_tournaments(self, interaction: discord.Interaction):
        """List tournaments"""
        lang = self.bot.get_user_language(interaction)
        
        tournaments = self.bot.db.get_tournaments(interaction.guild.id, status='active')
        
        if not tournaments:
            embed = discord.Embed(
                title=get_translation("active_tournaments", lang),
                description=get_translation("no_active_tournaments", lang),
                color=0x0099ff
            )
            await interaction.response.send_message(embed=embed)
            return
        
        embed = discord.Embed(
            title=get_translation("active_tournaments", lang),
            color=0x0099ff,
            timestamp=datetime.utcnow()
        )
        
        for tournament in tournaments:
            t_id, t_name, t_status, t_start, t_end = tournament
            embed.add_field(
                name=f"#{t_id} - {t_name}",
                value=f"📅 {t_start[:10]} - {t_end[:10]}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
        self.bot.db.log_command('tournaments', interaction.user.id, interaction.guild.id)
    
    @app_commands.command(
        name="scheduleannouncement",
        description="Schedule an announcement"
    )
    @app_commands.describe(
        channel="Channel to send announcement",
        message="Message to announce",
        day="Day to send (1-31)",
        hour="Hour to send (0-23)",
        minute="Minute to send (0-59)"
    )
    async def schedule_announcement(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        message: str,
        day: int,
        hour: int,
        minute: int
    ):
        """Schedule an announcement"""
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
        
        # Validate time
        if not (1 <= day <= 31) or not (0 <= hour <= 23) or not (0 <= minute <= 59):
            embed = discord.Embed(
                title=get_translation("error", lang),
                description=get_translation("invalid_time", lang),
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Create schedule time
        now = datetime.now()
        try:
            schedule_time = datetime(now.year, now.month, day, hour, minute)
            if schedule_time < now:
                if now.month == 12:
                    schedule_time = datetime(now.year + 1, 1, day, hour, minute)
                else:
                    schedule_time = datetime(now.year, now.month + 1, day, hour, minute)
        except ValueError:
            embed = discord.Embed(
                title=get_translation("error", lang),
                description=get_translation("invalid_date", lang),
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Schedule announcement
        announcement_id = self.bot.db.schedule_announcement(
            interaction.guild.id,
            channel.id,
            message,
            schedule_time,
            interaction.user.id
        )
        
        embed = discord.Embed(
            title=get_translation("announcement_scheduled", lang),
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name=get_translation("channel", lang), value=channel.mention, inline=True)
        embed.add_field(name=get_translation("schedule_time", lang), value=schedule_time.strftime("%d/%m/%Y %H:%M"), inline=True)
        embed.add_field(name=get_translation("message", lang), value=message[:100] + "..." if len(message) > 100 else message, inline=False)
        
        await interaction.response.send_message(embed=embed)
        self.bot.db.log_command('scheduleannouncement', interaction.user.id, interaction.guild.id)
    
    async def _extract_team_name(self, guild, team_mention):
        """Extract team name from mention or return as is"""
        # Check if it's a role mention
        if team_mention.startswith('<@&') and team_mention.endswith('>'):
            try:
                role_id = int(team_mention[3:-1])
                role = guild.get_role(role_id)
                return role.name if role else team_mention
            except ValueError:
                return team_mention
        
        # Check if it's a user mention
        elif team_mention.startswith('<@') and team_mention.endswith('>'):
            try:
                user_id = int(team_mention[2:-1])
                user = guild.get_member(user_id)
                return user.display_name if user else team_mention
            except ValueError:
                return team_mention
        
        return team_mention