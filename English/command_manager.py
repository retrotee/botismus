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
        """Returns a formatted list of all commands."""
        if not self.commands:
            return "No commands available."

        result = "**Available Commands:**\n"
        for name, data in self.commands.items():
            result += f"• /{name} - {data['description']}\n"
        return result

    async def load_commands(self):
        """Loads saved commands at startup."""
        try:
            if os.path.exists(self.commands_file):
                with open(self.commands_file, 'r', encoding='utf-8') as f:
                    self.commands = json.load(f)
                    for cmd_name, cmd_data in self.commands.items():
                        success = await self.register_command(cmd_name, cmd_data)
                        if success:
                            logging.info(f"Command '{cmd_name}' loaded successfully!")
                        else:
                            logging.error(f"Error loading command '{cmd_name}'")
                    logging.info(f"Successfully loaded {len(self.commands)} commands!")
        except Exception as e:
            logging.error(f"Error loading commands: {str(e)}")

    def save_commands(self):
        """Saves commands to a JSON file."""
        try:
            with open(self.commands_file, 'w', encoding='utf-8') as f:
                json.dump(self.commands, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            logging.error(f"Error saving commands: {str(e)}")
            return False

    async def create_command(self, name: str, description: str, response: str):
        """Creates a new command."""
        try:
            # Delete existing command if present
            if name in self.commands:
                await self.delete_command(name)

            # Validate command name
            if not name.replace('-', '').replace('_', '').isalnum():
                raise ValueError("Command name may only contain letters, numbers, underscores, and hyphens!")

            self.commands[name] = {
                "description": description,
                "response": response
            }

            # Register and save command
            success = await self.register_command(name, self.commands[name])
            if success and self.save_commands():
                return True

            # If something fails, rollback the command
            del self.commands[name]
            return False

        except Exception as e:
            raise Exception(f"Error creating command: {str(e)}")

    async def register_command(self, name: str, cmd_data: dict):
        """Registers a command with the bot."""
        try:
            # Remove existing command instances
            if name in self.command_instances:
                self.bot.remove_command(name)
                del self.command_instances[name]

            # Define the command callback
            async def command_callback(ctx, *, args=""):
                try:
                    response = cmd_data["response"]
                    response = response.replace("{args}", args)
                    response = response.replace("${input}", args)
                    await ctx.send(response)
                except Exception as e:
                    await ctx.send(f"Error executing command: {str(e)}")

            # Create the command
            @self.bot.command(name=name, help=cmd_data["description"])
            async def dynamic_command(ctx, *, args=""):
                await command_callback(ctx, args=args)

            # Save the command instance
            self.command_instances[name] = dynamic_command

            # Also create a slash command
            @self.bot.tree.command(name=name, description=cmd_data["description"])
            async def dynamic_slash_command(interaction: discord.Interaction, args: str = ""):
                response = cmd_data["response"]
                response = response.replace("{args}", args)
                response = response.replace("${input}", args)
                await interaction.response.send_message(response)

            try:
                await self.bot.tree.sync()
            except Exception as e:
                logging.warning(f"Error synchronizing slash commands: {str(e)}")

            return True

        except Exception as e:
            logging.error(f"Error registering command '{name}': {str(e)}")
            return False

    async def delete_command(self, name: str):
        """Deletes an existing command."""
        try:
            if name not in self.commands:
                raise ValueError(f"Command '{name}' does not exist!")

            # Remove command instances
            if name in self.command_instances:
                self.bot.remove_command(name)
                del self.command_instances[name]

            # Remove command from storage
            del self.commands[name]

            # Save changes
            if self.save_commands():
                try:
                    await self.bot.tree.sync()
                except Exception as e:
                    logging.warning(f"Error synchronizing slash commands: {str(e)}")
                return True

            return False

        except Exception as e:
            raise Exception(f"Error deleting command: {str(e)}")
