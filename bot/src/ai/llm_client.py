#!/usr/bin/env python3
"""
OpenRouter LLM Client for PyQwerty Bot
Handles communication with OpenRouter API
"""

import os
import asyncio
import aiohttp
import json
from typing import Optional, Dict, Any

class OpenRouterClient:
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.model = os.getenv('OPENROUTER_MODEL', 'google/gemini-2.0-flash-exp')
        self.max_tokens = int(os.getenv('OPENROUTER_MAX_TOKENS', '150'))
        self.temperature = float(os.getenv('OPENROUTER_TEMPERATURE', '0.8'))
        self.base_url = 'https://openrouter.ai/api/v1'
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
        
        print(f"🔗 OpenRouter client initialized")
        print(f"🤖 Model: {self.model}")
        print(f"🎛️ Max tokens: {self.max_tokens}, Temperature: {self.temperature}")
    
    async def generate_response(self, prompt: str) -> Optional[str]:
        """Generate response using OpenRouter API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://github.com/your-repo',  # Replace with your repo
                'X-Title': 'PyQwerty Discord Bot'
            }
            
            payload = {
                'model': self.model,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': self.max_tokens,
                'temperature': self.temperature,
                'top_p': 0.9,
                'frequency_penalty': 0.1,
                'presence_penalty': 0.1
            }
            
            timeout = aiohttp.ClientTimeout(total=30)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f'{self.base_url}/chat/completions',
                    headers=headers,
                    json=payload
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'choices' in data and len(data['choices']) > 0:
                            message = data['choices'][0].get('message', {})
                            content = message.get('content', '').strip()
                            
                            print(f"✅ Generated response: \"{content[:100]}...\"")
                            return content
                        else:
                            print("❌ No choices in API response")
                            return None
                    
                    elif response.status == 429:
                        print("⏱️ Rate limited by OpenRouter, waiting...")
                        await asyncio.sleep(5)
                        return await self.generate_response(prompt)  # Retry once
                    
                    else:
                        error_text = await response.text()
                        print(f"❌ OpenRouter API error {response.status}: {error_text}")
                        return None
        
        except asyncio.TimeoutError:
            print("⏱️ OpenRouter API timeout")
            return None
        
        except Exception as e:
            print(f"❌ OpenRouter client error: {e}")
            return None
    
    async def test_connection(self) -> bool:
        """Test connection to OpenRouter API"""
        try:
            test_prompt = "Respond with just the word 'test'"
            response = await self.generate_response(test_prompt)
            
            if response:
                print(f"✅ OpenRouter connection test successful: {response}")
                return True
            else:
                print("❌ OpenRouter connection test failed")
                return False
        
        except Exception as e:
            print(f"❌ OpenRouter connection test error: {e}")
            return False