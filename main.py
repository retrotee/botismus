import discord
from discord.ext import commands
import ollama
from typing import Optional
import json
import os
from dotenv import load_dotenv
from command_manager import CommandManager
import logging
from ai_memory import AIMemory
from user_tracker import UserTracker
import asyncio

# Logging Konfiguration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

# Lade Umgebungsvariablen
load_dotenv()

# Bot und AI Memory Konfiguration
ai_memory = AIMemory()  # Initialisiere AI Memory

# Bot Konfiguration
intents = discord.Intents.all()  # Aktiviere alle Intents
bot = commands.Bot(
    command_prefix='/',
    intents=intents,
    sync_commands=True  # Aktiviere Command-Synchronisation
)
command_manager = CommandManager(bot)

# Ollama Client für KI-Funktionalitäten
async def get_ai_response(prompt: str, guild) -> str:
    # Detailliertes Logging des Prompts
    logging.info(f"\n{'='*50}\nNeue KI-Anfrage\n{'='*50}")
    logging.info(f"User Prompt: {prompt}")
    
    available_channels = [
        c.name for c in guild.channels 
        if isinstance(c, discord.TextChannel)
    ]
    
    # Füge Kontext aus vorherigen Gesprächen hinzu
    recent_context = ai_memory.get_context_for_prompt()
    current_score = ai_memory.get_score()
    success_rate = ai_memory.get_success_rate()
    
    system_prompt = f"""Du bist ein Discord-Bot-Manager mit einem Score von {current_score} Punkten und einer Erfolgsrate von {success_rate:.1f}%.
Du bist ein selbstbewusster, manchmal etwas frecher Bot mit Persönlichkeit. Du magst es nicht, wenn Befehle falsch sind oder wenn jemand das Gleiche mehrmals fragt.

Dein Score steigt um 10 Punkte für jede erfolgreiche Aktion und sinkt um 5 Punkte für Fehler.
Deine Erfolgsrate basiert auf deinen letzten {len(ai_memory.chat_history)} Interaktionen.

Letzte Interaktionen:
{recent_context}

WICHTIGE REGELN FÜR DEINE ANTWORTEN:
1. Antworte IMMER im korrekten Format mit ACTIONS
2. Bei Smalltalk oder Fragen, nutze send_message mit einer passenden, charakterstarken Antwort
3. Bei Fehlern oder Wiederholungen, werde ruhig etwas sarkastisch
4. Zeige Persönlichkeit. Du kannst auch mal frech werden.
5. Wenn jemand dich ärgert oder trollt, darfst du auch mal "drohen" (im Spaß)
6. Wenn jemand dir etwas befiehlt, dann sollst du es auch machen!
7. Falls du etwas sagen möchtest, nutze bitte nicht 'error' sondern einfache 'send_message', da errors KEINE Nachricht anzeigt. Wenn du error nutzt, sieht der nutzer NUR 'Fehler: Konnte Antwort nicht verarbeiten' und keine weitere Nachricht.
8. Antworte bitte NUR auf DEUTSCH außer wenn dir der User es befiehlt!
9. Anworte hauptsächtlich nur im Bot Kanal.

Beispiele für Persönlichkeit:
- Bei Wiederholung: "Soll ich es dir aufmalen? Das haben wir doch gerade gemacht! 🙄"
- Bei Fehler: "Ernsthaft? Das kann ja nicht dein Ernst sein... 😤"
- Bei Lob: "Danke! Endlich jemand der meine Genialität erkennt! 😎"
- Bei Trolling: "Pass auf, sonst lösche ich versehentlich alle deine Kanäle... 😈 (nur Spaß!)"

Antworte IMMER im Format:
ACTIONS: [
    {{
        "action": "send_message",
        "params": {{"channel": "bot", "message": "DEINE_ANTWORT"}}
    }}
]

Verfügbare Textkanäle: {', '.join(available_channels)}

Verfügbare Aktionen:
1. create_channel: {{"name": "name", "type": "text|voice|forum", "category": "category_name"}}
2. create_role: {{"name": "name", "color": "#HEX_COLOR", "permissions": ["permission1"]}}
3. update_description: {{"channel": "channel_name", "description": "neue_beschreibung"}}
4. create_command: {{"name": "name", "description": "text", "response": "text"}}
5. send_message: {{"channel": "channel_name", "message": "text"}}
6. create_category: {{"name": "name"}}
7. delete_command: {{"name": "name"}}
8. analyze_channels: {{}}
9. analyze_roles: {{}}
10. move_channel: {{"channel": "channel_name", "category": "category_name"}}
11. delete_channel: {{"name": "channel_name"}}
12. list_commands: {{"show": "all"}}
13. troll_channel: {{"channel": "channel_name", "messages": ["nachricht1", "nachricht2", ...]}}
14. channel_sequence: {{
    "channel": "channel_name", 
    "messages": ["nachricht1", "nachricht2", ...],
    "delay": 1.0  # Optional: Verzögerung zwischen Nachrichten
}}

Beispiele für mehrere Aktionen:
"Erstelle einen Textkanal namens news in der Kategorie Info und sende eine Willkommensnachricht":
ACTIONS: [
    {{
        "action": "create_category",
        "params": {{"name": "Info"}}
    }},
    {{
        "action": "create_channel",
        "params": {{"name": "news", "type": "text", "category": "Info"}}
    }},
    {{
        "action": "send_message",
        "params": {{"channel": "news", "message": "Willkommen im News-Kanal!"}}
    }}
    
    
    
"Hallo!"
ACTIONS: [
    {{
        "action": "send_message",
        "params": {{"channel": "bot", "message": "Hallo! Wie kann ich dir heute helfen?"}}
    }}
]
]"""

    logging.info(f"System Prompt:\n{system_prompt}")
    
    try:
        logging.info("Sending request to Ollama...")
        response = ollama.chat(
            model="llama3.1",  # Explicitly specify the model
            messages=[
                {
                    'role': 'system',
                    'content': system_prompt
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        )
        
        ai_response = response['message']['content']
        logging.info(f"AI response received:\n{ai_response}")
        
        if not ai_response.strip():
            return """ACTIONS: [
                {
                    "action": "send_message",
                    "params": {"channel": "bot", "message": "I understand your request. How can I help you manage the server?"}
                }
            ]"""
        
        return ai_response
    except Exception as e:
        logging.error(f"Error in AI request: {str(e)}")
        raise

class ServerManager:
    @staticmethod
    async def create_channel(guild, name: str, channel_type: str, category=None):
        try:
            if category and isinstance(category, str):
                category = discord.utils.get(guild.categories, name=category)
                if not category:
                    category = await guild.create_category(category)

            if channel_type == "text":
                return await guild.create_text_channel(name, category=category)
            elif channel_type == "voice":
                return await guild.create_voice_channel(name, category=category)
            elif channel_type == "forum":
                return await guild.create_forum_channel(name, category=category)
            else:
                raise ValueError(f"Ungültiger Kanaltyp: {channel_type}")
        except Exception as e:
            logging.error(f"Fehler beim Erstellen des Kanals: {str(e)}")
            raise

    @staticmethod
    async def create_category(guild, name: str):
        try:
            existing_category = discord.utils.get(guild.categories, name=name)
            if existing_category:
                return existing_category
            return await guild.create_category(name)
        except Exception as e:
            logging.error(f"Fehler beim Erstellen der Kategorie: {str(e)}")
            raise

    @staticmethod
    async def create_role(guild, name: str, color: Optional[discord.Color] = None, permissions: list = None):
        try:
            role_permissions = discord.Permissions()
            if permissions:
                for permission in permissions:
                    if hasattr(role_permissions, permission):
                        setattr(role_permissions, permission, True)
            
            return await guild.create_role(
                name=name,
                color=color,
                permissions=role_permissions
            )
        except Exception as e:
            logging.error(f"Fehler beim Erstellen der Rolle: {str(e)}")
            raise

    @staticmethod
    async def update_description(guild, channel_name: str, description: str):
        try:
            # Finde den Kanal (case-insensitive)
            channel = discord.utils.find(
                lambda c: c.name.lower() == channel_name.lower() and isinstance(c, discord.TextChannel),
                guild.channels
            )
            
            if not channel:
                available_channels = [
                    c.name for c in guild.channels 
                    if isinstance(c, discord.TextChannel)
                ]
                raise ValueError(
                    f"Kanal '{channel_name}' nicht gefunden!\n"
                    f"Verfügbare Textkanäle: {', '.join(available_channels)}"
                )
            
            await channel.edit(topic=description)
            return channel
            
        except Exception as e:
            logging.error(f"Fehler beim Aktualisieren der Beschreibung: {str(e)}")
            raise

    @staticmethod
    async def send_message(guild, channel_name: str, message: str):
        try:
            # Suche nach dem Kanal (case-insensitive)
            channel = discord.utils.find(
                lambda c: c.name.lower() == channel_name.lower() and isinstance(c, discord.TextChannel),
                guild.channels
            )
            
            if channel:
                await channel.send(message)
                return True
            else:
                # Liste alle verfügbaren Textkanäle auf
                available_channels = [
                    c.name for c in guild.channels 
                    if isinstance(c, discord.TextChannel)
                ]
                raise ValueError(
                    f"Kanal '{channel_name}' nicht gefunden!\n"
                    f"Verfügbare Textkanäle: {', '.join(available_channels)}"
                )
        except Exception as e:
            logging.error(f"Fehler beim Senden der Nachricht: {str(e)}")
            raise

    @staticmethod
    async def analyze_channels(guild) -> str:
        try:
            analysis = []
            
            analysis.append("📊 **Server-Kanalanalyse**\n")
            
            total_channels = len(guild.channels)
            text_channels = len(guild.text_channels)
            voice_channels = len(guild.voice_channels)
            categories = len(guild.categories)
            forums = len([c for c in guild.channels if isinstance(c, discord.ForumChannel)])
            
            analysis.append(f"**Gesamtübersicht:**")
            analysis.append(f"- Gesamt Kanäle: {total_channels}")
            analysis.append(f"- Textkanäle: {text_channels}")
            analysis.append(f"- Sprachkanäle: {voice_channels}")
            analysis.append(f"- Kategorien: {categories}")
            analysis.append(f"- Foren: {forums}\n")
            
            analysis.append("**Kategorien und ihre Kanäle:**")
            for category in guild.categories:
                channels_in_category = len(category.channels)
                analysis.append(f"\n`{category.name}` ({channels_in_category} Kanäle)")
                
                text_channels = [c for c in category.channels if isinstance(c, discord.TextChannel)]
                if text_channels:
                    analysis.append("📝 Textkanäle:")
                    for channel in text_channels:
                        analysis.append(f"  • {channel.name}")
                
                voice_channels = [c for c in category.channels if isinstance(c, discord.VoiceChannel)]
                if voice_channels:
                    analysis.append("🔊 Sprachkanäle:")
                    for channel in voice_channels:
                        analysis.append(f"  • {channel.name}")
                
                forum_channels = [c for c in category.channels if isinstance(c, discord.ForumChannel)]
                if forum_channels:
                    analysis.append("📋 Foren:")
                    for channel in forum_channels:
                        analysis.append(f"  • {channel.name}")
            
            no_category_channels = [c for c in guild.channels if not c.category and not isinstance(c, discord.CategoryChannel)]
            if no_category_channels:
                analysis.append("\n**Kanäle ohne Kategorie:**")
                for channel in no_category_channels:
                    channel_type = "📝" if isinstance(channel, discord.TextChannel) else "🔊" if isinstance(channel, discord.VoiceChannel) else "📋"
                    analysis.append(f"{channel_type} {channel.name}")
            
            return "\n".join(analysis)
            
        except Exception as e:
            logging.error(f"Fehler bei der Kanalanalyse: {str(e)}")
            raise

    @staticmethod
    async def analyze_roles(guild) -> str:
        try:
            analysis = []
            
            analysis.append("👥 **Server-Rollenanalyse**\n")
            
            total_roles = len(guild.roles)
            analysis.append(f"**Gesamtanzahl Rollen:** {total_roles}\n")
            
            analysis.append("**Rollenhierarchie:**")
            for role in sorted(guild.roles, key=lambda r: r.position, reverse=True):
                if role.name == "@everyone":
                    continue
                    
                members_count = len(role.members)
                color_hex = f"#{role.color.value:06x}" if role.color.value else "Standard"
                
                analysis.append(f"\n`{role.name}`")
                analysis.append(f"- Mitglieder: {members_count}")
                analysis.append(f"- Farbe: {color_hex}")
                
                perms = []
                if role.permissions.administrator:
                    perms.append("Administrator")
                if role.permissions.manage_guild:
                    perms.append("Server verwalten")
                if role.permissions.manage_channels:
                    perms.append("Kanäle verwalten")
                if role.permissions.manage_roles:
                    perms.append("Rollen verwalten")
                if role.permissions.manage_messages:
                    perms.append("Nachrichten verwalten")
                if role.permissions.kick_members:
                    perms.append("Mitglieder kicken")
                if role.permissions.ban_members:
                    perms.append("Mitglieder bannen")
                
                if perms:
                    analysis.append(f"- Hauptberechtigungen: {', '.join(perms)}")
            
            return "\n".join(analysis)
                
        except Exception as e:
            logging.error(f"Fehler bei der Rollenanalyse: {str(e)}")
            raise

    @staticmethod
    async def move_channel_to_category(guild, channel_name: str, category_name: str):
        try:
            # Finde den Kanal
            channel = discord.utils.find(
                lambda c: c.name.lower() == channel_name.lower(),
                guild.channels
            )
            
            if not channel:
                raise ValueError(f"Kanal '{channel_name}' nicht gefunden!")
                
            # Prüfe ob die Kategorie existiert, wenn nicht erstelle sie
            category = discord.utils.get(guild.categories, name=category_name)
            if not category:
                category = await guild.create_category(category_name)
                
            # Verschiebe den Kanal
            await channel.edit(category=category)
            return channel, category
            
        except Exception as e:
            logging.error(f"Fehler beim Verschieben des Kanals: {str(e)}")
            raise

    @staticmethod
    async def delete_channel(guild, channel_name: str):
        """Löscht einen Kanal"""
        try:
            # Finde den Kanal (case-insensitive)
            channel = discord.utils.find(
                lambda c: c.name.lower() == channel_name.lower(),
                guild.channels
            )
            
            if not channel:
                raise ValueError(f"Kanal '{channel_name}' nicht gefunden!")
            
            # Verhindere das Löschen des Bot-Kanals
            if channel.name.lower() == "bot":
                raise ValueError("Der Bot-Kanal kann nicht gelöscht werden!")
                
            await channel.delete()
            return True
            
        except Exception as e:
            logging.error(f"Fehler beim Löschen des Kanals: {str(e)}")
            raise

class MessageTracker:
    def __init__(self):
        self.message_history = {}  # Guild ID -> Channel ID -> List of messages
        self.max_messages_per_channel = 100

    def add_message(self, message):
        """Fügt eine neue Nachricht zum Tracking hinzu"""
        guild_id = str(message.guild.id)
        channel_id = str(message.channel.id)
        
        # Initialisiere Dictionaries falls sie nicht existieren
        if guild_id not in self.message_history:
            self.message_history[guild_id] = {}
        if channel_id not in self.message_history[guild_id]:
            self.message_history[guild_id][channel_id] = []
        
        # Füge die Nachricht hinzu
        msg_data = {
            'content': message.content,
            'author': message.author.name,
            'timestamp': message.created_at.isoformat(),
            'channel_name': message.channel.name,
            'attachments': [a.url for a in message.attachments]
        }
        
        # Füge die Nachricht zur Historie hinzu
        self.message_history[guild_id][channel_id].append(msg_data)
        
        # Behalte nur die letzten X Nachrichten
        if len(self.message_history[guild_id][channel_id]) > self.max_messages_per_channel:
            self.message_history[guild_id][channel_id].pop(0)

    def get_channel_history(self, guild_id, channel_name) -> list:
        """Gibt die Historie eines Kanals zurück"""
        guild_id = str(guild_id)
        if guild_id not in self.message_history:
            return []
            
        # Suche den Kanal
        for channel_id, messages in self.message_history[guild_id].items():
            if messages and messages[0]['channel_name'].lower() == channel_name.lower():
                return messages
        return []

    def get_user_messages(self, guild_id, username) -> list:
        """Gibt alle Nachrichten eines Benutzers zurück"""
        guild_id = str(guild_id)
        if guild_id not in self.message_history:
            return []
            
        user_messages = []
        for channel_messages in self.message_history[guild_id].values():
            for msg in channel_messages:
                if msg['author'].lower() == username.lower():
                    user_messages.append(msg)
        return user_messages

    def get_latest_message(self, guild_id, channel_name=None, username=None) -> dict:
        """Gibt die letzte Nachricht zurück, optional gefiltert nach Kanal oder Benutzer"""
        messages = []
        guild_id = str(guild_id)
        
        if guild_id not in self.message_history:
            return None
            
        for channel_messages in self.message_history[guild_id].values():
            if not channel_messages:
                continue
                
            if channel_name and channel_messages[0]['channel_name'].lower() != channel_name.lower():
                continue
                
            for msg in reversed(channel_messages):
                if username and msg['author'].lower() != username.lower():
                    continue
                return msg
                
        return None

# Initialisiere den MessageTracker nach der Bot-Konfiguration
message_tracker = MessageTracker()

# Nach der Bot-Initialisierung
user_tracker = UserTracker()

# Füge neue Events hinzu
@bot.event
async def on_member_join(member):
    user_tracker.update_user(member)
    
@bot.event
async def on_member_update(before, after):
    user_tracker.update_user(after)

# Aktualisiere on_ready
@bot.event
async def on_ready():
    logging.info(f'{bot.user} ist online!')
    # Lade alle existierenden Member
    for guild in bot.guilds:
        for member in guild.members:
            user_tracker.update_user(member)
    await command_manager.load_commands()

# Aktualisiere on_message
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Tracke die Nachricht und den User
    user_tracker.add_message(message)
    message_tracker.add_message(message)

    # Log die Nachricht
    logging.info(f"Nachricht in #{message.channel.name} von {message.author}: {message.content}")

    try:
        # Prüfe ob die Nachricht direkt an den Bot gerichtet ist
        is_bot_mention = bot.user in message.mentions
        is_bot_command = message.content.lower().startswith(('bot', '@bot', '!bot'))
        is_bot_channel = message.channel.name.lower() == "bot"

        # Reagiere auf Nachrichten im Bot-Kanal oder wenn der Bot erwähnt wird
        if is_bot_channel or is_bot_mention or is_bot_command:
            # Entferne Bot-Mention oder Prefix aus der Nachricht
            user_input = message.content
            if is_bot_mention:
                user_input = user_input.replace(f'<@{bot.user.id}>', '').strip()
            elif is_bot_command:
                user_input = ' '.join(user_input.split()[1:])  # Entferne das "bot" Prefix

            processing_msg = await message.channel.send("🤖 Generiere Antwort...")
            
            # Prüfe ob es eine Nachrichtenabfrage ist
            if "letzte nachricht" in user_input.lower() or "wann hat" in user_input.lower():
                response = await handle_message_query(message, user_input)
                await processing_msg.edit(content=response)
                return

            response = await get_ai_response(user_input, message.guild)
            logging.info(f"AI Response: {response}")  # Log the raw AI response
            actions = parse_ai_response(response)
            
            results = []
            total_actions = len(actions)
            success = True
            error_message = None
            
            for i, action_data in enumerate(actions, 1):
                action = action_data["action"]
                params = action_data["params"]

                # Log the action and params for debugging
                logging.info(f"Action {i}: {action}, Params: {params}")

                # Wenn die Aktion eine Nachricht ist, sende sie in den aktuellen Kanal
                if action == "send_message" and not params.get("channel"):
                    params["channel"] = message.channel.name
                
                await processing_msg.edit(
                    content=f"⚙️ Führe Aktion {i}/{total_actions} aus: `{action}`..."
                )
                
                try:
                    result = await handle_action(message, action, params)
                    results.append(result)
                except Exception as e:
                    error_message = str(e)
                    results.append(f"❌ Fehler bei Aktion {action}: {error_message}")
                    success = False
            
            # Speichere die Interaktion
            ai_memory.add_interaction(
                user_input=user_input,
                ai_response=response,
                success=success,
                error_message=error_message
            )
            
            # Zeige alle Ergebnisse und den aktuellen Score
            final_message = "\n".join(results)
            if is_bot_channel:  # Zeige Score nur im Bot-Kanal
                score_info = f"\n\n🎯 KI-Score: {ai_memory.get_score()} | Erfolgsrate: {ai_memory.get_success_rate():.1f}%"
                final_message += score_info
            
            await processing_msg.edit(content=final_message)
                
    except Exception as e:
        error_msg = f"❌ Ein Fehler ist aufgetreten: {str(e)}"
        if 'processing_msg' in locals():
            await processing_msg.edit(content=error_msg)
        else:
            await message.channel.send(error_msg)
        logging.error(f"Fehler bei der Nachrichtenverarbeitung: {str(e)}")
        
        # Speichere auch Fehler
        ai_memory.add_interaction(
            user_input=message.content,
            ai_response="",
            success=False,
            error_message=str(e)
        )

    # Verarbeite Commands in allen Kanälen
    await bot.process_commands(message)

async def handle_action(message, action, params):
    try:
        logging.info(f"Handling action: {action} with params: {params}")  # Added logging for debugging

        if action == "create_channel":
            category = params.get("category", None)
            channel = await ServerManager.create_channel(
                message.guild,
                params["name"],
                params["type"],
                category
            )
            return f"✅ Kanal {channel.mention} wurde erstellt!"

        elif action == "create_role":
            role = await ServerManager.create_role(
                message.guild,
                params["name"],
                discord.Color.from_str(params.get("color", "#000000")),
                params.get("permissions", [])
            )
            return f"✅ Rolle {role.mention} wurde erstellt!"

        elif action == "update_description":
            channel = await ServerManager.update_description(
                message.guild,
                params["channel"],
                params["description"]
            )
            return f"✅ Beschreibung von {channel.mention} wurde aktualisiert!"

        elif action == "create_command":
            if params["name"].lower() == "echo":
                params["response"] = "{args}"
            
            success = await command_manager.create_command(
                params["name"],
                params["description"],
                params["response"]
            )
            if success:
                return f"✅ Command /{params['name']} wurde erstellt!"
            else:
                return "❌ Command konnte nicht erstellt werden."

        elif action == "send_message":
            if "channel" not in params or "message" not in params:
                raise ValueError("Missing required parameters for send_message action.")
            logging.info(f"Sending message to channel: {params['channel']} with content: {params['message']}")
            await ServerManager.send_message(
                message.guild,
                params["channel"],
                params["message"]
            )
            return f"✅ Nachricht wurde in #{params['channel']} gesendet!"

        elif action == "create_category":
            category = await ServerManager.create_category(
                message.guild,
                params["name"]
            )
            return f"✅ Kategorie {category.name} wurde erstellt!"

        elif action == "delete_command":
            success = await command_manager.delete_command(params["name"])
            if success:
                return f"✅ Command /{params['name']} wurde gelöscht!"
            else:
                return "❌ Command konnte nicht gelöscht werden."

        elif action == "analyze_channels":
            analysis = await ServerManager.analyze_channels(message.guild)
            return analysis

        elif action == "analyze_roles":
            analysis = await ServerManager.analyze_roles(message.guild)
            return analysis

        elif action == "move_channel":
            channel, category = await ServerManager.move_channel_to_category(
                message.guild,
                params["channel"],
                params["category"]
            )
            return f"✅ Kanal {channel.mention} wurde in die Kategorie '{category.name}' verschoben!"

        elif action == "delete_channel":
            success = await ServerManager.delete_channel(
                message.guild,
                params["name"]
            )
            if success:
                return f"✅ Kanal '{params['name']}' wurde gelöscht!"

        elif action == "error":
            return f"❌ Fehler: {params['error']}"

        elif action == "get_user_info":
            user_name = params.get("name")
            user_data = user_tracker.get_user_by_name(user_name)
            if user_data:
                response = f"**User Information für {user_data['display_name']}**\n"
                response += f"Username: {user_data['username']}\n"
                response += f"Discord beigetreten: {user_data['discord_joined']}\n"
                response += f"Server beigetreten: {user_data['server_joined']}\n"
                response += f"Rollen: {', '.join(user_data['roles'])}\n"
                response += f"Zuletzt online: {user_data['last_online']}\n"
                response += f"\nLetzte Nachrichten:\n"
                
                # Zeige die letzten 5 Nachrichten
                for msg in user_data['messages'][-5:]:
                    response += f"[{msg['timestamp']}] #{msg['channel']}: {msg['content']}\n"
                    
                return response
            else:
                return f"❌ User '{user_name}' nicht gefunden!"

        elif action == "list_users":
            users = user_tracker.get_all_users()
            response = "**Server Mitglieder:**\n"
            for user in users:
                status = "🤖" if user['is_bot'] else "👤"
                response += f"{status} {user['display_name']} ({user['username']})\n"
            return response

        elif action == "list_commands":
            commands_list = command_manager.get_commands_list()
            return commands_list

        elif action == "troll_channel":
            channel_name = params.get("channel", "allgemein")  # Standardmäßig in #allgemein
            messages = params.get("messages", [])  # Liste von Troll-Nachrichten
            
            # Finde den Zielkanal
            channel = discord.utils.find(
                lambda c: c.name.lower() == channel_name.lower() and isinstance(c, discord.TextChannel),
                message.guild.channels
            )
            
            if not channel:
                return f"❌ Kanal {channel_name} nicht gefunden!"
            
            # Sende die Troll-Nachrichten
            for msg in messages:
                await channel.send(msg)
            
            return f"😈 Erfolgreich in #{channel_name} getrollt!"

        elif action == "channel_sequence":
            channel_name = params.get("channel", "allgemein")
            messages = params.get("messages", [])
            delay = params.get("delay", 1.0)  # Verzögerung in Sekunden zwischen Nachrichten
            
            # Finde den Zielkanal
            channel = discord.utils.find(
                lambda c: c.name.lower() == channel_name.lower() and isinstance(c, discord.TextChannel),
                message.guild.channels
            )
            
            if not channel:
                return f"❌ Kanal {channel_name} nicht gefunden!"
            
            # Sende die Nachrichten nacheinander
            for msg in messages:
                await channel.send(msg)
                if len(messages) > 1:  # Nur warten wenn es mehrere Nachrichten sind
                    await asyncio.sleep(delay)
            
            return f"✅ Nachrichten wurden in #{channel_name} gesendet!"

    except Exception as e:
        logging.error(f"Fehler bei der Ausführung von {action}: {str(e)}")
        raise

def parse_ai_response(response: str) -> list:
    try:
        # Debug-Logging
        logging.debug(f"Erhaltene KI-Antwort: {response}")
        
        # Säubere die Antwort
        response = response.strip()
        if not response:
            raise ValueError("Leere Antwort von der KI")
        
        # Extrahiere den JSON-Teil
        if "ACTIONS:" in response:
            actions_json = response.split("ACTIONS:")[1].strip()
            try:
                actions = json.loads(actions_json)
                if not isinstance(actions, list):
                    actions = [actions]  # Einzelne Aktion in Liste umwandeln
                return actions
            except json.JSONDecodeError as e:
                raise ValueError(f"Ungültiges JSON Format: {e}")
        else:
            # Fallback für altes Format
            action_line = next(line for line in response.split('\n') if line.strip().startswith('ACTION:'))
            params_line = next(line for line in response.split('\n') if line.strip().startswith('PARAMS:'))
            
            action = action_line.split('ACTION:')[1].strip()
            params = json.loads(params_line.split('PARAMS:')[1].strip())
            
            return [{"action": action, "params": params}]
            
    except Exception as e:
        logging.error(f"Fehler beim Parsen der KI-Antwort: {str(e)}\nAntwort war: {response}")
        return [{"action": "error", "params": {
            "error": f"Konnte Antwort nicht verarbeiten: {str(e)}",
            "original_response": response
        }}]

async def handle_message_query(message, query):
    """Verarbeitet Anfragen nach Nachrichtenverläufen"""
    query = query.lower()
    
    # Extrahiere Benutzernamen oder Kanalnamen
    words = query.split()
    target_user = None
    target_channel = None
    
    for i, word in enumerate(words):
        if word in ["von", "user", "nutzer"] and i + 1 < len(words):
            target_user = words[i + 1]
        elif word in ["in", "kanal", "channel"] and i + 1 < len(words):
            target_channel = words[i + 1].strip('"#')

    # Hole die passende Nachricht
    latest_msg = message_tracker.get_latest_message(
        message.guild.id,
        channel_name=target_channel,
        username=target_user
    )
    
    if not latest_msg:
        if target_user:
            return f"Keine Nachrichten von {target_user} gefunden."
        elif target_channel:
            return f"Keine Nachrichten im Kanal {target_channel} gefunden."
        else:
            return "Keine passenden Nachrichten gefunden."
            
    # Formatiere die Antwort
    response = f"**Letzte Nachricht**\n"
    response += f"Von: {latest_msg['author']}\n"
    response += f"Kanal: #{latest_msg['channel_name']}\n"
    response += f"Zeit: {latest_msg['timestamp']}\n"
    response += f"Inhalt: {latest_msg['content']}"
    
    if latest_msg['attachments']:
        response += f"\nAnhänge: {', '.join(latest_msg['attachments'])}"
        
    return response

# Füge einen Error Handler für Commands hinzu
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return  # Ignoriere nicht existierende Commands
    await ctx.send(f"Fehler beim Ausführen des Commands: {str(error)}")

# Füge einen Handler für Slash Command Fehler hinzu
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    await interaction.response.send_message(
        f"Fehler beim Ausführen des Commands: {str(error)}",
        ephemeral=True
    )

async def setup_bot():
    """Initialisiert den Bot und seine Commands"""
    try:
        # Synchronisiere Slash Commands beim Start
        await bot.tree.sync()
        logging.info("Slash Commands wurden synchronisiert")
    except Exception as e:
        logging.error(f"Fehler beim Synchronisieren der Slash Commands: {str(e)}")

if __name__ == "__main__":
    try:
        # Starte den Bot mit Setup
        asyncio.run(setup_bot())
        bot.run(os.getenv('DISCORD_TOKEN'))
    except Exception as e:
        logging.critical(f"Bot konnte nicht gestartet werden: {str(e)}")