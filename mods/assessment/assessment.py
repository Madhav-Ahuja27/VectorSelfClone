import json
import os
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from mods.config import ProfileManager

ROOT_DIR = Path(__file__).resolve().parents[2]
FIVE_FACTOR_E_DIR = ROOT_DIR / "five-factor-e-main" / "five-factor-e-main"
QUESTION_FILE = FIVE_FACTOR_E_DIR / "data" / "IPIP-NEO" / "120" / "questions.json"
PERSONALITY_PROFILE_JSON = ROOT_DIR / "personality_profile.json"
SOUL_MD_FILE = ROOT_DIR / "SOUL.md"
CURRENT_NODE_FILE = ROOT_DIR / "CurrentNode.json"


def _load_ipipneo_class():
    try:
        from ipipneo.ipipneo import IpipNeo
        return IpipNeo
    except ModuleNotFoundError:
        sys.path.insert(0, str(FIVE_FACTOR_E_DIR))
        from ipipneo.ipipneo import IpipNeo
        return IpipNeo


class AssessmentModule:
    """Local assessment module using IPIP-NEO-120 and profile generation."""

    def __init__(self, profile_manager: Optional[ProfileManager] = None):
        self.profile_manager = profile_manager or ProfileManager(profiles_directory=Path.cwd())
        self._ipipneo_class = _load_ipipneo_class()

    def load_questions(self) -> List[Dict[str, Any]]:
        if not QUESTION_FILE.exists():
            raise FileNotFoundError(f"IPIP-NEO question file not found at {QUESTION_FILE}")

        with open(QUESTION_FILE, "r", encoding="utf-8") as stream:
            payload = json.load(stream)

        return payload.get("questions", [])

    def ask_questions_interactive(self, shuffle: bool = False) -> List[Dict[str, int]]:
        questions = self.load_questions()
        if not questions:
            raise ValueError("No assessment questions were loaded.")

        if shuffle:
            random.shuffle(questions)

        answers: List[Dict[str, int]] = []

        print("\nStarting IPIP-NEO 120 assessment. Answer each question using a value from 1 to 5.")
        print("1 = Strongly Disagree, 5 = Strongly Agree\n")

        for index, question in enumerate(questions, start=1):
            while True:
                prompt = f"Q{index:03d} ({question.get('id')}): {question.get('text')}\nYour answer [1-5]: "
                choice = input(prompt).strip()
                if choice in {"1", "2", "3", "4", "5"}:
                    answers.append({"id_question": int(question.get("id", index)), "id_select": int(choice)})
                    break
                print("Invalid answer. Please enter a number between 1 and 5.")

        return answers

    def load_answers_file(self, answers_file: str) -> List[Dict[str, int]]:
        target_path = Path(answers_file)
        if not target_path.exists():
            raise FileNotFoundError(f"Answers file not found: {answers_file}")

        with open(target_path, "r", encoding="utf-8") as stream:
            payload = json.load(stream)

        if not isinstance(payload, dict) or "answers" not in payload:
            raise ValueError("Answers file must be a JSON object containing an 'answers' list.")

        return payload["answers"]

    def score_answers(self, sex: str, age: int, answers: List[Dict[str, int]]) -> Dict[str, Any]:
        sex = str(sex).strip().upper() if sex else "N"
        age = int(age)

        answers_payload = {"answers": answers}
        return self._ipipneo_class(question=120).compute(
            sex=sex,
            age=age,
            answers=answers_payload,
            compare=True,
        )

    def _normalize_list_value(self, value: Any) -> Any:
        if value is None:
            return ""
        if isinstance(value, bool):
            return str(value)
        return value

    def _describe_big5_trait(self, trait_name: str, trait_data: Dict[str, Any]) -> str:
        label = trait_data.get("score") or trait_data.get("label") or trait_data.get("status")
        label_text = str(label).title() if label else "Unknown"
        description = f"{label_text} {trait_name.capitalize()} with {len(trait_data.get('traits', []))} related facets."

        if trait_name.lower() == "openness":
            if label == "high":
                description = "Curious, imaginative, and comfortable with novel ideas."
            elif label == "low":
                description = "Practical, conventional, and focused on familiar experiences."
        elif trait_name.lower() == "conscientiousness":
            if label == "high":
                description = "Organized, dependable, and goal-directed."
            elif label == "low":
                description = "Flexible, spontaneous, and comfortable with ambiguity."
        elif trait_name.lower() == "extraversion":
            if label == "high":
                description = "Sociable, energetic, and comfortable taking initiative."
            elif label == "low":
                description = "Reserved, introspective, and thoughtful in social settings."
        elif trait_name.lower() == "agreeableness":
            if label == "high":
                description = "Cooperative, compassionate, and concerned about others."
            elif label == "low":
                description = "Direct, independent, and comfortable challenging ideas."
        elif trait_name.lower() == "neuroticism":
            if label == "high":
                description = "Emotionally sensitive and aware of potential stressors."
            elif label == "low":
                description = "Emotionally stable and calm under pressure."

        return description

    def _build_profile_config(
        self,
        result: Dict[str, Any],
        user_info: Dict[str, Any],
        answers: List[Dict[str, int]],
    ) -> Dict[str, Any]:
        user_info = {**user_info}
        username = str(user_info.get("username") or user_info.get("user_name") or "assessment_user").strip() or "assessment_user"
        name = str(user_info.get("name") or user_info.get("full_name") or username).strip() or username
        age = int(user_info.get("age", 30))
        gender = str(user_info.get("sex") or user_info.get("gender") or user_info.get("sex_at_birth") or "N").strip()

        personalities = result.get("person", {}).get("result", {}).get("personalities", [])
        trait_descriptions = {}
        big5_summary = {}

        for personality in personalities:
            if not isinstance(personality, dict):
                continue
            for trait_name, trait_data in personality.items():
                big5_summary[trait_name] = {
                    "score": trait_data.get("score"),
                    "level": trait_data.get("score"),
                    "facets": trait_data.get("traits", []),
                }
                trait_descriptions[trait_name.capitalize()] = self._describe_big5_trait(trait_name, trait_data)

        extraversion_level = big5_summary.get("extraversion", {}).get("level", "average")
        agreeableness_level = big5_summary.get("agreeableness", {}).get("level", "average")

        if extraversion_level == "high":
            tone = "Warm, energetic, and engaging."
        elif extraversion_level == "low":
            tone = "Calm, reflective, and gentle."
        else:
            tone = "Balanced, attentive, and thoughtful."

        if agreeableness_level == "low":
            tone += " Communicative style may be direct and honest."
        elif agreeableness_level == "high":
            tone += " Communicative style is kind and cooperative."

        profile_config = {
            "required": {
                "username": username,
                "name": name,
            },
            "basic_info": {
                "Age": str(age),
                "Gender": gender,
            },
            "personality_traits": trait_descriptions,
            "response_styles": {
                "Preferred Tone": tone,
                "Empathy Level": "Adapt responses to maintain warmth and clarity.",
                "Pacing": "Keep responses concise and thoughtful unless more detail is requested.",
            },
            "knowledge_and_expertise": {
                "Assessment Method": "IPIP-NEO 120 question personality inventory",
                "Use Case": "Persona generation for AI response style and relationship modeling.",
            },
            "relationships": {
                "Personalization Approach": "Use personality profile and preferences to make recommendations more relevant.",
            },
            "sample_conversations": [
                {
                    "user": "Hello, can you tell me something about my personality?",
                    "ai": "Based on your assessment, you tend to be curious, thoughtful, and balanced. I can keep the tone warm and supportive while staying focused."
                }
            ],
            "off_topic_message": {
                "reply": False,
                "guidance": "If conversation becomes inappropriate or off-topic, answer politely but steer back to meaningful, helpful dialogue."
            },
            "questionnaire": {
                "answers": {
                    "question_set": 120,
                    "responses": answers,
                },
                "summary": {
                    "model": "IPIP-NEO",
                    "question_set": 120,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                },
                "big5_scores": big5_summary,
            },
            "assessment_metadata": {
                "model": "IPIP-NEO",
                "version": result.get("version"),
                "sex": result.get("person", {}).get("sex"),
                "age": result.get("person", {}).get("age"),
            },
        }

        if user_info.get("occupation"):
            profile_config["basic_info"]["Occupation"] = str(user_info["occupation"])

        if user_info.get("interests"):
            profile_config["basic_info"]["Interests"] = str(user_info["interests"])

        return profile_config

    def create_profile_from_result(
        self,
        profile_name: str,
        result: Dict[str, Any],
        user_info: Dict[str, Any],
        answers: List[Dict[str, int]],
        file_path: Optional[str] = None,
    ) -> Any:
        config_data = self._build_profile_config(result=result, user_info=user_info, answers=answers)
        return self.profile_manager.create_profile(profile_name=profile_name, config_data=config_data, file_path=file_path)

    def generate_soul_md(self, profile_name: str, result: Dict[str, Any], user_info: Dict[str, Any]) -> Path:
        personalities = result.get("person", {}).get("result", {}).get("personalities", [])
        intro = [
            f"# SOUL Profile for {user_info.get('name', profile_name)}",
            "",
            f"Generated from a local IPIP-NEO 120-question assessment on {datetime.now(timezone.utc).date()}",
            "",
            "## Personality Summary",
        ]

        for personality in personalities:
            if not isinstance(personality, dict):
                continue
            for trait_name, trait_data in personality.items():
                score_label = trait_data.get("score") or "Unknown"
                intro.append(f"- **{trait_name.capitalize()}**: {score_label.title()}")

        intro.extend([
            "",
            "## Persona Recommendations",
            "- Use this profile to guide tone, engagement pace, and recommendation style.",
            "- Showcase empathy and honesty when neuroticism is higher, and keep suggestions grounded when openness is lower.",
            "- In conversations, reference the user's curiosity, personal preferences, and communication needs.",
        ])

        SOUL_MD_FILE.write_text("\n".join(intro), encoding="utf-8")
        return SOUL_MD_FILE

    def save_personality_profile_json(
        self,
        profile_name: str,
        result: Dict[str, Any],
        profile_config: Dict[str, Any],
        user_info: Dict[str, Any],
    ) -> Path:
        payload = {
            "profile_name": profile_name,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "assessment_model": "IPIP-NEO",
            "question_set": 120,
            "user_info": {
                "username": user_info.get("username"),
                "name": user_info.get("name"),
                "age": user_info.get("age"),
                "gender": user_info.get("sex"),
            },
            "result": result,
            "profile": profile_config,
        }

        PERSONALITY_PROFILE_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return PERSONALITY_PROFILE_JSON

    def generate_current_node(self, profile_name: str, profile_config: Dict[str, Any]) -> Path:
        current_node = {
            "node_id": "personality_profile",
            "type": "personality_profile",
            "title": "IPIP-NEO 120 Personality Profile",
            "summary": f"Personality profile generated from a local IPIP-NEO 120 assessment for {profile_name}.",
            "source": str(PERSONALITY_PROFILE_JSON.name),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metadata": {
                "username": profile_config.get("required", {}).get("username"),
                "big5_scores": profile_config.get("questionnaire", {}).get("big5_scores", {}),
            },
        }
        CURRENT_NODE_FILE.write_text(json.dumps(current_node, indent=2, ensure_ascii=False), encoding="utf-8")
        return CURRENT_NODE_FILE

    def run(
        self,
        profile_name: Optional[str] = None,
        user_info: Optional[Dict[str, Any]] = None,
        answers_file: Optional[str] = None,
        answers: Optional[List[Dict[str, int]]] = None,
        shuffle: bool = False,
        save_profile_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        user_info = user_info or {}
        profile_name = profile_name or f"{user_info.get('username', 'assessment')}_profile"

        if answers is not None:
            assessment_answers = answers
        elif answers_file:
            assessment_answers = self.load_answers_file(answers_file)
        else:
            assessment_answers = self.ask_questions_interactive(shuffle=shuffle)

        sex = str(user_info.get("sex") or user_info.get("gender") or "N").strip().upper()
        age = int(user_info.get("age", 30))

        result = self.score_answers(sex=sex, age=age, answers=assessment_answers)
        profile = self.create_profile_from_result(
            profile_name=profile_name,
            result=result,
            user_info=user_info,
            answers=assessment_answers,
            file_path=save_profile_path,
        )

        self.save_personality_profile_json(
            profile_name=profile_name,
            result=result,
            profile_config=profile.config_data,
            user_info=user_info,
        )
        self.generate_soul_md(profile_name=profile_name, result=result, user_info=user_info)
        self.generate_current_node(profile_name=profile_name, profile_config=profile.config_data)

        print(f"\nCreated profile: {profile.profile_name}")
        print(f"Saved profile file: {profile.source_file}")
        print(f"Saved personality file: {PERSONALITY_PROFILE_JSON}")
        print(f"Saved SOUL profile: {SOUL_MD_FILE}")
        print(f"Saved current node: {CURRENT_NODE_FILE}\n")

        return {
            "profile": profile,
            "personality_profile_json": str(PERSONALITY_PROFILE_JSON),
            "soul_md": str(SOUL_MD_FILE),
            "current_node": str(CURRENT_NODE_FILE),
        }
