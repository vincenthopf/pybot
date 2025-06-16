#!/usr/bin/env python3
"""
Message Examples Extractor
Extracts specific examples and creates detailed style documentation.
"""

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List
import random
from datetime import datetime

class MessageExamplesExtractor:
    def __init__(self, messages_file: str):
        self.messages_file = messages_file
        self.messages = []
        self.examples = defaultdict(list)
        
    def load_messages(self):
        """Load messages"""
        with open(self.messages_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.messages = [msg for msg in data['messages'] if msg['content'].strip()]
        print(f"✅ Loaded {len(self.messages)} non-empty messages")
        
    def extract_by_length(self):
        """Extract examples by message length"""
        one_word = []
        two_three_words = []
        short_responses = []  # 4-10 words
        medium_messages = []  # 11-20 words
        long_messages = []    # 20+ words
        
        for msg in self.messages:
            content = msg['content'].strip()
            words = content.split()
            word_count = len(words)
            
            if word_count == 1:
                one_word.append(content)
            elif word_count in [2, 3]:
                two_three_words.append(content)
            elif 4 <= word_count <= 10:
                short_responses.append(content)
            elif 11 <= word_count <= 20:
                medium_messages.append(content)
            elif word_count > 20:
                long_messages.append(content)
        
        self.examples['one_word'] = random.sample(one_word, min(20, len(one_word)))
        self.examples['two_three_words'] = random.sample(two_three_words, min(20, len(two_three_words)))
        self.examples['short_responses'] = random.sample(short_responses, min(30, len(short_responses)))
        self.examples['medium_messages'] = random.sample(medium_messages, min(20, len(medium_messages)))
        self.examples['long_messages'] = random.sample(long_messages, min(15, len(long_messages)))
        
    def extract_by_conversation_function(self):
        """Extract by conversational function"""
        agreements = []
        disagreements = []
        questions = []
        responses_to_questions = []
        topic_starters = []
        casual_acknowledgments = []
        
        # Pattern matching
        for i, msg in enumerate(self.messages):
            content = msg['content'].strip().lower()
            
            # Agreements
            if any(word in content for word in ['yes', 'yeah', 'yep', 'true', 'right', 'exactly', 'definitely']):
                agreements.append(msg['content'].strip())
            
            # Disagreements  
            if any(word in content for word in ['no', 'nah', 'nope', 'wrong', 'false', 'disagree']):
                disagreements.append(msg['content'].strip())
            
            # Questions
            if content.endswith('?'):
                questions.append(msg['content'].strip())
            
            # Casual acknowledgments
            if any(word in content for word in ['ok', 'alright', 'cool', 'nice', 'got it', 'fair']):
                casual_acknowledgments.append(msg['content'].strip())
        
        self.examples['agreements'] = random.sample(agreements, min(15, len(agreements)))
        self.examples['disagreements'] = random.sample(disagreements, min(15, len(disagreements)))
        self.examples['questions'] = random.sample(questions, min(15, len(questions)))
        self.examples['casual_acknowledgments'] = random.sample(casual_acknowledgments, min(15, len(casual_acknowledgments)))
        
    def extract_by_style_patterns(self):
        """Extract by specific style patterns"""
        lowercase_starts = []
        all_lowercase = []
        with_slang = []
        with_contractions = []
        with_typos = []
        rapid_fire = []
        
        slang_words = ['lol', 'lmao', 'bruh', 'fr', 'nah', 'yah', 'ok', 'wtf', 'tbh', 'imo', 'bro', 'dude']
        contractions = ["don't", "can't", "won't", "isn't", "aren't", "wasn't", "weren't", 
                       "haven't", "hasn't", "hadn't", "wouldn't", "couldn't", "shouldn't",
                       "i'm", "you're", "he's", "she's", "it's", "we're", "they're",
                       "i've", "you've", "we've", "they've", "i'll", "you'll", "he'll",
                       "she'll", "it'll", "we'll", "they'll", "i'd", "you'd", "he'd",
                       "she'd", "it'd", "we'd", "they'd", "im", "ur", "u"]
        
        for msg in self.messages:
            content = msg['content'].strip()
            content_lower = content.lower()
            
            # Lowercase starts
            if content and content[0].islower():
                lowercase_starts.append(content)
            
            # All lowercase
            if content.islower() and len(content) > 3:
                all_lowercase.append(content)
            
            # With slang
            if any(slang in content_lower for slang in slang_words):
                with_slang.append(content)
            
            # With contractions
            if any(contraction in content_lower for contraction in contractions):
                with_contractions.append(content)
        
        self.examples['lowercase_starts'] = random.sample(lowercase_starts, min(20, len(lowercase_starts)))
        self.examples['all_lowercase'] = random.sample(all_lowercase, min(20, len(all_lowercase)))
        self.examples['with_slang'] = random.sample(with_slang, min(20, len(with_slang)))
        self.examples['with_contractions'] = random.sample(with_contractions, min(20, len(with_contractions)))
        
    def extract_context_responses(self):
        """Extract responses that show how Py responds in different contexts"""
        # Look for replies to understand response patterns
        replies_to_others = []
        conversation_starters = []
        
        for msg in self.messages:
            if msg['reply_to']:
                replies_to_others.append(msg['content'].strip())
            else:
                # Likely conversation starter or standalone comment
                if len(msg['content'].split()) > 2:  # Not just "ok" or "lol"
                    conversation_starters.append(msg['content'].strip())
        
        self.examples['replies_to_others'] = random.sample(replies_to_others, min(25, len(replies_to_others)))
        self.examples['conversation_starters'] = random.sample(conversation_starters, min(20, len(conversation_starters)))
        
    def extract_topic_specific(self):
        """Extract messages about specific topics"""
        gaming_messages = []
        personal_messages = []
        reaction_messages = []
        
        gaming_keywords = ['game', 'play', 'server', 'minecraft', 'discord', 'stream', 'video']
        personal_keywords = ['i', 'my', 'me', 'myself', 'mine']
        reaction_keywords = ['lol', 'lmao', 'haha', 'omg', 'wtf', 'damn', 'shit', 'fuck']
        
        for msg in self.messages:
            content_lower = msg['content'].lower()
            
            if any(keyword in content_lower for keyword in gaming_keywords):
                gaming_messages.append(msg['content'].strip())
            
            if any(keyword in content_lower for keyword in personal_keywords):
                personal_messages.append(msg['content'].strip())
                
            if any(keyword in content_lower for keyword in reaction_keywords):
                reaction_messages.append(msg['content'].strip())
        
        self.examples['gaming_messages'] = random.sample(gaming_messages, min(15, len(gaming_messages)))
        self.examples['personal_messages'] = random.sample(personal_messages, min(20, len(personal_messages)))
        self.examples['reaction_messages'] = random.sample(reaction_messages, min(15, len(reaction_messages)))
        
    def analyze_response_patterns(self):
        """Analyze how Py responds to different types of messages"""
        # This would require analyzing the context of what he's responding to
        # For now, let's categorize his standalone messages
        
        explanatory = []  # Messages that explain something
        affirmative = []  # Simple yes/agreement responses  
        negative = []     # No/disagreement responses
        questioning = []  # When he asks for clarification
        
        for msg in self.messages:
            content = msg['content'].strip()
            content_lower = content.lower()
            
            # Explanatory (longer messages with "because", "since", "so")
            if any(word in content_lower for word in ['because', 'since', 'so that', 'the reason']):
                explanatory.append(content)
            
            # Simple affirmative
            if content_lower in ['yes', 'yeah', 'yep', 'true', 'right', 'ok', 'alright', 'sure']:
                affirmative.append(content)
            
            # Simple negative
            if content_lower in ['no', 'nah', 'nope', 'wrong', 'false']:
                negative.append(content)
            
            # Questioning/clarification
            if any(word in content_lower for word in ['what', 'how', 'why', 'when', 'where']) and '?' in content:
                questioning.append(content)
        
        self.examples['explanatory'] = explanatory[:15]
        self.examples['affirmative'] = affirmative[:15] 
        self.examples['negative'] = negative[:15]
        self.examples['questioning'] = questioning[:15]
        
    def generate_style_guide(self):
        """Generate a comprehensive style guide"""
        style_guide = {
            'core_characteristics': {
                'message_length': 'Extremely brief - averages 4.8 words per message',
                'capitalization': 'Predominantly lowercase (73%), casual style',
                'punctuation': 'Minimal - often omits ending punctuation',
                'tone': 'Casual, direct, understated',
                'formality': 'Very informal, conversational'
            },
            'vocabulary_patterns': {
                'most_common_starters': ['i', 'it', 'im', 'yeah', 'bro'],
                'frequent_words': ['i', 'it', 'to', 's', 'the', 'a', 'and', 'my', 'you', 'is'],
                'slang_usage': 'Moderate - uses "bro", "lol", "wtf", "ur" but not excessively',
                'contractions': 'Common - "im", "ur", "dont", etc.'
            },
            'conversational_behavior': {
                'agreement_style': 'Simple affirmation - "yes", "yeah", "true"',
                'disagreement_style': 'Direct but not aggressive - "no", "nah"', 
                'questions': 'Rare (1.8% of messages), usually seeking clarification',
                'responses': 'Brief acknowledgments, rarely elaborates'
            },
            'emotional_expression': {
                'generally_neutral': '89.5% of messages are emotionally neutral',
                'positive_expressions': 'Understated - "cool", "nice", occasional "lol"',
                'negative_expressions': 'Direct but not dramatic',
                'enthusiasm': 'Rarely expressed overtly'
            },
            'examples_by_category': self.examples
        }
        
        return style_guide
    
    def extract_all_examples(self):
        """Extract all example categories"""
        print("🔍 Extracting message examples by category...")
        
        self.extract_by_length()
        print("  ✅ Length-based examples")
        
        self.extract_by_conversation_function()
        print("  ✅ Conversational function examples")
        
        self.extract_by_style_patterns()
        print("  ✅ Style pattern examples")
        
        self.extract_context_responses()
        print("  ✅ Context response examples")
        
        self.extract_topic_specific()
        print("  ✅ Topic-specific examples")
        
        self.analyze_response_patterns()
        print("  ✅ Response pattern examples")
        
    def save_style_guide(self, output_file: str = None):
        """Save comprehensive style guide"""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'data/processed/pyqwerty_style_guide_{timestamp}.json'
        
        style_guide = self.generate_style_guide()
        
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(style_guide, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Style guide saved to: {output_file}")
        return output_file
    
    def print_examples_summary(self):
        """Print summary of extracted examples"""
        print(f"\n{'='*80}")
        print(f"📋 MESSAGE EXAMPLES SUMMARY")
        print(f"{'='*80}")
        
        for category, examples in self.examples.items():
            if examples:
                print(f"\n📁 {category.upper().replace('_', ' ')} ({len(examples)} examples):")
                for i, example in enumerate(examples[:5], 1):
                    print(f"  {i}. \"{example}\"")
                if len(examples) > 5:
                    print(f"  ... and {len(examples) - 5} more")

def main():
    """Main function"""
    
    # Find the most recent messages file
    data_dir = Path('data/raw')
    message_files = list(data_dir.glob('pyqwerty_messages_*.json'))
    latest_file = max(message_files, key=lambda x: x.stat().st_mtime)
    
    print(f"📁 Using message file: {latest_file}")
    
    extractor = MessageExamplesExtractor(str(latest_file))
    extractor.load_messages()
    extractor.extract_all_examples()
    extractor.print_examples_summary()
    
    style_guide_file = extractor.save_style_guide()
    
    print(f"\n🎯 Message examples extraction complete!")
    print(f"Style guide saved: {style_guide_file}")

if __name__ == '__main__':
    main()