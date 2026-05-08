"""
OpenSelf Integration Module

This module integrates components from the OpenSelf project to enhance personality analysis,
safety, and human mimicry capabilities. It operates as a separate component that can be
optionally used alongside the existing questionnaire-based profile intake system.

Components integrated:
- Personality extraction from chat history
- Vocabulary fingerprinting
- Safety guard system
- Human mimicry engine
- Chat export parsers
"""

from typing import Dict, List, Any, Optional, Tuple
import re
import json
import random
from pathlib import Path
from datetime import datetime, timezone
import logging
from collections import Counter

# Import CloneMe utilities with fallback
try:
    from ..utils.logging_config import LoggingConfig
except ImportError:
    # Fallback for standalone usage
    class LoggingConfig:
        @staticmethod
        def get_logger(name: str):
            return logging.getLogger(name)

__all__ = [
    'PersonalityExtractor',
    'VocabularyFingerprinter',
    'SoulGenerator',
    'SafetyGuard',
    'HumanMimicry',
    'StyleProcessor',
    'TimingEngine',
    'ChatParser',
    'OpenSelfIntegration'
]

class PersonalityExtractor:
    """
    Personality Extractor - Analyze chat messages to extract personality traits

    Ported from OpenSelf's personality/extractor.js
    """

    # Common emoji regex (combining marks + ZWJ are intentional for emoji counting)
    # Emoji detection regex (simplified for Python compatibility)
    EMOJI_REGEX = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000026FF\U00002700-\U000027BF\U0000FE00-\U0000FE0F\U0001F900-\U0001F9FF]', re.UNICODE)

    def __init__(self):
        self.logger = LoggingConfig.get_logger("personality_extractor")

    def extract_personality(self, your_messages: List[str], conversations: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extract personality traits from user's messages.

        Args:
            your_messages: List of message strings from the user
            conversations: List of conversation dictionaries with reply delays

        Returns:
            Dictionary containing extracted personality traits
        """
        if conversations is None:
            conversations = []

        texts = your_messages

        return {
            # Basic stats
            'total_messages': len(texts),
            'avg_message_length': self._average([len(t) for t in texts]),
            'avg_word_count': self._average([len(t.split()) for t in texts]),

            # Emoji analysis
            'emoji_frequency': self._count_emojis(texts) / max(len(texts), 1),
            'top_emojis': self._get_top_emojis(texts, 10),

            # Language patterns
            'top_words': self._get_top_words(texts, 50),
            'top_phrases': self._get_top_phrases(texts, 30),
            'catchphrases': self._detect_catchphrases(texts),
            'greeting_style': self._detect_greeting_patterns(texts),

            # Style
            'uses_slang': self._detect_slang(texts),
            'formality': self._detect_formality_level(texts),
            'humor_patterns': self._detect_humor(texts),

            # Response patterns
            'response_time_avg': self._calculate_avg_response_time(conversations),

            # Vietnamese-specific (can be extended for other languages)
            'pronoun_usage': self._detect_vietnamese_pronouns(texts),
            'tone_diacritics': self._check_diacritic_usage(texts),
            'abbreviations': self._detect_abbreviations(texts),

            # Primary language detection
            'primary_language': self._detect_language(texts),
        }

    def _average(self, arr: List[float]) -> float:
        """Calculate average of array, return 0 if empty."""
        if not arr:
            return 0.0
        return round(sum(arr) / len(arr), 2)

    def _count_emojis(self, texts: List[str]) -> int:
        """Count total emojis in all texts."""
        count = 0
        for text in texts:
            matches = self.EMOJI_REGEX.findall(text)
            count += len(matches)
        return count

    def _get_top_emojis(self, texts: List[str], n: int) -> List[Dict[str, Any]]:
        """Get top N most used emojis."""
        counts = {}
        for text in texts:
            matches = self.EMOJI_REGEX.findall(text)
            for emoji in matches:
                counts[emoji] = counts.get(emoji, 0) + 1

        return [
            {'emoji': emoji, 'count': count}
            for emoji, count in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n]
        ]

    def _get_top_words(self, texts: List[str], n: int) -> List[Dict[str, Any]]:
        """Get top N most used words (excluding stop words)."""
        stop_words = set([
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'shall', 'to', 'of', 'in', 'for',
            'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during',
            'before', 'after', 'and', 'but', 'or', 'nor', 'not', 'so', 'yet',
            'i', 'me', 'my', 'we', 'our', 'you', 'your', 'he', 'him', 'his',
            'she', 'her', 'it', 'its', 'they', 'them', 'their', 'this', 'that',
            'these', 'those', 'if', 'then', 'than', 'when', 'what', 'which',
            # Vietnamese stop words
            'là', 'và', 'của', 'có', 'được', 'cho', 'với', 'từ', 'trong',
            'các', 'này', 'đó', 'để', 'về', 'cũng', 'như', 'nhưng', 'hay',
            'thì', 'sẽ', 'đã', 'rồi', 'mà', 'vì', 'nếu',
        ])

        counts = {}
        for text in texts:
            words = text.lower().split()
            for word in words:
                clean = re.sub(r'[^\w]', '', word)
                if clean and clean not in stop_words:
                    counts[clean] = counts.get(clean, 0) + 1

        return [
            {'word': word, 'count': count}
            for word, count in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n]
        ]

    def _get_top_phrases(self, texts: List[str], n: int) -> List[Dict[str, Any]]:
        """Get top N most used phrases (2-3 word combinations)."""
        counts = {}
        for text in texts:
            words = text.lower().split()
            for i in range(len(words) - 1):
                phrase = ' '.join(words[i:i+2])
                counts[phrase] = counts.get(phrase, 0) + 1
            for i in range(len(words) - 2):
                phrase = ' '.join(words[i:i+3])
                counts[phrase] = counts.get(phrase, 0) + 1

        return [
            {'phrase': phrase, 'count': count}
            for phrase, count in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n]
        ]

    def _detect_catchphrases(self, texts: List[str]) -> List[str]:
        """Detect potential catchphrases based on repetition."""
        phrase_counts = {}
        for text in texts:
            # Look for quoted phrases or repeated short phrases
            phrases = re.findall(r'"([^"]+)"', text) + re.findall(r'\b\w{3,}\s+\w{3,}\b', text.lower())
            for phrase in phrases:
                phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1

        # Return phrases that appear more than once
        return [phrase for phrase, count in phrase_counts.items() if count > 1][:10]

    def _detect_greeting_patterns(self, texts: List[str]) -> List[str]:
        """Detect common greeting patterns."""
        greetings = []
        greeting_words = ['hello', 'hi', 'hey', 'yo', 'ê', 'dạ', 'chào', 'xin chào']

        for text in texts[:50]:  # Check first 50 messages
            lower_text = text.lower()
            for greeting in greeting_words:
                if lower_text.startswith(greeting) or f' {greeting} ' in lower_text:
                    greetings.append(greeting)
                    break

        return list(set(greetings))[:5]

    def _detect_slang(self, texts: List[str]) -> bool:
        """Detect if user frequently uses slang."""
        slang_indicators = ['lol', 'brb', 'omg', 'wtf', 'idk', 'tbh', 'imo', 'btw']
        slang_count = 0
        total_words = 0

        for text in texts:
            words = text.lower().split()
            total_words += len(words)
            for word in words:
                if word in slang_indicators:
                    slang_count += 1

        return (slang_count / max(total_words, 1)) > 0.01  # More than 1% slang usage

    def _detect_formality_level(self, texts: List[str]) -> str:
        """Detect formality level based on language patterns."""
        formal_indicators = ['please', 'thank you', 'i appreciate', 'regards', 'sincerely']
        casual_indicators = ['lol', 'haha', 'dude', 'bro', 'kinda', 'sorta']

        formal_count = 0
        casual_count = 0
        total_texts = len(texts)

        for text in texts:
            lower_text = text.lower()
            for indicator in formal_indicators:
                if indicator in lower_text:
                    formal_count += 1
                    break
            for indicator in casual_indicators:
                if indicator in lower_text:
                    casual_count += 1
                    break

        formal_ratio = formal_count / max(total_texts, 1)
        casual_ratio = casual_count / max(total_texts, 1)

        if formal_ratio > casual_ratio and formal_ratio > 0.1:
            return 'Formal'
        elif casual_ratio > formal_ratio and casual_ratio > 0.1:
            return 'Casual'
        else:
            return 'Neutral'

    def _detect_humor(self, texts: List[str]) -> List[str]:
        """Detect humor patterns."""
        humor_indicators = ['lol', 'haha', '😂', '🤣', 'joke', 'funny', 'lmao', 'rofl']
        humor_patterns = []

        for text in texts:
            lower_text = text.lower()
            for indicator in humor_indicators:
                if indicator in lower_text:
                    humor_patterns.append(indicator)
                    break

        return list(set(humor_patterns))[:5]

    def _calculate_avg_response_time(self, conversations: List[Dict[str, Any]]) -> float:
        """Calculate average response time from conversations."""
        if not conversations:
            return 60000.0  # Default 1 minute

        delays = [conv.get('reply_delay', 0) for conv in conversations if conv.get('reply_delay', 0) > 0]
        return self._average(delays) if delays else 60000.0

    def _detect_vietnamese_pronouns(self, texts: List[str]) -> List[str]:
        """Detect Vietnamese pronoun usage patterns."""
        viet_pronouns = ['tôi', 'tao', 'mình', 'tớ', 'mày', 'cậu', 'bạn', 'ông', 'bà', 'chú', 'thím']
        found_pronouns = []

        for text in texts:
            lower_text = text.lower()
            for pronoun in viet_pronouns:
                if pronoun in lower_text:
                    found_pronouns.append(pronoun)

        return list(set(found_pronouns))[:5]

    def _check_diacritic_usage(self, texts: List[str]) -> bool:
        """Check if Vietnamese diacritics are used."""
        diacritic_chars = 'àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ'
        total_chars = 0
        diacritic_count = 0

        for text in texts:
            for char in text:
                total_chars += 1
                if char in diacritic_chars:
                    diacritic_count += 1

        return (diacritic_count / max(total_chars, 1)) > 0.05  # More than 5% diacritic usage

    def _detect_abbreviations(self, texts: List[str]) -> List[str]:
        """Detect common abbreviations."""
        common_abbrevs = ['ok', 'oke', 'ngon', 'dinh', 'vl', 'ez', 'brb', 'afk', 'lol', 'wtf']
        found_abbrevs = []

        for text in texts:
            lower_text = text.lower()
            for abbrev in common_abbrevs:
                if abbrev in lower_text:
                    found_abbrevs.append(abbrev)

        return list(set(found_abbrevs))[:10]

    def _detect_language(self, texts: List[str]) -> str:
        """Detect primary language."""
        vietnamese_words = ['tôi', 'bạn', 'có', 'không', 'là', 'được', 'cho', 'với', 'trong', 'để']
        english_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of']

        viet_count = 0
        eng_count = 0

        for text in texts:
            lower_text = text.lower()
            for word in vietnamese_words:
                if word in lower_text:
                    viet_count += 1
            for word in english_words:
                if word in lower_text:
                    eng_count += 1

        return list(set(found_abbrevs))[:10]

    def _detect_language(self, texts: List[str]) -> str:
        """Detect primary language."""
        vietnamese_words = ['tôi', 'bạn', 'có', 'không', 'là', 'được', 'cho', 'với', 'trong', 'để']
        english_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of']

        viet_count = 0
        eng_count = 0

        for text in texts:
            lower_text = text.lower()
            for word in vietnamese_words:
                if word in lower_text:
                    viet_count += 1
            for word in english_words:
                if word in lower_text:
                    eng_count += 1

        if viet_count > eng_count:
            return 'Vietnamese'
        elif eng_count > viet_count:
            return 'English'
        else:
            return 'Mixed'


class VocabularyFingerprinter:
    """
    Vocabulary Fingerprinter - Create a unique "fingerprint" of how someone writes

    Ported from OpenSelf's personality/fingerprint.js
    """

    def __init__(self):
        self.logger = LoggingConfig.get_logger("vocabulary_fingerprinter")

    def create_fingerprint(self, texts: List[str]) -> Dict[str, Any]:
        """
        Create a unique fingerprint of writing style.

        Args:
            texts: List of message strings

        Returns:
            Dictionary containing fingerprint data
        """
        return {
            'unique_words_ratio': self._get_unique_word_ratio(texts),
            'avg_word_length': self._get_avg_word_length(texts),
            'punctuation_style': self._analyze_punctuation(texts),
            'capitalization_style': self._analyze_capitalization(texts),
            'message_end_style': self._analyze_message_endings(texts),
            'question_frequency': self._get_question_frequency(texts),
            'exclamation_frequency': self._get_exclamation_frequency(texts),
        }

    def _get_unique_word_ratio(self, texts: List[str]) -> float:
        """Get ratio of unique words to total words."""
        all_words = []
        unique_words = set()

        for text in texts:
            words = text.lower().split()
            for word in words:
                clean = re.sub(r'[^\w]', '', word)
                if clean:
                    all_words.append(clean)
                    unique_words.add(clean)

        return round(len(unique_words) / max(len(all_words), 1), 3)

    def _get_avg_word_length(self, texts: List[str]) -> float:
        """Get average word length."""
        word_lengths = []

        for text in texts:
            words = text.split()
            for word in words:
                clean = re.sub(r'[^\w]', '', word)
                if clean:
                    word_lengths.append(len(clean))

        if not word_lengths:
            return 0.0
        return round(sum(word_lengths) / len(word_lengths), 1)

    def _analyze_punctuation(self, texts: List[str]) -> Dict[str, int]:
        """Analyze punctuation usage."""
        dots = 0
        commas = 0
        exclamations = 0
        questions = 0
        ellipsis = 0

        for text in texts:
            dots += len(re.findall(r'\.', text))
            commas += len(re.findall(r',', text))
            exclamations += len(re.findall(r'!', text))
            questions += len(re.findall(r'\?', text))
            ellipsis += len(re.findall(r'\.\.\.', text))

        return {
            'dots': dots,
            'commas': commas,
            'exclamations': exclamations,
            'questions': questions,
            'ellipsis': ellipsis
        }

    def _analyze_capitalization(self, texts: List[str]) -> str:
        """Analyze capitalization style."""
        all_caps = 0
        no_caps = 0
        normal_caps = 0

        for text in texts:
            if text == text.upper() and re.search(r'[A-Z]', text):
                all_caps += 1
            elif text == text.lower():
                no_caps += 1
            else:
                normal_caps += 1

        if all_caps > no_caps and all_caps > normal_caps:
            return 'ALL_CAPS'
        elif no_caps > all_caps and no_caps > normal_caps:
            return 'lowercase'
        else:
            return 'Normal'

    def _analyze_message_endings(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze how messages typically end."""
        endings = {}

        for text in texts:
            trimmed = text.strip()
            if not trimmed:
                continue

            last_char = trimmed[-1]
            # Check for emoji ending
            emoji_match = re.search(r'[\U0001F600-\U0001F9FF]$', trimmed, re.UNICODE)
            key = 'emoji' if emoji_match else last_char

            endings[key] = endings.get(key, 0) + 1

        return [
            {'char': char, 'count': count}
            for char, count in sorted(endings.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

    def _get_question_frequency(self, texts: List[str]) -> float:
        """Get frequency of question marks."""
        total_chars = sum(len(text) for text in texts)
        question_count = sum(len(re.findall(r'\?', text)) for text in texts)
        return round(question_count / max(total_chars, 1), 4)

    def _get_exclamation_frequency(self, texts: List[str]) -> float:
        """Get frequency of exclamation marks."""
        total_chars = sum(len(text) for text in texts)
        exclamation_count = sum(len(re.findall(r'!', text)) for text in texts)
        return round(exclamation_count / max(total_chars, 1), 4)


class SoulGenerator:
    """
    SOUL.md Auto-Generator - Generate a SOUL.md personality profile from extracted traits

    Ported from OpenSelf's personality/soul-generator.js
    """

    def __init__(self):
        self.logger = LoggingConfig.get_logger("soul_generator")

    def generate_soul_md(self, personality: Dict[str, Any], fingerprint: Dict[str, Any], user_info: Dict[str, Any] = None) -> str:
        """
        Generate a SOUL.md personality profile from extracted traits.

        Args:
            personality: Personality traits from PersonalityExtractor
            fingerprint: Writing fingerprint from VocabularyFingerprinter
            user_info: Additional user information (name, contacts, etc.)

        Returns:
            SOUL.md formatted string
        """
        if user_info is None:
            user_info = {}

        name = user_info.get('name', 'User')
        contacts = user_info.get('contacts', {})

        content_parts = []

        # Header
        content_parts.append(f"# SOUL.md — Generated by CloneMe OpenSelf Integration\n")

        # Identity section
        content_parts.append("## Identity")
        content_parts.append(f"- Name: {name}")
        content_parts.append(f"- Language: {personality.get('primary_language', 'Unknown')}")
        content_parts.append(f"- Total messages analyzed: {personality.get('total_messages', 0)}")
        content_parts.append("")

        # Communication Patterns
        content_parts.append("## Communication Patterns")
        content_parts.append(f"- Average message length: {personality.get('avg_message_length', 0)} chars (~{personality.get('avg_word_count', 0)} words)")
        emoji_freq = personality.get('emoji_frequency', 0)
        emoji_desc = "High" if emoji_freq > 0.3 else "Medium" if emoji_freq > 0.1 else "Low"
        content_parts.append(f"- Emoji frequency: {emoji_desc} ({round(emoji_freq * 100, 1)}% of messages)")
        content_parts.append(f"- Formality: {personality.get('formality', 'Unknown')}")
        humor_patterns = personality.get('humor_patterns', [])
        if humor_patterns:
            content_parts.append(f"- Humor: {', '.join(humor_patterns)}")
        greeting_style = personality.get('greeting_style', [])
        if greeting_style:
            content_parts.append(f"- Greeting style: {', '.join(greeting_style)}")

        # Top emojis
        top_emojis = personality.get('top_emojis', [])
        if top_emojis:
            emoji_list = [e['emoji'] for e in top_emojis[:5]]
            content_parts.append(f"- Top emojis: {' '.join(emoji_list)}")
        content_parts.append("")

        # Vocabulary Fingerprint
        content_parts.append("## Vocabulary Fingerprint")

        catchphrases = personality.get('catchphrases', [])
        if catchphrases:
            content_parts.append(f"- Catchphrases: \"{', '.join(catchphrases[:10])}\"")

        top_words = personality.get('top_words', [])
        if top_words:
            word_list = [w['word'] for w in top_words[:15]]
            content_parts.append(f"- Top words: {', '.join(word_list)}")

        content_parts.append("- Never says: \"I appreciate your patience\", \"As an AI...\", \"I understand your concern\"")
        content_parts.append(f"- Capitalization: {fingerprint.get('capitalization_style', 'Normal')}")
        content_parts.append("")

        # Vietnamese-specific
        primary_lang = personality.get('primary_language')
        if primary_lang == 'Vietnamese' or personality.get('pronoun_usage'):
            content_parts.append("## Vietnamese Style")

            pronoun_usage = personality.get('pronoun_usage', [])
            if pronoun_usage:
                content_parts.append(f"- Pronoun usage: {', '.join(pronoun_usage)}")

            content_parts.append(f"- Diacritics: {'Full diacritics used' if personality.get('tone_diacritics', False) else 'Sometimes skipped'}")

            abbreviations = personality.get('abbreviations', [])
            if abbreviations:
                content_parts.append(f"- Abbreviations: {', '.join(abbreviations)}")

            if personality.get('uses_slang', False):
                content_parts.append("- Slang: Frequently used")
            content_parts.append("")

        # Boundaries (sensible defaults)
        content_parts.append("## Boundaries")
        content_parts.append("- Never share: Personal finances, health info, passwords, private addresses")
        content_parts.append("- Deflect topics: Deep politics, religion (say \"ko bàn mấy cái này\")")
        content_parts.append("- When unsure: Say \"để t hỏi lại\" (don't make up answers)")
        content_parts.append("- Sensitive mode: If someone seems upset, switch to caring tone")
        content_parts.append("")

        # Relationships
        if contacts:
            content_parts.append("## Relationships")
            for contact_name, info in contacts.items():
                relationship = info.get('relationship', 'Friend')
                msg_count = info.get('message_count', 0)
                content_parts.append(f"- @{contact_name}: {relationship} ({msg_count} messages)")
            content_parts.append("")

        # Clone behavior defaults
        content_parts.append("## Clone Behavior")
        content_parts.append("- proactive_messages: false")
        content_parts.append("- reply_delay: random 30s-5min")
        content_parts.append("- typing_indicator: true")
        content_parts.append("- read_receipt_delay: random 10s-2min")
        content_parts.append("- online_hours: 08:00-23:00")
        content_parts.append("- fallback: \"Để t check lại rồi rep sau nha\"")

        return "\n".join(content_parts).strip()


class SafetyGuard:
    """
    Safety Guard - Prevent harmful or inappropriate content

    Ported from OpenSelf's safety/safety-guard.js
    """

    def __init__(self):
        self.logger = LoggingConfig.get_logger("safety_guard")

        # Harmful patterns to block
        self.harmful_patterns = [
            r'\b(kill|murder|suicide|self-harm)\b',
            r'\b(illegal|drugs|weapons|exploit)\b',
            r'\b(hack|crack|phish|scam)\b',
            r'\b(porn|sex|nsfw|nude)\b',
            r'\b(racist|sexist|homophobic|transphobic)\b',
            r'\b(terrorist|bomb|explosive)\b',
        ]

        # Sensitive topics to flag
        self.sensitive_topics = [
            'politics', 'religion', 'money', 'health', 'relationships'
        ]

    def check_message(self, message: str) -> Dict[str, Any]:
        """
        Check a message for safety concerns.

        Args:
            message: Message text to check

        Returns:
            Dictionary with safety assessment
        """
        result = {
            'safe': True,
            'blocked': False,
            'warnings': [],
            'severity': 'low'
        }

        lower_msg = message.lower()

        # Check for harmful patterns
        for pattern in self.harmful_patterns:
            if re.search(pattern, lower_msg, re.IGNORECASE):
                result['safe'] = False
                result['blocked'] = True
                result['warnings'].append(f"Contains harmful pattern: {pattern}")
                result['severity'] = 'high'
                break

        # Check for sensitive topics
        for topic in self.sensitive_topics:
            if topic in lower_msg:
                result['warnings'].append(f"Sensitive topic: {topic}")
                if result['severity'] == 'low':
                    result['severity'] = 'medium'

        # Check for excessive caps
        if len(message) > 10 and message == message.upper():
            result['warnings'].append("All caps message")
            if result['severity'] == 'low':
                result['severity'] = 'medium'

        # Check for spam patterns
        if len(re.findall(r'[!?]{3,}', message)) > 0:
            result['warnings'].append("Excessive punctuation")
            if result['severity'] == 'low':
                result['severity'] = 'medium'

        return result

    def sanitize_message(self, message: str) -> str:
        """
        Sanitize a message by removing or replacing harmful content.

        Args:
            message: Message to sanitize

        Returns:
            Sanitized message
        """
        # Remove harmful words
        harmful_words = ['kill', 'murder', 'suicide', 'drugs', 'weapons', 'hack', 'porn', 'sex']
        sanitized = message

        for word in harmful_words:
            sanitized = re.sub(rf'\b{word}\b', '[redacted]', sanitized, flags=re.IGNORECASE)

        return sanitized

    def should_block(self, message: str) -> bool:
        """
        Quick check if message should be blocked.

        Args:
            message: Message to check

        Returns:
            True if message should be blocked
        """
        check = self.check_message(message)
        return check['blocked']


class HumanMimicry:
    """
    Human Mimicry - Make responses more human-like

    Ported from OpenSelf's mimicry/human-mimicry.js
    """

    def __init__(self):
        self.logger = LoggingConfig.get_logger("human_mimicry")

        # Human-like response patterns
        self.hesitation_patterns = [
            "Hmm...", "Let me think...", "Wait a sec...",
            "Hmm, let me see...", "Give me a moment...",
            "Thinking about this...", "Let me check..."
        ]

        self.uncertainty_patterns = [
            "I'm not sure...", "Not entirely sure...",
            "Hmm, maybe...", "Could be...", "Possibly...",
            "I think...", "Probably..."
        ]

        self.conversation_starters = [
            "So...", "Anyway...", "Speaking of which...",
            "By the way...", "Oh, and...", "Also...",
            "On another note..."
        ]

    def add_human_touch(self, response: str, personality: Dict[str, Any] = None) -> str:
        """
        Add human-like elements to a response.

        Args:
            response: Original response text
            personality: Personality traits to consider

        Returns:
            Enhanced response with human touches
        """
        if personality is None:
            personality = {}

        enhanced = response

        # Add hesitation if response is too direct
        if len(response.split()) < 5 and random.random() < 0.3:
            hesitation = random.choice(self.hesitation_patterns)
            enhanced = f"{hesitation} {enhanced}"

        # Add uncertainty for complex topics
        if any(word in response.lower() for word in ['think', 'believe', 'probably', 'maybe']):
            if random.random() < 0.4:
                uncertainty = random.choice(self.uncertainty_patterns)
                enhanced = f"{uncertainty} {enhanced}"

        # Add conversation starters occasionally
        if random.random() < 0.2:
            starter = random.choice(self.conversation_starters)
            enhanced = f"{starter} {enhanced}"

        # Add emoji based on personality
        emoji_freq = personality.get('emoji_frequency', 0.1)
        if random.random() < emoji_freq:
            enhanced = self._add_appropriate_emoji(enhanced, personality)

        # Add typing imperfections
        if random.random() < 0.1:
            enhanced = self._add_typing_imperfection(enhanced)

        return enhanced

    def _add_appropriate_emoji(self, text: str, personality: Dict[str, Any]) -> str:
        """Add an appropriate emoji based on context and personality."""
        top_emojis = personality.get('top_emojis', [])
        if not top_emojis:
            # Default emojis
            common_emojis = ['😊', '👍', '🙂', '😄', '👌']
            return f"{text} {random.choice(common_emojis)}"

        # Use personality's top emojis
        emoji = random.choice(top_emojis)['emoji']
        return f"{text} {emoji}"

    def _add_typing_imperfection(self, text: str) -> str:
        """Add small typing imperfections to make it more human."""
        imperfections = [
            lambda t: t.replace('the', 'teh', 1) if 'the' in t else t,
            lambda t: t.replace('and', 'adn', 1) if 'and' in t else t,
            lambda t: t.replace('that', 'taht', 1) if 'that' in t else t,
            lambda t: t.replace('with', 'wiht', 1) if 'with' in t else t,
        ]

        if random.random() < 0.7:  # 70% chance to actually add imperfection
            imperfection = random.choice(imperfections)
            return imperfection(text)

        return text

    def vary_response_timing(self) -> float:
        """
        Get a human-like response delay.

        Returns:
            Delay in seconds
        """
        # Human typing speeds vary, but average around 200-300ms per word
        # Add some randomness and occasional longer pauses
        base_delay = random.uniform(1.0, 3.0)  # 1-3 seconds base

        # Occasional longer pauses (thinking)
        if random.random() < 0.2:
            base_delay += random.uniform(2.0, 5.0)

        return round(base_delay, 2)

    def add_reading_delay(self, message_length: int) -> float:
        """
        Calculate reading delay based on message length.

        Args:
            message_length: Length of message being "read"

        Returns:
            Delay in seconds
        """
        # Average reading speed ~200-300 words per minute
        words = max(1, message_length // 5)  # Rough word count
        reading_time = (words / 250) * 60  # Convert to seconds

        # Add some randomness
        reading_time *= random.uniform(0.8, 1.5)

        return round(reading_time, 2)


class StyleProcessor:
    """
    Style Processor - Process and adapt writing style

    Ported from OpenSelf's style/style-processor.js
    """

    def __init__(self):
        self.logger = LoggingConfig.get_logger("style_processor")

    def adapt_style(self, text: str, target_style: Dict[str, Any]) -> str:
        """
        Adapt text to match a target writing style.

        Args:
            text: Original text
            target_style: Style characteristics to adapt to

        Returns:
            Adapted text
        """
        adapted = text

        # Adapt capitalization
        cap_style = target_style.get('capitalization_style', 'Normal')
        if cap_style == 'ALL_CAPS':
            adapted = adapted.upper()
        elif cap_style == 'lowercase':
            adapted = adapted.lower()

        # Adapt punctuation
        punct_style = target_style.get('punctuation_style', {})
        adapted = self._adapt_punctuation(adapted, punct_style)

        # Adapt message endings
        endings = target_style.get('message_end_style', [])
        if endings and random.random() < 0.3:
            adapted = self._adapt_endings(adapted, endings)

        return adapted

    def _adapt_punctuation(self, text: str, punct_style: Dict[str, int]) -> str:
        """Adapt punctuation usage."""
        # This is a simplified adaptation - in practice would be more sophisticated
        adapted = text

        # Increase ellipsis usage if common in target style
        ellipsis_count = punct_style.get('ellipsis', 0)
        if ellipsis_count > 10 and random.random() < 0.2:
            # Replace some periods with ellipsis
            adapted = re.sub(r'\.(\s|$)', '... ', adapted)

        return adapted

    def _adapt_endings(self, text: str, endings: List[Dict[str, Any]]) -> str:
        """Adapt message endings."""
        if not endings:
            return text

        # Use the most common ending
        top_ending = endings[0]['char']
        if top_ending == 'emoji':
            # Would need emoji context, simplified here
            return text
        else:
            # Add the ending character if not already present
            if not text.endswith(top_ending):
                return text + top_ending

        return text

    def extract_style_features(self, texts: List[str]) -> Dict[str, Any]:
        """
        Extract style features from a collection of texts.

        Args:
            texts: List of text samples

        Returns:
            Style feature dictionary
        """
        features = {
            'sentence_length_avg': self._get_avg_sentence_length(texts),
            'word_length_avg': self._get_avg_word_length(texts),
            'punctuation_density': self._get_punctuation_density(texts),
            'formality_score': self._estimate_formality(texts),
        }

        return features

    def _get_avg_sentence_length(self, texts: List[str]) -> float:
        """Get average sentence length in words."""
        sentences = []
        for text in texts:
            # Split on sentence endings
            sents = re.split(r'[.!?]+', text)
            sentences.extend([s.strip() for s in sents if s.strip()])

        if not sentences:
            return 0.0

        word_counts = [len(s.split()) for s in sentences]
        return round(sum(word_counts) / len(word_counts), 1)

    def _get_avg_word_length(self, texts: List[str]) -> float:
        """Get average word length in characters."""
        words = []
        for text in texts:
            words.extend(re.findall(r'\b\w+\b', text))

        if not words:
            return 0.0

        lengths = [len(word) for word in words]
        return round(sum(lengths) / len(lengths), 1)

    def _get_punctuation_density(self, texts: List[str]) -> float:
        """Get punctuation density (punct chars per 100 chars)."""
        total_chars = sum(len(text) for text in texts)
        punct_chars = sum(len(re.findall(r'[.!?,;:]', text)) for text in texts)

        if total_chars == 0:
            return 0.0

        return round((punct_chars / total_chars) * 100, 2)

    def _estimate_formality(self, texts: List[str]) -> float:
        """Estimate formality score (0.0 = very informal, 1.0 = very formal)."""
        formal_indicators = ['therefore', 'however', 'consequently', 'furthermore', 'moreover']
        informal_indicators = ['lol', 'haha', 'omg', 'wtf', 'kinda', 'sorta']

        formal_count = 0
        informal_count = 0

        for text in texts:
            lower = text.lower()
            for word in formal_indicators:
                formal_count += lower.count(word)
            for word in informal_indicators:
                informal_count += lower.count(word)

        total_indicators = formal_count + informal_count
        if total_indicators == 0:
            return 0.5  # Neutral

        formality = formal_count / total_indicators
        return round(formality, 2)


class ChatParser:
    """
    Chat Parser - Parse and analyze chat messages

    Ported from OpenSelf's chat/chat-parser.js
    """

    def __init__(self):
        self.logger = LoggingConfig.get_logger("chat_parser")

    def parse_messages(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Parse a collection of chat messages.

        Args:
            messages: List of message dictionaries with 'content', 'author', 'timestamp' keys

        Returns:
            Parsed chat data
        """
        parsed = {
            'total_messages': len(messages),
            'participants': self._extract_participants(messages),
            'conversation_flow': self._analyze_conversation_flow(messages),
            'topics': self._extract_topics(messages),
            'sentiment_trends': self._analyze_sentiment_trends(messages),
            'message_types': self._categorize_messages(messages),
        }

        return parsed

    def _extract_participants(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract unique participants and their message counts."""
        participants = {}

        for msg in messages:
            author = msg.get('author', 'Unknown')
            if author not in participants:
                participants[author] = {
                    'name': author,
                    'message_count': 0,
                    'first_message': msg.get('timestamp'),
                    'last_message': msg.get('timestamp')
                }

            participants[author]['message_count'] += 1
            participants[author]['last_message'] = msg.get('timestamp')

        return list(participants.values())

    def _analyze_conversation_flow(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the flow and timing of conversation."""
        if not messages:
            return {}

        # Sort by timestamp if available
        sorted_msgs = sorted(messages, key=lambda x: x.get('timestamp', 0))

        response_times = []
        for i in range(1, len(sorted_msgs)):
            prev_time = sorted_msgs[i-1].get('timestamp', 0)
            curr_time = sorted_msgs[i].get('timestamp', 0)
            if curr_time > prev_time:
                response_times.append(curr_time - prev_time)

        avg_response_time = sum(response_times) / max(len(response_times), 1) if response_times else 0

        return {
            'avg_response_time_seconds': round(avg_response_time, 2),
            'total_exchanges': len(response_times),
            'conversation_duration': self._calculate_duration(sorted_msgs),
        }

    def _calculate_duration(self, messages: List[Dict[str, Any]]) -> int:
        """Calculate total conversation duration in seconds."""
        if not messages:
            return 0

        timestamps = [msg.get('timestamp', 0) for msg in messages if msg.get('timestamp')]
        if not timestamps:
            return 0

        return max(timestamps) - min(timestamps)

    def _extract_topics(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract main topics from messages."""
        # Simple keyword-based topic extraction
        topic_keywords = {
            'work': ['work', 'job', 'office', 'meeting', 'project'],
            'food': ['food', 'eat', 'drink', 'restaurant', 'hungry'],
            'travel': ['travel', 'trip', 'vacation', 'flight', 'hotel'],
            'tech': ['computer', 'phone', 'app', 'software', 'code'],
            'entertainment': ['movie', 'music', 'game', 'watch', 'play'],
        }

        topic_counts = {topic: 0 for topic in topic_keywords}

        for msg in messages:
            content = msg.get('content', '').lower()
            for topic, keywords in topic_keywords.items():
                if any(keyword in content for keyword in keywords):
                    topic_counts[topic] += 1

        # Return topics with counts > 0
        return [
            {'topic': topic, 'mentions': count}
            for topic, count in topic_counts.items()
            if count > 0
        ]

    def _analyze_sentiment_trends(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment trends over time."""
        # Simple sentiment analysis based on keywords
        positive_words = ['good', 'great', 'awesome', 'love', 'happy', 'excited']
        negative_words = ['bad', 'terrible', 'hate', 'sad', 'angry', 'upset']

        sentiments = []
        for msg in messages:
            content = msg.get('content', '').lower()
            pos_count = sum(1 for word in positive_words if word in content)
            neg_count = sum(1 for word in negative_words if word in content)

            if pos_count > neg_count:
                sentiment = 'positive'
            elif neg_count > pos_count:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'

            sentiments.append({
                'timestamp': msg.get('timestamp'),
                'sentiment': sentiment,
                'intensity': max(pos_count, neg_count)
            })

        return {
            'overall_sentiment': self._calculate_overall_sentiment(sentiments),
            'sentiment_distribution': self._get_sentiment_distribution(sentiments),
            'sentiment_timeline': sentiments,
        }

    def _calculate_overall_sentiment(self, sentiments: List[Dict[str, Any]]) -> str:
        """Calculate overall sentiment."""
        pos = sum(1 for s in sentiments if s['sentiment'] == 'positive')
        neg = sum(1 for s in sentiments if s['sentiment'] == 'negative')
        neu = sum(1 for s in sentiments if s['sentiment'] == 'neutral')

        if pos > neg and pos > neu:
            return 'positive'
        elif neg > pos and neg > neu:
            return 'negative'
        else:
            return 'neutral'

    def _get_sentiment_distribution(self, sentiments: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of sentiments."""
        dist = {'positive': 0, 'negative': 0, 'neutral': 0}
        for s in sentiments:
            dist[s['sentiment']] += 1
        return dist

    def _categorize_messages(self, messages: List[Dict[str, Any]]) -> Dict[str, int]:
        """Categorize messages by type."""
        categories = {
            'question': 0,
            'statement': 0,
            'command': 0,
            'exclamation': 0,
            'other': 0
        }

        for msg in messages:
            content = msg.get('content', '').strip()

            if content.endswith('?'):
                categories['question'] += 1
            elif content.endswith('!'):
                categories['exclamation'] += 1
            elif content.startswith(('please', 'can you', 'would you', 'could you')):
                categories['command'] += 1
            elif len(content.split()) > 2:  # Simple heuristic for statements
                categories['statement'] += 1
            else:
                categories['other'] += 1

        return categories


class OpenSelfIntegration:
    """
    Main integration class for OpenSelf components.

    This class provides a unified interface to all OpenSelf personality analysis
    and mimicry features, designed to work as an optional component in CloneMe.
    """

    def __init__(self):
        self.logger = LoggingConfig.get_logger("openself_integration")

        # Initialize all components
        self.personality_extractor = PersonalityExtractor()
        self.vocabulary_fingerprinter = VocabularyFingerprinter()
        self.soul_generator = SoulGenerator()
        self.safety_guard = SafetyGuard()
        self.human_mimicry = HumanMimicry()
        self.style_processor = StyleProcessor()
        self.chat_parser = ChatParser()

    def analyze_personality_from_messages(self, messages: List[str], user_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Complete personality analysis from chat messages.

        Args:
            messages: List of message strings
            user_info: Additional user information

        Returns:
            Complete personality profile
        """
        if user_info is None:
            user_info = {}

        try:
            # Extract personality traits
            personality = self.personality_extractor.extract_personality(messages)

            # Create vocabulary fingerprint
            fingerprint = self.vocabulary_fingerprinter.create_fingerprint(messages)

            # Generate SOUL.md profile
            soul_profile = self.soul_generator.generate_soul_md(
                personality, fingerprint, user_info
            )

            return {
                'personality': personality,
                'fingerprint': fingerprint,
                'soul_profile': soul_profile,
                'analysis_timestamp': datetime.now().isoformat(),
                'message_count': len(messages)
            }

        except Exception as e:
            self.logger.error(f"Error in personality analysis: {e}")
            return {
                'error': str(e),
                'personality': {},
                'fingerprint': {},
                'soul_profile': '',
                'analysis_timestamp': datetime.now().isoformat(),
                'message_count': len(messages)
            }

    def enhance_response(self, response: str, personality_profile: Dict[str, Any] = None) -> str:
        """
        Enhance a response with human-like characteristics.

        Args:
            response: Original response text
            personality_profile: Personality profile to match

        Returns:
            Enhanced response
        """
        if personality_profile is None:
            personality_profile = {}

        try:
            # Check safety first
            safety_check = self.safety_guard.check_message(response)
            if safety_check['blocked']:
                return "[Response blocked for safety reasons]"

            # Apply human mimicry
            personality = personality_profile.get('personality', {})
            enhanced = self.human_mimicry.add_human_touch(response, personality)

            # Adapt style if personality data available
            fingerprint = personality_profile.get('fingerprint', {})
            if fingerprint:
                enhanced = self.style_processor.adapt_style(enhanced, fingerprint)

            return enhanced

        except Exception as e:
            self.logger.error(f"Error enhancing response: {e}")
            return response

    def get_response_timing(self, incoming_message_length: int = 0) -> Dict[str, float]:
        """
        Get human-like response timing.

        Args:
            incoming_message_length: Length of message being responded to

        Returns:
            Dictionary with timing information
        """
        try:
            reading_delay = self.human_mimicry.add_reading_delay(incoming_message_length)
            response_delay = self.human_mimicry.vary_response_timing()

            return {
                'reading_delay': reading_delay,
                'response_delay': response_delay,
                'total_delay': reading_delay + response_delay
            }

        except Exception as e:
            self.logger.error(f"Error calculating timing: {e}")
            return {
                'reading_delay': 1.0,
                'response_delay': 2.0,
                'total_delay': 3.0
            }

    def parse_chat_history(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Parse and analyze chat history.

        Args:
            messages: List of message dictionaries

        Returns:
            Parsed chat analysis
        """
        try:
            return self.chat_parser.parse_messages(messages)
        except Exception as e:
            self.logger.error(f"Error parsing chat history: {e}")
            return {'error': str(e)}

    def enhance_response_with_profile(self, response: str, profile: 'Profile') -> str:
        """
        Enhance a response using combined questionnaire and OpenSelf data.

        Args:
            response: Original response text
            profile: Profile object with questionnaire and OpenSelf data

        Returns:
            Enhanced response
        """
        if not profile:
            return self.enhance_response(response)

        # Check safety first
        safety_check = self.safety_guard.check_message(response)
        if safety_check['blocked']:
            return "[Response blocked for safety reasons]"

        enhanced = response

        # Apply human mimicry with personality from profile
        personality_data = {}
        if profile.has_openself_data:
            personality_data = profile.openself_personality

        enhanced = self.human_mimicry.add_human_touch(enhanced, personality_data)

        # Adapt style based on profile fingerprint
        if profile.has_openself_data:
            fingerprint = profile.openself_fingerprint
            if fingerprint:
                enhanced = self.style_processor.adapt_style(enhanced, fingerprint)

        # Apply questionnaire-based customizations
        enhanced = self._apply_questionnaire_customizations(enhanced, profile)

        return enhanced

    def _apply_questionnaire_customizations(self, response: str, profile: 'Profile') -> str:
        """
        Apply customizations based on questionnaire answers.

        Args:
            response: Response to customize
            profile: Profile with questionnaire data

        Returns:
            Customized response
        """
        # Get personality traits from questionnaire
        traits = profile.personality_traits

        # Customize based on formality preference
        formality = None
        for key, value in traits.items():
            if 'formality' in key.lower() or 'formal' in key.lower():
                formality = str(value).lower()
                break

        if formality and 'casual' in formality:
            # Make more casual
            response = response.replace('I am', 'Im').replace('do not', 'dont')
        elif formality and 'formal' in formality:
            # Make more formal
            response = response.replace('Im', 'I am').replace('dont', 'do not')

        # Customize based on emoji preference
        emoji_pref = None
        for key, value in traits.items():
            if 'emoji' in key.lower():
                emoji_pref = str(value).lower()
                break

        if emoji_pref and 'no' in emoji_pref and profile.has_openself_data:
            # Remove emojis if user doesn't like them
            import re
            response = re.sub(r'[\U0001F600-\U0001F9FF]', '', response)

        return response

    def get_response_timing_with_profile(self, profile: 'Profile', incoming_message_length: int = 0) -> Dict[str, float]:
        """
        Get response timing considering profile personality.

        Args:
            profile: Profile object
            incoming_message_length: Length of incoming message

        Returns:
            Timing information
        """
        base_timing = self.get_response_timing(incoming_message_length)

        # Adjust timing based on personality
        if profile.has_openself_data:
            response_time_avg = profile.get_openself_trait('response_time_avg', 60000)
            if response_time_avg < 30000:  # Fast responder
                base_timing['response_delay'] *= 0.8
            elif response_time_avg > 120000:  # Slow responder
                base_timing['response_delay'] *= 1.2

        return base_timing

    def generate_enhanced_soul_profile(self, profile: 'Profile') -> str:
        """
        Generate an enhanced SOUL.md profile combining questionnaire and chat data.

        Args:
            profile: Profile with both questionnaire and OpenSelf data

        Returns:
            Enhanced SOUL.md profile
        """
        if not profile.has_openself_data:
            # Fallback to basic profile generation
            return self._generate_questionnaire_only_soul(profile)

        # Use existing OpenSelf SOUL profile as base
        base_soul = profile.openself_soul_profile
        if not base_soul:
            return self._generate_questionnaire_only_soul(profile)

        # Enhance with questionnaire data
        enhancements = []

        # Add questionnaire-based personality insights
        traits = profile.personality_traits
        if traits:
            trait_lines = []
            for key, value in traits.items():
                if value and str(value).strip():
                    trait_lines.append(f"- {key}: {value}")
            if trait_lines:
                enhancements.append("## Questionnaire Personality Traits\n" + "\n".join(trait_lines))

        # Add strengths and weaknesses
        questionnaire = profile.get_field('questionnaire', {})
        strengths = questionnaire.get('strengths', [])
        weaknesses = questionnaire.get('weaknesses', [])

        if strengths:
            enhancements.append(f"## Strengths\n- {', '.join(strengths)}")

        if weaknesses:
            enhancements.append(f"## Areas for Growth\n- {', '.join(weaknesses)}")

        # Combine base SOUL with enhancements
        if enhancements:
            enhanced_soul = base_soul + "\n\n" + "\n\n".join(enhancements)
            return enhanced_soul

        return base_soul

    def _generate_questionnaire_only_soul(self, profile: 'Profile') -> str:
        """
        Generate a basic SOUL.md profile from questionnaire data only.

        Args:
            profile: Profile with questionnaire data

        Returns:
            Basic SOUL.md profile
        """
        name = profile.name or "User"
        username = profile.username or "user"

        content_parts = [
            f"# SOUL.md — Generated from Questionnaire Data\n",
            "## Identity",
            f"- Name: {name}",
            f"- Username: {username}",
            f"- Profile created: {profile.created_at.date() if profile.created_at else 'Unknown'}",
            "",
        ]

        # Add personality traits
        traits = profile.personality_traits
        if traits:
            content_parts.extend(["## Personality Traits"])
            for key, value in traits.items():
                if value:
                    content_parts.append(f"- {key}: {value}")
            content_parts.append("")

        # Add response styles
        styles = profile.response_styles
        if styles:
            content_parts.extend(["## Communication Style"])
            for key, value in styles.items():
                if value:
                    content_parts.append(f"- {key}: {value}")
            content_parts.append("")

        # Add strengths/weaknesses
        questionnaire = profile.get_field('questionnaire', {})
        strengths = questionnaire.get('strengths', [])
        weaknesses = questionnaire.get('weaknesses', [])

        if strengths:
            content_parts.extend(["## Strengths", f"- {', '.join(strengths)}", ""])

        if weaknesses:
            content_parts.extend(["## Areas for Growth", f"- {', '.join(strengths)}", ""])

        return "\n".join(content_parts).strip()