import requests
import os
import logging
from datetime import datetime
from app.models.news_item import NewsItem


API_KEY = os.getenv("GNEWS_API_KEY")

logger = logging.getLogger("uvicorn.error")

# GNews endpoints
TOP_HEADLINES_URL = "https://gnews.io/api/v4/top-headlines"
SEARCH_URL = "https://gnews.io/api/v4/search"

COUNTRY_QUERY = {
    "dk": "Denmark",
    "no": "Norway",
    "se": "Sweden",
    "gb": "United Kingdom",
    "ie": "Ireland",
    "us": "United States",
    "nl": "Netherlands",
    "be": "Belgium",
    "de": "Germany",
    "fr": "France",
    "ch": "Switzerland",
    "at": "Austria",
    "it": "Italy",
    "pt": "Portugal",
    "pl": "Poland",
    "cz": "Czech Republic",
    "sk": "Slovakia",
    "si": "Slovenia",
    "hu": "Hungary",
    "ro": "Romania",
    "bg": "Bulgaria",
    "gr": "Greece",
    "lv": "Latvia",
    "lt": "Lithuania",
    "rs": "Serbia",
    "ru": "Russia",
    "ua": "Ukraine",
    "il": "Israel",
    "ae": "United Arab Emirates",
    "tr": "Turkey",
    "th": "Thailand",
    "id": "Indonesia"
}

LANGUAGE_BY_COUNTRY = {
    "dk": "da",
    "no": "no",
    "se": "sv",
    "gb": "en",
    "ie": "en",
    "us": "en",
    "nl": "nl",
    "be": "nl",
    "de": "de",
    "fr": "fr",
    "ch": "de",
    "at": "de",
    "it": "it",
    "pt": "pt",
    "pl": "pl",
    "cz": "cs",
    "sk": "sk",
    "si": "sl",
    "hu": "hu",
    "ro": "ro",
    "bg": "bg",
    "gr": "el",
    "lv": "lv",
    "lt": "lt",
    "rs": "sr",
    "ru": "ru",
    "ua": "uk",
    "il": "he",
    "ae": "ar",
    "tr": "tr",
    "th": "th",
    "id": "id"
}

FALLBACK_QUERIES_BY_COUNTRY = {
    "dk": ["danmark", "dansk", "denmark", "copenhagen", "koebenhavn"]
}

POSITIVE_KEYWORDS = {"rally", "growth", "record", "gain"}
NEGATIVE_KEYWORDS = {"drop", "tighten", "flu", "risk", "loss"}

TOPIC_KEYWORDS = {

    "Investments": {"stock", "fund", "equity", "dividend", "crypto", "bitcoin", "portfolio", "yield", "bonds", "shares", "nasdaq", "dow", "investor", "interest rate", "inflation"},
    "Business": {"market", "business", "ipo", "finance", "dollar", "economy", "bank", "corporate", "merger", "ceo", "revenue", "startup"},
    "Conflict & Crime": {"war", "crime", "police", "military", "attack", "conflict", "murder", "arrest", "court", "fraud", "scam", "missile", "troops"},
    "Fashion": {"fashion", "style", "trend", "designer", "runway", "apparel", "vogue", "brand", "luxury", "clothing", "wear", "outfit"},
    "Travel": {"travel", "flight", "tourism", "airline", "hotel", "vacation", "tourist", "destination", "border", "passenger"},
    "Sports": {"game", "nba", "spurs", "sports", "athletic", "court", "match", "team", "player", "olympics", "championship", "tournament", "football", "soccer", "tennis"},
    "Technology": {"cybersecurity", "ai", "tech", "software", "vulnerability", "online", "data", "apple", "google", "microsoft", "chip", "semiconductor", "app"},
    "Health": {"health", "flu", "medical", "vaccine", "virus", "hospital", "disease", "treatment", "cancer", "doctor", "patient", "clinic"},
    "Politics": {"election", "vote", "president", "government", "parliament", "law", "minister", "senate", "policy", "democrat", "republican", "campaign"},
    "Entertainment": {"movie", "music", "actor", "celebrity", "hollywood", "film", "concert", "award", "star", "netflix", "show", "album"}
}

DK_QUERY_TERMS = [
    "Danmark",
    "København",
    "Mette Frederiksen",
    "regering"
]


def _parse_published_hour(raw_date):
    if not raw_date:
        return None

    try:
        dt_str = raw_date.replace("Z", "+00:00")
        return datetime.fromisoformat(dt_str).hour
    except ValueError:
        return None


def _score_sentiment(text):
    lowered = (text or "").lower()
    if any(word in lowered for word in POSITIVE_KEYWORDS):
        return 0.4
    if any(word in lowered for word in NEGATIVE_KEYWORDS):
        return -0.4
    return 0.0


def _classify_topic(text):
    lowered = (text or "").lower()
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(word in lowered for word in keywords):
            return topic
    return "General"


def _build_dk_query(category):
    fallback_terms = FALLBACK_QUERIES_BY_COUNTRY.get("dk", [])
    terms = DK_QUERY_TERMS + fallback_terms
    base = " OR ".join(terms)
    if category:
        return f"({base}) AND {category}"
    return base

def _get_mock_articles():
    # Simulerer en lang artikel på omkring 4000 ord
    long_body_sim = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 300 + 
        " Analysis shows extensive long-form coverage of this breaking event. " * 100
    )

    mock_items = [
        {"title": "Global markets steady after mixed earnings", "description": "Stocks remained unchanged as tech rally offsets health sector declines.", "source": "Reuters", "topic": "Business", "published_hour": 11, "url": "https://reuters.com", "content": long_body_sim},
        {"title": "Elections update: key races tighten in final week", "description": "New polling data suggests tight margins in key swing areas.", "source": "AP News", "topic": "Politics", "published_hour": 11, "url": "https://apnews.com", "content": long_body_sim},
        {"title": "New AI tools reshape newsroom workflows", "description": "Automated editors and summarizers gain widespread adoption.", "source": "BBC News", "topic": "Technology", "published_hour": 11, "url": "https://bbc.com", "content": long_body_sim},
        {"title": "Copenhagen hosts sustainability summit", "description": "Leaders discuss climate metrics and new green infrastructure bonds.", "source": "CNN", "topic": "Health", "published_hour": 12, "url": "https://cnn.com", "content": long_body_sim},
        {"title": "Tech shares rally as chip demand rises", "description": "Semiconductor manufacturing reaches new historical highs this quarter.", "source": "Bloomberg", "topic": "Technology", "published_hour": 12, "url": "https://bloomberg.com", "content": long_body_sim},
        {"title": "Health officials monitor seasonal flu trends", "description": "Early indicators show moderate levels with updated treatments available.", "source": "DR Nyheder", "topic": "Health", "published_hour": 11, "url": "https://dr.dk", "content": long_body_sim},
        {"title": "Breakthrough in quantum computing efficiency", "description": "Scientists stabilize qubits at slightly higher temperatures.", "source": "TechRadar", "topic": "Science", "published_hour": 12, "url": "https://techradar.com", "content": long_body_sim},
        {"title": "Football championship group stages conclude", "description": "Underdog team advances after a dramatic final match penalty.", "source": "ESPN", "topic": "Sports", "published_hour": 12, "url": "https://espn.com", "content": long_body_sim},
        {"title": "Central bank signals potential rate cut", "description": "Inflation targets flattening faster than initially projected.", "source": "Financial Times", "topic": "Business", "published_hour": 11, "url": "https://ft.com", "content": long_body_sim},
        {"title": "Mars rover discovers ancient water paths", "description": "Sedimentary rock patterns confirm historical stream flows on surface.", "source": "NASA", "topic": "Science", "published_hour": 12, "url": "https://nasa.gov", "content": long_body_sim}
    ]

    return [
        NewsItem(
            title=item["title"],
            url=item["url"],
            source=item["source"],
            description=item["description"],
            topic=item["topic"],
            published_hour=item["published_hour"],
            content=item["content"]  # <-- Tilføj denne linje
        )
        for item in mock_items
    ]

    return [
        NewsItem(
            title=item["title"],
            url=item["url"],
            source=item["source"],
            description=item["description"],
            topic=item["topic"],
            published_hour=item["published_hour"]
        )
        for item in mock_items
    ]

def _is_rate_limited(response):
    if response.status_code == 429:
        return True

    try:
        body = response.json()
    except ValueError:
        return False

    if isinstance(body, dict):
        message = body.get("message") or ""
        errors = body.get("errors") or []
        combined = " ".join([message] + errors)
        combined = combined.lower()
        return (
            "request limit" in combined
            or "too many requests" in combined
            or "rate limit" in combined
        )

    return False

def get_top_headlines(country="us", category=None, search_mode=None):
    if not API_KEY:
        return None, "GNEWS_API_KEY is not set", 500

    if country == "dk":
        if search_mode not in {"strict", "broad"}:
            search_mode = "strict"
    else:
        search_mode = None

    use_dk_fallback = search_mode == "broad"

    query_suffix = category if category else None
    dk_query = _build_dk_query(category) if country == "dk" else None

    # Pass parameters to the API
    params = {
        "country": country,
        "token": API_KEY,
        "max": 18
    }

    language = LANGUAGE_BY_COUNTRY.get(country)
    if language:
        params["lang"] = language

    if category:
        params["topic"] = category
        params["q"] = category
    if dk_query:
        params["q"] = dk_query
    
    if country == "dk" and search_mode == "strict":
        logger.info("GNews top-headlines params: %s", params)
        response = requests.get(TOP_HEADLINES_URL, params=params)

        if _is_rate_limited(response):
            return _get_mock_articles(), None, None
        if response.status_code != 200:
            message = "GNews API error"
            try:
                body = response.json()
                if isinstance(body, dict):
                    if body.get("message"):
                        message = body["message"]
                    elif body.get("errors"):
                        message = ", ".join(body["errors"])
            except ValueError:
                if response.text:
                    message = response.text
            return None, f"{message}", response.status_code

        articles = response.json().get("articles", [])
    elif country == "dk":
        articles = []
    else:
        logger.info("GNews top-headlines params: %s", params)
        response = requests.get(TOP_HEADLINES_URL, params=params)

        if _is_rate_limited(response):
            return _get_mock_articles(), None, None
        if response.status_code != 200:
            message = "GNews API error"
            try:
                body = response.json()
                if isinstance(body, dict):
                    if body.get("message"):
                        message = body["message"]
                    elif body.get("errors"):
                        message = ", ".join(body["errors"])
            except ValueError:
                if response.text:
                    message = response.text
            return None, f"{message}", response.status_code

        articles = response.json().get("articles", [])

    if not articles and country == "dk" and use_dk_fallback:
        fallback_queries = FALLBACK_QUERIES_BY_COUNTRY.get(country)
        if fallback_queries:
            query_list = list(fallback_queries)
        else:
            query_list = []
            if category:
                query_list.append(category)

            country_query = COUNTRY_QUERY.get(country)
            if country_query:
                query_list.append(country_query)

            if not query_list:
                query_list.append("news")

        for query in query_list:
            if dk_query:
                query = dk_query
            elif query_suffix:
                if query:
                    query = f"{query} AND {query_suffix}"
                else:
                    query = query_suffix
            search_params = {
                "q": query,
                "token": API_KEY,
                "max": 18,
                "sortby": "publishedAt"
            }

            if country == "dk":
                language_candidates = ["da", "en"]
            else:
                language_candidates = [language] if language else [None]

            for lang in language_candidates:
                if lang:
                    search_params["lang"] = lang
                else:
                    search_params.pop("lang", None)

                logger.info("GNews search params: %s", search_params)
                search_response = requests.get(SEARCH_URL, params=search_params)
                logger.info(
                    "GNews search status=%s totalArticles=%s",
                    search_response.status_code,
                    (search_response.json().get("totalArticles")
                     if search_response.headers.get("content-type", "").startswith("application/json")
                     else "n/a")
                )

                if _is_rate_limited(search_response):
                    return _get_mock_articles(), None, None
                if search_response.status_code != 200:
                    message = "GNews API error"
                    try:
                        body = search_response.json()
                        if isinstance(body, dict):
                            if body.get("message"):
                                message = body["message"]
                            elif body.get("errors"):
                                message = ", ".join(body["errors"])
                    except ValueError:
                        if search_response.text:
                            message = search_response.text
                    return None, f"{message}", search_response.status_code

                articles = search_response.json().get("articles", [])
                if articles:
                    break

            if articles:
                break

    # Map (transform) the News API's data to NewsItem model
    news_list = []
    hour_counts = {}
    for art in articles[:18]:
        source = art.get("source") or {}
        raw_date = art.get("publishedAt") or art.get("published_date")
        base_hour = _parse_published_hour(raw_date)
        published_hour = None
        if base_hour is not None:
            seen_count = hour_counts.get(base_hour, 0)
            hour_counts[base_hour] = seen_count + 1
            published_hour = base_hour + (seen_count * 0.05) if seen_count else base_hour
        text_blob = f"{art.get('title', '')} {art.get('description', '')}"
        sentiment = _score_sentiment(text_blob)

        # Access the category passed into the get_top_headlines outer function signature
        if category and category != "All categories":
            topic = category.title()
        else:
            topic = _classify_topic(text_blob)
        item = NewsItem(
            title=art.get("title", ""),
            url=art.get("url", ""),
            source=source.get("name", "Unknown source"),
            description=art.get("description"),
            topic=topic,
            published_hour=published_hour,
            sentiment=sentiment
        )
        news_list.append(item)
    return news_list, None, None