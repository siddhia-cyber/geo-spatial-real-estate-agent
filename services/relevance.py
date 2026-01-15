def compute_relevance_score(
    vector_score: float,
    property_data: dict,
    bhk=None,
    max_price=None,
    require_gym=False
) -> float:
    """
    Combines semantic similarity with intent signals.
    """

    score = vector_score  # base semantic score

    # Intent-based boosts
    if bhk and property_data["bhk"] == bhk:
        score += 0.25

    if max_price and property_data["price"] <= max_price:
        score += 0.25

    if require_gym and "Gymnasium" in property_data["amenities"]:
        score += 0.15

    return round(score, 3)




