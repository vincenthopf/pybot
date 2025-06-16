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
        self.rate_limit_seconds = int(os.getenv('RATE_LIMIT_MESSAGES', '8'))
        
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
        self.base_response_rate = 0.25  # Default 25% response rate
        self.allow_gifs = False       # Allow GIF responses
        
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
        
        response_probability = self.base_response_rate  # Configurable base response rate
        
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
            
            # Build prompt with message history and GIF settings
            prompt = self.prompt_builder.build_prompt(
                recent_messages, 
                trigger_message, 
                allow_gifs=self.allow_gifs
            )
            
            print(f"🧠 Generating response for: \"{trigger_message.content[:50]}...\"")
            
            # Generate response using LLM
            response = await self.llm_client.generate_response(prompt)
            
            if not response or not response.strip():
                print("❌ Empty response from LLM")
                return
            
            # Check if response contains a GIF command
            gif_url = self.extract_gif_command(response)
            
            if gif_url:
                # Handle GIF response
                await self.send_gif_response(trigger_message, response, gif_url)
            else:
                # Handle regular text response
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
    
    def extract_gif_command(self, response: str) -> str:
        """Extract GIF URL from response if present"""
        import re
        
        # Look for GIF command format: [GIF: search_term]
        gif_match = re.search(r'\[GIF:\s*([^\]]+)\]', response, re.IGNORECASE)
        if gif_match:
            search_term = gif_match.group(1).strip()
            return self.get_gif_url(search_term)
        
        return None
    
    def get_gif_url(self, search_term: str) -> str:
        """Get a GIF URL for the search term using embeddable direct links"""
        # Use reliable GIF URLs that Discord will embed
        predefined_gifs = {
            'fire': 'https://c.tenor.com/SOVMSXAQbrcAAAAC/fire-flame.gif',
            'rage': 'https://c.tenor.com/Q6VJvI2tTJgAAAAC/mad-angry.gif',
            'angry': 'https://c.tenor.com/fqYKuph4LesAAAAC/angry-mad.gif',
            'frustrated': 'https://c.tenor.com/1MTtKJKdoe8AAAAC/frustrated-annoyed.gif',
            'cooked': 'https://c.tenor.com/5iRznPZtxQ4AAAAC/cooked-done.gif',
            'washed': 'https://c.tenor.com/XR1Gq-RGdSMAAAAC/washed-up.gif',
            'crying': 'https://c.tenor.com/BpNuKy7D1KYAAAAC/crying-sad.gif',
            'dead': 'https://c.tenor.com/UeMFAlw6mVcAAAAC/dead-skull.gif',
            'gg': 'https://c.tenor.com/mGGe6k5iPqkAAAAC/gg-good-game.gif',
            'valorant': 'https://c.tenor.com/WNF7k-_DdKAAAAAC/valorant-riot.gif',
            'minecraft': 'https://c.tenor.com/aSyKY8JsB-8AAAAC/minecraft-block.gif',
            'gaming': 'https://c.tenor.com/1Z6mNMxKgJwAAAAC/gaming-gamer.gif',
            'bruh': 'https://c.tenor.com/1okcayEZflIAAAAC/bruh-moment.gif',
            'cringe': 'https://c.tenor.com/xFOprSGKFJkAAAAC/cringe-awkward.gif',
            'sus': 'https://c.tenor.com/Uh7L3BxhfYMAAAAC/sus-suspicious.gif',
            'sheesh': 'https://c.tenor.com/cJgEOhG9TS8AAAAC/sheesh-damn.gif',
            'no way': 'https://c.tenor.com/8-DfXPJVP-YAAAAC/no-way-shocked.gif',
            'what': 'https://c.tenor.com/lqaGkRhWQe8AAAAC/what-confused.gif'
        }
        
        search_lower = search_term.lower()
        
        # Try exact match first
        if search_lower in predefined_gifs:
            return predefined_gifs[search_lower]
        
        # Try partial matches
        for key, url in predefined_gifs.items():
            if key in search_lower or search_lower in key:
                return url
        
        # Default fallback GIF for unknown terms
        return predefined_gifs.get('bruh', 'https://c.tenor.com/1okcayEZflIAAAAC/bruh-moment.gif')
    
    async def send_gif_response(self, trigger_message: discord.Message, original_response: str, gif_url: str):
        """Send a GIF response with optional text using Discord embeds"""
        import re
        
        # Extract text part (remove GIF command)
        text_response = re.sub(r'\[GIF:\s*[^\]]+\]', '', original_response, flags=re.IGNORECASE).strip()
        
        # Validate any remaining text
        if text_response:
            validated_text = self.style_validator.validate_and_adjust(text_response)
        else:
            validated_text = ""
        
        print(f"🎬 Sending GIF: {gif_url}")
        if validated_text:
            print(f"💬 With text: \"{validated_text}\"")
        
        # Create embed for better GIF display
        embed = discord.Embed(description=validated_text if validated_text else "")
        embed.set_image(url=gif_url)
        embed.color = 0x7289DA  # Discord blurple
        
        # Determine if should reply
        should_reply = self.should_use_reply(original_response, trigger_message)
        
        # Send the message with embedded GIF
        try:
            if should_reply:
                if validated_text:
                    await trigger_message.reply(content=validated_text, embed=embed)
                else:
                    await trigger_message.reply(embed=embed)
            else:
                if validated_text:
                    await trigger_message.channel.send(content=validated_text, embed=embed)
                else:
                    await trigger_message.channel.send(embed=embed)
        except discord.HTTPException:
            # Fallback to just URL if embed fails
            print("⚠️ Embed failed, sending as URL")
            if should_reply:
                if validated_text:
                    await trigger_message.reply(f"{validated_text}\n{gif_url}")
                else:
                    await trigger_message.reply(gif_url)
            else:
                if validated_text:
                    await trigger_message.channel.send(f"{validated_text}\n{gif_url}")
                else:
                    await trigger_message.channel.send(gif_url)
    
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
            gifs = "Enabled" if self.allow_gifs else "Disabled"
            await message.channel.send(f"📊 PyQwerty bot status: {status}\n🎯 Response rate: {int(self.base_response_rate * 100)}%\n🎬 GIFs: {gifs}")
        
        elif command.startswith('rate '):
            try:
                new_rate = int(command.split()[1])
                if 0 <= new_rate <= 100:
                    self.base_response_rate = new_rate / 100
                    await message.channel.send(f"🎯 Response rate set to {new_rate}%")
                else:
                    await message.channel.send("❌ Rate must be between 0-100")
            except (ValueError, IndexError):
                await message.channel.send("❌ Usage: `!py rate <0-100>`")
        
        elif command == 'gifs':
            self.allow_gifs = not self.allow_gifs
            status = "enabled" if self.allow_gifs else "disabled"
            await message.channel.send(f"🎬 GIFs {status}")
        
        elif command == 'help':
            help_text = """🤖 **PyQwerty Bot Commands**
            
`!py pause` - Pause bot responses
`!py resume` - Resume bot responses  
`!py status` - Show bot status and settings
`!py rate <0-100>` - Set response rate percentage
`!py gifs` - Toggle GIF responses on/off
`!py help` - Show this help message

**Examples:**
`!py rate 50` - Respond to 50% of messages
`!py gifs` - Enable PyQwerty to reply with reaction GIFs"""
            await message.channel.send(help_text)
    
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