# xSportBS Discord Bot

## Overview

xSportBS is a powerful multilingual Discord bot designed for server management and protection, with a specialized focus on match management systems. The bot supports Spanish (primary), English, and Portuguese languages with automatic timezone conversions and comprehensive administrative tools.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Web Dashboard**: Flask-based web interface with Bootstrap 5 styling
- **Responsive Design**: Mobile-friendly layout with language switcher
- **Real-time Stats**: Dynamic bot statistics display via API endpoints
- **Multilingual Support**: Complete translation system for ES/EN/PT

### Backend Architecture
- **Discord.py Framework**: Modern slash command system with cogs architecture
- **Modular Design**: Separated command categories (Admin, Match, Help)
- **Asynchronous Processing**: Event-driven architecture with async/await patterns
- **Keep-Alive System**: Flask server for continuous hosting on Replit

### Database Architecture
- **SQLite Database**: Local file-based storage for simplicity
- **Tables**:
  - `command_logs`: Track slash command usage
  - `event_logs`: Bot activity and events
  - `bot_settings`: Guild-specific configurations
- **Thread-Safe Operations**: Database locking for concurrent access

## Key Components

### Bot Core (`bot/bot.py`)
- **XSportBSBot Class**: Main bot instance extending discord.Bot
- **Cog Management**: Modular command loading system
- **Language Detection**: User language preference handling
- **Guild Settings**: Per-server configuration management

### Command System
- **Admin Commands** (`bot/commands/admin.py`):
  - Channel management and logging configuration
  - User/role DM functionality
  - Custom embed creation with image support
- **Match Commands** (`bot/commands/match.py`):
  - Match creation with team listings and scheduling
  - Automatic reminder system (10 and 3 minutes before)
  - Match ending and active match listing
- **Help Commands** (`bot/commands/help.py`):
  - Comprehensive command documentation
  - Language-specific help responses

### Utility Systems
- **Translation Engine** (`bot/utils/translations.py`):
  - Complete translation dictionaries for 3 languages
  - Dynamic content localization
- **Scheduler** (`bot/utils/scheduler.py`):
  - APScheduler integration for match reminders
  - Timezone-aware scheduling
- **Database Handler** (`bot/utils/database.py`):
  - SQLite operations with connection pooling
  - Automatic table initialization

### Web Dashboard (`web/`)
- **Flask Application**: Lightweight web interface
- **Templates**: HTML templates with dynamic content
- **Static Assets**: CSS/JS for responsive design
- **API Endpoints**: Bot statistics and status information

## Data Flow

### Command Processing
1. User inputs slash command
2. Language detection from user/guild settings
3. Permission validation (admin-only commands)
4. Command execution with database logging
5. Localized response with translation buttons

### Match Management Flow
1. Admin creates match with `/creatematch`
2. Match stored in memory with unique ID
3. Scheduler creates reminder jobs (10 and 3 minutes before)
4. Reminders sent via DM to target roles
5. Match can be ended with `/endmatch`

### Database Operations
1. All commands logged with timestamps
2. Guild settings stored persistently
3. Thread-safe operations ensure data integrity
4. Automatic database initialization on startup

## External Dependencies

### Core Dependencies
- **discord.py**: Discord API interaction
- **Flask**: Web dashboard framework
- **APScheduler**: Task scheduling for reminders
- **SQLite3**: Database operations (built-in)

### Frontend Dependencies
- **Bootstrap 5**: CSS framework for responsive design
- **Font Awesome**: Icon library
- **Vanilla JavaScript**: Language switching and API calls

### Environment Requirements
- **BOT_TOKEN**: Discord bot token (Replit secret)
- **Python 3.8+**: Runtime environment

## Deployment Strategy

### Replit Hosting
- **Keep-Alive System**: Flask server prevents bot sleeping
- **Port Configuration**: Web dashboard on port 5000
- **Environment Variables**: Bot token stored in Replit secrets
- **Continuous Running**: Threading system keeps both bot and web server active

### File Structure
```
├── main.py                 # Entry point
├── keep_alive.py          # Web server for hosting
├── bot/
│   ├── bot.py            # Main bot class
│   ├── commands/         # Command modules
│   └── utils/            # Utility modules
└── web/
    ├── app.py            # Flask application
    ├── templates/        # HTML templates
    └── static/           # CSS/JS assets
```

### Recent Major Updates (July 2025)

#### Advanced Sports Management Features Added
- **Points System**: Automatic team scoring (3 points for wins, 1 for draws)
- **Match Results Recording**: Complete match outcome tracking with statistics
- **Tournament Management**: Create and manage multiple tournaments
- **Team Statistics**: Comprehensive win/loss/draw tracking and rankings
- **Match History**: Detailed record of all completed matches
- **Scheduled Announcements**: Program announcements for future delivery
- **Member Activity Tracking**: Monitor joins, leaves, and messaging activity

#### Enhanced Database Schema
New tables added:
- `teams`: Team statistics and points tracking
- `match_results`: Complete match outcome records
- `tournaments`: Tournament management system
- `scheduled_announcements`: Automated announcement system
- `member_activity`: User activity logging

#### New Slash Commands
- `/recordresult`: Record match scores and update team stats
- `/teamstats`: Display team rankings and statistics
- `/matchhistory`: Show recent match results
- `/createtournament`: Create tournament competitions
- `/tournaments`: List active tournaments
- `/scheduleannouncement`: Program future announcements

### Startup Sequence
1. `main.py` starts keep-alive web server
2. Bot token retrieved from environment
3. XSportBSBot instance created and configured
4. Advanced commands cog loaded with sports management features
5. Cogs loaded and slash commands synced
6. Scheduled announcement checker started
7. Both systems run concurrently in separate threads

### Database Initialization
- SQLite database created automatically on first run
- Tables initialized with proper schema including new advanced features
- Thread-safe operations ensure data consistency
- Automatic team creation and statistics tracking
- No external database dependencies required