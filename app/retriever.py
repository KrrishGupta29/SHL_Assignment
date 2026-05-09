import os
import json
import re

from rank_bm25 import BM25Okapi


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

catalog_path = os.path.join(
    BASE_DIR,
    "catalog.json"
)

with open(
    catalog_path,
    "r",
    encoding="utf-8"
) as f:

    catalog = json.load(f)


def preprocess(text):

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    return text.split()


documents = []

for item in catalog:

    text = f"""
    {item.get('name', '')}
    {item.get('description', '')}
    {' '.join(item.get('keys', []))}
    {' '.join(item.get('job_levels', []))}
    {' '.join(item.get('languages', []))}
    {item.get('duration', '')}
    """

    documents.append(text)

tokenized_docs = [
    preprocess(doc)
    for doc in documents
]

bm25 = BM25Okapi(tokenized_docs)


TECH_KEYWORDS = [
    "java",
    "python",
    "sql",
    "cloud",
    "aws",
    "backend",
    "frontend",
    "developer",
    "programming",
    "software",
    "coding",
    "engineering",
    "linux",
    "networking",
    "data",
    "ai",
    "machine learning",
    "javascript",
    "react",
    "node",
    "spring",
    "api",
    "database"
]


def is_technical_query(query):

    query = query.lower()

    return any(
        keyword in query
        for keyword in TECH_KEYWORDS
    )


def score_bonus(item, query):

    score = 0

    query = query.lower()

    name = item.get(
        "name",
        ""
    ).lower()

    description = item.get(
        "description",
        ""
    ).lower()

    keys = " ".join(
        item.get("keys", [])
    ).lower()

    important_words = query.split()

    # Basic keyword overlap
    for word in important_words:

        if word in name:
            score += 8

        if word in description:
            score += 3

    # TECHNICAL ROLE BOOSTING
    if is_technical_query(query):

        if (
            "knowledge & skills"
            in keys
        ):
            score += 25

        # Strong Java-specific boosting
        if "java" in query:

            if "java" in name:
                score += 50

            if "java" in description:
                score += 25

        # Backend engineering boosts
        backend_words = [
            "backend",
            "developer",
            "software",
            "engineering",
            "programming"
        ]

        if any(
            word in query
            for word in backend_words
        ):

            # Cognitive tests useful for engineers
            if (
                "ability & aptitude"
                in keys
            ):
                score += 15

            # Personality useful for stakeholder interaction
            if (
                "personality & behavior"
                in keys
            ):
                score += 10

    # Communication-related boosts
    communication_words = [
        "communication",
        "stakeholder",
        "client",
        "leadership",
        "teamwork",
        "collaboration"
    ]

    if any(
        word in query
        for word in communication_words
    ):

        if (
            "personality & behavior"
            in keys
        ):
            score += 20

        if (
            "communication"
            in name
        ):
            score += 15

    # SHL benchmark-style defaults
    # OPQ32r is heavily used for professional hiring
    if (
        "opq32r"
        in name
    ):

        if any(
            word in query
            for word in [
                "manager",
                "developer",
                "engineer",
                "professional",
                "leadership",
                "stakeholder"
            ]
        ):
            score += 35

    # Verify G+ for technical/professional hiring
    if (
        "verify"
        in name
        and "g+" in name
    ):

        if is_technical_query(query):
            score += 30

    # Penalize unrelated products
    irrelevant_words = [
        "informatica",
        "sales compensation",
        "interviewing",
        "hiring concepts",
        "retail cashier"
    ]

    if any(
        bad in name
        for bad in irrelevant_words
    ):
        score -= 40

    return score


def search_catalog(query, top_k=10):

    tokenized_query = preprocess(query)

    scores = bm25.get_scores(
        tokenized_query
    )

    scored_results = []

    for item, bm25_score in zip(
        catalog,
        scores
    ):

        final_score = (
            bm25_score
            + score_bonus(item, query)
        )

        scored_results.append(
            (item, final_score)
        )

    scored_results.sort(
        key=lambda x: x[1],
        reverse=True
    )

    results = []

    seen = set()

    for item, score in scored_results:

        link = item.get(
            "link",
            ""
        )

        if not link:
            continue

        if link in seen:
            continue

        # Filter irrelevant HR/admin tests
        if is_technical_query(query):

            bad_words = [
                "interviewing",
                "hiring concepts",
                "sales compensation",
                "hr",
                "recruiter"
            ]

            item_name = item.get(
                "name",
                ""
            ).lower()

            if any(
                bad in item_name
                for bad in bad_words
            ):
                continue

        results.append(item)

        seen.add(link)

        if len(results) >= top_k:
            break

    return results