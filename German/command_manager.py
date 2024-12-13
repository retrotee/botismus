import json
import os
from discord.ext import commands
import logging
import discord
import asyncio
from typing import Optional, Dict, Any

class CommandManager:
    def __init__(self, bot):
        self.bot = bot
        self.commands_file = "commands.json"
        self.commands: Dict[str, Dict[str, Any]] = {}
        self.command_instances = {}

    def get_commands_list(self) -> str:
        """Gibt eine formatierte Liste aller Commands zurück"""
        if not self.commands:
            return "Keine Commands verfügbar."
        
        result = "**Verfügbare Commands:**\n"
        for name, data in self.commands.items():
            result += f"• /{name} - {data['description']}\n"
        return result

    async def load_commands(self):
        """Lädt gespeicherte Commands beim Start"""
        try:
            if os.path.exists(self.commands_file):
                with open(self.commands_file, 'r', encoding='utf-8') as f:
                    self.commands = json.load(f)
                    for cmd_name, cmd_data in self.commands.items():
                        success = await self.register_command(cmd_name, cmd_data)
                        if success:
                            logging.info(f"Command '{cmd_name}' erfolgreich geladen!")
                        else:
                            logging.error(f"Fehler beim Laden von Command '{cmd_name}'")
                    logging.info(f"Erfolgreich {len(self.commands)} Commands geladen!")
        except Exception as e:
            logging.error(f"Fehler beim Laden der Commands: {str(e)}")

    def save_commands(self):
        """Speichert Commands in eine JSON-Datei"""
        try:
            with open(self.commands_file, 'w', encoding='utf-8') as f:
                json.dump(self.commands, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            logging.error(f"Fehler beim Speichern der Commands: {str(e)}")
            return False

    async def create_command(self, name: str, description: str, response: str):
        """Erstellt einen neuen Command"""
        try:
            # Lösche existierenden Command falls vorhanden
            if name in self.commands:
                await self.delete_command(name)
            
            # Validiere Command-Name
            if not name.replace('-', '').replace('_', '').isalnum():
                raise ValueError("Command-Name darf nur Buchstaben, Zahlen, Unterstriche und Bindestriche enthalten!")

            self.commands[name] = {
                "description": description,
                "response": response
            }
            
            # Registriere und speichere Command
            success = await self.register_command(name, self.commands[name])
            if success and self.save_commands():
                return True
            
            # Wenn etwas fehlschlägt, Command rückgängig machen
            del self.commands[name]
            return False
                
        except Exception as e:
            raise Exception(f"Fehler beim Erstellen des Commands: {str(e)}")

    async def register_command(self, name: str, cmd_data: dict):
        """Registriert einen Command beim Bot"""
        try:
            # Entferne existierende Command-Instanzen
            if name in self.command_instances:
                self.bot.remove_command(name)
                del self.command_instances[name]

            # Definiere den Command-Callback
            async def command_callback(ctx, *, args=""):
                try:
                    response = cmd_data["response"]
                    response = response.replace("{args}", args)
                    response = response.replace("${input}", args)
                    await ctx.send(response)
                except Exception as e:
                    await ctx.send(f"Fehler beim Ausführen des Commands: {str(e)}")

            # Erstelle den Command
            @self.bot.command(name=name, help=cmd_data["description"])
            async def dynamic_command(ctx, *, args=""):
                await command_callback(ctx, args=args)

            # Speichere die Command-Instanz
            self.command_instances[name] = dynamic_command

            # Erstelle auch einen Slash Command
            @self.bot.tree.command(name=name, description=cmd_data["description"])
            async def dynamic_slash_command(interaction: discord.Interaction, args: str = ""):
                response = cmd_data["response"]
                response = response.replace("{args}", args)
                response = response.replace("${input}", args)
                await interaction.response.send_message(response)

            try:
                await self.bot.tree.sync()
            except Exception as e:
                logging.warning(f"Fehler beim Synchronisieren der Slash Commands: {str(e)}")

            return True
            
        except Exception as e:
            logging.error(f"Fehler beim Registrieren des Commands '{name}': {str(e)}")
            return False

    async def delete_command(self, name: str):
        """Löscht einen existierenden Command"""
        try:
            if name not in self.commands:
                raise ValueError(f"Command '{name}' existiert nicht!")
            
            # Entferne Command-Instanzen
            if name in self.command_instances:
                self.bot.remove_command(name)
                del self.command_instances[name]
            
            # Entferne Command aus der Speicherung
            del self.commands[name]
            
            # Speichere Änderungen
            if self.save_commands():
                try:
                    await self.bot.tree.sync()
                except Exception as e:
                    logging.warning(f"Fehler beim Synchronisieren der Slash Commands: {str(e)}")
                return True
            
            return False
                
        except Exception as e:
            raise Exception(f"Fehler beim Löschen des Commands: {str(e)}")