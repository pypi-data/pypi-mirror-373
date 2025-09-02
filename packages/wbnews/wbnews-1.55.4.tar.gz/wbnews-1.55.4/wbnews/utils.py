import logging

import numpy as np
import pandas as pd
from django.utils.html import strip_tags
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger("news")


def _get_similarity_matrix_df(data: dict[int, str]) -> pd.DataFrame:
    # Convert texts to TF-IDF vectors
    ids, texts = zip(*data.items())
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts)
    # Compute pairwise cosine similarity...
    similarity_matrix = cosine_similarity(tfidf_matrix)
    # convert the matrix into a proper dataframe
    return pd.DataFrame(similarity_matrix, index=ids, columns=ids)


def detect_near_duplicates(data: dict[int, str], threshold: float = 0.9) -> list[int]:
    """
    Detects near-duplicate articles based on TF-IDF & Cosine Similarity.

    Parameters:
    - data (dict[int, str]): dictionary of new id with their respective content
    - threshold (float): Similarity threshold (default = 0.9).

    Returns:
    - List of duplicated ids
    """
    if len(data.keys()) < 2:
        return []
    logger.info(f"Processing {len(data.keys())} news")
    # Cleanup step
    clean_data = {}
    for _id, text in data.items():
        clean_data[_id] = strip_tags(text)

    # get similarity matrix
    df = _get_similarity_matrix_df(data)

    # Replace the lower matrix triangle with NaN
    df = df.where(np.triu(np.ones(df.shape)).astype(bool))
    # melt the symmetrical matrix into a key value store
    df = df.stack().reset_index(name="value")
    # remove duplicate pair with same id (expected to be 1.0)
    df = df[df["level_0"] != df["level_1"]]
    # get duplicates candidates
    df = df[df["value"] > threshold]
    # return only one side of the duplicate pair
    duplicate_ids = df["level_1"].unique().tolist()
    logger.info(f"{len(duplicate_ids)} duplicated news found")

    return duplicate_ids
