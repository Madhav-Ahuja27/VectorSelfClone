# OpenSelf Integration

This module integrates personality analysis and human mimicry components from the OpenSelf project into CloneMe. It operates as a separate, optional component that doesn't interfere with the existing questionnaire-based profile system.

## Features

- **Personality Extraction**: Analyzes chat messages to extract personality traits, emoji usage, language patterns, and communication style
- **Vocabulary Fingerprinting**: Creates unique "fingerprints" of writing style including word usage, punctuation, and capitalization patterns
- **SOUL.md Generation**: Automatically generates personality profiles in SOUL.md format
- **Safety Guard**: Prevents harmful or inappropriate content
- **Human Mimicry**: Makes responses more human-like with natural timing and imperfections
- **Style Processing**: Adapts writing style to match target personalities
- **Chat Parsing**: Analyzes conversation flow, topics, and sentiment trends

## Usage

### Basic Integration

```python
from mods.openself_integration import OpenSelfIntegration

# Initialize the integration
openself = OpenSelfIntegration()

# Analyze personality from chat messages
messages = ["Hello!", "How are you?", "I'm doing great!"]
profile = openself.analyze_personality_from_messages(messages)

# Enhance responses with human-like characteristics
response = "I understand your concern"
enhanced = openself.enhance_response(response, profile)

# Check response safety
safety = openself.validate_response_safety(response)

# Get human-like timing
timing = openself.get_response_timing(len("incoming message"))
```

### Integration with Existing Profile System

The OpenSelf integration can work alongside your existing questionnaire-based profile intake:

```python
from mods.config.profile_manager import ProfileManager
from mods.config.profile_intake import ProfileIntakePipeline
from mods.openself_integration import OpenSelfIntegration

# Load existing profile
profile_manager = ProfileManager()
existing_profile = profile_manager.load_profile("user_profile.json")

# Add OpenSelf analysis
openself = OpenSelfIntegration()
chat_messages = ["message1", "message2", "..."]  # From chat history
personality_data = openself.analyze_personality_from_messages(chat_messages)

# Merge with existing profile
# (You can extend the ProfileIntakePipeline to include this data)
```

## Components

### PersonalityExtractor
Extracts personality traits from text:
- Language detection (English/Vietnamese/Mixed)
- Emoji usage patterns
- Communication formality
- Humor and greeting styles
- Catchphrases and slang usage

### VocabularyFingerprinter
Creates writing style fingerprints:
- Unique word ratios
- Average word/sentence lengths
- Punctuation patterns
- Capitalization styles
- Message ending preferences

### SoulGenerator
Generates SOUL.md personality profiles for AI training.

### SafetyGuard
Validates content for harmful patterns and sensitive topics.

### HumanMimicry
Adds human-like elements to responses:
- Hesitation patterns
- Natural timing variations
- Typing imperfections
- Conversation flow

### StyleProcessor
Adapts text style to match target personalities.

### ChatParser
Analyzes conversation structure and sentiment.

## Architecture

This integration is designed as a separate component that:
- Doesn't modify existing CloneMe functionality
- Can be optionally enabled/disabled
- Provides additional personality data sources
- Enhances response naturalness when used

## Dependencies

- Python 3.11+
- Standard library modules (re, random, datetime, etc.)
- CloneMe's logging configuration (with fallback)

## Testing

The module includes comprehensive personality analysis from chat messages and maintains safety checks for all generated content.