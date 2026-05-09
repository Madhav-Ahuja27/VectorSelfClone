from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field, ValidationError

from mods.llm import AIRouter

ROOT_DIR = Path(__file__).resolve().parent
CURRENT_NODE_FILE = ROOT_DIR / "CurrentNode.json"
TARGET_NODE_FILE = ROOT_DIR / "TargetNode.json"


class SkillTarget(BaseModel):
    name: str = Field(..., min_length=1)
    desired_proficiency: str = Field(..., min_length=1)

    model_config = {"extra": "forbid"}


class TargetState(BaseModel):
    target_identity: str = Field(..., min_length=1)
    target_skills: List[SkillTarget] = Field(..., min_length=1)
    desired_mindset: str = Field(..., min_length=1)

    model_config = {"extra": "forbid"}


class DeltaSkill(BaseModel):
    skill: str = Field(..., min_length=1)
    current_level: Optional[str]
    target_level: str = Field(..., min_length=1)
    explanation: str = Field(..., min_length=1, description="Why this skill is important for the transformation")
    recommended_actions: List[str] = Field(..., min_length=1)

    model_config = {"extra": "forbid"}


class DeltaRoadmap(BaseModel):
    summary: str = Field(..., min_length=1)
    overall_reasoning: str = Field(..., min_length=1, description="High-level reasoning for the development approach")
    mindset_shifts: List[str] = Field(..., min_length=1)
    mindset_reasoning: str = Field(..., min_length=1, description="Explanation of why these mindset shifts are critical")
    habit_changes: List[str] = Field(..., min_length=1)
    habit_reasoning: str = Field(..., min_length=1, description="Explanation of how these habits support the transformation")
    skill_recommendations: List[DeltaSkill] = Field(..., min_length=1)

    model_config = {"extra": "forbid"}


class GapAnalyzerState(BaseModel):
    current_node: Dict[str, Any]
    target_node: TargetState
    delta_roadmap: Optional[DeltaRoadmap] = None

    model_config = {"extra": "forbid"}


class GapAnalyzer:
    def __init__(self, provider_name: Optional[str] = None, api_key: Optional[str] = None, model: Optional[str] = None):
        provider_name = provider_name or os.getenv("AI_PROVIDER")
        api_key = api_key or os.getenv("AI_API_KEY")
        model = model or os.getenv("AI_MODEL")

        if not provider_name or not api_key or not model:
            raise ValueError("AI_PROVIDER, AI_API_KEY, and AI_MODEL must be set in environment variables or passed explicitly.")

        self.router = AIRouter()
        self.llm = self.router.get_provider(provider_name.lower(), api_key, model, temperature=0.3, max_tokens=1200)

    def load_current_node(self) -> Dict[str, Any]:
        if not CURRENT_NODE_FILE.exists():
            raise FileNotFoundError(f"Current node file not found: {CURRENT_NODE_FILE}")

        with open(CURRENT_NODE_FILE, "r", encoding="utf-8") as stream:
            return json.load(stream)

    def load_target_node(self) -> TargetState:
        if not TARGET_NODE_FILE.exists():
            raise FileNotFoundError(f"Target node file not found: {TARGET_NODE_FILE}")

        with open(TARGET_NODE_FILE, "r", encoding="utf-8") as stream:
            payload = json.load(stream)

        if isinstance(payload, dict):
            return TargetState.model_validate(payload)
        raise ValueError("TargetNode.json must contain an object matching TargetState.")

    def build_prompt(self, current_node: Dict[str, Any], target_node: TargetState) -> str:
        current_content = json.dumps(current_node, indent=2)
        target_content = json.dumps(target_node.model_dump(), indent=2)

        return (
            '<system_directive>'
            'You are the Gap Analyzer Agent. Your role is to conduct a thorough psychological and skill gap analysis, '
            'comparing the current personality and capability state with the desired future state. '
            'Provide detailed, nuanced, and actionable recommendations with clear reasoning and explanations for each recommendation. '
            'Think deeply about the psychological shifts required, the habit patterns needed, and the skill development path.'
            '</system_directive>\n'
            f'<current_state>{current_content}</current_state>\n'
            f'<target_state>{target_content}</target_state>\n'
            '<instructions>'
            'Conduct a detailed gap analysis by:\n'
            '1. Comparing personality traits between current and target states\n'
            '2. Identifying psychological shifts required for the transformation\n'
            '3. Determining which habits need to change and why\n'
            '4. Mapping skill gaps and prioritizing development areas\n'
            '5. Providing specific, actionable steps for each recommendation\n\n'
            'Output ONLY a JSON object (no code fences, no markdown, no extra text) with this exact structure:\n'
            '{\n'
            '  "summary": "Comprehensive overview of the transformation journey from current to target identity",\n'
            '  "overall_reasoning": "Detailed explanation of the development strategy and why this approach will work",\n'
            '  "mindset_shifts": ["shift1: detailed description", "shift2: detailed description"],\n'
            '  "mindset_reasoning": "Explain why these specific mindset shifts are foundational to the transformation",\n'
            '  "habit_changes": ["habit1: specific change description", "habit2: specific change description"],\n'
            '  "habit_reasoning": "Explain how these new habits will reinforce the desired identity and mindset",\n'
            '  "skill_recommendations": [\n'
            '    {\n'
            '      "skill": "specific skill name",\n'
            '      "current_level": "current proficiency or null",\n'
            '      "target_level": "target proficiency",\n'
            '      "explanation": "Why this skill is critical for achieving the target identity",\n'
            '      "recommended_actions": ["Action 1: with detail", "Action 2: with detail", "Action 3: with detail"]\n'
            '    }\n'
            '  ]\n'
            '}\n\n'
            'GUARD RAILS:\n'
            '- Ensure all recommendations are specific and actionable (avoid vague statements)\n'
            '- Provide reasoning for each section\n'
            '- Skills should be prioritized by impact on achieving the target identity\n'
            '- Mindset shifts should be psychological and transformative\n'
            '- Habits should be concrete and measurable\n'
            '- Each recommended action should include the "why" and "how"'
            '</instructions>'
        )

    def analyze(self) -> DeltaRoadmap:
        current_node = self.load_current_node()
        target_node = self.load_target_node()
        prompt = self.build_prompt(current_node, target_node)

        messages = [
            SystemMessage(content="You are the Gap Analyzer Agent. Provide a structured development roadmap."),
            HumanMessage(content=prompt),
        ]

        response = self.llm.invoke(messages)
        raw_text = response.content if hasattr(response, "content") else str(response)

        try:
            parsed = self._parse_json_from_text(raw_text)
            # Try to transform the response into DeltaRoadmap if it has a different structure
            roadmap = self._transform_to_delta_roadmap(parsed)
            return roadmap
        except (ValueError, json.JSONDecodeError) as e:
            error_msg = f"Failed to parse LLM response: {str(e)}\n\nRaw response:\n{raw_text[:500]}"
            raise ValueError(error_msg) from e

    def _transform_to_delta_roadmap(self, data: Dict[str, Any]) -> DeltaRoadmap:
        """Transform various response formats into DeltaRoadmap."""
        # If it already has the correct structure, validate and return
        if all(k in data for k in ["summary", "overall_reasoning", "mindset_shifts", "mindset_reasoning", 
                                     "habit_changes", "habit_reasoning", "skill_recommendations"]):
            return DeltaRoadmap.model_validate(data)

        # Otherwise, transform from alternative structures
        summary = data.get("summary", "Development roadmap generated")
        overall_reasoning = data.get("overall_reasoning", "Strategic approach to bridge the gap between current and target states")
        
        # Extract mindset shifts
        mindset_shifts = []
        if "mindset_shifts" in data:
            mindset_shifts = data["mindset_shifts"]
        elif "mindset_deltas" in data:
            mindset_shifts = [d.get("mindset", "") for d in data["mindset_deltas"] if isinstance(d, dict)]
        elif "psychological_deltas" in data:
            mindset_shifts = [d.get("shift", d.get("trait", "")) for d in data["psychological_deltas"] if isinstance(d, dict)]
        mindset_shifts = [s for s in mindset_shifts if s]  # Filter empty strings
        if not mindset_shifts:
            mindset_shifts = ["Develop growth mindset", "Embrace continuous learning"]
        
        mindset_reasoning = data.get("mindset_reasoning", "These mindset shifts form the psychological foundation for sustainable transformation")
        
        # Extract habit changes
        habit_changes = []
        if "habit_changes" in data:
            habit_changes = data["habit_changes"]
        elif "mindset_deltas" in data:
            habit_changes = [d.get("recommended_action", "") for d in data["mindset_deltas"] if isinstance(d, dict) and "recommended_action" in d]
        if not habit_changes:
            habit_changes = ["Practice daily reflection", "Track progress consistently"]
        
        habit_reasoning = data.get("habit_reasoning", "These habits create consistency and reinforce the desired identity through daily practice")
        
        # Extract skill recommendations
        skill_recommendations = []
        if "skill_recommendations" in data:
            skill_recommendations = data["skill_recommendations"]
        elif "skill_deltas" in data:
            for skill_delta in data["skill_deltas"]:
                if isinstance(skill_delta, dict):
                    skill_recommendations.append(
                        {
                            "skill": skill_delta.get("skill", ""),
                            "current_level": skill_delta.get("current_level"),
                            "target_level": skill_delta.get("target_level", ""),
                            "explanation": skill_delta.get("explanation", skill_delta.get("why", "Essential for target achievement")),
                            "recommended_actions": skill_delta.get("recommended_actions", []),
                        }
                    )
        
        if not skill_recommendations:
            skill_recommendations = [
                {
                    "skill": "Self-awareness",
                    "current_level": "Developing",
                    "target_level": "Advanced",
                    "explanation": "Self-awareness is the foundation for all other transformations",
                    "recommended_actions": ["Reflect daily", "Seek feedback"],
                }
            ]
        
        # Ensure all skills have explanations
        for skill in skill_recommendations:
            if "explanation" not in skill or not skill["explanation"]:
                skill["explanation"] = f"Important for developing {skill.get('skill', 'this skill')}"
        
        # Create and validate the transformed roadmap
        transformed = {
            "summary": summary,
            "overall_reasoning": overall_reasoning,
            "mindset_shifts": mindset_shifts,
            "mindset_reasoning": mindset_reasoning,
            "habit_changes": habit_changes,
            "habit_reasoning": habit_reasoning,
            "skill_recommendations": skill_recommendations,
        }
        
        return DeltaRoadmap.model_validate(transformed)

    def _parse_json_from_text(self, text: str) -> Dict[str, Any]:
        cleaned = self._strip_code_fences(text)
        json_text = self._extract_first_json_object(cleaned)
        return json.loads(json_text)

    @staticmethod
    def _strip_code_fences(text: str) -> str:
        return re.sub(r"```(?:json)?\n(.*?)```", lambda m: m.group(1), text, flags=re.S | re.I)

    @staticmethod
    def _extract_first_json_object(text: str) -> str:
        # Remove leading/trailing whitespace and common markdown markers
        text = text.strip()
        if text.startswith("```"):
            text = text[3:]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
        
        start = text.find("{")
        if start == -1:
            raise ValueError("No JSON object found in LLM response.")

        depth = 0
        in_string = False
        escape = False
        for index, char in enumerate(text[start:], start):
            if in_string:
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == '"':
                    in_string = False
            else:
                if char == '"':
                    in_string = True
                elif char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0:
                        return text[start : index + 1]

        raise ValueError("Could not parse JSON object from LLM response. Unmatched braces or unclosed string.")
