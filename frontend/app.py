import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# Set what is seen in the browser window tab and the main title on the page
st.set_page_config(page_title="NewsSync AI", page_icon="🚀")
st.title("Welcome to NewsSync AI")

search_query = st.text_input("Search for a topic:")

# URL where the backend container lives inside the Docker network
BACKEND_URL = "http://backend:8000"

st.sidebar.header("Filters")

country_options = {
    "USA": "us",
    "Denmark": "dk",
    "Norway": "no",
    "Sweden": "se",
    "United Kingdom": "gb",
    "Ireland": "ie",
    "Netherlands": "nl",
    "Belgium": "be",
    "Germany": "de",
    "France": "fr",
    "Switzerland": "ch",
    "Austria": "at",
    "Italy": "it",
    "Portugal": "pt",
    "Poland": "pl",
    "Czech Republic": "cz",
    "Slovakia": "sk",
    "Slovenia": "si",
    "Hungary": "hu",
    "Romania": "ro",
    "Bulgaria": "bg",
    "Greece": "gr",
    "Latvia": "lv",
    "Lithuania": "lt",
    "Serbia": "rs",
    "Russia": "ru",
    "Ukraine": "ua",
    "Israel": "il",
    "UAE (Dubai)": "ae",
    "Turkey": "tr",
    "Thailand": "th",
    "Indonesia (Bali)": "id"
}

category_options = {
    "All categories": None,
    "Business": "business",
    "Technology": "technology",
    "Science": "science",
    "Sports": "sports",
    "Health": "health",
    "Entertainment": "entertainment"
}

search_mode_options = {
    "Strict Danish Sources": "strict",
    "Broad Search": "broad"
}

selected_country_label = st.sidebar.selectbox(
    "Select country",
    list(country_options.keys())
)
selected_category_label = st.sidebar.selectbox(
    "Select category",
    list(category_options.keys()),
    index=0
)

selected_country = country_options[selected_country_label]
selected_category = category_options[selected_category_label]

selected_search_mode_label = None
if selected_country == "dk":
    selected_search_mode_label = st.sidebar.selectbox(
        "Search Mode",
        list(search_mode_options.keys()),
        index=0
    )

selected_search_mode = None
if selected_search_mode_label:
    selected_search_mode = search_mode_options[selected_search_mode_label]

mock_articles = [
    {
        "title": "Global markets steady after mixed earnings",
        "source": "Reuters",
        "url": "https://example.com/markets-steady",
        "description": "Investors weigh tech gains against softer retail data."
    },
    {
        "title": "Elections update: key races tighten in final week",
        "source": "BBC News",
        "url": "https://example.com/elections-update",
        "description": "Polls show a narrower margin across several districts."
    },
    {
        "title": "New AI tools reshape newsroom workflows",
        "source": "CNN",
        "url": "https://example.com/ai-newsrooms",
        "description": "Editors adopt automation for faster breaking news."
    },
    {
        "title": "Copenhagen hosts sustainability summit",
        "source": "DR Nyheder",
        "url": "https://example.com/copenhagen-summit",
        "description": "Leaders discuss climate targets and green transport."
    },
    {
        "title": "Tech shares rally as chip demand rises",
        "source": "Bloomberg",
        "url": "https://example.com/chips-rally",
        "description": "Semiconductor firms report strong quarterly outlooks."
    },
    {
        "title": "Health officials monitor seasonal flu trends",
        "source": "AP News",
        "url": "https://example.com/flu-trends",
        "description": "Hospitals prepare for a potential winter surge."
    },
    {
        "title": "Oil prices slip as supply outlook improves",
        "source": "Reuters",
        "url": "https://example.com/oil-prices",
        "description": "Traders adjust to stronger output forecasts."
    },
    {
        "title": "Major tech firm unveils new privacy controls",
        "source": "BBC News",
        "url": "https://example.com/privacy-controls",
        "description": "The update adds clearer options for data sharing."
    },
    {
        "title": "Sports federation announces tournament host",
        "source": "CNN",
        "url": "https://example.com/tournament-host",
        "description": "The event will take place next summer."
    },
    {
        "title": "Danish startups attract record investment",
        "source": "DR Nyheder",
        "url": "https://example.com/danish-startups",
        "description": "Funding rounds highlight strong Nordic interest."
    },
    {
        "title": "Central bank signals cautious rate path",
        "source": "Bloomberg",
        "url": "https://example.com/central-bank",
        "description": "Officials cite mixed inflation indicators."
    },
    {
        "title": "Wildfire containment improves after rainfall",
        "source": "AP News",
        "url": "https://example.com/wildfire-update",
        "description": "Crews continue to monitor hotspots."
    },
    {
        "title": "Energy grid upgrades accelerate across Europe",
        "source": "Reuters",
        "url": "https://example.com/grid-upgrades",
        "description": "Projects aim to improve resilience and capacity."
    },
    {
        "title": "Public transport fares to be frozen this year",
        "source": "BBC News",
        "url": "https://example.com/fare-freeze",
        "description": "Officials say the move supports commuters."
    },
    {
        "title": "New streaming lineup targets family audiences",
        "source": "CNN",
        "url": "https://example.com/streaming-lineup",
        "description": "A slate of shows launches this fall."
    },
    {
        "title": "Cultural festival draws record visitors",
        "source": "DR Nyheder",
        "url": "https://example.com/cultural-festival",
        "description": "Organizers report higher attendance than last year."
    },
    {
        "title": "Pharma sector sees steady demand growth",
        "source": "Bloomberg",
        "url": "https://example.com/pharma-demand",
        "description": "Analysts note stable pipelines and approvals."
    },
    {
        "title": "Regional airline adds new routes",
        "source": "AP News",
        "url": "https://example.com/new-routes",
        "description": "The expansion focuses on short-haul travel."
    }
]

# Pure mock mode during testing to avoid API usage.
data = mock_articles

# Backend request temporarily disabled to avoid API calls.
# try:
#     params = {"country": selected_country}
#     if selected_category:
#         params["category"] = selected_category
#     if selected_search_mode:
#         params["search_mode"] = selected_search_mode
#
#     response = requests.get(BACKEND_URL, params=params)
#     if response.status_code == 200:
#         data = response.json()
#     else:
#         data = mock_articles
# except Exception:
#     data = mock_articles

if search_query:
    search_lower = search_query.strip().lower()
    data = [
        item for item in data
        if search_lower in (item.get("title") or "").lower()
        or search_lower in (item.get("description") or "").lower()
    ]

if not data:
    st.info("No articles match your search.")
else:
    st.success(f"Found: {len(data)} articles")

    df = pd.DataFrame(data)
    source_counts = df["source"].value_counts()

    fig, ax = plt.subplots()
    ax.bar(source_counts.index, source_counts.values)
    ax.set_title("Articles by Source")
    ax.set_ylabel("Count")
    ax.tick_params(axis="x", rotation=45)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.tight_layout()
    st.pyplot(fig)

    for item in data:
        st.subheader(item.get("title", "Unknown title"))
        st.caption(f"Source: {item.get('source', 'Unknown source')}")
        if item.get("description"):
            st.write(item.get("description"))
        if item.get("url"):
            st.write(item.get("url"))
        st.divider()