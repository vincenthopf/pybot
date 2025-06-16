#!/usr/bin/env python3
"""
Discord Message Crawler for Pyqwerty Bot
Crawls all messages from a specific user across all accessible channels.
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import discord
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MessageCrawler:
    def __init__(self, token: str, target_user_id: int):
        self.target_user_id = target_user_id
        
        # Configure specific intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.guild_messages = True
        intents.members = True
        
        self.client = discord.Client(intents=intents)
        self.token = token
        self.messages = []
        self.stats = {
            'total_messages': 0,
            'servers_scanned': 0,
            'channels_scanned': 0,
            'errors': 0
        }
        
        # Setup event handlers
        self.client.event(self.on_ready)
    
    async def on_ready(self):
        """Called when bot is ready"""
        print(f'Logged in as {self.client.user}')
        print(f'Bot is in {len(self.client.guilds)} servers')
        
        # Start crawling
        await self.crawl_all_messages()
        
        # Save results
        await self.save_messages()
        
        # Print stats
        self.print_stats()
        
        # Close connection
        await self.client.close()
    
    async def crawl_all_messages(self):
        """Crawl messages from all accessible servers and channels"""
        print(f"\nStarting to crawl messages for user ID: {self.target_user_id}")
        
        for guild in self.client.guilds:
            print(f"\nScanning server: {guild.name} (ID: {guild.id})")
            self.stats['servers_scanned'] += 1
            
            # Get target user in this guild
            target_member = guild.get_member(self.target_user_id)
            if not target_member:
                print(f"  ⚠️  Target user not found in {guild.name}")
                continue
            
            print(f"  ✅ Found user: {target_member.display_name}")
            
            # Crawl all text channels
            for channel in guild.text_channels:
                try:
                    if not channel.permissions_for(guild.me).read_message_history:
                        print(f"    ❌ No permission to read {channel.name}")
                        continue
                    
                    print(f"    📂 Scanning #{channel.name}...")
                    self.stats['channels_scanned'] += 1
                    
                    channel_messages = await self.crawl_channel(channel, target_member)
                    if channel_messages:
                        print(f"      📄 Found {len(channel_messages)} messages")
                        self.messages.extend(channel_messages)
                    
                except discord.Forbidden:
                    print(f"    ❌ Access denied to #{channel.name}")
                    self.stats['errors'] += 1
                except Exception as e:
                    print(f"    ❌ Error in #{channel.name}: {e}")
                    self.stats['errors'] += 1
    
    async def crawl_channel(self, channel: discord.TextChannel, target_member: discord.Member) -> List[Dict]:
        """Crawl messages from a specific channel for the target user"""
        messages = []
        
        try:
            async for message in channel.history(limit=None, oldest_first=True):
                if message.author.id == self.target_user_id:
                    message_data = {
                        'id': message.id,
                        'content': message.content,
                        'timestamp': message.created_at.isoformat(),
                        'channel_id': channel.id,
                        'channel_name': channel.name,
                        'guild_id': channel.guild.id,
                        'guild_name': channel.guild.name,
                        'author_id': message.author.id,
                        'author_name': message.author.display_name,
                        'reply_to': message.reference.message_id if message.reference else None,
                        'attachments': [att.url for att in message.attachments],
                        'embeds': len(message.embeds),
                        'reactions': [{'emoji': str(reaction.emoji), 'count': reaction.count} 
                                    for reaction in message.reactions],
                        'mentions': [user.id for user in message.mentions],
                        'edited': message.edited_at.isoformat() if message.edited_at else None
                    }
                    messages.append(message_data)
                    self.stats['total_messages'] += 1
                
                # Rate limiting - Discord allows 50 requests per second
                if len(messages) % 100 == 0:
                    await asyncio.sleep(0.1)
        
        except discord.HTTPException as e:
            print(f"      ❌ HTTP error: {e}")
            self.stats['errors'] += 1
        
        return messages
    
    async def save_messages(self):
        """Save crawled messages to JSON file"""
        if not self.messages:
            print("\n❌ No messages found to save!")
            return
        
        # Create output directory
        output_dir = Path('data/raw')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'pyqwerty_messages_{timestamp}.json'
        filepath = output_dir / filename
        
        # Prepare data for saving
        output_data = {
            'metadata': {
                'target_user_id': self.target_user_id,
                'crawl_timestamp': datetime.now().isoformat(),
                'total_messages': len(self.messages),
                'date_range': {
                    'earliest': min(msg['timestamp'] for msg in self.messages),
                    'latest': max(msg['timestamp'] for msg in self.messages)
                } if self.messages else None,
                'stats': self.stats
            },
            'messages': sorted(self.messages, key=lambda x: x['timestamp'])
        }
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Messages saved to: {filepath}")
        print(f"📊 File size: {filepath.stat().st_size / 1024 / 1024:.2f} MB")
    
    def print_stats(self):
        """Print crawling statistics"""
        print(f"\n{'='*50}")
        print(f"📈 CRAWLING COMPLETE")
        print(f"{'='*50}")
        print(f"Total messages found: {self.stats['total_messages']}")
        print(f"Servers scanned: {self.stats['servers_scanned']}")
        print(f"Channels scanned: {self.stats['channels_scanned']}")
        print(f"Errors encountered: {self.stats['errors']}")
        
        if self.messages:
            # Channel breakdown
            channel_counts = {}
            for msg in self.messages:
                channel_key = f"{msg['guild_name']}#{msg['channel_name']}"
                channel_counts[channel_key] = channel_counts.get(channel_key, 0) + 1
            
            print(f"\n📊 Messages per channel:")
            for channel, count in sorted(channel_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {channel}: {count}")
    
    async def run(self):
        """Start the crawler"""
        try:
            await self.client.start(self.token)
        except KeyboardInterrupt:
            print("\n⚠️  Crawling interrupted by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            if not self.client.is_closed():
                await self.client.close()

async def main():
    """Main function"""
    # Get configuration
    bot_token = os.getenv('DISCORD_BOT_TOKEN')
    target_user_id = int(os.getenv('TARGET_USER_ID', '707614458826194955'))
    
    if not bot_token:
        print("❌ Error: DISCORD_BOT_TOKEN not found!")
        print("Please create a .env file with your bot token.")
        print("Copy .env.example to .env and fill in your values.")
        return
    
    print("🤖 Discord Message Crawler")
    print(f"Target User ID: {target_user_id}")
    print("Starting crawler...\n")
    
    # Create and run crawler
    crawler = MessageCrawler(bot_token, target_user_id)
    await crawler.run()

if __name__ == '__main__':
    asyncio.run(main())