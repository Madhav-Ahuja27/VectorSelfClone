import json
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root to path so imports work
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st
from mods.assessment.assessment import AssessmentModule
from mods.config import ProfileManager
from agent_graph import GapAnalyzer, TargetState

PROFILE_MANAGER = ProfileManager(profiles_directory=Path.cwd())
ASSESSMENT_MODULE = AssessmentModule(profile_manager=PROFILE_MANAGER)
PROJECT_ROOT = Path.cwd()
TARGET_NODE_FILE = PROJECT_ROOT / "TargetNode.json"
CURRENT_NODE_FILE = PROJECT_ROOT / "CurrentNode.json"


def load_target_node() -> dict | None:
    if TARGET_NODE_FILE.exists():
        with open(TARGET_NODE_FILE, "r", encoding="utf-8") as stream:
            return json.load(stream)
    return None


def save_target_node(target_state: TargetState) -> Path:
    with open(TARGET_NODE_FILE, "w", encoding="utf-8") as stream:
        json.dump(target_state.model_dump(), stream, indent=2, ensure_ascii=False)
    return TARGET_NODE_FILE


def load_current_node() -> dict | None:
    if CURRENT_NODE_FILE.exists():
        with open(CURRENT_NODE_FILE, "r", encoding="utf-8") as stream:
            return json.load(stream)
    return None


def render_roadmap(roadmap: Any) -> None:
    st.subheader("Developmental Roadmap")
    st.markdown(f"**Summary:** {roadmap.summary}")
    
    st.markdown("---")
    st.markdown(f"**Overall Strategy:** {roadmap.overall_reasoning}")
    st.markdown("---")

    with st.expander("🧠 Mindset Shifts", expanded=True):
        st.markdown(f"**Why:** {roadmap.mindset_reasoning}")
        st.markdown("**Required Shifts:**")
        for shift in roadmap.mindset_shifts:
            st.markdown(f"- {shift}")

    with st.expander("📋 Habit Changes", expanded=True):
        st.markdown(f"**Why:** {roadmap.habit_reasoning}")
        st.markdown("**New Habits to Develop:**")
        for habit in roadmap.habit_changes:
            st.markdown(f"- {habit}")

    with st.expander("🎯 Skill Recommendations", expanded=True):
        for skill in roadmap.skill_recommendations:
            with st.container(border=True):
                st.markdown(f"### {skill.skill}")
                st.markdown(f"**Why this matters:** {skill.explanation}")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Current Level:** {skill.current_level or 'Not yet developed'}")
                with col2:
                    st.markdown(f"**Target Level:** {skill.target_level}")
                st.markdown("**Recommended Actions:**")
                for action in skill.recommended_actions:
                    st.markdown(f"- {action}")
                st.markdown("---")


def main():
    st.set_page_config(page_title="Local IPIP-NEO 120 Assessment", page_icon="🧠")
    tabs = st.tabs(["Personality Assessment", "Future Self Definition"])

    with tabs[0]:
        st.title("Local IPIP-NEO 120 Personality Assessment")
        st.markdown(
            "Use this tool to complete a local IPIP-NEO 120 questionnaire and generate a personality profile `personality_profile.json`, `SOUL.md`, and `current_node.json`."
        )

        user_name = st.text_input("Username", value=os.getenv("ASSESSMENT_USER_NAME", "assessment_user"))
        full_name = st.text_input("Full name", value=os.getenv("ASSESSMENT_USER_FULLNAME", user_name))
        sex = st.selectbox("Sex", ["M", "F", "N"], index=0)
        age = st.number_input("Age", min_value=10, max_value=110, value=int(os.getenv("ASSESSMENT_USER_AGE", "30")))

        questions = ASSESSMENT_MODULE.load_questions()
        if not questions:
            st.error("Could not load the assessment questions. Check the data path.")
            return

        st.write("### Answer all questions using a value from 1 to 5")
        answers = []
        for question in questions:
            key = f"question_{question.get('id')}"
            answers.append(
                {
                    "id_question": int(question.get("id", 0)),
                    "id_select": st.radio(
                        f"{question.get('id')}. {question.get('text')}",
                        [1, 2, 3, 4, 5],
                        index=2,
                        key=key,
                        horizontal=True,
                    ),
                }
            )

        if st.button("Generate Personality Profile"):
            user_info = {
                "username": user_name,
                "name": full_name,
                "sex": sex,
                "age": age,
            }
            try:
                output = ASSESSMENT_MODULE.run(
                    profile_name=f"{user_name}_assessment",
                    user_info=user_info,
                    answers=answers,
                    answers_file=None,
                    shuffle=False,
                    save_profile_path=None,
                )
                st.success("Personality profile generated successfully.")
                st.write("**Files created:**")
                st.write(f"- {output['personality_profile_json']}")
                st.write(f"- {output['soul_md']}")
                st.write(f"- {output['current_node']}")
            except Exception as error:
                st.error(f"Failed to generate assessment: {error}")

    with tabs[1]:
        st.title("Future Self Definition")
        st.markdown("Define your target identity, skills, and mindset to generate a gap-analysis roadmap.")

        target_identity = st.text_input("Target Identity", key="target_identity")
        desired_mindset = st.text_area("Desired Mindset / Habits", key="desired_mindset", height=140)

        st.markdown("### Target Skills")
        proficiency_options = ["Beginner", "Intermediate", "Advanced", "Expert"]
        skills = []
        for index in range(5):
            cols = st.columns([3, 2])
            skill_name = cols[0].text_input(f"Skill name #{index + 1}", key=f"skill_name_{index}")
            desired_level = cols[1].selectbox("Proficiency", proficiency_options, index=1, key=f"skill_level_{index}")
            skills.append({"name": skill_name.strip(), "desired_proficiency": desired_level})

        if st.button("Save Target Node"):
            chosen_skills = [skill for skill in skills if skill["name"]]
            if not target_identity.strip():
                st.error("Please provide a Target Identity.")
            elif not desired_mindset.strip():
                st.error("Please provide your desired mindset / habits.")
            elif not chosen_skills:
                st.error("Please define at least one target skill.")
            else:
                try:
                    target_state = TargetState(
                        target_identity=target_identity.strip(),
                        target_skills=[skill for skill in chosen_skills],
                        desired_mindset=desired_mindset.strip(),
                    )
                    save_target_node(target_state)
                    st.success(f"TargetNode.json saved successfully to {TARGET_NODE_FILE}.")
                except Exception as error:
                    st.error(f"Unable to save target node: {error}")

        target_data = load_target_node()
        if target_data:
            with st.expander("Loaded TargetNode.json"):
                st.json(target_data)

        current_data = load_current_node()
        if current_data:
            with st.expander("Loaded CurrentNode.json"):
                st.json(current_data)
        else:
            st.warning("CurrentNode.json not found. Generate a personality profile first.")

        if st.button("Generate Developmental Roadmap"):
            if not TARGET_NODE_FILE.exists():
                st.error("TargetNode.json not found. Save the target node first.")
            elif not CURRENT_NODE_FILE.exists():
                st.error("CurrentNode.json not found. Run the assessment first to generate it.")
            else:
                try:
                    analyzer = GapAnalyzer()
                    roadmap = analyzer.analyze()
                    st.success("Developmental roadmap generated successfully.")
                    render_roadmap(roadmap)
                except Exception as error:
                    st.error(f"Failed to generate roadmap: {error}")


if __name__ == "__main__":
    main()
