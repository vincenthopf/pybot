#!/usr/bin/env python3
"""
Style Validator for PyQwerty Bot
Ensures responses match analyzed style patterns from the 1,386 message dataset
"""

import json
import re
import random
from pathlib import Path
from typing import List, Dict, Any, Optional

class StyleValidator:
    def __init__(self):
        self.style_profile = self.load_style_profile()
        self.load_style_patterns()
        print("✅ Style validator initialized with authentic patterns")
    
    def load_style_profile(self) -> Dict[str, Any]:
        """Load the comprehensive style profile"""
        # Find the most recent style profile
        profile_files = list(Path('data/processed').glob('pyqwerty_*_profile_*.json'))
        
        if not profile_files:
            print("⚠️ No style profile found, using basic validation")
            return {}
        
        latest_profile = max(profile_files, key=lambda x: x.stat().st_mtime)
        
        with open(latest_profile, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_style_patterns(self):
        """Extract key patterns from style analysis"""
        if not self.style_profile:
            # Fallback patterns if no profile
            self.patterns = {
                'avg_word_count': 4.8,
                'lowercase_percentage': 73.0,
                'no_punctuation_percentage': 92.5,
                'common_starters': ['i', 'it', 'im', 'yeah', 'bro'],
                'common_words': ['i', 'it', 'to', 'the', 'a', 'and', 'my', 'you'],
                'slang_terms': ['bro', 'lol', 'nah', 'fr', 'wtf', 'ur'],
                'contractions': ['im', 'ur', 'dont', 'cant', 'wont']
            }
            return
        
        # Extract patterns from loaded profile
        basic_stats = self.style_profile.get('basic_stats', {})
        vocab = self.style_profile.get('vocabulary', {})
        style = self.style_profile.get('punctuation_and_style', {})
        
        self.patterns = {
            'avg_word_count': basic_stats.get('avg_word_count', 4.8),
            'lowercase_percentage': style.get('style_percentages', {}).get('starts_with_lowercase', 73.0),
            'no_punctuation_percentage': style.get('style_percentages', {}).get('no_punctuation_end', 92.5),
            'common_starters': [word for word, _ in vocab.get('most_common_words', [])[:10]],
            'common_words': [word for word, _ in vocab.get('most_common_words', [])[:20]],
            'slang_terms': ['bro', 'lol', 'nah', 'fr', 'wtf', 'ur', 'yall', 'cuz'],
            'contractions': ['im', 'ur', 'dont', 'cant', 'wont', 'ill', 'youre']
        }
    
    def validate_and_adjust(self, response: str) -> str:
        """Validate response against style patterns and adjust if needed"""
        if not response or not response.strip():
            return ""
        
        # Clean up the response
        adjusted = response.strip()
        
        # 1. Remove all mentions (we'll use Discord replies instead)
        adjusted = self.remove_mentions(adjusted)
        
        # 2. Enforce lowercase (except ALL-CAPS emphasis)
        adjusted = self.enforce_capitalization(adjusted)
        
        # 3. Remove ending punctuation (92.5% of messages have no ending punctuation)
        adjusted = self.remove_ending_punctuation(adjusted)
        
        # 4. Check message length and adjust if too verbose
        adjusted = self.adjust_message_length(adjusted)
        
        # 5. Ensure slang/contractions are used authentically
        adjusted = self.apply_authentic_slang(adjusted)
        
        # 6. Final validation
        if not self.is_valid_response(adjusted):
            # Fallback to a typical Py response if validation fails
            return self.get_fallback_response()
        
        return adjusted
    
    def remove_mentions(self, text: str) -> str:
        """Remove all mentions from the response (we'll use replies instead)"""
        import re
        
        # Remove all user mentions (we'll use Discord replies instead)
        # Pattern matches <@123456789> and <@!123456789>
        mention_pattern = r'<@!?\d+>'
        text = re.sub(mention_pattern, '', text).strip()
        
        # Clean up any double spaces left behind
        text = ' '.join(text.split())
        
        return text
    
    def enforce_capitalization(self, text: str) -> str:
        """Enforce lowercase with ALL-CAPS emphasis only"""
        # Split into words to handle ALL-CAPS emphasis
        words = text.split()
        adjusted_words = []
        
        for word in words:
            # Keep ALL-CAPS words (emphasis like DAMN, WTF, etc.)
            if word.isupper() and len(word) > 1:
                adjusted_words.append(word)
            # Handle contractions properly (i'm, don't, etc.)
            elif "'" in word:
                adjusted_words.append(word.lower())
            # Everything else lowercase
            else:
                adjusted_words.append(word.lower())
        
        return ' '.join(adjusted_words)
    
    def remove_ending_punctuation(self, text: str) -> str:
        """Remove ending punctuation (matches 92.5% pattern)"""
        # Remove ending punctuation but keep internal punctuation
        text = text.rstrip('.,!?;')
        
        # Keep ellipses if they're meaningful
        if text.endswith('...'):
            return text
        
        return text
    
    def adjust_message_length(self, text: str) -> str:
        """Adjust message length to match typical patterns"""
        words = text.split()
        word_count = len(words)
        
        # If message is too long (>15 words), try to shorten it
        if word_count > 15:
            # Keep first part that's more natural
            if word_count > 20:
                # Very long - take first sentence or reasonable chunk
                sentences = re.split(r'[.!?]', text)
                if sentences:
                    return sentences[0].strip()
            
            # Moderately long - trim to key message
            return ' '.join(words[:12])
        
        return text
    
    def apply_authentic_slang(self, text: str) -> str:
        """Apply authentic slang patterns"""
        # Common replacements based on Py's patterns
        replacements = {
            r'\byou\b': 'u',
            r'\byour\b': 'ur', 
            r'\bbecause\b': 'cuz',
            r'\bfor real\b': 'fr',
            r'\bthough\b': 'tho',
            r'\bsomething\b': 'smth',
            r'\bwant to\b': 'wanna',
            r'\bgoing to\b': 'gonna',
            r'\bdon\'t know\b': 'idk',
            r'\bok\b': 'ok',  # Keep simple
        }
        
        adjusted = text
        for pattern, replacement in replacements.items():
            adjusted = re.sub(pattern, replacement, adjusted, flags=re.IGNORECASE)
        
        return adjusted
    
    def is_valid_response(self, response: str) -> bool:
        """Check if response meets basic validation criteria"""
        if not response or not response.strip():
            return False
        
        # Check length (should be reasonable)
        word_count = len(response.split())
        if word_count == 0 or word_count > 25:
            return False
        
        # Check for proper lowercase (allowing ALL-CAPS emphasis)
        words = response.split()
        proper_case_count = 0
        
        for word in words:
            # ALL-CAPS words are fine
            if word.isupper():
                continue
            # Contractions should be lowercase
            elif "'" in word and word.islower():
                proper_case_count += 1
            # Regular words should be lowercase
            elif word.islower():
                proper_case_count += 1
        
        # At least 80% should follow lowercase rules
        if len(words) > 0 and (proper_case_count / len(words)) < 0.8:
            return False
        
        return True
    
    def get_fallback_response(self) -> str:
        """Get a fallback response if validation fails"""
        # Use authentic short responses from the analysis
        fallback_responses = [
            "nah",
            "fr",
            "idk",
            "crazy",
            "bro",
            "yeah",
            "wtf",
            "lmao"
        ]
        
        return random.choice(fallback_responses)
    
    def get_response_stats(self, response: str) -> Dict[str, Any]:
        """Get statistics about the response for debugging"""
        words = response.split()
        
        return {
            'word_count': len(words),
            'char_count': len(response),
            'has_ending_punctuation': response.endswith(('.', '!', '?')),
            'is_all_lowercase': response.islower(),
            'contains_slang': any(slang in response.lower() for slang in self.patterns['slang_terms'])
        }