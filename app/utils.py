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

    words = query.split()

    # ---------------------------
    # 1. EXPLICIT INFORMATIONAL / COMPARISON QUERIES (NEVER VAGUE)
    # ---------------------------
    informational_signals = [
        "what is",
        "difference between",
        "compare",
        "comparison",
        "how does",
        "explain",
        "opq",
        "gsa",
        "verify",
        "assessment center",
        "vs"
    ]

    if any(
        phrase in query
        for phrase in informational_signals
    ):
        return False

    # ---------------------------
    # 2. CLEAR HIRING INTENT PHRASES
    # ---------------------------
    hiring_intents = [
        "i need",
        "we need",
        "we are hiring",
        "looking for",
        "hire",
        "screening",
        "assessment for"
    ]

    has_hiring_intent = any(
        phrase in query
        for phrase in hiring_intents
    )

    # ---------------------------
    # 3. DOMAIN KEYWORDS (TECH + BUSINESS)
    # ---------------------------
    meaningful_keywords = [
        "java", "python", "sql", "cloud",
        "developer", "engineer", "backend",
        "frontend", "devops", "data",
        "machine learning", "ai",
        "communication", "stakeholder",
        "leadership", "manager", "senior",
        "sales", "customer", "analytics",
        "cognitive", "personality", "behavioral"
    ]

    matched = [
        w for w in meaningful_keywords
        if w in query
    ]

    # ---------------------------
    # 4. STRICT VAGUE CHECK
    # ---------------------------

    # If query is extremely short AND no clear intent → vague
    if len(words) < 4:
        return True

    # If hiring intent exists but no meaningful context → vague
    if has_hiring_intent and len(matched) == 0:
        return True

    # If only 1 weak keyword match → still vague
    if len(matched) <= 1 and not has_hiring_intent:
        return True

    return False

def get_clarification_question(query):

    query = query.lower()

    if (
        "contact center" in query
        or "call center" in query
        or "customer service" in query
    ):
        return (
            "What language and regional accent "
            "will the candidates primarily use?"
        )

    if "leadership" in query:
        return (
            "Is this for hiring, promotion, "
            "or leadership development?"
        )

    if (
        "developer" in query
        or "engineer" in query
        or "software" in query
    ):
        return (
            "Which technologies, programming languages, "
            "or seniority level are required?"
        )

    if "sales" in query:
        return (
            "Is this for inside sales, field sales, "
            "or customer-facing account management?"
        )

    return (
        "Could you share more about the role, "
        "skills, seniority, or hiring goals?"
    )

def get_test_type(assessment):

    keys = assessment.get("keys", [])

    if not keys:
        return "Assessment"

    mapping = {
        "Personality & Behavior": "P",
        "Knowledge & Skills": "K",
        "Ability & Aptitude": "A",
        "Biodata & Situational Judgment": "B",
        "Simulations": "S",
        "Competencies": "C"
    }

    result = []

    for key in keys:
        if key in mapping:
            result.append(mapping[key])

    return ",".join(result) if result else "Assessment"
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