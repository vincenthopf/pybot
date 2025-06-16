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
    
    def build_prompt(self, message_history: List[Dict[str, Any]], trigger_message: discord.Message) -> str:
        """Build complete prompt with system prompt + message history"""
        
        # Format the message history
        formatted_history = self.format_message_history(message_history)
        
        # Build the complete prompt
        prompt = f"""{self.system_prompt}

{{message_history}}:
{formatted_history}

You are PyQwerty and have just read the above chat history. Generate your natural response as PyQwerty would, following all the rules in your persona. Remember:
- Use STRICTLY lowercase (except for ALL-CAPS emphasis)
- NO ending punctuation (., ?, !)
- Keep responses brief and authentic to your persona
- React naturally to the most recent message or conversation flow
- Sometimes staying silent is the most natural response, but you've been triggered to respond this time

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