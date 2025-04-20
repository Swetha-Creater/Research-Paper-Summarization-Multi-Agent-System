def classify_topic(text: str, topic_list: list[str]) -> str:
    """
    Simple keyword-based topic classification.
    Returns the first matching topic, or 'Uncategorized'.
    """
    text_lower = text.lower()
    for topic in topic_list:
        if topic.lower() in text_lower:
            return topic
    return "Uncategorized"


def topic_classification_agent(input: dict) -> dict:
    """
    Classifies each item based on topic list.

    Input:
    {
        "items": [
            { "id": "chunk_1", "text": "Transformers improve NLP..." },
            ...
        ],
        "topic_list": ["NLP", "Computer Vision", "Healthcare"]
    }

    Output:
    {
        "classified": [
            { "id": "chunk_1", "text": "...", "classified_topic": "NLP" },
            ...
        ]
    }
    """
    items = input.get("items", [])
    topic_list = input.get("topic_list", [])

    for item in items:
        text = item.get("text", "")
        topic = classify_topic(text, topic_list)
        item["classified_topic"] = topic

    return {"classified": items}
