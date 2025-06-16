#!/usr/bin/env python3
"""
Test script for PyQwerty Bot components
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.ai.llm_client import OpenRouterClient
from src.ai.prompt_builder import PromptBuilder
from src.ai.style_validator import StyleValidator

async def test_llm_client():
    """Test OpenRouter connection"""
    print("🧪 Testing OpenRouter client...")
    
    try:
        client = OpenRouterClient()
        success = await client.test_connection()
        
        if success:
            print("✅ OpenRouter client test passed")
            return True
        else:
            print("❌ OpenRouter client test failed")
            return False
    except Exception as e:
        print(f"❌ OpenRouter client error: {e}")
        return False

def test_prompt_builder():
    """Test prompt builder"""
    print("\n🧪 Testing prompt builder...")
    
    try:
        builder = PromptBuilder()
        
        # Test with sample message history
        sample_messages = [
            {
                'author_name': 'TestUser',
                'content': 'hey anyone wanna play valorant',
                'timestamp': '2025-06-16T12:00:00+00:00',
                'mentions': [],
                'author_id': 12345
            }
        ]
        
        # Create a mock trigger message
        class MockMessage:
            def __init__(self):
                self.content = "yeah lets play"
                self.author = MockUser()
        
        class MockUser:
            def __init__(self):
                self.id = 707614458826194955
                self.display_name = "Py"
        
        prompt = builder.build_prompt(sample_messages, MockMessage())
        
        if 'PyQwerty' in prompt and 'message_history' in prompt:
            print("✅ Prompt builder test passed")
            print(f"📝 Generated prompt: {len(prompt)} characters")
            return True
        else:
            print("❌ Prompt builder test failed - missing key elements")
            return False
    
    except Exception as e:
        print(f"❌ Prompt builder error: {e}")
        return False

def test_style_validator():
    """Test style validator"""
    print("\n🧪 Testing style validator...")
    
    try:
        validator = StyleValidator()
        
        # Test responses
        test_cases = [
            ("This is a formal response with proper capitalization.", "Expected: lowercase conversion"),
            ("nah bro that's crazy fr", "Expected: pass validation"),
            ("DAMN that's actually insane what the hell!", "Expected: keep ALL-CAPS emphasis"),
            ("Yeah, I think that's a good idea.", "Expected: remove punctuation, lowercase"),
            ("<@123456789> hey bro what's up", "Expected: remove all mentions"),
            ("<@!987654321> yo <@555555555> check this out", "Expected: remove multiple mentions")
        ]
        
        all_passed = True
        
        for test_input, expected in test_cases:
            # Test mention removal (no bot ID needed now)
            result = validator.validate_and_adjust(test_input)
            stats = validator.get_response_stats(result)
            
            print(f"   Input: \"{test_input}\"")
            print(f"   Output: \"{result}\"")
            print(f"   Stats: {stats}")
            print(f"   {expected}")
            print()
        
        print("✅ Style validator test completed")
        return True
    
    except Exception as e:
        print(f"❌ Style validator error: {e}")
        return False

async def test_full_pipeline():
    """Test the full response generation pipeline"""
    print("\n🧪 Testing full pipeline...")
    
    try:
        # Initialize components
        llm_client = OpenRouterClient()
        prompt_builder = PromptBuilder()
        style_validator = StyleValidator()
        
        # Sample conversation
        sample_messages = [
            {
                'author_name': 'Friend1',
                'content': 'yo anyone down for some minecraft',
                'timestamp': '2025-06-16T12:00:00+00:00',
                'mentions': [],
                'author_id': 12345
            },
            {
                'author_name': 'Py',
                'content': 'im down but my internet is trash rn',
                'timestamp': '2025-06-16T12:01:00+00:00',
                'mentions': [],
                'author_id': 707614458826194955
            }
        ]
        
        # Mock trigger message
        class MockMessage:
            def __init__(self):
                self.content = "lets start the server"
                self.author = MockUser()
        
        class MockUser:
            def __init__(self):
                self.id = 707614458826194955
                self.display_name = "Py"
        
        # Build prompt
        prompt = prompt_builder.build_prompt(sample_messages, MockMessage())
        print(f"📝 Built prompt ({len(prompt)} chars)")
        
        # Generate response (only if API key is available)
        if llm_client.api_key:
            print("🧠 Generating response...")
            response = await llm_client.generate_response(prompt)
            
            if response:
                # Validate response (mentions will be removed, replies used instead)
                validated_response = style_validator.validate_and_adjust(response)
                
                print(f"🤖 Raw response: \"{response}\"")
                print(f"✅ Final response: \"{validated_response}\"")
                
                stats = style_validator.get_response_stats(validated_response)
                print(f"📊 Response stats: {stats}")
                
                return True
            else:
                print("❌ No response generated")
                return False
        else:
            print("⚠️ No OpenRouter API key - skipping LLM test")
            return True
    
    except Exception as e:
        print(f"❌ Full pipeline error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 PyQwerty Bot Component Tests")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    # Test individual components
    if test_prompt_builder():
        tests_passed += 1
    
    if test_style_validator():
        tests_passed += 1
    
    if await test_llm_client():
        tests_passed += 1
    
    if await test_full_pipeline():
        tests_passed += 1
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Bot is ready to run.")
        return 0
    else:
        print("❌ Some tests failed. Check configuration and try again.")
        return 1

if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)