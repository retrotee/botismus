import discord
from datetime import datetime
from typing import Dict, List, Optional

class UserTracker:
    def __init__(self):
        self.users: Dict = {}
        self.message_history: Dict = {}

    def update_user(self, member: discord.Member):
        """Update or add user information"""
        self.users[str(member.id)] = {
            'username': member.name,
            'display_name': member.display_name,
            'discord_joined': member.created_at.isoformat(),
            'server_joined': member.joined_at.isoformat() if member.joined_at else None,
            'roles': [role.name for role in member.roles],
            'last_online': datetime.now().isoformat(),
            'is_bot': member.bot
        }

    def add_message(self, message: discord.Message):
        """Track a new message from a user"""
        user_id = str(message.author.id)
        if user_id not in self.message_history:
            self.message_history[user_id] = []

        self.message_history[user_id].append({
            'content': message.content,
            'timestamp': message.created_at.isoformat(),
            'channel': message.channel.name
        })

        # Keep only last 100 messages per user
        if len(self.message_history[user_id]) > 100:
            self.message_history[user_id].pop(0)

    def get_user_by_name(self, username: str) -> Optional[Dict]:
        """Get user data by username"""
        for user_id, user_data in self.users.items():
            if user_data['username'].lower() == username.lower():
                user_data['messages'] = self.message_history.get(user_id, [])
                return user_data
        return None

    def get_all_users(self) -> List[Dict]:
        """Get list of all tracked users"""
        return list(self.users.values())