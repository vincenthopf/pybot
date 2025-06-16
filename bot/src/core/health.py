#!/usr/bin/env python3
"""
Simple health check server for the Discord bot
"""

import asyncio
from aiohttp import web
import json
import os

class HealthCheckServer:
    def __init__(self, bot_instance=None):
        self.bot = bot_instance
        self.app = web.Application()
        self.setup_routes()
    
    def setup_routes(self):
        """Setup health check routes"""
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_get('/status', self.status_check)
    
    async def health_check(self, request):
        """Basic health check endpoint"""
        return web.json_response({
            "status": "healthy",
            "service": "pyqwerty-discord-bot",
            "timestamp": asyncio.get_event_loop().time()
        })
    
    async def status_check(self, request):
        """Detailed status check"""
        status = {
            "status": "running",
            "service": "pyqwerty-discord-bot",
            "version": "1.0.0",
            "bot_connected": False,
            "bot_active": False
        }
        
        if self.bot:
            status["bot_connected"] = not self.bot.client.is_closed()
            status["bot_active"] = self.bot.is_active
            if self.bot.client.user:
                status["bot_user"] = {
                    "id": self.bot.client.user.id,
                    "name": self.bot.client.user.name
                }
        
        return web.json_response(status)
    
    async def start_server(self, host='0.0.0.0', port=8080):
        """Start the health check server"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        print(f"🏥 Health check server started on {host}:{port}")
        return runner