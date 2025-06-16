#!/usr/bin/env python3
"""
Debug script to list all members in accessible servers
"""

import asyncio
import os
from dotenv import load_dotenv
import discord

load_dotenv()

class MemberLister:
    def __init__(self, token: str):
        intents = discord.Intents.default()
        intents.members = True
        intents.guilds = True
        
        self.client = discord.Client(intents=intents)
        self.token = token
        
        self.client.event(self.on_ready)
    
    async def on_ready(self):
        print(f'Logged in as {self.client.user}')
        
        for guild in self.client.guilds:
            print(f"\n🏠 Server: {guild.name} (ID: {guild.id})")
            print(f"   Members: {guild.member_count}")
            
            # List members with "py" in their name
            py_members = []
            for member in guild.members:
                if 'py' in member.name.lower() or 'py' in member.display_name.lower():
                    py_members.append(member)
            
            if py_members:
                print(f"   👥 Members with 'py' in name:")
                for member in py_members:
                    print(f"      - {member.display_name} (@{member.name}) - ID: {member.id}")
            else:
                print(f"   ❌ No members found with 'py' in name")
            
            # Show first 10 members
            print(f"   📝 First 10 members:")
            for i, member in enumerate(guild.members[:10]):
                print(f"      {i+1}. {member.display_name} (@{member.name}) - ID: {member.id}")
        
        await self.client.close()
    
    async def run(self):
        await self.client.start(self.token)

async def main():
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("❌ DISCORD_BOT_TOKEN not found!")
        return
    
    lister = MemberLister(token)
    await lister.run()

if __name__ == '__main__':
    asyncio.run(main())