import os


from groq import Groq

from app.retriever import search_catalog
from app.utils import (
    build_context,
    latest_user_message,
    detect_comparison,
    detect_refinement,
    is_vague,
    out_of_scope
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


def generate_reply(messages):

    try:

        latest_query = latest_user_message(messages)

        full_context = build_context(messages)

        # Guardrails
        if out_of_scope(latest_query):

            return {
                "reply": (
                    "I can only assist with SHL "
                    "assessment recommendations."
                ),
                "recommendations": [],
                "end_of_conversation": True
            }

        # Clarification
        if is_vague(full_context):

            return {
                "reply": (
                    "Could you share more about the role, "
                    "skills, seniority, or traits needed?"
                ),
                "recommendations": [],
                "end_of_conversation": False
            }

        # Retrieval
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

        # Comparison mode
        if detect_comparison(latest_query):

            context = "\n\n".join([
                f"""
                NAME: {item['name']}
                DESCRIPTION: {item['description'][:1500]}
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

            except Exception:

                return {
                    "reply": (
                        "I encountered an issue while "
                        "comparing the assessments."
                    ),
                    "recommendations": [],
                    "end_of_conversation": False
                }

        # Recommendation mode
        recommendations = []

        for item in retrieved[:5]:

            recommendations.append({
                "name": item["name"],
                "url": item["url"],
                "test_type": item.get(
                    "test_type",
                    "Assessment"
                )
            })

        recommendation_context = "\n\n".join([
            item["name"]
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

        except Exception:

            return {
                "reply": (
                    "Here are some SHL assessments "
                    "that may fit your requirements."
                ),
                "recommendations": recommendations,
                "end_of_conversation": False
            }

    except Exception:

        return {
            "reply": (
                "An unexpected error occurred while "
                "processing the request."
            ),
            "recommendations": [],
            "end_of_conversation": False
        }