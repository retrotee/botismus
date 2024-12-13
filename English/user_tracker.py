import discord
from datetime import datetime
from typing import Optional, List, Dict

class UserTracker:
    def __init__(self):
        self.users: Dict[int, Dict] = {}  # user_id -> user_data
        
    def update_user(self, member: discord.Member):
        """Aktualisiert oder erstellt User-Informationen"""
        user_data = {
            'id': member.id,
            'display_name': member.display_name,
            'username': str(member),
            'discord_joined': member.created_at.isoformat(),
            'server_joined': member.joined_at.isoformat() if member.joined_at else None,
            'roles': [role.name for role in member.roles if role.name != "@everyone"],
            'last_online': datetime.now().isoformat(),
            'is_bot': member.bot,
            'avatar_url': str(member.avatar.url) if member.avatar else None,
            'status': str(member.status),
            'activities': [str(activity) for activity in member.activities],
            'messages': []
        }
        
        # Behalte existierende Nachrichten wenn der User bereits existiert
        if member.id in self.users:
            user_data['messages'] = self.users[member.id].get('messages', [])
            
        self.users[member.id] = user_data
        
    def add_message(self, message: discord.Message):
        """Fügt eine neue Nachricht zum User-Tracking hinzu"""
        if message.author.id not in self.users:
            self.update_user(message.author)
            
        msg_data = {
            'content': message.content,
            'channel': message.channel.name,
            'timestamp': message.created_at.isoformat(),
            'attachments': [a.url for a in message.attachments],
            'edited': message.edited_at.isoformat() if message.edited_at else None
        }
        
        self.users[message.author.id]['messages'].append(msg_data)
        self.users[message.author.id]['last_online'] = datetime.now().isoformat()
        
    def get_user_info(self, user_id: int) -> Optional[Dict]:
        """Gibt detaillierte Informationen über einen User zurück"""
        return self.users.get(user_id)
        
    def get_all_users(self) -> List[Dict]:
        """Gibt eine Liste aller User zurück"""
        return list(self.users.values())
        
    def get_user_by_name(self, name: str) -> Optional[Dict]:
        """Sucht einen User nach Namen (display_name oder username)"""
        name = name.lower()
        for user in self.users.values():
            if (name in user['display_name'].lower() or 
                name in user['username'].lower()):
                return user
        return None 