from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path

from .profile_manager import ProfileManager
from .profile import Profile

# Import OpenSelf integration
try:
    from ..openself_integration import OpenSelfIntegration
except ImportError:
    OpenSelfIntegration = None


class ProfileIntakePipeline:
    """Pipeline for ingesting questionnaire answers into AI profiles."""

    def __init__(self, profile_manager: ProfileManager):
        self.profile_manager = profile_manager
        self.schema = profile_manager.schema
        # Initialize OpenSelf integration if available
        self.openself = OpenSelfIntegration() if OpenSelfIntegration else None

    def create_profile_from_questionnaire(
        self,
        profile_name: str,
        answers: Union[Dict[str, Any], List[Tuple[str, Any]]],
        base_profile_name: Optional[str] = None,
        file_path: Optional[Union[str, Path]] = None,
    ) -> Profile:
        """Create a new profile from questionnaire answers, optionally merging with an existing profile."""
        answer_map = self._normalize_answers(answers)
        source_data = self._build_profile_config(answer_map)

        if base_profile_name:
            base_profile = self.profile_manager.get_profile(base_profile_name)
            if base_profile:
                merged_config = self._deep_merge(base_profile.config_data, source_data)
                return self.profile_manager.create_profile(profile_name, merged_config, file_path)

        return self.profile_manager.create_profile(profile_name, source_data, file_path)

    def merge_questionnaire_into_profile(
        self,
        profile: Profile,
        answers: Union[Dict[str, Any], List[Tuple[str, Any]]],
        save: bool = False,
        file_path: Optional[Union[str, Path]] = None,
    ) -> Profile:
        """Merge questionnaire answers into an existing Profile object."""
        answer_map = self._normalize_answers(answers)
        source_data = self._build_profile_config(answer_map)
        merged_config = self._deep_merge(profile.config_data, source_data)
        merged_profile = Profile(profile_name=profile.profile_name, config_data=merged_config, schema=self.schema)

        if save:
            self.profile_manager.save_profile(merged_profile, file_path or profile.source_file)

        return merged_profile

    def create_profile_from_questionnaire_and_chat(
        self,
        profile_name: str,
        answers: Union[Dict[str, Any], List[Tuple[str, Any]]],
        chat_messages: Optional[List[str]] = None,
        user_info: Optional[Dict[str, Any]] = None,
        base_profile_name: Optional[str] = None,
        file_path: Optional[Union[str, Path]] = None,
    ) -> Profile:
        """
        Create a profile from questionnaire answers and optionally enhance with chat analysis.

        Args:
            profile_name: Name for the new profile
            answers: Questionnaire answers
            chat_messages: Optional list of chat messages for personality analysis
            user_info: Optional user information for OpenSelf analysis
            base_profile_name: Optional base profile to merge with
            file_path: Optional file path to save to

        Returns:
            Enhanced Profile instance
        """
        # First create profile from questionnaire
        answer_map = self._normalize_answers(answers)
        questionnaire_config = self._build_profile_config(answer_map)

        # Add OpenSelf analysis if available and chat messages provided
        openself_data = {}
        if self.openself and chat_messages:
            try:
                openself_result = self.openself.analyze_personality_from_messages(
                    chat_messages, user_info or {}
                )
                openself_data = {
                    'personality_analysis': openself_result.get('personality', {}),
                    'vocabulary_fingerprint': openself_result.get('fingerprint', {}),
                    'soul_profile': openself_result.get('soul_profile', ''),
                    'message_count': openself_result.get('message_count', 0),
                    'analysis_timestamp': openself_result.get('analysis_timestamp'),
                }
            except Exception as e:
                # Log error but don't fail profile creation
                print(f"Warning: OpenSelf analysis failed: {e}")
                openself_data = {'error': str(e)}

        # Merge OpenSelf data into profile config
        if openself_data:
            questionnaire_config['openself_analysis'] = openself_data

        # Merge with base profile if specified
        if base_profile_name:
            base_profile = self.profile_manager.get_profile(base_profile_name)
            if base_profile:
                merged_config = self._deep_merge(base_profile.config_data, questionnaire_config)
                return self.profile_manager.create_profile(profile_name, merged_config, file_path)

        return self.profile_manager.create_profile(profile_name, questionnaire_config, file_path)

    def enhance_profile_with_chat_analysis(
        self,
        profile: Profile,
        chat_messages: List[str],
        user_info: Optional[Dict[str, Any]] = None,
        save: bool = False,
        file_path: Optional[Union[str, Path]] = None,
    ) -> Profile:
        """
        Enhance an existing profile with OpenSelf chat analysis.

        Args:
            profile: Existing profile to enhance
            chat_messages: Chat messages for analysis
            user_info: Optional user information
            save: Whether to save the enhanced profile
            file_path: Optional save path

        Returns:
            Enhanced Profile instance
        """
        if not self.openself:
            return profile

        try:
            openself_result = self.openself.analyze_personality_from_messages(
                chat_messages, user_info or {}
            )

            openself_data = {
                'personality_analysis': openself_result.get('personality', {}),
                'vocabulary_fingerprint': openself_result.get('fingerprint', {}),
                'soul_profile': openself_result.get('soul_profile', ''),
                'message_count': openself_result.get('message_count', 0),
                'analysis_timestamp': openself_result.get('analysis_timestamp'),
            }

            # Merge OpenSelf data into existing profile
            enhanced_config = dict(profile.config_data)
            enhanced_config['openself_analysis'] = openself_data

            enhanced_profile = Profile(
                profile_name=profile.profile_name,
                config_data=enhanced_config,
                schema=self.schema,
                source_file=profile.source_file
            )

            if save:
                self.profile_manager.save_profile(
                    enhanced_profile,
                    file_path or profile.source_file
                )

            return enhanced_profile

        except Exception as e:
            print(f"Warning: Failed to enhance profile with chat analysis: {e}")
            return profile

    def _normalize_answers(
        self,
        answers: Union[Dict[str, Any], List[Tuple[str, Any]]],
    ) -> Dict[str, Any]:
        if isinstance(answers, list):
            normalized: Dict[str, Any] = {}
            for item in answers:
                if not isinstance(item, (list, tuple)) or len(item) != 2:
                    raise ValueError("Answer list items must be 2-element tuples or lists")
                normalized[str(item[0]).strip()] = item[1]
            return normalized

        if not isinstance(answers, dict):
            raise TypeError("Questionnaire answers must be a dict or list of tuples")

        return {str(key).strip(): value for key, value in answers.items()}

    def _build_profile_config(self, answers: Dict[str, Any]) -> Dict[str, Any]:
        """Build profile config data from normalized questionnaire answers."""
        questionnaire: Dict[str, Any] = {}
        basic_info: Dict[str, Any] = {}
        personality_traits: Dict[str, Any] = {}
        response_styles: Dict[str, Any] = {}
        knowledge_and_expertise: Dict[str, Any] = {}
        relationships: Dict[str, Any] = {}
        strengths: List[str] = []
        weaknesses: List[str] = []
        preferences: Dict[str, Any] = {}

        for question, answer in answers.items():
            parsed_answer = self._normalize_answer(answer)
            normalized_question = question.strip()
            questionnaire[normalized_question] = parsed_answer
            lower_question = normalized_question.lower()

            if "strength" in lower_question and "weakness" not in lower_question:
                strengths.append(str(parsed_answer))
            elif "weakness" in lower_question:
                weaknesses.append(str(parsed_answer))
            elif any(term in lower_question for term in ["preference", "favorite", "likes", "dislikes", "prefer"]):
                preferences[normalized_question] = parsed_answer

            section = self._guess_profile_section(lower_question)
            if section == "basic_info":
                basic_info[normalized_question] = parsed_answer
            elif section == "personality_traits":
                personality_traits[normalized_question] = parsed_answer
            elif section == "response_styles":
                response_styles[normalized_question] = parsed_answer
            elif section == "knowledge_and_expertise":
                knowledge_and_expertise[normalized_question] = parsed_answer
            elif section == "relationships":
                relationships[normalized_question] = parsed_answer

        # Derive required fields from answers or create safe defaults.
        username = self._find_first_matching_answer(answers, ["username", "user name", "display name"])
        name = self._find_first_matching_answer(answers, ["name", "full name", "your name"])
        username = username or self._find_first_matching_answer(answers, ["email", "handle"]) or "user"
        name = name or username or "Unnamed User"

        profile_config: Dict[str, Any] = {
            "required": {
                "username": username,
                "name": name,
            },
            "basic_info": basic_info,
            "personality_traits": personality_traits,
            "response_styles": response_styles or {"casual": "Respond in a friendly, conversational manner"},
            "knowledge_and_expertise": knowledge_and_expertise,
            "relationships": relationships,
            "sample_conversations": [
                {"user": "Hello!", "ai": "Hi there! How can I help you today?"}
            ],
            "off_topic_message": {
                "reply": False,
                "guidance": "Do not respond to clearly inappropriate or off-topic content unless the overall conversation requires a safe, polite redirect."
            },
            "questionnaire": {
                "answers": questionnaire,
                "preferences": preferences,
                "strengths": strengths,
                "weaknesses": weaknesses,
            },
        }

        return profile_config

    def _guess_profile_section(self, question_text: str) -> Optional[str]:
        """Guess which profile section an answer belongs to based on the question text."""
        section_map = {
            "basic_info": ["name", "age", "gender", "occupation", "role", "location", "hometown", "job", "title"],
            "personality_traits": ["introvert", "extrovert", "personality", "temperament", "mood", "formality", "humor", "communication style", "style"],
            "response_styles": ["greeting", "question", "casual", "emoji", "slang", "tone", "phrasing", "word choice"],
            "knowledge_and_expertise": ["expertise", "skill", "strength", "weakness", "knowledge", "experience", "background", "training"],
            "relationships": ["friend", "relationship", "interaction", "conflict", "trust", "boundaries", "communication"]
        }

        for section, keywords in section_map.items():
            if any(keyword in question_text for keyword in keywords):
                return section

        return None

    def _find_first_matching_answer(self, answers: Dict[str, Any], keys: List[str]) -> Optional[str]:
        for candidate in keys:
            for question, answer in answers.items():
                if candidate in str(question).lower():
                    return self._normalize_answer(answer)
        return None

    def _normalize_answer(self, answer: Any) -> str:
        if answer is None:
            return ""
        if isinstance(answer, str):
            return answer.strip()
        try:
            return str(answer).strip()
        except Exception:
            return ""

    def _deep_merge(self, base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
        merged = {**base}
        for key, value in overlay.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged
