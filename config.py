import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.1')
    BOT_CHANNEL = "bot"
    COMMAND_PREFIX = "/"
    LOG_FILE = "bot.log"
    
    # Neue Konfigurationsoptionen
    ALLOWED_CHANNELS = ["bot", "bot-config", "bot-commands"]  # Kanäle in denen der Bot reagiert
    MAX_COMMANDS_PER_SERVER = 50  # Maximale Anzahl eigener Commands pro Server
    COMMAND_COOLDOWN = 3  # Sekunden zwischen Command-Ausführungen
    DEBUG_MODE = False  # Debug-Modus für zusätzliche Logging-Informationen