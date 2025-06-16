#!/usr/bin/env python3
"""
Prompt Builder for PyQwerty Bot
Loads systemprompt.md and builds complete prompts with message history
"""

import json
from pathlib import Path
from typing import List, Dict, Any
import discord

class PromptBuilder:
    def __init__(self):
        self.system_prompt = self.load_system_prompt()
        print(f"✅ Loaded system prompt ({len(self.system_prompt)} characters)")
    
    def load_system_prompt(self) -> str:
        """Load the exact system prompt from systemprompt.md"""
        prompt_file = Path('systemprompt.md')
        
        if not prompt_file.exists():
            raise FileNotFoundError("systemprompt.md not found!")
        
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        if not content:
            raise ValueError("systemprompt.md is empty!")
        
        return content
    
    def format_message_history(self, messages: List[Dict[str, Any]]) -> str:
        """Format message history for the prompt"""
        if not messages:
            return "No recent messages in this channel."
        
        formatted_messages = []
        
        for msg in messages:
            author_name = msg.get('author_name', 'Unknown')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', '')
            
            # Skip empty messages
            if not content.strip():
                continue
            
            # Format timestamp (just time, not full date)
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime('%H:%M')
            except:
                time_str = ''
            
            # Handle mentions in message content
            mentions = msg.get('mentions', [])
            display_content = content
            
            # Replace user IDs with mention format for context
            for user_id in mentions:
                display_content = display_content.replace(f'<@{user_id}>', f'<@{user_id}>')
            
            # Format: [Time] Username: Message
            if time_str:
                formatted_msg = f"[{time_str}] {author_name}: {display_content}"
            else:
                formatted_msg = f"{author_name}: {display_content}"
            
            formatted_messages.append(formatted_msg)
        
        return '\n'.join(formatted_messages)
    
    def build_prompt(self, message_history: List[Dict[str, Any]], trigger_message: discord.Message, patience_level: int = 70, allow_long_messages: bool = False, allow_gifs: bool = False) -> str:
        """Build complete prompt with system prompt + message history + current state"""
        
        # Format the message history
        formatted_history = self.format_message_history(message_history)
        
        # Build patience context
        if patience_level <= 20:
            patience_context = "CURRENT MOOD: You are VERY frustrated/angry. You're more likely to insult people, tell them to shut up, rage at stupid comments, or be aggressive. You might use ALL-CAPS more."
        elif patience_level <= 40:
            patience_context = "CURRENT MOOD: You are annoyed/irritated. You're more sarcastic, dismissive, and likely to call people out on stupid stuff."
        elif patience_level <= 60:
            patience_context = "CURRENT MOOD: You are somewhat neutral but slightly on edge. Normal PyQwerty behavior."
        elif patience_level <= 80:
            patience_context = "CURRENT MOOD: You are in a decent mood. More friendly than usual, but still keeping your personality."
        else:
            patience_context = "CURRENT MOOD: You are chill and in a good mood. More helpful and friendly, but still authentically PyQwerty."
        
        # Build message length context
        if allow_long_messages:
            length_context = "MESSAGE LENGTH: You can write longer responses when needed (2-4 sentences), but still keep your casual style and no ending punctuation."
        else:
            length_context = "MESSAGE LENGTH: Keep responses very brief - usually 1-8 words, maximum 1-2 short sentences."
        
        # Build GIF context
        if allow_gifs:
            gif_context = """GIF RESPONSES: You can now reply with GIFs! Use the format [GIF: search_term] anywhere in your response.

Available GIF reactions: fire, rage, angry, frustrated, cooked, washed, crying, dead, gg, valorant, minecraft, gaming, bruh, cringe, sus, sheesh, no way, what

Examples:
- For amazing plays: "that was insane [GIF: fire]"
- When angry: "[GIF: rage] shut up bro"
- For losses: "we're so cooked [GIF: crying]"
- For cringe moments: "[GIF: bruh]"
- Just GIFs: "[GIF: sheesh]"

Use GIFs when they fit your reaction naturally - especially when frustrated (rage GIFs), celebrating (fire GIFs), or reacting to cringe."""
        else:
            gif_context = "GIF RESPONSES: Disabled - respond with text only."
        
        # Build the complete prompt
        prompt = f"""{self.system_prompt}

{patience_context}

{length_context}

{gif_context}

{{message_history}}:
{formatted_history}

You are PyQwerty and have just read the above chat history. Generate your natural response as PyQwerty would, following all the rules in your persona AND your current mood/settings. Remember:
- Use STRICTLY lowercase (except for ALL-CAPS emphasis when angry)
- NO ending punctuation (., ?, !)
- React naturally to the most recent message or conversation flow
- Your patience level affects how aggressive/friendly you are
- Adjust response length based on settings but maintain your style
- Use GIFs when enabled and they fit your reaction naturally

Your response:"""
        
        return prompt
    
    def validate_system_prompt(self) -> bool:
        """Validate that the system prompt contains key elements"""
        required_elements = [
            'PyQwerty',
            'lowercase',
            'punctuation',
            'message_history',
            'Discord'
        ]
        
        for element in required_elements:
            if element.lower() not in self.system_prompt.lower():
                print(f"⚠️ Warning: '{element}' not found in system prompt")
                return False
        
        print("✅ System prompt validation passed")
        return True