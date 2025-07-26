import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from bot.utils.translations import get_translation

class MatchScheduler:
    def __init__(self, bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        
    def start(self):
        """Start the scheduler"""
        self.scheduler.start()
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
    
    def schedule_reminder(self, match_id, reminder_time, minutes_before, language='es'):
        """Schedule a match reminder"""
        job_id = f"reminder_{match_id}_{minutes_before}"
        
        self.scheduler.add_job(
            self._send_reminder,
            DateTrigger(run_date=reminder_time),
            args=[match_id, minutes_before, language],
            id=job_id,
            replace_existing=True
        )
    
    async def _send_reminder(self, match_id, minutes_before, language):
        """Send reminder for a match"""
        # Get match info from bot
        match_commands_cog = self.bot.get_cog('MatchCommands')
        if not match_commands_cog or match_id not in match_commands_cog.active_matches:
            return
        
        match_info = match_commands_cog.active_matches[match_id]
        guild = self.bot.get_guild(match_info['guild_id'])
        if not guild:
            return
        
        # Convert mentions to text for DM
        team1_text = await self._convert_mention_to_text(guild, match_info['team1'])
        team2_text = await self._convert_mention_to_text(guild, match_info['team2'])
        
        # Create reminder message
        if language == 'en':
            time_str = match_info['datetime'].strftime("%B %d at %H:%M GMT")
            reminder_msg = f"🔔 **Match Reminder**\n\n**{team1_text} vs {team2_text}**\nStarts in {minutes_before} minutes!\n\n📅 {time_str}"
        elif language == 'pt':
            time_str = match_info['datetime'].strftime("%d de %B às %H:%M")
            reminder_msg = f"🔔 **Lembrete de Partida**\n\n**{team1_text} vs {team2_text}**\nComeça em {minutes_before} minutos!\n\n📅 {time_str}"
        else:  # Spanish
            months_es = {
                1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
                5: "mayo", 6: "junio", 7: "julio", 8: "agosto", 
                9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
            }
            month_name = months_es[match_info['datetime'].month]
            time_str = f"{match_info['datetime'].day} de {month_name} a las {match_info['datetime'].strftime('%H:%M')}"
            reminder_msg = f"🔔 **Recordatorio de Partido**\n\n**{team1_text} vs {team2_text}**\n¡Comienza en {minutes_before} minutos!\n\n📅 {time_str}"
        
        # Send DM reminders to mentioned teams/users
        await self._send_reminder_dm(guild, match_info['team1'], match_info['team2'], reminder_msg)
        
        print(f"Sent {minutes_before}-minute reminder for match {match_id}")
    
    async def _send_reminder_dm(self, guild, team1, team2, message):
        """Send reminder DM to mentioned teams/users"""
        teams = [team1, team2]
        
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
                                await member.send(message)
                                await asyncio.sleep(0.5)  # Rate limiting
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
                            await user.send(message)
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
