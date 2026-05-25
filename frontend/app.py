import streamlit as st
import requests
import html
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

st.markdown(
    """
    <style>
    html, body, [class*="css"]  {
        font-family: "Inter", "Helvetica Neue", "Segoe UI", sans-serif;
    }
    .app-title {
        font-size: 2.1rem;
        font-weight: 700;
        line-height: 1.2;
        margin-bottom: 0.4rem;
    }
    div[data-testid="stImage"] {
        background: #FFFFFF;
        border: 1px solid #E6E6E6;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 8px;
    }
    div[data-testid="stImage"] img {
        width: 100%;
        height: auto;
    }
    .stSidebar div[data-testid="stSelectbox"] > div {
        border: 1px solid #E6E6E6;
        border-radius: 10px;
        background: #FAFAFA;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Set what is seen in the browser window tab and the main title on the page
st.set_page_config(page_title="NewsSync AI", page_icon="🚀", layout="wide")
st.markdown('<div class="app-title">Welcome to NewsSync AI</div>', unsafe_allow_html=True)

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

mock_articles_by_country = {
    "USA": [
        {
            "title": "Global markets steady after mixed earnings",
            "source": "Reuters",
            "url": "https://example.com/markets-steady",
            "description": "Investors weigh tech gains against softer retail data as trading volumes ease. Analysts say the mixed results point to a cautious outlook for the next quarter. Several firms reiterated guidance, keeping sentiment stable. Market strategists expect short-term range-bound moves.",
            "topic": "Business",
            "published_hour": 9
        },
        {
            "title": "Elections update: key races tighten in final week",
            "source": "BBC News",
            "url": "https://example.com/elections-update",
            "description": "Polls show a narrower margin across several districts as turnout efforts intensify. Campaigns are focusing on undecided voters with late policy announcements. Analysts note rising engagement in suburban areas. Debate performances are expected to shape final preferences.",
            "topic": "Politics",
            "published_hour": 11
        },
        {
            "title": "New AI tools reshape newsroom workflows",
            "source": "CNN",
            "url": "https://example.com/ai-newsrooms",
            "description": "Editors are adopting automation to speed up breaking news production. Newsrooms are testing summarization, transcription, and fact-check aids. Managers emphasize clear human oversight for sensitive stories. The shift is expected to reduce turnaround times.",
            "topic": "Technology",
            "published_hour": 13
        },
        {
            "title": "Tech shares rally as chip demand rises",
            "source": "Bloomberg",
            "url": "https://example.com/chips-rally",
            "description": "Semiconductor firms report strong quarterly outlooks as data center demand accelerates. Supply chain delays have eased, supporting higher shipment forecasts. Analysts expect continued pricing strength through the year. The rally lifted major tech indices.",
            "topic": "Business",
            "published_hour": 15
        },
        {
            "title": "Health officials monitor seasonal flu trends",
            "source": "Reuters",
            "url": "https://example.com/flu-trends",
            "description": "Hospitals are preparing for a potential winter surge as flu activity increases. Public health officials recommend updated vaccinations for vulnerable groups. Clinics report higher appointment volumes compared to last month. Officials say hospitalization rates remain manageable.",
            "topic": "Health",
            "published_hour": 16
        }
    ],
    "Denmark": [
        {
            "title": "Copenhagen hosts sustainability summit",
            "source": "DR Nyheder",
            "url": "https://example.com/copenhagen-summit",
            "description": "Leaders discuss climate targets and green transport initiatives in Copenhagen. Delegates presented new funding models for city-wide retrofits. Experts highlighted measurable progress in cycling infrastructure. The summit concluded with a shared action plan.",
            "topic": "Energy",
            "published_hour": 9
        },
        {
            "title": "Danish startups attract record investment",
            "source": "Borsen",
            "url": "https://example.com/danish-startups",
            "description": "Funding rounds highlight strong Nordic interest in Danish startups. Several late-stage firms closed larger than expected rounds. Investors cited steady revenue growth and international expansion. The trend signals a healthy venture environment.",
            "topic": "Business",
            "published_hour": 11
        },
        {
            "title": "Regional commuter rail expansion approved",
            "source": "TV2",
            "url": "https://example.com/rail-expansion",
            "description": "New routes aim to reduce travel times across regions and improve reliability. Transport officials say the plan will add capacity during peak hours. Construction is scheduled to begin later this year. Local councils welcomed the investment.",
            "topic": "Business",
            "published_hour": 13
        },
        {
            "title": "Cultural festival draws record visitors",
            "source": "DR Nyheder",
            "url": "https://example.com/cultural-festival",
            "description": "Organizers report higher attendance than last year with strong weekend turnout. The festival expanded its program with new stages and family events. Local businesses saw a boost in foot traffic. Officials praised the event's accessibility.",
            "topic": "Culture",
            "published_hour": 15
        },
        {
            "title": "Public health campaign boosts vaccination uptake",
            "source": "TV2",
            "url": "https://example.com/vaccination-uptake",
            "description": "Officials say new outreach improved local coverage in several municipalities. Mobile clinics and extended hours helped reach more residents. Health authorities noted a clear rise in appointment bookings. The campaign will run through the end of the month.",
            "topic": "Health",
            "published_hour": 17
        }
    ]
}

# Pure mock mode during testing to avoid API usage.
data = mock_articles_by_country.get(selected_country_label, mock_articles_by_country["USA"])

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
    st.write("")

    df = pd.DataFrame(data)
    source_counts = df["source"].value_counts()

    tab1, tab2, tab3 = st.tabs(["Market Distribution", "Timeline Trends", "Efficiency Metrics"])

    with tab1:
        st.write("")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Articles by Source")
            pastel_colors = [
                "#9575CD",
                "#4FC3F7",
                "#4DB6AC",
                "#FFF176",
                "#FF8A65",
                "#BA68C8"
            ]
            fig, ax = plt.subplots(figsize=(6, 4.2))
            ax.pie(
                source_counts.values,
                labels=source_counts.index,
                autopct="%1.0f%%",
                startangle=90,
                colors=pastel_colors,
                textprops={"color": "black"}
            )
            centre_circle = plt.Circle((0, 0), 0.55, fc="white")
            fig.gca().add_artist(centre_circle)
            ax.axis("equal")
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)

    topics_series = df["topic"].value_counts().sort_values(ascending=True)

    if not topics_series.empty:
        with tab1:
            with col2:
                st.subheader("Topics Covered Most")
                fig, ax = plt.subplots(figsize=(6, 4.2))
                ax.barh(topics_series.index, topics_series.values)
                ax.set_xlabel("Count")
                ax.xaxis.set_major_locator(MaxNLocator(integer=True))
                plt.tight_layout()
                st.pyplot(fig, use_container_width=True)

    time_series = df.dropna(subset=["published_hour"]).copy()
    if not time_series.empty:
        time_series["hour"] = time_series["published_hour"].astype(int)

        # Pivot to get a time-series per source (rows=hour, columns=source).
        hourly_by_source = (
            time_series.groupby(["hour", "source"]).size().unstack(fill_value=0)
        )

        with tab2:
            st.write("")
            col3, col4 = st.columns(2)

            with col3:
                st.subheader("Articles Over Time by Source")
                st.line_chart(hourly_by_source, use_container_width=True)

            # Cumulative counts per source to build a stacked area chart over the day.
            cumulative_by_source = hourly_by_source.cumsum()
            with col4:
                st.subheader("Cumulative Articles Over the Day")
                st.area_chart(cumulative_by_source, use_container_width=True)

    df["word_count"] = df["description"].fillna("").str.split().str.len()
    df["read_time_min"] = (df["word_count"] / 200).round(2)
    read_time_by_source = (
        df.groupby("source")["read_time_min"].mean().round(2)
    ).sort_values(ascending=False)

    with tab3:
        st.write("")
        _, col_center, _ = st.columns([1, 2, 1])
        with col_center:
            st.subheader("Estimated Reading Time per Source (min)")
            fig, ax = plt.subplots(figsize=(6, 4.2))
            ax.bar(read_time_by_source.index, read_time_by_source.values)
            ax.set_ylabel("Minutes")
            plt.xticks(rotation=45, ha="right")
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)

    topic_badge_styles = {
        "Business": {"bg": "#E8F5E9", "fg": "#2E7D32"},
        "Technology": {"bg": "#E3F2FD", "fg": "#1565C0"},
        "Politics": {"bg": "#FFEBEE", "fg": "#C62828"},
        "Health": {"bg": "#F3E5F5", "fg": "#6A1B9A"},
        "Energy": {"bg": "#FFF8E1", "fg": "#8D6E63"},
        "Culture": {"bg": "#F1F8E9", "fg": "#2E7D32"},
        "Sports": {"bg": "#E1F5FE", "fg": "#0277BD"}
    }

    def render_article_expander(item):
        title = html.escape(item.get("title", "Unknown title"))
        source = html.escape(item.get("source", "Unknown source"))
        topic = item.get("topic", "General")
        style = topic_badge_styles.get(topic, {"bg": "#ECEFF1", "fg": "#455A64"})
        description = html.escape(item.get("description", ""))
        url = html.escape(item.get("url", ""))

        summary_style = (
            f"background: {style['bg']}; color: {style['fg']};"
            " padding: 10px 12px; border-radius: 10px;"
            " font-weight: 600;"
        )
        details_style = (
            "border: 1px solid #E6E6E6; border-radius: 12px;"
            " padding: 6px; margin-bottom: 12px;"
        )
        body_style = "padding: 8px 12px;"

        st.markdown(
            f"""
            <details style="{details_style}">
                <summary style="{summary_style}">{topic} · {title}</summary>
                <div style="{body_style}">
                    <div><strong>Source:</strong> {source}</div>
                    <div style="margin-top: 6px;">{description}</div>
                    <div style="margin-top: 8px;">
                        <a href="{url}" target="_blank">Open original article</a>
                    </div>
                </div>
            </details>
            """,
            unsafe_allow_html=True
        )

    for item in data:
        render_article_expander(item)