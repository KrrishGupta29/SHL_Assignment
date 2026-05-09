import os
import json

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

documents = []

for item in catalog:

    text = f"""
    {item['name']}
    {item['description']}
    """

    documents.append(text.lower())

# BM25 setup
tokenized_docs = [
    doc.split()
    for doc in documents
]

bm25 = BM25Okapi(tokenized_docs)


def search_catalog(query, top_k=10):

    tokenized_query = (
        query.lower().split()
    )

    scores = bm25.get_scores(
        tokenized_query
    )

    scored_results = list(
        zip(catalog, scores)
    )

    scored_results.sort(
        key=lambda x: x[1],
        reverse=True
    )

    results = []

    seen = set()

    for item, score in scored_results:

        if item["url"] not in seen:

            results.append(item)

            seen.add(item["url"])

        if len(results) >= top_k:
            break

    return results