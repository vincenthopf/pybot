#!/usr/bin/env python3
"""
PyQwerty Discord Bot Runner
Entry point for running the bot
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.core.bot import PyQwertyBot

async def main():
    """Main entry point"""
    print("🚀 Starting PyQwerty Discord Bot...")
    print("📋 Using systemprompt.md for persona")
    print("📊 Using analyzed style patterns from 1,386 messages")
    print("=" * 60)
    
    # Import health check server
    from src.core.health import HealthCheckServer
    
    try:
        # Create bot instance
        bot = PyQwertyBot()
        
        # Start health check server (optional)
        health_server = HealthCheckServer(bot)
        health_runner = None
        
        try:
            health_runner = await health_server.start_server()
        except Exception as e:
            print(f"⚠️ Health check server failed to start: {e}")
        
        # Start the bot
        await bot.start()
        
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return 1
    finally:
        # Cleanup health server if it was started
        if 'health_runner' in locals() and health_runner:
            await health_runner.cleanup()
    
    return 0

if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)