import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.1')
    BOT_CHANNEL = "bot"
    COMMAND_PREFIX = "/"
    LOG_FILE = "bot.log"

    # New configuration options
    ALLOWED_CHANNELS = ["bot", "bot-config", "bot-commands"]  # Channels in which the bot responds
    MAX_COMMANDS_PER_SERVER = 50  # Maximum number of custom commands per server
    COMMAND_COOLDOWN = 3  # Seconds between command executions
    DEBUG_MODE = False  # Debug mode for additional logging information
