
## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Setup](#detailed-setup)
4. [Configuration](#configuration)
5. [Running the Project](#running-the-project)
   - [Mode 1: Local Personality Assessment](#mode-1-local-personality-assessment)
   - [Mode 2: Discord Integration](#mode-2-discord-integration)
6. [Creating Enhanced Profiles](#creating-enhanced-profiles)
7. [Advanced Features](#advanced-features)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **Python**: 3.11.6 or higher
- **Operating System**: Windows, macOS, or Linux
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: 500MB free space

### Required Accounts & API Keys

**AI API Provider** (choose one):
   - **OpenAI**: https://platform.openai.com/api-keys
   - **Claude/Anthropic**: https://console.anthropic.com/
   - **Groq**: https://console.groq.com/

---

## Quick Start

### 1. Clone and Setup
```bash
cd /path/to/your/projects
git clone <repository-url>
cd repo_name
pip install -r requirements.txt
```

### 2. Configure Environment

```

### 3. Run the Bot
```bash
python main.py
```


## Detailed Setup

### Step 1: Install Dependencies
```bash
# Install Python requirements
pip install -r requirements.txt

# Optional: Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Verify Installation
Run the setup verification script:
```bash
python scripts/setup.py
```

Expected output:
```
🔧 CloneMe Setup Verification
✅ Python version: 3.11.6
✅ Required packages installed
✅ Project structure valid
✅ Ready to configure!
```

### Step 3: Environment Configuration
Create or edit `.env` file in the project root:


# AI Provider Configuration
AI_PROVIDER="openai"  # Options: openai, claude, groq
AI_API_KEY="your_actual_api_key_here"
AI_MODEL="gpt-4"  # Options: gpt-4, gpt-3.5-turbo, claude-3-sonnet, etc.
AI_PROFILE="default"  # Profile to use (see profiles/ directory)

# Optional: Advanced Settings
LOG_LEVEL="INFO"
MAX_TOKENS="2000"
TEMPERATURE="0.7"
```

### AI Provider Setup

#### OpenAI
```env
AI_PROVIDER="openai"
AI_API_KEY="sk-your-openai-key-here"
AI_MODEL="gpt-4"  # or gpt-3.5-turbo
```

#### Claude/Anthropic
```env
AI_PROVIDER="claude"
AI_API_KEY="sk-ant-your-claude-key-here"
AI_MODEL="claude-3-sonnet-20240229"
```

#### Groq
```env
AI_PROVIDER="groq"
AI_API_KEY="gsk-your-groq-key-here"
AI_MODEL="mixtral-8x7b-32768"
```

---

## Running the Project

### Mode 1: Local Personality Assessment

Generate a personality profile using the **IPIP-NEO 120 questionnaire** (local, no Discord required):

#### Option A: CLI Mode
```bash
# Basic assessment (interactive 120 questions)
PLATFORM=assessment python main.py

# With custom user info
PLATFORM=assessment \
ASSESSMENT_USER_NAME="john_doe" \
ASSESSMENT_USER_FULLNAME="John Doe" \
ASSESSMENT_USER_SEX="M" \
ASSESSMENT_USER_AGE=28 \
python main.py
```

This generates three files in the project root:
- **`personality_profile.json`** – Complete IPIP-NEO results and profile config
- **`SOUL.md`** – Personality summary in Markdown format
- **`CurrentNode.json`** – State snapshot for pipeline use

#### Option B: Streamlit Web UI
```bash
# Make sure you're in the project root directory
cd C:\Users\madha\Downloads\BehaviouralMapping

# Then run:
streamlit run mods/assessment/streamlit_app.py
```
Then open `http://localhost:8501` in your browser. Answer all 120 questions with a slider (1–5 scale).

#### Option C: Programmatic (Python)
```python
from mods.assessment.assessment import AssessmentModule
from mods.config import ProfileManager

pm = ProfileManager(profiles_directory=".")
assessment = AssessmentModule(profile_manager=pm)

# Option 1: Interactive
result = assessment.run(
    profile_name="my_assessment",
    user_info={"username": "john", "name": "John Doe", "age": 28, "sex": "M"},
    shuffle=False
)

# Option 2: Load from JSON answers file
result = assessment.run(
    profile_name="my_assessment",
    user_info={"username": "john", "name": "John Doe", "age": 28, "sex": "M"},
    answers_file="my_answers.json"
)

print(f"Profile created: {result['profile'].profile_name}")
print(f"Personality file: {result['personality_profile_json']}")
```

**Answer File Format** (`my_answers.json`):
```json
{
  "answers": [
    {"id_question": 1, "id_select": 4},
    {"id_question": 2, "id_select": 3},
    ...
  ]
}
```

---

### Mode 2: Discord Integration

Run the bot connected to Discord (requires `DISCORD_SELF_TOKEN`):

#### Prerequisites
1. Get your Discord self-token from an existing Discord session
2. Add to `.env`:
   ```env
   PLATFORM="discord"
   DISCORD_SELF_TOKEN="your_discord_token_here"
   AI_PROVIDER="openai"
   AI_API_KEY="your_api_key"
   AI_MODEL="gpt-4"
   ```

#### Run
```bash
python main.py
```

The bot will:
- Listen to Discord messages
- Use your configured AI provider to generate responses
- Apply your personality profile to responses
- Load and use `personality_profile.json` if it exists in the project root

---

## Creating Enhanced Profiles

### Option 1: Use Default Profile
The project includes a default profile. No additional setup needed.

### Option 2: Create Custom Profile with Questionnaire

```python
from mods.config.profile_intake import ProfileIntakePipeline
from mods.config.profile_manager import ProfileManager

# Initialize components
pm = ProfileManager('profiles')
pipeline = ProfileIntakePipeline(pm)

# Your personality questionnaire
questionnaire = {
    'name': 'Your Name',
    'username': 'your_discord_username',
    'age': 25,
    'communication_style': 'casual and friendly',
    'formality_level': 'informal',
    'humor_style': 'witty and sarcastic',
    'strengths': ['problem solving', 'creativity', 'coding'],
    'weaknesses': ['perfectionism', 'overthinking'],
    'favorite_topics': ['AI', 'programming', 'gaming'],
    'response_preferences': 'helpful, concise, with occasional humor'
}

# Create profile
profile = pipeline.create_profile_from_questionnaire(
    'my_custom_profile',
    questionnaire,
    {'name': 'Your Name', 'username': 'your_username'}
)

print(f"✅ Profile created: {profile.name}")
```

### Option 3: Create Enhanced Profile with OpenSelf Analysis

```python
# Include chat history for personality analysis
chat_history = [
    "Hey, what's up? Been working on this cool project.",
    "Yeah, Python is my jam. Love the simplicity!",
    "Haha, that's hilarious! You got me laughing.",
    "Totally get that. Sometimes you just need to debug with print statements.",
    "Gaming is life! Just finished an epic session.",
    "Open source is awesome. Contributing back feels great.",
    "Bruh, this bug is killing me. Spent 3 hours on it already.",
    "Coffee is my fuel. Can't function without at least 2 cups in the morning."
]

# Create enhanced profile with OpenSelf analysis
enhanced_profile = pipeline.create_profile_from_questionnaire_and_chat(
    'my_enhanced_profile',
    questionnaire,
    chat_history,
    {'name': 'Your Name', 'username': 'your_username'}
)

print(f"✅ Enhanced profile created with OpenSelf: {enhanced_profile.has_openself_data}")
```

### Managing Multiple Profiles

```python
# Create different profiles for different contexts
work_profile = pipeline.create_profile_from_questionnaire_and_chat(
    'work_profile',
    work_questionnaire,
    work_chat_history,
    {'name': 'Professional You', 'username': 'work_username'}
)

casual_profile = pipeline.create_profile_from_questionnaire_and_chat(
    'casual_profile',
    casual_questionnaire,
    casual_chat_history,
    {'name': 'Casual You', 'username': 'casual_username'}
)

# Switch profiles by updating .env
# AI_PROFILE="work_profile" or AI_PROFILE="casual_profile"
```
