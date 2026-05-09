import os
import traceback

from groq import Groq

from app.retriever import search_catalog

from app.utils import (
    build_context,
    latest_user_message,
    detect_comparison,
    detect_refinement,
    is_vague,
    out_of_scope,
    get_clarification_question,
    get_test_type
)

from app.prompts import (
    SYSTEM_PROMPT,
    COMPARISON_PROMPT,
    RECOMMENDATION_PROMPT
)

from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def format_recommendation(item):

    return {
        "name": item.get("name", ""),
        "url": item.get("link", ""),
        "test_type": get_test_type(item),
        "duration": item.get("duration", ""),
        "remote_testing": item.get("remote", ""),
        "adaptive_support": item.get("adaptive", ""),
        "description": item.get("description", ""),
        "languages": item.get("languages", []),
        "job_levels": item.get("job_levels", []),
        "keys": item.get("keys", [])
    }


def generate_reply(messages):

    try:

        latest_query = latest_user_message(messages)

        full_context = build_context(messages)

        # =========================
        # OUT OF SCOPE GUARDRAIL
        # =========================
        if out_of_scope(latest_query):

            return {
                "reply": (
                    "I can only assist with SHL "
                    "assessment recommendations."
                ),
                "recommendations": [],
                "end_of_conversation": True
            }

        # =========================
        # CLARIFICATION HANDLING
        # =========================
        if is_vague(full_context):

            return {
                "reply": get_clarification_question(full_context),
                "recommendations": [],
                "end_of_conversation": False
            }

        # =========================
        # RETRIEVAL
        # =========================
        retrieved = search_catalog(full_context)

        # No retrieval results
        if not retrieved:

            return {
                "reply": (
                    "I could not find relevant SHL "
                    "assessments for this request. "
                    "Could you provide more details?"
                ),
                "recommendations": [],
                "end_of_conversation": False
            }

        # =========================
        # COMPARISON MODE
        # =========================
        if detect_comparison(latest_query):

            context = "\n\n".join([
                f"""
NAME: {item.get('name', '')}

DESCRIPTION:
{item.get('description', '')[:1500]}

JOB LEVELS:
{', '.join(item.get('job_levels', []))}

LANGUAGES:
{', '.join(item.get('languages', []))}

DURATION:
{item.get('duration', '')}

TEST TYPE:
{get_test_type(item)}
"""
                for item in retrieved[:5]
            ])

            prompt = f"""
{COMPARISON_PROMPT}

USER QUERY:
{latest_query}

CATALOG DATA:
{context}
"""

            try:

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "system",
                            "content": SYSTEM_PROMPT
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0
                )

                return {
                    "reply": response.choices[0].message.content,
                    "recommendations": [],
                    "end_of_conversation": False
                }

            except Exception as e:

                traceback.print_exc()

                return {
                    "reply": (
                        "I encountered an issue while "
                        "comparing the assessments."
                    ),
                    "recommendations": [],
                    "end_of_conversation": False
                }

        # =========================
        # RECOMMENDATION MODE
        # =========================
        recommendations = []

        for item in retrieved[:5]:

            recommendations.append(
                format_recommendation(item)
            )

        recommendation_context = "\n\n".join([
            f"""
NAME: {item.get('name', '')}

DESCRIPTION:
{item.get('description', '')[:1000]}

JOB LEVELS:
{', '.join(item.get('job_levels', []))}

LANGUAGES:
{', '.join(item.get('languages', []))}

DURATION:
{item.get('duration', '')}

TEST TYPE:
{get_test_type(item)}

KEYS:
{', '.join(item.get('keys', []))}
"""
            for item in retrieved[:5]
        ])

        prompt = f"""
{RECOMMENDATION_PROMPT}

USER REQUIREMENTS:
{full_context}

RECOMMENDED ASSESSMENTS:
{recommendation_context}
"""

        try:

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0
            )

            return {
                "reply": response.choices[0].message.content,
                "recommendations": recommendations,
                "end_of_conversation": False
            }

        except Exception as e:

            traceback.print_exc()

            return {
                "reply": (
                    "Here are some SHL assessments "
                    "that may fit your requirements."
                ),
                "recommendations": recommendations,
                "end_of_conversation": False
            }

    except Exception as e:

        traceback.print_exc()

        return {
            "reply": (
                f"Unexpected error: {str(e)}"
            ),
            "recommendations": [],
            "end_of_conversation": False
        }