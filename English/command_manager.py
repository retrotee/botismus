import json
import logging
from typing import Dict, Any

class CommandManager:
    def __init__(self, bot):
        self.bot = bot
        self.commands = {}
        try:
            self.load_commands()
        except Exception as e:
            logging.error(f"Error loading commands: {e}")
            self.save_commands()  # Create initial commands file

    async def process_response(self, response: str, message):
        try:
            # Extract the actions part
            if "ACTIONS:" not in response:
                await message.channel.send("Error: Invalid response format")
                return

            actions_str = response.split("ACTIONS:")[1].strip()
            actions = json.loads(actions_str)

            for action in actions:
                await self.execute_action(action, message)

        except Exception as e:
            logging.error(f"Error processing response: {e}")
            await message.channel.send("Error: Could not process response")

    async def execute_action(self, action: Dict[str, Any], message):
        action_type = action.get("action")
        params = action.get("params", {})

        if action_type == "send_message":
            channel_name = params.get("channel")
            channel = discord.utils.get(message.guild.channels, name=channel_name)
            if channel:
                await channel.send(params.get("message"))

        # Add other action handlers here...

    def load_commands(self):
        try:
            with open("commands.json", "r") as f:
                self.commands = json.load(f)
        except FileNotFoundError:
            self.commands = {}

    def save_commands(self):
        with open("commands.json", "w") as f:
            json.dump(self.commands, f, indent=2)
