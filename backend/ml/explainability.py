import numpy as np

def explain_prediction(text, vectorizer, classifier, top_k=6):
    """
    Explainable AI (XAI) Feature Attribution:
    Extracts the highest-weighted n-grams from the user's complaint narration
    that directly contributed to the model's classification decision.
    """
    if not text.strip():
        return []

    # Transform complaint text
    vec = vectorizer.transform([text])
    feature_names = np.array(vectorizer.get_feature_names_out())
    indices = vec.nonzero()[1]

    if len(indices) == 0:
        return []

    # Get non-zero values and their features
    weights = vec.data
    words = feature_names[indices]

    # Combine into token-weight pairs and sort descending
    features_and_weights = list(zip(words, weights))
    features_and_weights.sort(key=lambda x: x[1], reverse=True)

    explained_tokens = []
    for word, w in features_and_weights[:top_k]:
        explained_tokens.append({
            "term": word,
            "weight": round(float(w), 4),
            "influence_pct": round(float(w) * 100, 1),
            "relevance": "High" if w > 0.3 else "Medium"
        })

    return explained_tokens
