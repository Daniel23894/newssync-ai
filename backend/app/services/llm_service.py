import json
import logging
import os
from typing import List, Optional, Tuple

import requests

from app.models.llm import LLMArticle


MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"

logger = logging.getLogger("uvicorn.error")


def _fallback_summary(articles: List[LLMArticle]) -> dict:
    """Create a lightweight summary when the LLM request fails."""
    topic_counts = {}
    for article in articles:
        topic = (article.topic or "General").strip() or "General"
        topic_counts[topic] = topic_counts.get(topic, 0) + 1

    sorted_topics = sorted(
        topic_counts.items(),
        key=lambda item: item[1],
        reverse=True
    )
    main_topics = [topic for topic, _ in sorted_topics[:5]]

    summary = (
        "Local Fallback: Analyzed "
        f"{len(articles)} articles across these main topics: "
        f"{', '.join(main_topics) if main_topics else 'General'}"
    )

    return {
        "summary": summary,
        "sentiment": "Neutral",
        "themes": main_topics,
        "rationale": "Local fallback used due to LLM request failure."
    }


def _build_article_block(articles: List[LLMArticle]) -> str:
    lines = []
    for idx, article in enumerate(articles, start=1):
        title = (article.title or "").strip()
        source = (article.source or "").strip()
        topic = (article.topic or "General").strip()
        description = (article.description or "").strip()

        lines.append(
            f"{idx}. Title: {title}\n"
            f"   Source: {source}\n"
            f"   Topic: {topic}\n"
            f"   Description: {description}"
        )

    return "\n".join(lines)


def _parse_llm_json(content: str) -> dict:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        return {
            "summary": content.strip(),
            "sentiment": "Unknown",
            "themes": [],
            "rationale": ""
        }

    themes = payload.get("themes") or []
    if not isinstance(themes, list):
        themes = [str(themes)]

    return {
        "summary": str(payload.get("summary", "")).strip(),
        "sentiment": str(payload.get("sentiment", "")).strip(),
        "themes": [str(theme).strip() for theme in themes if str(theme).strip()],
        "rationale": str(payload.get("rationale", "")).strip()
    }


def generate_llm_summary(
    articles: List[LLMArticle]
) -> Tuple[Optional[dict], Optional[str], Optional[int]]:
    """Generate LLM-backed insights with a local fallback for resilience."""
    if not MISTRAL_API_KEY:
        return None, "MISTRAL_API_KEY is not set", 500

    if not articles:
        return None, "No articles provided", 400

    article_block = _build_article_block(articles)

    system_prompt = (
        "You are a news analyst. Return valid JSON only. "
        "No markdown or extra text."
    )
    user_prompt = (
        "Read the articles and produce a short overview. "
        "Focus on main themes and overall sentiment. "
        "Output JSON with keys: summary, sentiment, themes, rationale. "
        "Sentiment must be Positive, Neutral, or Negative.\n\n"
        f"Articles:\n{article_block}"
    )

    payload = {
        "model": "mistral-small-latest",
        "temperature": 0.2,
        "max_tokens": 500,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            MISTRAL_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
    except requests.RequestException:
        logger.exception("Mistral request failed")
        return _fallback_summary(articles), None, None

    if response.status_code != 200:
        message = "Mistral API error"
        try:
            body = response.json()
            message = body.get("message") or body.get("detail") or message
        except ValueError:
            if response.text:
                message = response.text
        logger.warning("Mistral API error: %s", message)
        return _fallback_summary(articles), None, None

    try:
        response_data = response.json()
        content = response_data["choices"][0]["message"]["content"]
    except (KeyError, TypeError, ValueError):
        logger.warning("Unexpected response from Mistral")
        return _fallback_summary(articles), None, None

    return _parse_llm_json(content), None, None
