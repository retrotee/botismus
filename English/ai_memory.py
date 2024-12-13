import json
import os
from typing import List, Dict


class AIMemory:
    def __init__(self):
        self.chat_history: List[Dict] = []
        self.score: int = 0
        self.success_count: int = 0
        self.total_interactions: int = 0
        
        # Try to load existing memory
        try:
            self.load_memory()
        except Exception as e:
            print(f"Error loading AI memory: {e}")
            # Initialize with empty values if loading fails
            self.save_memory()  # Create initial memory file

    def add_interaction(self, prompt: str, response: str, success: bool = True):
        self.chat_history.append({
            "prompt": prompt,
            "response": response,
            "success": success
        })
        
        # Update stats
        self.total_interactions += 1
        if success:
            self.score += 10
            self.success_count += 1
        else:
            self.score -= 5
            
        # Keep only last 100 interactions
        if len(self.chat_history) > 100:
            self.chat_history.pop(0)
            
        # Save after each interaction
        self.save_memory()

    def get_context_for_prompt(self) -> str:
        # Return last 5 interactions as context
        context = []
        for interaction in self.chat_history[-5:]:
            context.append(f"User: {interaction['prompt']}")
            context.append(f"Bot: {interaction['response']}")
        return "\n".join(context)

    def get_score(self) -> int:
        return self.score

    def get_success_rate(self) -> float:
        if self.total_interactions == 0:
            return 100.0
        return (self.success_count / self.total_interactions) * 100

    def save_memory(self):
        memory_data = {
            "chat_history": self.chat_history,
            "score": self.score,
            "success_count": self.success_count,
            "total_interactions": self.total_interactions
        }
        with open("ai_memory.json", "w") as f:
            json.dump(memory_data, f, indent=2)

    def load_memory(self):
        if os.path.exists("ai_memory.json"):
            with open("ai_memory.json", "r") as f:
                memory_data = json.load(f)
                self.chat_history = memory_data.get("chat_history", [])
                self.score = memory_data.get("score", 0)
                self.success_count = memory_data.get("success_count", 0)
                self.total_interactions = memory_data.get("total_interactions", 0)
