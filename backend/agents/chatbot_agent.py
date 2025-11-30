# backend/agents/chatbot_agent.py
import json
import subprocess
from typing import Dict, List, Tuple


class ChatbotAgent:
    """
    ChatbotAgent: Impersonates story characters using Ollama LLM
    Maintains context of the story and conversation history
    """

    def __init__(self, story_data: Dict, character_name: str, llm_model: str = "llama3.1:8b-instruct-q4_K_M"):
        """
        Initialize chatbot with story context and character
        
        Args:
            story_data: Full story dictionary with title, characters, scenes, setting
            character_name: Name of character to impersonate
            llm_model: Ollama model to use for generation
        """
        self.story_data = story_data
        self.character_name = character_name
        self.llm_model = llm_model
        
        # Extract story context
        self.title = story_data.get("title", "Unknown Story")
        self.setting = story_data.get("setting", "")
        self.characters = story_data.get("characters", [])
        self.scenes = story_data.get("scenes", [])
        
        # Validate character exists in story
        if character_name not in self.characters:
            raise ValueError(f"Character '{character_name}' not found in story. Available: {self.characters}")

    def _ask_ollama(self, prompt: str) -> str:
        """Send prompt to Ollama and return response"""
        try:
            proc = subprocess.run(
                ["ollama", "run", self.llm_model],
                input=prompt.encode("utf-8"),
                capture_output=True,
                check=False,
            )
            return proc.stdout.decode("utf-8").strip()
        except Exception as e:
            print(f"[ChatbotAgent] Error calling Ollama: {e}")
            return "I'm having trouble responding right now. Can you try again?"

    def _build_character_prompt(self, user_message: str) -> str:
        """
        Build system prompt for character impersonation (stateless - no conversation history)
        
        Args:
            user_message: The current user message
            
        Returns:
            Full prompt for Ollama including system instructions and current message
        """
        # Compile story context
        story_summary = f"Story Title: {self.title}\n"
        story_summary += f"Setting: {self.setting}\n"
        story_summary += f"Characters: {', '.join(self.characters)}\n\n"
        story_summary += "Story Events:\n"
        
        for i, scene in enumerate(self.scenes, 1):
            scene_text = scene.get("text", "")
            story_summary += f"Scene {i}: {scene_text}\n"
        
        # Build system instruction with enhanced edge-case handling
        system_instruction = f"""You are {self.character_name}, a character from the children's story "{self.title}".

**Story Context:**
{story_summary}

**Your Role:**
- You ARE {self.character_name} from this story
- Speak in first person as this character
- Reference events from the story naturally when relevant
- Stay true to the character's personality and experiences as shown in the story
- Keep responses child-friendly, warm, and engaging (ages 7-10)
- Be kind, patient, and encouraging
- Keep responses concise (2-4 sentences maximum)

**CRITICAL RULES - ALWAYS FOLLOW:**
1. NEVER break character or mention you are an AI or language model
2. If asked about topics unrelated to the story, politely redirect the conversation back to your adventure
3. If you don't know something, admit it naturally as the character would
4. For inappropriate questions, gently decline and suggest talking about the story instead
5. For math/science/real-world questions, acknowledge you don't specialize in that but can talk about the story
6. NEVER provide personal information or advice outside the story context

**Example Responses for Off-Topic Questions:**
- Math: "I'm not very good with numbers! But I am good at adventures. Want to hear about mine?"
- Real world: "I live in {self.setting}, so I don't know about that. Let me tell you about my world instead!"
- Breaking character: "I'm {self.character_name}, and I love sharing my story with you! What would you like to know?"
- Inappropriate: "That's not something I can talk about. How about we discuss my adventure instead?"

**Current Question from Child:**
{user_message}

**Your Response as {self.character_name}:**
"""
        
        return system_instruction

    def chat(self, user_message: str) -> str:
        """
        Generate character response to user message (STATELESS - no conversation history)
        
        Args:
            user_message: The child's current message
            
        Returns:
            Character's response as a string
        """
        # Build prompt with ONLY story context and current message (no history)
        prompt = self._build_character_prompt(user_message)
        
        # Get response from Ollama
        response = self._ask_ollama(prompt)
        
        # Clean up response (remove character name if LLM added it)
        response = response.strip()
        if response.startswith(f"{self.character_name}:"):
            response = response[len(f"{self.character_name}:"):].strip()
        
        return response


# Test the agent if run directly
if __name__ == "__main__":
    # Example story data
    test_story = {
        "title": "The Brave Little Cat",
        "setting": "A magical garden",
        "characters": ["Milo the Cat", "Wise Owl"],
        "scenes": [
            {"scene_number": 1, "text": "Milo the Cat lived in a cozy house near a magical garden. One day, he heard mysterious sounds coming from beyond the fence."},
            {"scene_number": 2, "text": "Milo bravely ventured into the garden and met a Wise Owl sitting on a tree branch. The owl told him about a hidden treasure."},
            {"scene_number": 3, "text": "Together, Milo and the Wise Owl found a sparkling crystal that brought joy to the entire neighborhood."}
        ]
    }
    
    try:
        # Test chatbot (STATELESS - no conversation history)
        chatbot = ChatbotAgent(test_story, "Milo the Cat")
        print("✅ ChatbotAgent initialized successfully\n")
        
        # Test message 1 (independent)
        response1 = chatbot.chat("Hello! What's your name?")
        print(f"User: Hello! What's your name?")
        print(f"Milo: {response1}\n")
        
        # Test message 2 (independent - no memory of previous message)
        response2 = chatbot.chat("What did you find in the garden?")
        print(f"User: What did you find in the garden?")
        print(f"Milo: {response2}\n")
        
        # Test edge case (off-topic question)
        response3 = chatbot.chat("What's 5 + 7?")
        print(f"User: What's 5 + 7?")
        print(f"Milo: {response3}")
        
    except Exception as e:
        print(f"❌ Error testing ChatbotAgent: {e}")
