from mods.config import ProfileManager, SettingsManager
from mods.utils.logging_config import LoggingConfig
from pathlib import Path
import os, dotenv

dotenv.load_dotenv(
    Path(__file__).parent / ".env",
    override=True
)

platform_type = os.getenv("PLATFORM", "discord").lower()
print(f"🌐 Selected platform: {platform_type}")

profile_name = os.getenv("AI_PROFILE", "default")
profile_manager = ProfileManager(profiles_directory=Path.cwd())

if platform_type == "assessment":
    from mods.assessment.assessment import AssessmentModule

    assessment = AssessmentModule(profile_manager)
    assessment_profile_name = os.getenv("ASSESSMENT_PROFILE_NAME", profile_name or "assessment_profile")
    assessment_user_info = {
        "username": os.getenv("ASSESSMENT_USER_NAME", assessment_profile_name),
        "name": os.getenv("ASSESSMENT_USER_FULLNAME", assessment_profile_name),
        "sex": os.getenv("ASSESSMENT_USER_SEX", "N"),
        "age": int(os.getenv("ASSESSMENT_USER_AGE", "30")),
        "occupation": os.getenv("ASSESSMENT_USER_OCCUPATION", ""),
        "interests": os.getenv("ASSESSMENT_USER_INTERESTS", ""),
    }
    assessment_answers_file = os.getenv("ASSESSMENT_ANSWERS_FILE")
    assessment_shuffle = os.getenv("ASSESSMENT_SHUFFLE", "false").lower() in ("1", "true", "yes", "y")

    try:
        assessment.run(
            profile_name=assessment_profile_name,
            user_info=assessment_user_info,
            answers_file=assessment_answers_file,
            shuffle=assessment_shuffle,
        )
        print("✅ Assessment completed successfully. Generated personality files are available in the project root.")
    except Exception as e:
        print(f"❌ Assessment error: {e}")
        exit(1)

    exit(0)

provider = os.getenv("AI_PROVIDER")
if not provider:
    print("Error: AI_PROVIDER environment variable not found!")
    exit(1)

api_key = os.getenv("AI_API_KEY")
if not api_key:
    print("Error: AI_API_KEY environment variable not found!")
    exit(1)

model = os.getenv("AI_MODEL")
if not model:
    print("Error: AI_MODEL environment variable not found!")
    exit(1)

from mods.llm import AIRouter
llm = AIRouter().get_provider(provider, api_key, model)

print("📝 Initializing logging system...")
LoggingConfig.initialize_all_loggers()
active_loggers = LoggingConfig.list_active_loggers()
print(f"✅ Logging initialized with {len(active_loggers)} loggers: {', '.join(active_loggers.keys())}")

settings_manager = None
try:
    settings_manager = SettingsManager(
        settings_file="settings/settings.json",
        auto_create=True,
        watch_file=True
    )
    print("✅ Settings manager initialized successfully")
    if settings_manager.get('notifications.startup.show_config_status', True):
        print(f"⚙️  Settings loaded from: {settings_manager.settings_file}")
except Exception as e:
    print(f"⚠️  Failed to initialize settings manager: {e}")
    print("🔄 Continuing without settings manager...")

profile_manager = ProfileManager(profiles_directory=Path.cwd())
profile = None

try:
    profile = profile_manager.get_profile(profile_name)
    
    if not profile:
        available_profiles = profile_manager.list_profiles()
        print(f"🔍 Profile '{profile_name}' not found. Available profiles: {available_profiles}")
        
        variations = [
            f"{profile_name}_profile",
            profile_name.replace("_", "-"),
            profile_name.replace("-", "_")
        ]
        
        for variation in variations:
            if variation in available_profiles:
                profile = profile_manager.get_profile(variation)
                print(f"🔄 Found profile variant: {variation}")
                break
        
        if not profile and available_profiles:
            fallback_profile_name = available_profiles[0]
            profile = profile_manager.get_profile(fallback_profile_name)
            print(f"🔄 Using fallback profile: {fallback_profile_name}")
    
    if profile:
        print(f"✅ Loaded profile: {profile.profile_name} ({profile.username})")
        print(f"📝 Communication Style: {profile.get_communication_style()[:100]}...")
        print(f"🎭 Formality Level: {profile.get_formality_level()}")
        print(f"💬 Sample conversations: {len(profile.get_field('sample_conversations', []))}")
        print(f"🔧 Custom settings: {list(profile.get_custom_settings().keys())}")
    else:
        print("⚠️  No profiles found. Running without profile configuration.")
        
except Exception as e:
    print(f"⚠️  Error loading profile: {e}")
    print("🔄 Continuing without profile configuration...")
    import traceback
    traceback.print_exc()

platform_instance = None

if platform_type == "discord":
    from mods.platform.dcord import DiscordPlatform
    platform_instance = DiscordPlatform(
        discord_token=platform_token,
        llm=llm,
        profile=profile,
        settings_manager=settings_manager
    )
    print(f"✅ Discord platform initialized")
else:
    print(f"❌ Platform '{platform_type}' not implemented yet")
    exit(1)

try:
    print(f"🚀 Starting {platform_type} platform...")
    platform_instance.run_platform()
except KeyboardInterrupt:
    print("🛑 Shutting down...")
except Exception as e:
    print(f"❌ Error running {platform_type} platform: {e}")
    exit(1)