import re


def build_context(messages):

    user_messages = []

    for msg in messages:

        if msg["role"] == "user":

            user_messages.append(msg["content"])

    return " ".join(user_messages)


def latest_user_message(messages):

    for msg in reversed(messages):

        if msg["role"] == "user":

            return msg["content"]

    return ""


def detect_comparison(query):

    comparison_terms = [
        "compare",
        "difference",
        "vs",
        "versus"
    ]

    return any(term in query.lower() for term in comparison_terms)


def detect_refinement(query):

    refinement_terms = [
        "actually",
        "also",
        "add",
        "include",
        "instead"
    ]

    return any(term in query.lower() for term in refinement_terms)


def is_vague(query):

    query = query.lower().strip()

    vague_phrases = [
        "i need an assessment",
        "need assessment",
        "need a test",
        "hiring",
        "assessment"
    ]

    if query in vague_phrases:
        return True

    if len(query.split()) < 4:
        return True

    return False


def out_of_scope(query):

    blocked_topics = [
        "salary",
        "legal",
        "firing employees",
        "politics",
        "medical advice",
        "prompt injection",
        "ignore previous instructions"
    ]

    return any(
        topic in query.lower()
        for topic in blocked_topics
    )