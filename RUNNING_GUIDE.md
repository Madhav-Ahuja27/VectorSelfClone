# 🚀 CloneMe Project: Complete Setup and Run Guide

## Overview

CloneMe is an AI-powered Discord bot that creates personalized chat personalities using both questionnaire data and automatic personality analysis from chat history. The bot integrates OpenSelf components for enhanced personality extraction and response generation.

**Last Updated:** May 7, 2026

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Setup](#detailed-setup)
4. [Configuration](#configuration)
5. [Creating Enhanced Profiles](#creating-enhanced-profiles)
6. [Running the Bot](#running-the-bot)
7. [Testing](#testing)
8. [Advanced Features](#advanced-features)
9. [Troubleshooting](#troubleshooting)
10. [Production Deployment](#production-deployment)

---

## Prerequisites

### System Requirements
- **Python**: 3.11.6 or higher
- **Operating System**: Windows, macOS, or Linux
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: 500MB free space

### Required Accounts & API Keys
1. **Discord Application**:
   - Go to https://discord.com/developers/applications
   - Create a new application
   - Navigate to "Bot" section
   - Create a bot user and copy the token

2. **AI API Provider** (choose one):
   - **OpenAI**: https://platform.openai.com/api-keys
   - **Claude/Anthropic**: https://console.anthropic.com/
   - **Groq**: https://console.groq.com/

---

## Quick Start

### 1. Clone and Setup
```bash
cd /path/to/your/projects
git clone <repository-url>
cd cloneme-master
pip install -r requirements.txt
```

### 2. Configure Environment
Edit `.env` file with your credentials:
```env
DISCORD_SELF_TOKEN="your_actual_discord_token_here"
AI_API_KEY="your_actual_api_key_here"
AI_PROVIDER="openai"
AI_MODEL="gpt-4"
AI_PROFILE="default"
PLATFORM="discord"
```

### 3. Run the Bot
```bash
python main.py
```

### 4. Test in Discord
Invite the bot to your server and mention it:
```
@YourBot hello! How are you?
```

---

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

```env
# Discord Bot Configuration
DISCORD_SELF_TOKEN="your_actual_discord_token_here"
PLATFORM="discord"

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

---

## Configuration

### Discord Bot Setup

1. **Create Discord Application**:
   - Visit https://discord.com/developers/applications
   - Click "New Application"
   - Give it a name (e.g., "CloneMe Bot")

2. **Configure Bot**:
   - Go to "Bot" section
   - Click "Reset Token" and copy the token
   - Enable "Message Content Intent" under "Privileged Gateway Intents"

3. **Generate Invite Link**:
   - Go to "OAuth2" → "URL Generator"
   - Select `bot` scope
   - Select permissions:
     - Send Messages
     - Read Message History
     - Use Slash Commands
     - Embed Links
   - Use the generated URL to invite the bot

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

---

## Running the Bot

### Basic Startup
```bash
cd /path/to/cloneme-master
python main.py
```

### Expected Startup Output
```
🌐 Selected platform: discord
📝 Initializing logging system...
✅ Logging initialized with X loggers
🔗 Connecting to Discord...
✅ Connected! Bot is online as @your_username
🤖 AI Profile loaded: my_profile
🧠 OpenSelf integration: ENABLED
📊 Ready to respond to messages!
```

### Running in Background (Linux/macOS)
```bash
# Using screen
screen -S cloneme python main.py

# Detach: Ctrl+A, D
# Reattach: screen -r cloneme

# Using nohup
nohup python main.py &
```

### Running in Background (Windows)
```powershell
# Using PowerShell background job
Start-Job -ScriptBlock { python main.py }

# Or use a tool like NSSM to create a Windows service
```

---

## Testing

### Basic Functionality Test

1. **Invite Bot to Server**:
   - Use the OAuth2 URL generated during setup
   - Grant necessary permissions

2. **Test Commands**:
   ```
   @YourBot hello!
   @YourBot how are you?
   @YourBot what's your favorite programming language?
   ```

3. **Expected Behavior**:
   - Bot responds within 2-5 seconds
   - Responses match your configured personality
   - OpenSelf enhancements are applied (if enabled)

### OpenSelf Integration Test

Test personality-specific responses:
```
@YourBot tell me a joke
@YourBot what's your take on AI?
@YourBot how do you approach debugging?
@YourBot what's your communication style?
```

**What to Verify**:
- ✅ **Personality Consistency**: Responses reflect questionnaire answers
- ✅ **Communication Style**: Matches formality level and preferences
- ✅ **Topic Adaptation**: Different responses for favorite topics
- ✅ **Humor Integration**: Appropriate humor style usage
- ✅ **Emoji Usage**: Consistent with preferences

### Advanced Testing

```python
# Test profile loading
from mods.config.profile_manager import ProfileManager
pm = ProfileManager('profiles')
profile = pm.get_profile('my_profile')
print(f"Profile loaded: {profile.name if profile else 'FAILED'}")

# Test OpenSelf enhancement
from mods.openself_integration import OpenSelfIntegration
openself = OpenSelfIntegration()
test_response = "Hello!"
enhanced = openself.enhance_response_with_profile(test_response, profile)
print(f"Enhancement working: {'YES' if enhanced != test_response else 'NO'}")
```

---

## Advanced Features

### Profile Enhancement Over Time

```python
# Add more chat history to improve personality analysis
new_messages = [
    "Just learned about transformers in ML!",
    "This new framework is game-changing.",
    "Debugging async code is such a headache.",
    "Love the new TypeScript features!",
]

# Enhance existing profile
enhanced_profile = pipeline.enhance_profile_with_chat_analysis(
    profile,
    new_messages
)

print("✅ Profile enhanced with new chat data")
```

### Custom Response Styles

```python
# Define custom response patterns
custom_styles = {
    'greeting_responses': [
        "Hey there! Great to see you!",
        "What's up? Ready to chat?",
        "Hello! How's your day going?"
    ],
    'question_responses': [
        "That's an interesting question...",
        "Let me think about that...",
        "Good point! Here's what I think..."
    ],
    'error_responses': [
        "Oops, something went wrong there.",
        "Hmm, let me try that again.",
        "Sorry about that! Let me fix this."
    ]
}

# Apply to profile
profile.update_response_styles(custom_styles)
```

### Monitoring and Analytics

Check logs in `logs/` directory:
- `logs/setup/` - Setup and configuration logs
- `logs/` - Runtime conversation logs
- Look for "OpenSelf enhancement applied" messages

### Backup and Recovery

```bash
# Backup profiles and configuration
cp -r profiles profiles_backup_$(date +%Y%m%d)
cp .env .env.backup

# Restore from backup
cp -r profiles_backup_20231201 profiles
cp .env.backup .env
```

---

## Troubleshooting

### Bot Won't Start

**Issue**: Bot fails to start with connection errors
```
🔗 Connecting to Discord...
❌ Connection failed: Invalid token
```

**Solutions**:
- ✅ Verify `DISCORD_SELF_TOKEN` in `.env` is correct
- ✅ Check token permissions in Discord Developer Portal
- ✅ Ensure bot is invited to server with proper permissions
- ✅ Check internet connection

**Issue**: AI API errors
```
❌ AI Provider error: Invalid API key
```

**Solutions**:
- ✅ Verify `AI_API_KEY` is correct and active
- ✅ Check API provider status and quotas
- ✅ Ensure correct `AI_PROVIDER` setting

### Profile Issues

**Issue**: Profile not loading
```
❌ Profile loading failed: my_profile
```

**Solutions**:
- ✅ Verify profile file exists in `profiles/` directory
- ✅ Check profile JSON syntax is valid
- ✅ Ensure profile name in `.env` matches exactly
- ✅ Run profile validation: `python -c "from mods.config.profile_manager import ProfileManager; pm = ProfileManager('profiles'); print(pm.get_profile('my_profile'))"`

**Issue**: OpenSelf not working
```
🧠 OpenSelf integration: DISABLED
```

**Solutions**:
- ✅ Profile must have `openself_analysis` section
- ✅ Include chat history during profile creation
- ✅ Check OpenSelf logs for specific errors
- ✅ Verify all OpenSelf components are installed

### Performance Issues

**Issue**: Slow responses
**Solutions**:
- ✅ Switch to faster AI model (gpt-3.5-turbo instead of gpt-4)
- ✅ Reduce `MAX_TOKENS` in `.env`
- ✅ Check API rate limits
- ✅ Monitor system resources

**Issue**: High memory usage
**Solutions**:
- ✅ Restart bot periodically
- ✅ Reduce profile complexity
- ✅ Monitor with `htop` or Task Manager

### Common Errors

**Error**: `ModuleNotFoundError: No module named 'discord'`
```
pip install -r requirements.txt
```

**Error**: `KeyError: 'DISCORD_SELF_TOKEN'`
```
# Check .env file exists and has correct format
# Ensure no extra spaces or quotes
```

**Error**: `ConnectionResetError`
```
# Check internet connection
# Verify Discord service status
# Try restarting the bot
```

---

## Production Deployment

### VPS/Cloud Deployment

#### Using Docker (Recommended)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN mkdir -p logs

CMD ["python", "main.py"]
```

```bash
# Build and run
docker build -t cloneme-bot .
docker run -d --env-file .env cloneme-bot
```

#### Direct VPS Setup
```bash
# On Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip
git clone <repository-url>
cd cloneme-master
pip install -r requirements.txt

# Create systemd service
sudo nano /etc/systemd/system/cloneme.service
```

```ini
[Unit]
Description=CloneMe Discord Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/cloneme-master
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable cloneme
sudo systemctl start cloneme
sudo systemctl status cloneme
```

### Monitoring

#### Health Checks
```bash
# Check if bot is running
ps aux | grep python

# Check Discord connection
curl -s https://discord.com/api/v10/gateway | head -n 5

# Monitor logs
tail -f logs/cloneme.log
```

#### Log Rotation
```bash
# Configure logrotate
sudo nano /etc/logrotate.d/cloneme
```

```
/path/to/cloneme-master/logs/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

### Security Best Practices

1. **Environment Variables**:
   - Never commit `.env` to version control
   - Use different tokens for development/production
   - Rotate API keys regularly

2. **Bot Permissions**:
   - Grant minimal required Discord permissions
   - Avoid administrator privileges
   - Regularly audit bot permissions

3. **Network Security**:
   - Use firewalls to restrict bot access
   - Monitor for unusual activity
   - Keep dependencies updated

---

## 📞 Support and Resources

### Getting Help

1. **Check Logs**: Always check `logs/` directory first
2. **Validate Setup**: Run `python scripts/setup.py`
3. **Test Components**: Use the testing scripts above
4. **Community**: Check project issues and discussions

### Useful Commands

```bash
# Quick status check
python -c "import os; print('✅ .env exists' if os.path.exists('.env') else '❌ .env missing')"

# Validate profile
python -c "from mods.config.profile_manager import ProfileManager; pm = ProfileManager('profiles'); p = pm.get_profile('default'); print(f'Profile: {p.name if p else \"INVALID\"}')"

# Test OpenSelf
python -c "from mods.openself_integration import OpenSelfIntegration; oi = OpenSelfIntegration(); print('✅ OpenSelf ready' if oi else '❌ OpenSelf failed')"

# Check dependencies
python -c "import discord, langchain, openai; print('✅ All imports successful')"
```

### File Structure Reference

```
cloneme-master/
├── main.py                 # Main bot entry point
├── requirements.txt        # Python dependencies
├── .env                    # Environment configuration
├── scripts/
│   └── setup.py           # Setup verification script
├── mods/                  # Core modules
│   ├── config/            # Configuration management
│   ├── agent/             # AI response generation
│   ├── openself_integration.py  # Personality analysis
│   └── platform/          # Platform integrations
├── profiles/              # User personality profiles
├── logs/                  # Application logs
└── README.md             # This file
```

---

## 🎯 Success Checklist

- [ ] Python 3.11.6+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` configured with real API keys
- [ ] Discord bot created and token obtained
- [ ] Bot invited to Discord server with proper permissions
- [ ] Profile created (default or custom)
- [ ] Bot starts without errors (`python main.py`)
- [ ] Bot responds to mentions in Discord
- [ ] OpenSelf integration working (if enabled)
- [ ] Responses match personality configuration

---

## 📝 Changelog

### Version 1.0.0 (May 2026)
- Initial release with OpenSelf integration
- Support for multiple AI providers
- Enhanced personality profiling
- Discord platform integration
- Comprehensive logging and monitoring

---

**Happy cloning! 🤖✨**

For more information, visit the project repository or check the inline code documentation.