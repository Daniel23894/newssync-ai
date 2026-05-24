import requests
import os
import logging
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

def get_top_headlines(country="us", category=None, search_mode=None):
    if not API_KEY:
        return None, "GNEWS_API_KEY is not set", 500

    if country == "dk":
        if search_mode not in {"strict", "broad"}:
            search_mode = "strict"
    else:
        search_mode = None

    use_dk_fallback = search_mode == "broad"

    # Pass parameters to the API
    params = {
        "country": country,
        "token": API_KEY,
        "max": 5
    }

    language = LANGUAGE_BY_COUNTRY.get(country)
    if language:
        params["lang"] = language

    if category:
        params["topic"] = category
    
    if country == "dk" and search_mode == "strict":
        logger.info("GNews top-headlines params: %s", params)
        response = requests.get(TOP_HEADLINES_URL, params=params)

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
            search_params = {
                "q": query,
                "token": API_KEY,
                "max": 5,
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
    for art in articles[:5]:
        source = art.get("source") or {}
        item = NewsItem(
            title=art.get("title", ""),
            url=art.get("url", ""),
            source=source.get("name", "Unknown source"),
            description=art.get("description") # .get tries find description. If not there, None will be used instead of a missing paramter crashing the program
        )
        news_list.append(item)
    return news_list, None, None