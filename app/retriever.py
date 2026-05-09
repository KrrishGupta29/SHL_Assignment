import os
import json
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

catalog_path = os.path.join(BASE_DIR, "catalog.json")

with open(catalog_path, "r", encoding="utf-8") as f:
    catalog = json.load(f)

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

documents = []

for item in catalog:

    text = f"""
    {item['name']}
    {item['description']}
    """

    documents.append(text)

# FAISS embeddings
embeddings = model.encode(documents)

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(np.array(embeddings).astype("float32"))

# BM25 setup
tokenized_docs = [
    doc.lower().split()
    for doc in documents
]

bm25 = BM25Okapi(tokenized_docs)


def search_catalog(query, top_k=10):

    # Semantic retrieval
    query_embedding = model.encode([query])

    distances, indices = index.search(
        np.array(query_embedding).astype("float32"),
        top_k
    )

    semantic_results = []

    for idx in indices[0]:

        semantic_results.append(catalog[idx])

    # BM25 retrieval
    tokenized_query = query.lower().split()

    bm25_scores = bm25.get_scores(tokenized_query)

    bm25_indices = np.argsort(bm25_scores)[::-1][:top_k]

    keyword_results = []

    for idx in bm25_indices:

        keyword_results.append(catalog[idx])

    # Merge unique
    scored = []

    for item in semantic_results:
        scored.append((item, 2))


    

    for item in keyword_results:
        scored.append((item, 1))

    

# Merge scores
    score_map = {}

    for item, score in scored:
        url = item["url"]
        if url not in score_map:
            score_map[url] = {
            "item": item,
            "score": 0
        }

        

    

    

        score_map[url]["score"] += score

    ranked = sorted(
    score_map.values(),
    key=lambda x: x["score"],
    reverse=True
)

    combined = [
    x["item"]
    for x in ranked
]

    seen = set()

    for item in semantic_results + keyword_results:

        if item["url"] not in seen:

            combined.append(item)

            seen.add(item["url"])

    return combined[:10]