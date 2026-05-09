import os
import sys
from pathlib import Path

# Add project root to path so imports work
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st
from mods.assessment.assessment import AssessmentModule
from mods.config import ProfileManager

PROFILE_MANAGER = ProfileManager(profiles_directory=Path.cwd())
ASSESSMENT_MODULE = AssessmentModule(profile_manager=PROFILE_MANAGER)


def main():
    st.set_page_config(page_title="Local IPIP-NEO 120 Assessment", page_icon="🧠")
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


if __name__ == "__main__":
    main()
