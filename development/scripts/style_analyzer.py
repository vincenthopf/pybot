#!/usr/bin/env python3
"""
Style Analyzer for Pyqwerty Bot
Analyzes Discord messages to extract writing style patterns.
"""

import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import statistics

class StyleAnalyzer:
    def __init__(self, messages_file: str):
        self.messages_file = messages_file
        self.messages = []
        self.style_profile = {}
        
    def load_messages(self):
        """Load messages from JSON file"""
        with open(self.messages_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.messages = data['messages']
        
        print(f"✅ Loaded {len(self.messages)} messages")
        
    def analyze_basic_stats(self) -> Dict[str, Any]:
        """Analyze basic message statistics"""
        if not self.messages:
            return {}
            
        message_lengths = []
        word_counts = []
        char_counts = []
        
        for msg in self.messages:
            content = msg['content'].strip()
            if content:  # Skip empty messages
                message_lengths.append(len(content))
                words = len(content.split())
                word_counts.append(words)
                char_counts.append(len(content))
        
        return {
            'total_messages': len(self.messages),
            'non_empty_messages': len(message_lengths),
            'avg_message_length': statistics.mean(message_lengths) if message_lengths else 0,
            'median_message_length': statistics.median(message_lengths) if message_lengths else 0,
            'avg_word_count': statistics.mean(word_counts) if word_counts else 0,
            'median_word_count': statistics.median(word_counts) if word_counts else 0,
            'avg_char_count': statistics.mean(char_counts) if char_counts else 0,
            'message_length_range': {
                'min': min(message_lengths) if message_lengths else 0,
                'max': max(message_lengths) if message_lengths else 0
            }
        }
    
    def analyze_vocabulary(self) -> Dict[str, Any]:
        """Analyze vocabulary patterns"""
        all_text = ' '.join([msg['content'] for msg in self.messages])
        
        # Word frequency
        words = re.findall(r'\b\w+\b', all_text.lower())
        word_freq = Counter(words)
        
        # Common phrases (2-3 word combinations)
        phrases_2 = []
        phrases_3 = []
        
        for msg in self.messages:
            content = msg['content'].lower()
            words = re.findall(r'\b\w+\b', content)
            
            # 2-word phrases
            for i in range(len(words) - 1):
                phrases_2.append(f"{words[i]} {words[i+1]}")
            
            # 3-word phrases
            for i in range(len(words) - 2):
                phrases_3.append(f"{words[i]} {words[i+1]} {words[i+2]}")
        
        phrase_freq_2 = Counter(phrases_2)
        phrase_freq_3 = Counter(phrases_3)
        
        return {
            'total_words': len(words),
            'unique_words': len(word_freq),
            'vocabulary_richness': len(word_freq) / len(words) if words else 0,
            'most_common_words': word_freq.most_common(20),
            'most_common_2word_phrases': phrase_freq_2.most_common(10),
            'most_common_3word_phrases': phrase_freq_3.most_common(10)
        }
    
    def analyze_punctuation_and_style(self) -> Dict[str, Any]:
        """Analyze punctuation and writing style patterns"""
        punctuation_counts = Counter()
        style_patterns = {
            'all_caps_messages': 0,
            'question_messages': 0,
            'exclamation_messages': 0,
            'ellipsis_usage': 0,
            'repeated_punctuation': 0,
            'starts_with_lowercase': 0,
            'no_punctuation_end': 0
        }
        
        for msg in self.messages:
            content = msg['content'].strip()
            if not content:
                continue
                
            # Count punctuation
            for char in content:
                if char in '.,!?;:-()[]{}"\'/\\':
                    punctuation_counts[char] += 1
            
            # Style patterns
            if content.isupper() and len(content) > 3:
                style_patterns['all_caps_messages'] += 1
            
            if content.endswith('?'):
                style_patterns['question_messages'] += 1
                
            if content.endswith('!'):
                style_patterns['exclamation_messages'] += 1
                
            if '...' in content:
                style_patterns['ellipsis_usage'] += 1
                
            # Repeated punctuation (!!!, ???, etc.)
            if re.search(r'[!?]{2,}', content):
                style_patterns['repeated_punctuation'] += 1
                
            # Starts with lowercase
            if content[0].islower():
                style_patterns['starts_with_lowercase'] += 1
                
            # No ending punctuation
            if not re.search(r'[.!?]$', content):
                style_patterns['no_punctuation_end'] += 1
        
        return {
            'punctuation_frequency': dict(punctuation_counts.most_common()),
            'style_patterns': style_patterns,
            'style_percentages': {
                key: (value / len(self.messages)) * 100 
                for key, value in style_patterns.items()
            }
        }
    
    def analyze_emojis(self) -> Dict[str, Any]:
        """Analyze emoji usage patterns"""
        emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F'  # emoticons
                                  r'\U0001F300-\U0001F5FF'   # symbols & pictographs
                                  r'\U0001F680-\U0001F6FF'   # transport & map
                                  r'\U0001F1E0-\U0001F1FF'   # flags
                                  r'\U00002600-\U000026FF'   # miscellaneous
                                  r'\U00002700-\U000027BF]+') # dingbats
        
        all_emojis = []
        messages_with_emojis = 0
        
        for msg in self.messages:
            content = msg['content']
            emojis = emoji_pattern.findall(content)
            if emojis:
                messages_with_emojis += 1
                all_emojis.extend(emojis)
        
        emoji_freq = Counter(all_emojis)
        
        return {
            'total_emojis': len(all_emojis),
            'unique_emojis': len(emoji_freq),
            'messages_with_emojis': messages_with_emojis,
            'emoji_usage_percentage': (messages_with_emojis / len(self.messages)) * 100,
            'most_common_emojis': emoji_freq.most_common(10),
            'avg_emojis_per_message': len(all_emojis) / len(self.messages)
        }
    
    def analyze_temporal_patterns(self) -> Dict[str, Any]:
        """Analyze when messages are sent"""
        hours = []
        days = []
        
        for msg in self.messages:
            timestamp = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
            hours.append(timestamp.hour)
            days.append(timestamp.strftime('%A'))
        
        hour_freq = Counter(hours)
        day_freq = Counter(days)
        
        return {
            'most_active_hours': hour_freq.most_common(5),
            'least_active_hours': hour_freq.most_common()[-5:],
            'most_active_days': day_freq.most_common(),
            'hour_distribution': dict(hour_freq),
            'day_distribution': dict(day_freq)
        }
    
    def analyze_interaction_patterns(self) -> Dict[str, Any]:
        """Analyze how user interacts (replies, mentions, etc.)"""
        reply_count = 0
        mention_count = 0
        reaction_count = 0
        attachment_count = 0
        embed_count = 0
        
        mentioned_users = []
        
        for msg in self.messages:
            if msg['reply_to']:
                reply_count += 1
                
            if msg['mentions']:
                mention_count += 1
                mentioned_users.extend(msg['mentions'])
                
            if msg['reactions']:
                reaction_count += len(msg['reactions'])
                
            if msg['attachments']:
                attachment_count += len(msg['attachments'])
                
            if msg['embeds']:
                embed_count += msg['embeds']
        
        mention_freq = Counter(mentioned_users)
        
        return {
            'reply_percentage': (reply_count / len(self.messages)) * 100,
            'mention_percentage': (mention_count / len(self.messages)) * 100,
            'messages_with_reactions': reaction_count,
            'messages_with_attachments': attachment_count,
            'messages_with_embeds': embed_count,
            'most_mentioned_users': mention_freq.most_common(5)
        }
    
    def extract_example_messages(self) -> Dict[str, List[str]]:
        """Extract example messages for different categories"""
        examples = {
            'short_messages': [],
            'medium_messages': [],
            'long_messages': [],
            'questions': [],
            'exclamations': [],
            'casual_responses': [],
            'with_emojis': []
        }
        
        emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F'
                                  r'\U0001F300-\U0001F5FF'
                                  r'\U0001F680-\U0001F6FF'
                                  r'\U0001F1E0-\U0001F1FF'
                                  r'\U00002600-\U000026FF'
                                  r'\U00002700-\U000027BF]+')
        
        for msg in self.messages:
            content = msg['content'].strip()
            if not content:
                continue
                
            word_count = len(content.split())
            
            # Categorize by length
            if word_count <= 3:
                if len(examples['short_messages']) < 10:
                    examples['short_messages'].append(content)
            elif word_count <= 10:
                if len(examples['medium_messages']) < 10:
                    examples['medium_messages'].append(content)
            else:
                if len(examples['long_messages']) < 10:
                    examples['long_messages'].append(content)
            
            # Questions
            if content.endswith('?') and len(examples['questions']) < 10:
                examples['questions'].append(content)
            
            # Exclamations
            if content.endswith('!') and len(examples['exclamations']) < 10:
                examples['exclamations'].append(content)
            
            # Casual responses (short, common words)
            casual_words = ['ok', 'yeah', 'lol', 'lmao', 'bruh', 'nice', 'cool', 'true', 'fr', 'nah']
            if any(word in content.lower() for word in casual_words) and len(examples['casual_responses']) < 10:
                examples['casual_responses'].append(content)
            
            # With emojis
            if emoji_pattern.search(content) and len(examples['with_emojis']) < 10:
                examples['with_emojis'].append(content)
        
        return examples
    
    def generate_style_profile(self) -> Dict[str, Any]:
        """Generate complete style profile"""
        print("\n🔍 Analyzing writing style...")
        
        basic_stats = self.analyze_basic_stats()
        print("  ✅ Basic statistics")
        
        vocabulary = self.analyze_vocabulary()
        print("  ✅ Vocabulary analysis")
        
        punctuation = self.analyze_punctuation_and_style()
        print("  ✅ Punctuation & style patterns")
        
        emojis = self.analyze_emojis()
        print("  ✅ Emoji usage")
        
        temporal = self.analyze_temporal_patterns()
        print("  ✅ Temporal patterns")
        
        interactions = self.analyze_interaction_patterns()
        print("  ✅ Interaction patterns")
        
        examples = self.extract_example_messages()
        print("  ✅ Example messages")
        
        self.style_profile = {
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'source_file': self.messages_file,
                'total_messages_analyzed': len(self.messages)
            },
            'basic_stats': basic_stats,
            'vocabulary': vocabulary,
            'punctuation_and_style': punctuation,
            'emoji_usage': emojis,
            'temporal_patterns': temporal,
            'interaction_patterns': interactions,
            'example_messages': examples
        }
        
        return self.style_profile
    
    def save_profile(self, output_file: str = None):
        """Save style profile to JSON file"""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'data/processed/pyqwerty_style_profile_{timestamp}.json'
        
        # Ensure directory exists
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.style_profile, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Style profile saved to: {output_file}")
        print(f"📊 File size: {Path(output_file).stat().st_size / 1024:.2f} KB")
        
        return output_file
    
    def print_summary(self):
        """Print analysis summary"""
        if not self.style_profile:
            return
            
        stats = self.style_profile['basic_stats']
        vocab = self.style_profile['vocabulary']
        style = self.style_profile['punctuation_and_style']
        emojis = self.style_profile['emoji_usage']
        
        print(f"\n{'='*60}")
        print(f"📊 STYLE ANALYSIS SUMMARY")
        print(f"{'='*60}")
        
        print(f"\n📈 Basic Statistics:")
        print(f"  Total messages: {stats['total_messages']}")
        print(f"  Average message length: {stats['avg_message_length']:.1f} characters")
        print(f"  Average words per message: {stats['avg_word_count']:.1f}")
        
        print(f"\n📚 Vocabulary:")
        print(f"  Total words used: {vocab['total_words']:,}")
        print(f"  Unique words: {vocab['unique_words']:,}")
        print(f"  Vocabulary richness: {vocab['vocabulary_richness']:.3f}")
        
        print(f"\n✍️ Writing Style:")
        print(f"  Lowercase starts: {style['style_percentages']['starts_with_lowercase']:.1f}%")
        print(f"  Questions: {style['style_percentages']['question_messages']:.1f}%")
        print(f"  Exclamations: {style['style_percentages']['exclamation_messages']:.1f}%")
        print(f"  All caps messages: {style['style_percentages']['all_caps_messages']:.1f}%")
        
        print(f"\n😊 Emoji Usage:")
        print(f"  Messages with emojis: {emojis['emoji_usage_percentage']:.1f}%")
        print(f"  Average emojis per message: {emojis['avg_emojis_per_message']:.2f}")
        
        print(f"\n🔤 Most Common Words:")
        for word, count in vocab['most_common_words'][:10]:
            print(f"  {word}: {count}")
        
        if emojis['most_common_emojis']:
            print(f"\n😄 Most Common Emojis:")
            for emoji, count in emojis['most_common_emojis'][:5]:
                print(f"  {emoji}: {count}")

def main():
    """Main function"""
    # Find the most recent messages file
    data_dir = Path('data/raw')
    if not data_dir.exists():
        print("❌ No data/raw directory found!")
        return
        
    message_files = list(data_dir.glob('pyqwerty_messages_*.json'))
    if not message_files:
        print("❌ No message files found in data/raw/")
        return
        
    # Use the most recent file
    latest_file = max(message_files, key=lambda x: x.stat().st_mtime)
    print(f"📁 Using message file: {latest_file}")
    
    # Analyze style
    analyzer = StyleAnalyzer(str(latest_file))
    analyzer.load_messages()
    analyzer.generate_style_profile()
    analyzer.print_summary()
    
    # Save profile
    profile_file = analyzer.save_profile()
    
    print(f"\n🎯 Style analysis complete!")
    print(f"Use this profile to train the bot: {profile_file}")

if __name__ == '__main__':
    main()