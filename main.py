import os
import asyncio
from bot.bot import XSportBSBot
from keep_alive import keep_alive

def main():
    """Main entry point for the Discord bot"""
    # Start the keep-alive server
    keep_alive()
    
    # Get bot token from Replit secrets
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("ERROR: BOT_TOKEN not found in environment variables!")
        print("Please set BOT_TOKEN in Replit secrets with your Discord bot token.")
        return
    
    # Create and run the bot
    bot = XSportBSBot()
    
    try:
        bot.run(token)
    except Exception as e:
        print(f"Error running bot: {e}")
        print("Make sure your BOT_TOKEN is valid and the bot has proper permissions.")

if __name__ == "__main__":
    main()
