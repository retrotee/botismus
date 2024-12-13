import json
import os
from datetime import datetime


class AIMemory:
    def __init__(self):
        self.memory_file = "ai_memory.json"
        self.chat_history = []
        self.score = 0
        self.load_memory()

    def load_memory(self):
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.chat_history = data.get('chat_history', [])
                    self.score = data.get('score', 0)
        except Exception as e:
            print(f"Error loading AI memory: {str(e)}")

    def save_memory(self):
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'chat_history': self.chat_history,
                    'score': self.score
                }, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving AI memory: {str(e)}")

    def add_interaction(self, user_input: str, ai_response: str, success: bool, error_message: str = None):
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'ai_response': ai_response,
            'success': success,
            'error': error_message,
            'score_change': 10 if success else -5
        }

        self.chat_history.append(interaction)
        self.score += interaction['score_change']

        # Keep only the last 100 interactions
        if len(self.chat_history) > 100:
            self.chat_history = self.chat_history[-100:]

        self.save_memory()

    def get_recent_history(self, count: int = 5) -> list:
        return self.chat_history[-count:]

    def get_score(self) -> int:
        return self.score

    def get_success_rate(self) -> float:
        if not self.chat_history:
            return 0.0
        successful = sum(1 for interaction in self.chat_history if interaction['success'])
        return (successful / len(self.chat_history)) * 100

    def get_context_for_prompt(self, max_items: int = 5) -> str:
        recent = self.get_recent_history(max_items)
        context = []
        for item in recent:
            context.append(f"User: {item['user_input']}")
            context.append(f"Bot: {item['ai_response']}")
        return "\n".join(context)
