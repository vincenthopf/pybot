#!/usr/bin/env python3
"""
Deep Style Analyzer for Pyqwerty Bot
Comprehensive analysis of Discord messages to extract detailed writing patterns.
"""

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple
import statistics
import string

class DeepStyleAnalyzer:
    def __init__(self, messages_file: str):
        self.messages_file = messages_file
        self.messages = []
        self.non_empty_messages = []
        self.comprehensive_profile = {}
        
    def load_messages(self):
        """Load and preprocess messages"""
        with open(self.messages_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.messages = data['messages']
        
        # Filter non-empty messages for most analyses
        self.non_empty_messages = [msg for msg in self.messages if msg['content'].strip()]
        
        print(f"✅ Loaded {len(self.messages)} total messages")
        print(f"✅ {len(self.non_empty_messages)} non-empty messages for analysis")
        
    def analyze_message_structure(self) -> Dict[str, Any]:
        """Deep analysis of message structure patterns"""
        structures = {
            'sentence_count_distribution': Counter(),
            'starts_with_patterns': Counter(),
            'ends_with_patterns': Counter(),
            'capitalization_patterns': {
                'proper_start': 0,
                'lowercase_start': 0,
                'number_start': 0,
                'symbol_start': 0,
                'all_caps': 0,
                'mixed_case': 0,
                'all_lowercase': 0
            },
            'grammar_patterns': {
                'contractions': 0,
                'abbreviations': 0,
                'slang_terms': 0,
                'filler_words': 0
            }
        }
        
        # Common contractions and slang
        contractions = ["don't", "can't", "won't", "isn't", "aren't", "wasn't", "weren't", 
                       "haven't", "hasn't", "hadn't", "wouldn't", "couldn't", "shouldn't",
                       "i'm", "you're", "he's", "she's", "it's", "we're", "they're",
                       "i've", "you've", "we've", "they've", "i'll", "you'll", "he'll",
                       "she'll", "it'll", "we'll", "they'll", "i'd", "you'd", "he'd",
                       "she'd", "it'd", "we'd", "they'd"]
        
        slang_terms = ["lol", "lmao", "bruh", "fr", "nah", "yah", "yeah", "ok", "omg", 
                      "wtf", "tbh", "imo", "smh", "rip", "pog", "ez", "gg", "kek",
                      "sus", "cringe", "based", "lit", "fire", "cap", "no cap", "bet"]
        
        filler_words = ["like", "um", "uh", "well", "so", "you know", "i mean", "basically"]
        
        for msg in self.non_empty_messages:
            content = msg['content'].strip()
            content_lower = content.lower()
            
            # Sentence count (rough approximation)
            sentence_count = len([s for s in re.split(r'[.!?]+', content) if s.strip()])
            structures['sentence_count_distribution'][sentence_count] += 1
            
            # Start patterns
            if content:
                first_char = content[0]
                if first_char.isupper():
                    structures['starts_with_patterns']['uppercase'] += 1
                elif first_char.islower():
                    structures['starts_with_patterns']['lowercase'] += 1
                elif first_char.isdigit():
                    structures['starts_with_patterns']['digit'] += 1
                else:
                    structures['starts_with_patterns']['symbol'] += 1
            
            # End patterns
            if content:
                last_char = content[-1]
                if last_char in '.!?':
                    structures['ends_with_patterns'][last_char] += 1
                elif last_char.isalnum():
                    structures['ends_with_patterns']['no_punctuation'] += 1
                else:
                    structures['ends_with_patterns']['other_symbol'] += 1
            
            # Capitalization analysis
            if content.isupper() and len(content) > 1:
                structures['capitalization_patterns']['all_caps'] += 1
            elif content.islower():
                structures['capitalization_patterns']['all_lowercase'] += 1
            elif content[0].isupper():
                structures['capitalization_patterns']['proper_start'] += 1
            elif content[0].islower():
                structures['capitalization_patterns']['lowercase_start'] += 1
            elif content[0].isdigit():
                structures['capitalization_patterns']['number_start'] += 1
            else:
                structures['capitalization_patterns']['symbol_start'] += 1
            
            # Grammar patterns
            for contraction in contractions:
                if contraction in content_lower:
                    structures['grammar_patterns']['contractions'] += 1
                    break
            
            for slang in slang_terms:
                if slang in content_lower:
                    structures['grammar_patterns']['slang_terms'] += 1
                    break
            
            for filler in filler_words:
                if filler in content_lower:
                    structures['grammar_patterns']['filler_words'] += 1
                    break
        
        return structures
    
    def analyze_linguistic_patterns(self) -> Dict[str, Any]:
        """Analyze linguistic and stylistic patterns"""
        patterns = {
            'word_length_distribution': Counter(),
            'syllable_patterns': Counter(),
            'repetition_patterns': {
                'repeated_words': Counter(),
                'repeated_phrases': Counter(),
                'word_doubling': 0  # "so so good", "very very"
            },
            'sentence_starters': Counter(),
            'discourse_markers': Counter(),
            'intensifiers': Counter(),
            'hedging_words': Counter()
        }
        
        # Common discourse markers, intensifiers, hedging words
        discourse_markers = ["so", "well", "now", "anyway", "actually", "basically", "literally"]
        intensifiers = ["very", "really", "super", "extremely", "totally", "absolutely", "quite"]
        hedging_words = ["maybe", "probably", "perhaps", "sort of", "kind of", "i think", "i guess"]
        
        all_words = []
        all_sentences = []
        
        for msg in self.non_empty_messages:
            content = msg['content'].strip()
            words = re.findall(r'\b\w+\b', content.lower())
            all_words.extend(words)
            
            # Word length distribution
            for word in words:
                patterns['word_length_distribution'][len(word)] += 1
            
            # Sentence starters (first word of message)
            if words:
                patterns['sentence_starters'][words[0]] += 1
            
            # Check for discourse markers, intensifiers, hedging
            content_lower = content.lower()
            for marker in discourse_markers:
                if marker in content_lower:
                    patterns['discourse_markers'][marker] += 1
            
            for intensifier in intensifiers:
                if intensifier in content_lower:
                    patterns['intensifiers'][intensifier] += 1
            
            for hedge in hedging_words:
                if hedge in content_lower:
                    patterns['hedging_words'][hedge] += 1
            
            # Word doubling pattern
            for i in range(len(words) - 1):
                if words[i] == words[i + 1]:
                    patterns['repetition_patterns']['word_doubling'] += 1
        
        # Repeated words analysis
        word_freq = Counter(all_words)
        patterns['repetition_patterns']['repeated_words'] = word_freq.most_common(50)
        
        return patterns
    
    def analyze_conversational_style(self) -> Dict[str, Any]:
        """Analyze conversational and social patterns"""
        conversation = {
            'response_patterns': {
                'agreement': 0,      # "yes", "yeah", "true", "exactly"
                'disagreement': 0,   # "no", "nah", "nope", "wrong"
                'uncertainty': 0,    # "maybe", "idk", "not sure"
                'acknowledgment': 0, # "ok", "alright", "got it"
                'enthusiasm': 0,     # "awesome", "cool", "nice"
                'dismissal': 0       # "whatever", "meh", "eh"
            },
            'question_types': {
                'yes_no': 0,
                'wh_questions': 0,
                'rhetorical': 0,
                'clarification': 0
            },
            'social_functions': {
                'greetings': 0,
                'farewells': 0,
                'thanks': 0,
                'apologies': 0,
                'compliments': 0,
                'complaints': 0
            },
            'conversation_flow': {
                'topic_shifts': 0,
                'back_references': 0,  # "that", "it", "this"
                'elaborations': 0      # "also", "plus", "and"
            }
        }
        
        # Pattern words for each category
        agreement_words = ["yes", "yeah", "yep", "true", "right", "exactly", "definitely", "absolutely"]
        disagreement_words = ["no", "nah", "nope", "wrong", "false", "disagree"]
        uncertainty_words = ["maybe", "idk", "dunno", "not sure", "possibly", "perhaps"]
        acknowledgment_words = ["ok", "okay", "alright", "got it", "i see", "fair"]
        enthusiasm_words = ["awesome", "cool", "nice", "great", "amazing", "sick", "dope"]
        dismissal_words = ["whatever", "meh", "eh", "don't care", "who cares"]
        
        greeting_words = ["hi", "hello", "hey", "sup", "what's up", "howdy"]
        farewell_words = ["bye", "goodbye", "see ya", "later", "cya", "peace"]
        thanks_words = ["thanks", "thank you", "thx", "ty", "appreciate"]
        apology_words = ["sorry", "my bad", "oops", "whoops", "apologize"]
        
        wh_words = ["what", "where", "when", "why", "who", "how", "which"]
        
        for msg in self.non_empty_messages:
            content_lower = msg['content'].lower()
            
            # Response patterns
            for word in agreement_words:
                if word in content_lower:
                    conversation['response_patterns']['agreement'] += 1
                    break
            
            for word in disagreement_words:
                if word in content_lower:
                    conversation['response_patterns']['disagreement'] += 1
                    break
            
            for word in uncertainty_words:
                if word in content_lower:
                    conversation['response_patterns']['uncertainty'] += 1
                    break
            
            for word in acknowledgment_words:
                if word in content_lower:
                    conversation['response_patterns']['acknowledgment'] += 1
                    break
            
            for word in enthusiasm_words:
                if word in content_lower:
                    conversation['response_patterns']['enthusiasm'] += 1
                    break
            
            for word in dismissal_words:
                if word in content_lower:
                    conversation['response_patterns']['dismissal'] += 1
                    break
            
            # Question analysis
            if msg['content'].strip().endswith('?'):
                first_word = msg['content'].strip().split()[0].lower() if msg['content'].strip().split() else ""
                if first_word in wh_words:
                    conversation['question_types']['wh_questions'] += 1
                else:
                    conversation['question_types']['yes_no'] += 1
            
            # Social functions
            for word in greeting_words:
                if word in content_lower:
                    conversation['social_functions']['greetings'] += 1
                    break
            
            for word in farewell_words:
                if word in content_lower:
                    conversation['social_functions']['farewells'] += 1
                    break
            
            for word in thanks_words:
                if word in content_lower:
                    conversation['social_functions']['thanks'] += 1
                    break
            
            for word in apology_words:
                if word in content_lower:
                    conversation['social_functions']['apologies'] += 1
                    break
        
        return conversation
    
    def analyze_topic_and_context(self) -> Dict[str, Any]:
        """Analyze topics and contextual patterns"""
        topics = {
            'topic_keywords': Counter(),
            'context_patterns': {
                'gaming_terms': 0,
                'tech_terms': 0,
                'social_terms': 0,
                'time_references': 0,
                'place_references': 0
            },
            'named_entities': {
                'mentioned_names': Counter(),
                'mentioned_places': Counter(),
                'mentioned_things': Counter()
            }
        }
        
        # Topic keyword lists
        gaming_terms = ["game", "play", "level", "win", "lose", "boss", "character", "server", 
                       "raid", "guild", "pvp", "fps", "rpg", "strategy", "console", "pc",
                       "steam", "discord", "minecraft", "fortnite", "apex", "valorant"]
        
        tech_terms = ["computer", "phone", "app", "website", "internet", "wifi", "software",
                     "hardware", "code", "programming", "bug", "update", "download", "install"]
        
        social_terms = ["friend", "friends", "family", "school", "work", "party", "hang out",
                       "meet", "chat", "talk", "message", "call", "text"]
        
        time_terms = ["today", "yesterday", "tomorrow", "now", "later", "soon", "never", 
                     "always", "morning", "afternoon", "evening", "night", "weekend"]
        
        all_text = " ".join([msg['content'] for msg in self.non_empty_messages])
        words = re.findall(r'\b\w+\b', all_text.lower())
        
        # Count topic keywords
        for word in words:
            if word in gaming_terms:
                topics['context_patterns']['gaming_terms'] += 1
            elif word in tech_terms:
                topics['context_patterns']['tech_terms'] += 1
            elif word in social_terms:
                topics['context_patterns']['social_terms'] += 1
            elif word in time_terms:
                topics['context_patterns']['time_references'] += 1
        
        # Overall word frequency for topic analysis
        topics['topic_keywords'] = Counter(words)
        
        return topics
    
    def analyze_emotional_tone(self) -> Dict[str, Any]:
        """Analyze emotional tone and sentiment patterns"""
        emotions = {
            'positive_indicators': 0,
            'negative_indicators': 0,
            'neutral_indicators': 0,
            'emotional_intensity': {
                'mild': 0,
                'moderate': 0,
                'strong': 0
            },
            'specific_emotions': {
                'joy': 0,
                'anger': 0,
                'sadness': 0,
                'fear': 0,
                'surprise': 0,
                'disgust': 0,
                'excitement': 0,
                'frustration': 0,
                'confusion': 0,
                'boredom': 0
            }
        }
        
        # Emotion word lists
        positive_words = ["good", "great", "awesome", "cool", "nice", "happy", "love", "like",
                         "amazing", "fantastic", "wonderful", "excellent", "perfect", "fun"]
        
        negative_words = ["bad", "terrible", "awful", "hate", "dislike", "sad", "angry", "mad",
                         "stupid", "dumb", "annoying", "frustrating", "boring", "sucks"]
        
        joy_words = ["happy", "joy", "excited", "thrilled", "delighted", "cheerful", "glad"]
        anger_words = ["angry", "mad", "furious", "pissed", "annoyed", "irritated", "rage"]
        sadness_words = ["sad", "depressed", "down", "upset", "disappointed", "hurt"]
        
        for msg in self.non_empty_messages:
            content_lower = msg['content'].lower()
            
            # Basic sentiment
            pos_count = sum(1 for word in positive_words if word in content_lower)
            neg_count = sum(1 for word in negative_words if word in content_lower)
            
            if pos_count > neg_count:
                emotions['positive_indicators'] += 1
            elif neg_count > pos_count:
                emotions['negative_indicators'] += 1
            else:
                emotions['neutral_indicators'] += 1
            
            # Specific emotions
            for word in joy_words:
                if word in content_lower:
                    emotions['specific_emotions']['joy'] += 1
                    break
            
            for word in anger_words:
                if word in content_lower:
                    emotions['specific_emotions']['anger'] += 1
                    break
            
            for word in sadness_words:
                if word in content_lower:
                    emotions['specific_emotions']['sadness'] += 1
                    break
        
        return emotions
    
    def analyze_advanced_patterns(self) -> Dict[str, Any]:
        """Advanced pattern analysis"""
        advanced = {
            'typing_behavior': {
                'typos_and_corrections': 0,
                'abbreviations': Counter(),
                'internet_slang': Counter(),
                'spelling_variations': Counter()
            },
            'message_timing': {
                'rapid_succession': 0,  # Messages sent within 30 seconds
                'conversation_gaps': [],
                'response_delays': []
            },
            'interaction_style': {
                'initiates_topics': 0,
                'responds_to_others': 0,
                'asks_questions': 0,
                'provides_answers': 0
            }
        }
        
        # Common abbreviations and slang
        abbreviations = ["u", "ur", "ppl", "plz", "thx", "ty", "np", "omg", "wtf", "lol", 
                        "lmao", "brb", "gtg", "ttyl", "imo", "tbh", "btw", "fyi"]
        
        # Analyze messages chronologically
        sorted_messages = sorted(self.non_empty_messages, key=lambda x: x['timestamp'])
        
        for i, msg in enumerate(sorted_messages):
            content_lower = msg['content'].lower()
            
            # Check for abbreviations
            words = content_lower.split()
            for word in words:
                if word in abbreviations:
                    advanced['typing_behavior']['abbreviations'][word] += 1
            
            # Check for rapid succession (if not first message)
            if i > 0:
                prev_time = datetime.fromisoformat(sorted_messages[i-1]['timestamp'].replace('Z', '+00:00'))
                curr_time = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
                time_diff = (curr_time - prev_time).total_seconds()
                
                if time_diff <= 30:  # Within 30 seconds
                    advanced['message_timing']['rapid_succession'] += 1
                
                advanced['message_timing']['response_delays'].append(time_diff)
            
            # Interaction analysis
            if msg['reply_to']:
                advanced['interaction_style']['responds_to_others'] += 1
            
            if msg['content'].strip().endswith('?'):
                advanced['interaction_style']['asks_questions'] += 1
        
        return advanced
    
    def generate_comprehensive_profile(self) -> Dict[str, Any]:
        """Generate the complete comprehensive style profile"""
        print("\n🔍 Performing deep style analysis...")
        
        # Load basic profile if exists
        basic_profile = {}
        basic_profile_path = 'data/processed/pyqwerty_style_profile_20250616_114547.json'
        if Path(basic_profile_path).exists():
            with open(basic_profile_path, 'r') as f:
                basic_profile = json.load(f)
            print("  ✅ Loaded existing basic profile")
        
        # Deep analyses
        message_structure = self.analyze_message_structure()
        print("  ✅ Message structure analysis")
        
        linguistic_patterns = self.analyze_linguistic_patterns()
        print("  ✅ Linguistic patterns analysis")
        
        conversational_style = self.analyze_conversational_style()
        print("  ✅ Conversational style analysis")
        
        topic_context = self.analyze_topic_and_context()
        print("  ✅ Topic and context analysis")
        
        emotional_tone = self.analyze_emotional_tone()
        print("  ✅ Emotional tone analysis")
        
        advanced_patterns = self.analyze_advanced_patterns()
        print("  ✅ Advanced patterns analysis")
        
        # Combine all analyses
        self.comprehensive_profile = {
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'source_file': self.messages_file,
                'total_messages': len(self.messages),
                'non_empty_messages': len(self.non_empty_messages),
                'analysis_type': 'comprehensive_deep_analysis'
            },
            'basic_profile': basic_profile,
            'deep_analysis': {
                'message_structure': message_structure,
                'linguistic_patterns': linguistic_patterns,
                'conversational_style': conversational_style,
                'topic_and_context': topic_context,
                'emotional_tone': emotional_tone,
                'advanced_patterns': advanced_patterns
            }
        }
        
        return self.comprehensive_profile
    
    def save_comprehensive_profile(self, output_file: str = None):
        """Save comprehensive profile"""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'data/processed/pyqwerty_comprehensive_profile_{timestamp}.json'
        
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.comprehensive_profile, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Comprehensive profile saved to: {output_file}")
        print(f"📊 File size: {Path(output_file).stat().st_size / 1024:.2f} KB")
        
        return output_file
    
    def print_comprehensive_summary(self):
        """Print detailed analysis summary"""
        if not self.comprehensive_profile:
            return
        
        deep = self.comprehensive_profile['deep_analysis']
        
        print(f"\n{'='*80}")
        print(f"🧠 COMPREHENSIVE STYLE ANALYSIS SUMMARY")
        print(f"{'='*80}")
        
        # Message Structure
        structure = deep['message_structure']
        print(f"\n📝 MESSAGE STRUCTURE:")
        cap_patterns = structure['capitalization_patterns']
        total_msgs = len(self.non_empty_messages)
        print(f"  Proper capitalization: {cap_patterns['proper_start']/total_msgs*100:.1f}%")
        print(f"  Lowercase starts: {cap_patterns['lowercase_start']/total_msgs*100:.1f}%")
        print(f"  All lowercase messages: {cap_patterns['all_lowercase']/total_msgs*100:.1f}%")
        print(f"  Contractions used: {structure['grammar_patterns']['contractions']} messages")
        print(f"  Slang terms used: {structure['grammar_patterns']['slang_terms']} messages")
        
        # Linguistic Patterns
        linguistic = deep['linguistic_patterns']
        print(f"\n🗣️ LINGUISTIC PATTERNS:")
        print(f"  Most common sentence starters: {dict(linguistic['sentence_starters'].most_common(5))}")
        print(f"  Word doubling instances: {linguistic['repetition_patterns']['word_doubling']}")
        if linguistic['discourse_markers']:
            print(f"  Discourse markers: {dict(linguistic['discourse_markers'].most_common(3))}")
        if linguistic['intensifiers']:
            print(f"  Intensifiers used: {dict(linguistic['intensifiers'].most_common(3))}")
        
        # Conversational Style
        convo = deep['conversational_style']
        print(f"\n💬 CONVERSATIONAL STYLE:")
        responses = convo['response_patterns']
        print(f"  Agreement responses: {responses['agreement']}")
        print(f"  Disagreement responses: {responses['disagreement']}")
        print(f"  Uncertainty expressions: {responses['uncertainty']}")
        print(f"  Acknowledgments: {responses['acknowledgment']}")
        print(f"  Enthusiastic responses: {responses['enthusiasm']}")
        
        questions = convo['question_types']
        total_questions = sum(questions.values())
        if total_questions > 0:
            print(f"  Questions asked: {total_questions} ({total_questions/total_msgs*100:.1f}%)")
            print(f"    - Yes/No questions: {questions['yes_no']}")
            print(f"    - Wh- questions: {questions['wh_questions']}")
        
        # Topic Analysis
        topics = deep['topic_and_context']
        print(f"\n📚 TOPICS & CONTEXT:")
        context = topics['context_patterns']
        print(f"  Gaming references: {context['gaming_terms']}")
        print(f"  Tech references: {context['tech_terms']}")
        print(f"  Social references: {context['social_terms']}")
        print(f"  Time references: {context['time_references']}")
        
        # Emotional Tone
        emotions = deep['emotional_tone']
        print(f"\n😊 EMOTIONAL TONE:")
        total_emotional = emotions['positive_indicators'] + emotions['negative_indicators'] + emotions['neutral_indicators']
        if total_emotional > 0:
            print(f"  Positive tone: {emotions['positive_indicators']/total_emotional*100:.1f}%")
            print(f"  Negative tone: {emotions['negative_indicators']/total_emotional*100:.1f}%")
            print(f"  Neutral tone: {emotions['neutral_indicators']/total_emotional*100:.1f}%")
        
        specific_emotions = emotions['specific_emotions']
        emotional_msgs = sum(specific_emotions.values())
        if emotional_msgs > 0:
            print(f"  Specific emotions expressed:")
            for emotion, count in specific_emotions.items():
                if count > 0:
                    print(f"    - {emotion.capitalize()}: {count}")
        
        # Advanced Patterns
        advanced = deep['advanced_patterns']
        print(f"\n🚀 ADVANCED PATTERNS:")
        abbrevs = advanced['typing_behavior']['abbreviations']
        if abbrevs:
            print(f"  Common abbreviations: {dict(abbrevs.most_common(5))}")
        
        timing = advanced['message_timing']
        print(f"  Rapid-fire messages (within 30s): {timing['rapid_succession']}")
        
        if timing['response_delays']:
            avg_delay = statistics.mean(timing['response_delays'])
            print(f"  Average response delay: {avg_delay:.1f} seconds")
        
        interaction = advanced['interaction_style']
        print(f"  Messages replying to others: {interaction['responds_to_others']}")
        print(f"  Questions asked: {interaction['asks_questions']}")

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
    
    # Deep analysis
    analyzer = DeepStyleAnalyzer(str(latest_file))
    analyzer.load_messages()
    analyzer.generate_comprehensive_profile()
    analyzer.print_comprehensive_summary()
    
    # Save comprehensive profile
    profile_file = analyzer.save_comprehensive_profile()
    
    print(f"\n🎯 Comprehensive style analysis complete!")
    print(f"Deep profile saved: {profile_file}")

if __name__ == '__main__':
    main()