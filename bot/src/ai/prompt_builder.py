#!/usr/bin/env python3
"""
Prompt Builder for PyQwerty Bot
Loads systemprompt.md and builds complete prompts with message history
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import pytz
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
        """Format message history for the prompt with improved context"""
        if not messages:
            return "No recent messages in this channel."
        
        # Ensure we have exactly the messages we want (up to 20)
        recent_messages = messages[-20:] if len(messages) > 20 else messages
        
        formatted_messages = []
        
        for i, msg in enumerate(recent_messages):
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
            
            # Handle mentions in message content for context
            mentions = msg.get('mentions', [])
            display_content = content
            
            # Keep mentions for context but they'll be removed from response
            for user_id in mentions:
                display_content = display_content.replace(f'<@{user_id}>', f'<@{user_id}>')
            
            # Determine if this is the latest message (last in the list)
            is_latest = (i == len(recent_messages) - 1)
            prefix = "LATEST MESSAGE:" if is_latest else f"[{time_str}]" if time_str else ""
            
            # Format message with clear indication of latest vs previous
            if is_latest:
                formatted_msg = f"LATEST MESSAGE: {author_name}: {display_content}"
            elif time_str:
                formatted_msg = f"[{time_str}] {author_name}: {display_content}"
            else:
                formatted_msg = f"{author_name}: {display_content}"
            
            formatted_messages.append(formatted_msg)
        
        return '\n'.join(formatted_messages)
    
    def get_texas_time_context(self) -> str:
        """Get current Texas time context for the prompt"""
        texas_tz = pytz.timezone('America/Chicago')
        texas_time = datetime.now(texas_tz)
        
        # Format time in a natural way
        time_str = texas_time.strftime("%I:%M %p")  # 3:45 PM
        date_str = texas_time.strftime("%A, %B %d")  # Monday, January 15
        
        return f"Current time in Texas: {time_str} on {date_str}"
    
    def build_prompt(self, message_history: List[Dict[str, Any]], trigger_message: discord.Message, allow_gifs: bool = False) -> str:
        """Build complete prompt with system prompt + message history + GIF settings"""
        
        # Format the message history
        formatted_history = self.format_message_history(message_history)
        
        # Get current Texas time context
        time_context = self.get_texas_time_context()
        
        # Build GIF context
        if allow_gifs:
            gif_context = """GIF RESPONSES: You can reply with GIFs! Use the format [GIF: search_term] anywhere in your response.

Available GIF reactions: fire, rage, angry, frustrated, cooked, washed, crying, dead, gg, valorant, minecraft, gaming, bruh, cringe, sus, sheesh, no way, what

Examples:
- For amazing plays: "that was insane [GIF: fire]"
- When annoyed: "[GIF: rage] shut up bro"
- For losses: "we're so cooked [GIF: crying]"
- For cringe moments: "[GIF: bruh]"
- Just GIFs: "[GIF: sheesh]"

Use GIFs when they fit your reaction naturally - especially when celebrating (fire GIFs) or reacting to cringe."""
        else:
            gif_context = "GIF RESPONSES: Disabled - respond with text only."
        
        # Build the complete prompt
        prompt = f"""{self.system_prompt}

{time_context}

{gif_context}

RECENT CHAT HISTORY (last 20 messages):
{formatted_history}

You are PyQwerty and have just read the above chat history. The "LATEST MESSAGE" is what just triggered you to respond. Generate your natural response as PyQwerty would, following all the rules in your persona. Remember:
- Use STRICTLY lowercase (except for ALL-CAPS emphasis when frustrated)
- NO ending punctuation (., ?, !)
- React naturally to the LATEST MESSAGE while considering the conversation context
- Use GIFs when enabled and they fit your reaction naturally
- You can reference the current time if relevant to your response

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