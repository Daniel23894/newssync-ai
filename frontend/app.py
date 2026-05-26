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
    .ai-cta {
        display: flex;
        justify-content: center;
        margin: 2px 0 2px 0;
    }
    .ai-cta div[data-testid="stButton"] > button {
        background: #FF7A1A !important;
        color: #FFFFFF !important;
        font-weight: 700;
        font-size: 1.22rem;
        padding: 1.0rem 2.9rem;
        border-radius: 12px;
        border: none;
        transition: all 0.2s ease-in-out;
        min-width: 320px;
        box-shadow: 0 12px 24px rgba(255, 122, 26, 0.4);
        letter-spacing: 0.3px;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.38);
    }
    .ai-cta div[data-testid="stButton"] > button:hover {
        background: #FF6A00 !important;
        transform: translateY(-1px);
    }
    .ai-summary-card {
        background: #1E222B;
        border: 1px solid #2D3139;
        border-radius: 12px;
        padding: 18px 20px;
        margin: 10px 0 24px 0;
        font-family: "Inter", "Helvetica Neue", "Segoe UI", sans-serif;
        line-height: 1.55;
    }
    .ai-summary-label {
        color: #FF6B4A;
        font-weight: 700;
        letter-spacing: 0.04em;
        font-size: 0.82rem;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .ai-summary-text {
        color: #F8FAFC;
        font-size: 0.98rem;
        line-height: 1.58;
        margin-bottom: 14px;
    }
    .ai-summary-list {
        color: #F8FAFC;
        padding-left: 18px;
        margin: 0 0 14px 0;
    }
    .ai-summary-list li {
        margin-bottom: 6px;
    }
    .ai-sentiment-pill {
        display: inline-block;
        background: #2D3139;
        color: #E2E8F0;
        border-radius: 12px;
        padding: 4px 10px;
        font-size: 0.9rem;
        font-weight: 600;
    }
    div[data-testid="stButton"] > button[aria-label="Translate to Local Language"] {
        background: #4A90E2 !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 600 !important;
    }
    div[data-testid="stButton"] > button[aria-label="Translate to Local Language"]:hover {
        background: #3B7BC1 !important;
        color: #FFFFFF !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.html(
    """
    <style>
    /* Force the Streamlit button to be bright branding orange */
    div[data-testid="stButton"] button {
        background-color: #FF6B4A !important;
        color: white !important;
        border: none !important;
        padding: 0.9rem 2.6rem !important;
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        width: auto !important;
        transition: transform 0.1s ease, background-color 0.2s ease !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.38) !important;
    }
    /* Add a subtle hover effect */
    div[data-testid="stButton"] button:hover {
        background-color: #E05333 !important;
        color: white !important;
        transform: scale(1.02);
    }
    </style>
    """
)

# Set what is seen in the browser window tab and the main title on the page
st.set_page_config(
    page_title="NewsSync & Mind AI: AI-Powered Media Analytics Dashboard",
    page_icon="N",
    layout="wide"
)
st.markdown(
    """
    <div style="margin-bottom: 1.5rem;">
        <div class="app-title" style="font-size: 2.2rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.5px;">
            News<span style="color: #FF6B4A;">Sync</span> &amp; Mind <span style="color: #FF6B4A;">AI</span>
        </div>
        <div style="font-size: 1.0rem; color: #8A92A6; font-weight: 450; margin-top: -2px;">
            AI-Powered Media Analytics Dashboard
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

search_col, reset_col = st.columns([5, 1], vertical_alignment="center")
with search_col:
    st.text_input(
        "Search for a topic:",
        key="search_query",
        placeholder="Search for a topic...",
        label_visibility="collapsed"
    )
with reset_col:
    if st.button("Reset", use_container_width=True):
        st.session_state.search_query = ""

search_query = st.session_state.get("search_query", "")

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

prev_country_label = st.session_state.get("prev_country_label")
prev_category_label = st.session_state.get("prev_category_label")
if (
    (prev_country_label is not None and prev_country_label != selected_country_label)
    or (prev_category_label is not None and prev_category_label != selected_category_label)
):
    st.session_state.llm_result = None
    st.session_state.llm_error = None
    st.session_state.llm_translation = None
    st.session_state.llm_translation_error = None

st.session_state.prev_country_label = selected_country_label
st.session_state.prev_category_label = selected_category_label


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

data = []
try:
    params = {"country": selected_country}
    if selected_category:
        params["category"] = selected_category
    if selected_search_mode:
        params["search_mode"] = selected_search_mode

    response = requests.get(BACKEND_URL, params=params)
    if response.status_code == 200:
        data = response.json()
    else:
        data = []
except Exception:
    data = []

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

    if "llm_result" not in st.session_state:
        st.session_state.llm_result = None
    if "llm_error" not in st.session_state:
        st.session_state.llm_error = None
    if "llm_translation" not in st.session_state:
        st.session_state.llm_translation = None
    if "llm_translation_error" not in st.session_state:
        st.session_state.llm_translation_error = None

    def build_llm_payload(items):
        trimmed = items
        return {
            "articles": [
                {
                    "title": item.get("title", ""),
                    "description": item.get("description", ""),
                    "source": item.get("source", ""),
                    "topic": item.get("topic", "")
                }
                for item in trimmed
            ]
        }

    generate_col, translate_col = st.columns([1, 1])
    with generate_col:
        if st.button("Generate AI Summary", use_container_width=True):
            st.session_state.llm_result = None
            st.session_state.llm_error = None
            st.session_state.llm_translation = None
            st.session_state.llm_translation_error = None
            payload = build_llm_payload(data)
            with st.spinner("Generating summary..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/llm/summary",
                        json=payload,
                        timeout=45
                    )
                    if response.status_code == 200:
                        st.session_state.llm_result = response.json()
                    else:
                        st.session_state.llm_error = response.json().get("detail", "LLM request failed")
                except requests.RequestException:
                    st.session_state.llm_error = "Could not reach LLM service."

    with translate_col:
        if st.session_state.get("llm_result"):
            if st.button("Translate to Local Language", key="translate_summary", use_container_width=True):
                st.session_state.llm_translation = None
                st.session_state.llm_translation_error = None
                summary_text = st.session_state.llm_result.get("summary", "")

                country_language_map = {
                    "Denmark": "Danish",
                    "Norway": "Norwegian",
                    "Sweden": "Swedish",
                    "United Kingdom": "English",
                    "Ireland": "English",
                    "USA": "English",
                    "Netherlands": "Dutch",
                    "Belgium": "Dutch",
                    "Germany": "German",
                    "France": "French",
                    "Switzerland": "German",
                    "Austria": "German",
                    "Italy": "Italian",
                    "Portugal": "Portuguese",
                    "Poland": "Polish",
                    "Czech Republic": "Czech",
                    "Slovakia": "Slovak",
                    "Slovenia": "Slovenian",
                    "Hungary": "Hungarian",
                    "Romania": "Romanian",
                    "Bulgaria": "Bulgarian",
                    "Greece": "Greek",
                    "Latvia": "Latvian",
                    "Lithuania": "Lithuanian",
                    "Serbia": "Serbian",
                    "Russia": "Russian",
                    "Ukraine": "Ukrainian",
                    "Israel": "Hebrew",
                    "UAE (Dubai)": "Arabic",
                    "Turkey": "Turkish",
                    "Thailand": "Thai",
                    "Indonesia (Bali)": "Indonesian"
                }
                target_language = country_language_map.get(selected_country_label, "English")

                with st.spinner("Translating summary..."):
                    try:
                        translate_payload = {
                            "text": summary_text,
                            "target_language": target_language
                        }
                        translate_response = requests.post(
                            f"{BACKEND_URL}/llm/translate",
                            json=translate_payload,
                            timeout=30
                        )
                        if translate_response.status_code == 200:
                            st.session_state.llm_translation = translate_response.json().get("translated_text")
                        else:
                            detail = translate_response.json().get("detail", "Translation failed")
                            st.session_state.llm_translation_error = detail
                    except requests.RequestException:
                        st.session_state.llm_translation_error = "Could not reach translation service."

    if st.session_state.llm_error:
        st.error(st.session_state.llm_error)
    elif st.session_state.llm_result:
        result = st.session_state.llm_result
        summary = result.get("summary", "")
        sentiment = result.get("sentiment", "Unknown")
        themes = result.get("themes", [])
        rationale = result.get("rationale", "")

        safe_summary = html.escape(summary)
        safe_sentiment = html.escape(sentiment)
        safe_rationale = html.escape(rationale)
        safe_themes = [html.escape(theme) for theme in themes if str(theme).strip()]
        if not safe_themes:
            safe_themes = ["General"]

        sentiment_value = safe_sentiment.strip().lower()
        if "positive" in sentiment_value:
            sentiment_color = "#7CFF90"
        elif "neutral" in sentiment_value:
            sentiment_color = "#FFE36D"
        elif "negative" in sentiment_value:
            sentiment_color = "#FF8A8A"
        else:
            sentiment_color = "#E2E8F0"

        theme_items = "".join([f"<li>{theme}</li>" for theme in safe_themes])
        rationale_block = ""
        if safe_rationale:
            rationale_block = (
                f"<div class=\"ai-summary-label\" style=\"color:#FF8C69;font-size:0.86rem;\">"
                "Why this sentiment</div>"
                f"<div class=\"ai-summary-text\">{safe_rationale}</div>"
            )

        st.markdown(
            '<h3 style="color: #FF8C69; margin-top: 0; font-size: 1.4rem;">AI Summary</h3>',
            unsafe_allow_html=True
        )

        translated_text = st.session_state.llm_translation
        translation_block = ""
        if translated_text:
            safe_translation = html.escape(translated_text)
            translation_block = (
                f"<div class=\"ai-summary-label\" style=\"color:#FF8C69;font-size:0.86rem;\">Translated summary</div>"
                f"<div class=\"ai-summary-text\" style=\"color:#F8FAFC;line-height:1.58;\">{safe_translation}</div>"
            )

        st.markdown(
            f"""
            <div class="ai-summary-card">
                <div class="ai-summary-label" style="color:#FF8C69;font-size:0.86rem;">Summary</div>
                <div class="ai-summary-text" style="color:#F8FAFC;line-height:1.58;"><strong>{safe_summary}</strong></div>
                <div class="ai-summary-label" style="color:#FF8C69;font-size:0.86rem;">Sentiment</div>
                <div class="ai-summary-text" style="color:#F8FAFC;line-height:1.58;">
                    <span class="ai-sentiment-pill" style="background:{sentiment_color};color:#0B0B0B;">{safe_sentiment}</span>
                </div>
                <div class="ai-summary-label" style="color:#FF8C69;font-size:0.86rem;">Main themes</div>
                <ul class="ai-summary-list" style="color:#F8FAFC;line-height:1.58;">{theme_items}</ul>
                {rationale_block}
                {translation_block}
                <div style="font-size: 0.8rem; color: #718096; margin-top: 12px; border-top: 1px solid #2D3139; padding-top: 8px; font-style: italic;">
                    Note: To optimize performance, the AI summary is generated using the top 12 most relevant articles.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    if st.session_state.llm_translation_error:
        st.error(st.session_state.llm_translation_error)

    df = pd.DataFrame(data)
    df["source"] = df["source"].apply(
        lambda x: f"{str(x)[:15]}..." if len(str(x)) > 15 else str(x)
    )
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
                textprops={"color": "black", "fontsize": 9}
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

            hourly_counts = hourly_by_source.sum(axis=1)
            with col4:
                st.subheader("Articles Per Hour")
                st.bar_chart(hourly_counts, use_container_width=True)

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

    st.markdown('<div style="margin: 16px 0 6px 0;"></div>', unsafe_allow_html=True)

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
        description_text = item.get("description") or ""
        content_text = item.get("content") or ""
        if content_text and description_text and content_text != description_text:
            body_text = f"{description_text}\n\n{content_text}"
        else:
            body_text = content_text or description_text or "No description available."
        body_text = html.escape(body_text)
        url = html.escape(item.get("url", "#"))

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
                    <div style="margin-top: 6px; color: #E2E8F0;">{body_text}</div>
                    <div style="margin-top: 10px;">
                        <a href="{url}" target="_blank" style="display: inline-block; background: #FF6B4A; color: #FFFFFF; padding: 6px 12px; border-radius: 8px; text-decoration: none; font-weight: 600;">
                            Open original article
                        </a>
                    </div>
                </div>
            </details>
            """,
            unsafe_allow_html=True
        )

    for item in data:
        render_article_expander(item)