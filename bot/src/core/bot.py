#!/usr/bin/env python3
"""
PyQwerty Discord Bot - Main Bot Implementation
Embodies PyQwerty persona using systemprompt.md and style analysis
"""

import asyncio
import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import discord
from dotenv import load_dotenv

from ..ai.llm_client import OpenRouterClient
from ..ai.prompt_builder import PromptBuilder
from ..ai.style_validator import StyleValidator

# Load environment variables
load_dotenv()

class PyQwertyBot:
    def __init__(self):
        # Configuration
        self.target_user_id = int(os.getenv('TARGET_USER_ID', '707614458826194955'))
        self.bot_token = os.getenv('DISCORD_BOT_TOKEN')
        self.rate_limit_seconds = int(os.getenv('RATE_LIMIT_MESSAGES', '30'))
        
        # Discord setup
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.guild_messages = True
        intents.members = True
        
        self.client = discord.Client(intents=intents)
        
        # AI components
        self.llm_client = OpenRouterClient()
        self.prompt_builder = PromptBuilder()
        self.style_validator = StyleValidator()
        
        # State tracking
        self.last_response_time = {}  # channel_id -> timestamp
        self.message_history = {}     # channel_id -> list of recent messages
        self.is_active = True
        
        # Setup event handlers
        self.client.event(self.on_ready)
        self.client.event(self.on_message)
        
        print("🤖 PyQwerty Bot initialized")
    
    async def on_ready(self):
        """Called when bot is ready"""
        print(f'✅ Bot logged in as {self.client.user}')
        print(f'📊 Bot is in {len(self.client.guilds)} servers')
        print(f'🎯 Responding to all users as PyQwerty (original user ID: {self.target_user_id})')
    
    async def on_message(self, message: discord.Message):
        """Handle incoming messages"""
        # Ignore bot messages and DMs
        if message.author.bot or not message.guild:
            return
        
        # Handle admin commands first
        if message.content.startswith('!py'):
            await self.handle_admin_command(message)
            return
        
        # Track message history for context
        await self.update_message_history(message)
        
        # Check if we should respond
        if await self.should_respond(message):
            await self.generate_and_send_response(message)
    
    async def update_message_history(self, message: discord.Message):
        """Update message history for context"""
        channel_id = message.channel.id
        
        if channel_id not in self.message_history:
            self.message_history[channel_id] = []
        
        # Add message to history
        message_data = {
            'id': message.id,
            'author_id': message.author.id,
            'author_name': message.author.display_name,
            'content': message.content,
            'timestamp': message.created_at.isoformat(),
            'reply_to': message.reference.message_id if message.reference else None,
            'mentions': [user.id for user in message.mentions],
            'attachments': len(message.attachments) > 0
        }
        
        self.message_history[channel_id].append(message_data)
        
        # Keep only last 25 messages (we'll use 20 for context)
        if len(self.message_history[channel_id]) > 25:
            self.message_history[channel_id] = self.message_history[channel_id][-25:]
    
    async def should_respond(self, message: discord.Message) -> bool:
        """Determine if bot should respond to this message"""
        # Don't respond to bot messages (including our own)
        if message.author.bot:
            return False
        
        # Check if bot is active
        if not self.is_active:
            return False
        
        # Rate limiting - don't respond too frequently
        channel_id = message.channel.id
        now = datetime.now()
        
        if channel_id in self.last_response_time:
            time_since_last = (now - self.last_response_time[channel_id]).total_seconds()
            if time_since_last < self.rate_limit_seconds:
                print(f"⏱️ Rate limited - {time_since_last:.1f}s since last response")
                return False
        
        # Sometimes don't respond (as specified in prompt - natural behavior)
        # Higher chance to respond if:
        # - Message mentions PyQwerty bot or someone specific
        # - Message is a question
        # - Message is about gaming topics
        # - Haven't responded in a while
        
        response_probability = 0.25  # Base 25% chance (slightly lower since responding to everyone)
        
        # Increase probability based on content
        content_lower = message.content.lower()
        
        # Check if bot is mentioned directly
        bot_mentioned = self.client.user in message.mentions if self.client.user else False
        if bot_mentioned:
            response_probability = 1.0  # Always respond when directly mentioned
        elif message.mentions:
            response_probability += 0.3  # Moderately likely to respond to other mentions
        
        if '?' in message.content:
            response_probability += 0.3  # More likely to respond to questions
        
        gaming_keywords = ['valorant', 'minecraft', 'game', 'play', 'rank', 'clutch', 'gg']
        if any(keyword in content_lower for keyword in gaming_keywords):
            response_probability += 0.3
        
        # Time since last response factor
        if channel_id in self.last_response_time:
            hours_since = (now - self.last_response_time[channel_id]).total_seconds() / 3600
            if hours_since > 2:
                response_probability += 0.2
        else:
            response_probability += 0.2  # First message in channel
        
        # Cap at 85% max probability
        response_probability = min(response_probability, 0.85)
        
        should_respond = random.random() < response_probability
        
        if should_respond:
            print(f"🎯 Will respond to {message.author.display_name} (probability: {response_probability:.2f})")
        else:
            print(f"🤐 Staying silent for {message.author.display_name} (probability: {response_probability:.2f})")
        
        return should_respond
    
    async def generate_and_send_response(self, trigger_message: discord.Message):
        """Generate and send PyQwerty response"""
        try:
            channel_id = trigger_message.channel.id
            
            # Get recent message history for context
            recent_messages = self.message_history.get(channel_id, [])[-20:]  # Last 20 messages
            
            # Build prompt with message history
            prompt = self.prompt_builder.build_prompt(recent_messages, trigger_message)
            
            print(f"🧠 Generating response for: \"{trigger_message.content[:50]}...\"")
            
            # Generate response using LLM
            response = await self.llm_client.generate_response(prompt)
            
            if not response or not response.strip():
                print("❌ Empty response from LLM")
                return
            
            # Validate and adjust response to match style (removes mentions, uses replies instead)
            validated_response = self.style_validator.validate_and_adjust(response)
            
            print(f"💬 Sending response: \"{validated_response}\"")
            
            # Check if response should be a reply (if it would have mentioned someone)
            should_reply = self.should_use_reply(response, trigger_message)
            
            if should_reply:
                # Send as reply to the original message
                await trigger_message.reply(validated_response)
            else:
                # Send as regular message
                await trigger_message.channel.send(validated_response)
            
            # Update last response time
            self.last_response_time[channel_id] = datetime.now()
            
        except Exception as e:
            print(f"❌ Error generating response: {e}")
    
    def should_use_reply(self, original_response: str, trigger_message: discord.Message) -> bool:
        """Determine if response should be sent as a reply based on context"""
        # Always reply if bot was mentioned directly
        if self.client.user and self.client.user in trigger_message.mentions:
            return True
        
        # Reply if the original LLM response contained mentions (before they were removed)
        if '<@' in original_response:
            return True
        
        # Reply if it's a question being answered
        if '?' in trigger_message.content:
            return True
        
        # Reply if responding to a specific statement (conversational context)
        # Check if recent messages show direct conversation flow
        channel_id = trigger_message.channel.id
        recent_messages = self.message_history.get(channel_id, [])
        
        if len(recent_messages) >= 2:
            # If last 2 messages were from same user, likely continuing conversation
            last_msg = recent_messages[-1]
            second_last = recent_messages[-2] if len(recent_messages) > 1 else None
            
            if (last_msg['author_id'] == trigger_message.author.id and 
                second_last and second_last['author_id'] == trigger_message.author.id):
                return True
        
        # Default to regular message for ambient responses
        return False
    
    async def handle_admin_command(self, message: discord.Message):
        """Handle admin commands"""
        if not message.content.startswith('!py'):
            return
        
        # Allow the original target user and server admins to use commands
        allowed_users = [self.target_user_id]  # Add more admin IDs here if needed
        if message.author.id not in allowed_users and not message.author.guild_permissions.administrator:
            return
        
        command = message.content[3:].strip().lower()
        
        if command == 'pause':
            self.is_active = False
            await message.channel.send("🛑 PyQwerty bot paused")
        
        elif command == 'resume':
            self.is_active = True
            await message.channel.send("▶️ PyQwerty bot resumed")
        
        elif command == 'status':
            status = "Active" if self.is_active else "Paused"
            await message.channel.send(f"📊 PyQwerty bot status: {status}")
    
    async def start(self):
        """Start the bot"""
        if not self.bot_token:
            raise ValueError("DISCORD_BOT_TOKEN not found in environment variables")
        
        try:
            await self.client.start(self.bot_token)
        except KeyboardInterrupt:
            print("\n⚠️ Bot stopped by user")
        except Exception as e:
            print(f"❌ Bot error: {e}")
        finally:
            if not self.client.is_closed():
                await self.client.close()

async def main():
    """Main function"""
    bot = PyQwertyBot()
    await bot.start()

if __name__ == '__main__':
    asyncio.run(main())