import streamlit as st
import requests
import html
import json
import re
from io import BytesIO
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

CHART_FIGSIZE = (6, 4)
CHART_DPI = 100



# Set what is seen in the browser window tab and the main title on the page
st.set_page_config(
    page_title="NewsSync & Mind AI: AI-Powered Media Analytics Dashboard",
    page_icon="N",
    layout="wide"
)
st.markdown(
    """
    <div style="margin-bottom: 1.5rem;">
        <div class="app-title" style="font-size: 2.2rem; font-weight: 800; letter-spacing: -0.5px;">
            News<span style="color: #FF6B4A;">Sync</span> &amp; Mind <span style="color: #FF6B4A;">AI</span>
        </div>
        <div style="font-size: 1.0rem; color: #8A92A6; font-weight: 450; margin-top: -2px;">
            AI-Powered Media Analytics Dashboard
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

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
    .chart-title {
        font-size: 1.75rem !important;
        font-weight: 800 !important;
        line-height: 1.2 !important;
        min-height: 2.1rem;
        margin: 0 0 0.75rem 0;
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
        object-fit: contain;
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
    /* 1. Generate AI Button (Din lækre orange farve) */
    .st-key-btn_generate button {
        background-color: #FF6B4A !important;
        color: white !important;
        border: none !important;
        padding: 0.55rem 1.8rem !important; font-size: 1.15rem !important; font-weight: 700 !important;
        border-radius: 8px !important; transition: transform 0.1s ease, background-color 0.2s ease !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.38) !important;
    }
    .st-key-btn_generate button:hover { background-color: #E05333 !important; transform: scale(1.02); }
    
    /* 2. Translate Button (En stærk, tillidsvækkende UX-blå) */
    .st-key-btn_translate button {
        background-color: #3B82F6 !important; 
        color: white !important;
        border: none !important;
        padding: 0.55rem 1.8rem !important; font-size: 1.15rem !important; font-weight: 700 !important;
        border-radius: 8px !important; transition: transform 0.1s ease, background-color 0.2s ease !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.38) !important;
    }
    .st-key-btn_translate button:hover { background-color: #2563EB !important; transform: scale(1.02); }

    /* 3. Reset Button */
    .st-key-btn_reset button {
        background-color: #374151 !important;
        color: #D1D5DB !important;
        border: none !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: background-color 0.2s ease !important;
    }
    .st-key-btn_reset button:hover { background-color: #4B5563 !important; color: white !important; }
    </style>
    """
)




def clear_search_callback():
    st.session_state.search_query = ""


def render_chart_title(title):
    st.markdown(f'<div class="chart-title">{html.escape(title)}</div>', unsafe_allow_html=True)


def render_chart(figure):
    figure.set_size_inches(*CHART_FIGSIZE, forward=True)
    figure.set_dpi(CHART_DPI)
    figure.tight_layout(pad=1.0)
    image_buffer = BytesIO()
    figure.savefig(
        image_buffer,
        format="png",
        dpi=CHART_DPI,
        bbox_inches=None,
        facecolor=figure.get_facecolor()
    )
    image_buffer.seek(0)
    st.image(image_buffer, use_container_width=True)

# URL where the backend container lives inside the Docker network
BACKEND_URL = "http://backend:8000"
DIV_TAG_PATTERN = r"</?div\b[^>]*>"

country_options = {
    "USA": "us", "Denmark": "dk", "Norway": "no", "Sweden": "se",
    "United Kingdom": "gb", "Ireland": "ie", "Netherlands": "nl",
    "Belgium": "be", "Germany": "de", "France": "fr", "Switzerland": "ch",
    "Austria": "at", "Italy": "it", "Portugal": "pt", "Poland": "pl",
    "Czech Republic": "cz", "Slovakia": "sk", "Slovenia": "si",
    "Hungary": "hu", "Romania": "ro", "Bulgaria": "bg", "Greece": "gr",
    "Latvia": "lv", "Lithuania": "lt", "Serbia": "rs", "Russia": "ru",
    "Ukraine": "ua", "Israel": "il", "UAE (Dubai)": "ae", "Turkey": "tr",
    "Thailand": "th", "Indonesia (Bali)": "id"
}

category_options = {
    "All categories": None, "Business": "business", "Investments": "investments",
    "Technology": "technology", "Science": "science", "Health": "health",
    "Sports": "sports", "Entertainment": "entertainment", "Politics": "politics",
    "Conflict & Crime": "crime", "Fashion": "fashion", "Travel": "travel"
}

search_mode_options = {
    "Strict Danish Sources": "strict",
    "Broad Search": "broad"
}

st.sidebar.header("Filters")

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

    # 1. Vi prøver at kalde det rigtige API først
    response = requests.get(BACKEND_URL, params=params, timeout=10)
    
    if response.status_code == 200:
        # SUCCES: Hvis API'et svarer, bruger vi de RIGTIGE live data!
        data = response.json()
        
        # SIKKERHED: Hvis API'et svarer med en tom liste, henter vi mock som backup
        if not data:
            if selected_country == "dk":
                data = [
                    {"title": "Globalt marked stabiliseres efter blandet indtjening", "description": "Aktiekurserne forbliver uændrede da tech-sektoren modvirker fald i sundhedssektoren.", "source": "Børsen", "topic": "Business", "published_hour": 4, "url": "https://borsen.dk"},
                    {"title": "Valgupdate: tætte marginer i de afgørende kredse", "description": "Nye meningsmålinger peger på ekstremt tætte løb i de største valgkredse.", "source": "Politiken", "topic": "Politics", "published_hour": 5, "url": "https://politiken.dk"},
                    {"title": "Nye AI-værktøjer ændrer arbejdsgange i mediehusene", "description": "Automatiserede redigeringsværktøjer vinder stor udbredelse på redaktionerne.", "source": "Berlingske", "topic": "Technology", "published_hour": 5, "url": "https://berlingske.dk"},
                    {"title": "København er vært for internationalt klimatopmøde", "description": "Ledere diskuterer grønne infrastrukturobligationer og bæredygtighed.", "source": "DR Nyheder", "topic": "Health", "published_hour": 6, "url": "https://dr.dk"},
                    {"title": "Tech-aktier stiger i takt med stigende efterspørgsel", "description": "Semiconductor-produktionen når nye historiske højder i dette kvartal.", "source": "TV2 Nyheder", "topic": "Technology", "published_hour": 7, "url": "https://tv2.dk"},
                    {"title": "Sundhedsmyndigheder overvåger den seneste influenza-bølge", "description": "Tidlige indikatorer viser moderate niveauer med opdaterede behandlinger.", "source": "Sundhedspolitisk Tidsskrift", "topic": "Health", "published_hour": 4, "url": "https://sundhedspolitisk.dk"},
                    {"title": "Gennembrud inden for kvantecomputeres effektivitet", "description": "Forskere stabiliserer qubits ved markant højere temperaturer.", "source": "Ingeniøren", "topic": "Science", "published_hour": 6, "url": "https://ing.dk"},
                    {"title": "Superligaens mesterskabsspil spidser til", "description": "Underdog-holdet rykker op efter en dramatisk straffesparksafgørelse.", "source": "Bold.dk", "topic": "Sports", "published_hour": 7, "url": "https://bold.dk"},
                    {"title": "Nationalbanken antyder potentiel rentenedsættelse", "description": "Inflationstargets flader ud hurtigere end oprindeligt forventet.", "source": "Finans.dk", "topic": "Business", "published_hour": 5, "url": "https://finans.dk"},
                    {"title": "Mars-rover opdager spor efter historiske vandveje", "description": "Sedimentære klippemønstre bekræfter historiske vandstrømme på overfladen.", "source": "Videnskab.dk", "topic": "Science", "published_hour": 4, "url": "https://videnskab.dk"}
                ]
            elif selected_country == "us":
                data = [
                    {"title": "Global markets steady after mixed earnings", "description": "Stocks remained unchanged as tech rally offsets health sector declines.", "source": "Reuters", "topic": "Business", "published_hour": 4, "url": "https://reuters.com"},
                    {"title": "Elections update: key races tighten in final week", "description": "New polling data suggests tight margins in key swing areas.", "source": "AP News", "topic": "Politics", "published_hour": 5, "url": "https://apnews.com"},
                    {"title": "New AI tools reshape newsroom workflows", "description": "Automated editors and summarizers gain widespread adoption.", "source": "BBC News", "topic": "Technology", "published_hour": 5, "url": "https://bbc.com"},
                    {"title": "Copenhagen hosts sustainability summit", "description": "Leaders discuss climate metrics and new green infrastructure bonds.", "source": "CNN", "topic": "Health", "published_hour": 6, "url": "https://cnn.com"},
                    {"title": "Tech shares rally as chip demand rises", "description": "Semiconductor manufacturing reaches new historical highs this quarter.", "source": "Bloomberg", "topic": "Technology", "published_hour": 7, "url": "https://bloomberg.com"},
                    {"title": "Health officials monitor seasonal flu trends", "description": "Early indicators show moderate levels with updated treatments available.", "source": "NPR News", "topic": "Health", "published_hour": 4, "url": "https://npr.org"},
                    {"title": "Breakthrough in quantum computing efficiency", "description": "Scientists stabilize qubits at slightly higher temperatures.", "source": "TechRadar", "topic": "Science", "published_hour": 6, "url": "https://techradar.com"},
                    {"title": "Football championship group stages conclude", "description": "Underdog team advances after a dramatic final match penalty.", "source": "ESPN", "topic": "Sports", "published_hour": 7, "url": "https://espn.com"},
                    {"title": "Central bank signals potential rate cut", "description": "Inflation targets flattening faster than initially projected.", "source": "Financial Times", "topic": "Business", "published_hour": 5, "url": "https://ft.com"},
                    {"title": "Mars rover discovers ancient water paths", "description": "Sedimentary rock patterns confirm historical stream flows on surface.", "source": "NASA News", "topic": "Science", "published_hour": 4, "url": "https://nasa.gov"}
                ]
    else:
        raise requests.RequestException

except Exception:
    # FALLBACK: Hvis API overhovedet ikke kan nås, eller crasher, bruger vi de tørre mock data baseret på land
    if selected_country == "dk":
        data = [
            {"title": "Globalt marked stabiliseres efter blandet indtjening (MOCK)", "description": "Aktiekurserne forbliver uændrede.", "source": "Børsen", "topic": "Business", "published_hour": 4, "url": "https://borsen.dk"}
        ]
    elif selected_country == "us":
        data = [
            {"title": "Global markets steady after mixed earnings (MOCK)", "description": "Stocks remained unchanged.", "source": "Reuters", "topic": "Business", "published_hour": 4, "url": "https://reuters.com"}
        ]
    else:
        data = []

st.markdown('<div style="max-width: 900px; margin: auto;">', unsafe_allow_html=True)
search_col, reset_col = st.columns([6, 1])

with search_col:
    st.text_input("Search:", key="search_query", placeholder="Search for a topic...", label_visibility="collapsed")

if st.session_state.get("search_query"):
    with reset_col:
        st.button("Reset", key="btn_reset", use_container_width=True, on_click=clear_search_callback)

st.markdown('</div>', unsafe_allow_html=True)

search_query = st.session_state.get("search_query", "")

if search_query:
    search_lower = search_query.strip().lower()
    data = [
        item for item in data
        if search_lower in (item.get("title") or "").lower()
        or search_lower in (item.get("description") or "").lower()
    ]

if selected_category:
    data = [item for item in data if item.get("topic").lower() == selected_category.lower()]

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

    # Tæt og symmetrisk layout for knapperne
    english_speaking_countries = ["USA", "United Kingdom", "Ireland"]

    col_gen, col_trans = st.columns(2)
    
    with col_gen:
        # VIGTIGT: key="btn_generate" triggerer CSS'en
        if st.button("Generate AI Summary", key="btn_generate", use_container_width=True):
            st.session_state.llm_result = None
            st.session_state.llm_error = None
            st.session_state.llm_translation = None
            st.session_state.llm_translation_error = None
            with st.spinner("Generating summary..."):
                try:
                    response = requests.post(f"{BACKEND_URL}/llm/summary", json=build_llm_payload(data), timeout=45)
                    if response.status_code == 200: st.session_state.llm_result = response.json()
                    else: st.session_state.llm_error = "LLM request failed"
                except requests.RequestException:
                    st.session_state.llm_error = "Could not reach LLM service."

    # Vis kun oversættelsesknappen for ikke-engelske lande
    if selected_country_label not in english_speaking_countries:
        with col_trans:
            if st.session_state.get("llm_result"):
                # VIGTIGT: key="btn_translate" triggerer CSS'en
                if st.button("Translate to Local Language", key="btn_translate", use_container_width=True):
                    st.session_state.llm_translation = None
                    st.session_state.llm_translation_error = None
                    
                    res = st.session_state.llm_result
                    full_text_to_translate = json.dumps({
                        "summary": res.get("summary", ""),
                        "themes": res.get("themes", []),
                        "rationale": res.get("rationale", "")
                    }, ensure_ascii=False)
                    
                    target_lang = {
                        "Denmark": "Danish", "Norway": "Norwegian", "Sweden": "Swedish",
                        "Germany": "German", "France": "French", "Russia": "Russian",
                        "Italy": "Italian", "Spain": "Spanish", "Netherlands": "Dutch"
                    }.get(selected_country_label, "English")

                    with st.spinner(f"Translating to {target_lang}..."):
                        try:
                            t_res = requests.post(f"{BACKEND_URL}/llm/translate", json={"text": full_text_to_translate, "target_language": target_lang}, timeout=60)
                            if t_res.status_code == 200: st.session_state.llm_translation = t_res.json().get("translated_text")
                            else: st.session_state.llm_translation_error = "Translation failed"
                        except requests.RequestException:
                            st.session_state.llm_translation_error = "Could not reach translation service."

    if st.session_state.llm_error:
        st.error(st.session_state.llm_error)
    elif st.session_state.llm_result:
        result = st.session_state.llm_result
        summary = result.get("summary", "")
        sentiment = result.get("sentiment", "Unknown")
        themes = result.get("themes", [])
        rationale = result.get("rationale", "") # Tilføjet rationale
        
        def clean_theme(theme):
            theme_text = re.sub(DIV_TAG_PATTERN, "", str(theme), flags=re.IGNORECASE)
            theme_text = theme_text.strip(" -*•")
            theme_text = theme_text.replace("**", "").replace("__", "")
            return html.escape(theme_text)

        safe_themes = [clean_theme(theme) for theme in themes if str(theme).strip()] or ["General"]
        sentiment_val = sentiment.strip().lower()
        
        if "positive" in sentiment_val: sentiment_color = "#7CFF90"
        elif "neutral" in sentiment_val: sentiment_color = "#FFE36D"
        elif "negative" in sentiment_val: sentiment_color = "#FF8A8A"
        else: sentiment_color = "#E2E8F0"

        if st.session_state.llm_translation:
            raw = st.session_state.llm_translation
            try:
                translated = json.loads(raw)
                t_summary = str(translated.get("summary", "")).strip() or summary
                t_themes = translated.get("themes") or themes
                t_rationale = str(translated.get("rationale", "")).strip() or rationale
            except (json.JSONDecodeError, AttributeError, TypeError):
                t_summary = raw
                t_themes = themes
                t_rationale = rationale

            t_summary = re.sub(DIV_TAG_PATTERN, "", t_summary, flags=re.IGNORECASE).strip()
            t_rationale = re.sub(DIV_TAG_PATTERN, "", t_rationale, flags=re.IGNORECASE).strip()
            t_theme_items = "".join([f"<li>{clean_theme(theme)}</li>" for theme in t_themes]) if t_themes else ""
            t_themes_block = f'<div class="ai-summary-label">Main themes</div><ul class="ai-summary-list">{t_theme_items}</ul>' if t_theme_items else ""
            t_rationale_block = f'<div class="ai-summary-label">Why this sentiment</div><div class="ai-summary-text">{html.escape(t_rationale)}</div>' if t_rationale else ""
            card_content = f"""
            <div class="ai-summary-label">AI Summary · Translated</div>
            <div class="ai-summary-text"><strong>{html.escape(t_summary)}</strong></div>
            <div class="ai-summary-label">Sentiment</div>
            <div class="ai-summary-text"><span class="ai-sentiment-pill" style="background:{sentiment_color};color:#0B0B0B;">{html.escape(sentiment)}</span></div>
            {t_themes_block}
            {t_rationale_block}
            """
        else:
            theme_items = "".join([f"<li>{theme}</li>" for theme in safe_themes])
            rationale_block = f'<div class="ai-summary-label">Why this sentiment</div><div class="ai-summary-text">{html.escape(rationale)}</div>' if rationale else ""
            card_content = f"""
            <div class="ai-summary-label">AI Summary</div>
            <div class="ai-summary-text"><strong>{html.escape(summary)}</strong></div>
            <div class="ai-summary-label">Sentiment</div>
            <div class="ai-summary-text"><span class="ai-sentiment-pill" style="background:{sentiment_color};color:#0B0B0B;">{html.escape(sentiment)}</span></div>
            <div class="ai-summary-label">Main themes</div>
            <ul class="ai-summary-list">{theme_items}</ul>
            {rationale_block}
            """

        st.markdown(f'<div class="ai-summary-card">{card_content}</div>', unsafe_allow_html=True)

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
            render_chart_title("Articles by Source")
            # Dine originale bløde farver
            pastel_colors = ["#9575CD", "#4FC3F7", "#4DB6AC", "#FFF176", "#FF8A65", "#BA68C8"]
            
            fig, ax = plt.subplots(figsize=CHART_FIGSIZE, facecolor="none")
            ax.set_facecolor("none")
            
            # Labels (udgivere) og autotexts (%) får nu nøjagtig samme tone og tykkelse
            wedges, texts, autotexts = ax.pie(
                source_counts.values,
                labels=source_counts.index,
                autopct="%1.0f%%",
                startangle=90,
                colors=pastel_colors,
                textprops={"fontsize": 9.5, "color": "#000000", "weight": "500"}
            )
            
            # Tonen på tallene indeni matches 1:1 med kilderne udenfor for et roligt layout
            for autotext in autotexts:
                autotext.set_color('#000000')
                autotext.set_weight('500')
                autotext.set_fontsize(9.5)
            
            centre_circle = plt.Circle((0, 0), 0.55, fc="none", ec="none")
            fig.gca().add_artist(centre_circle)
            ax.axis("equal")
            render_chart(fig)

    topics_series = df["topic"].value_counts().sort_values(ascending=True)

    if not topics_series.empty:
        with tab1:
            with col2:
                render_chart_title("Topics Covered Most")
                fig_topic, ax_topic = plt.subplots(figsize=CHART_FIGSIZE, facecolor="none")
                ax_topic.set_facecolor("none")
                
                # FIX: Ændret til en lidt mørkere, elegant stål-blå nuance
                ax_topic.barh(topics_series.index, topics_series.values, color="#1E88E5", height=0.55)
                
                ax_topic.set_xlabel("Count", color="#000000")
                ax_topic.tick_params(colors="#000000")
                ax_topic.xaxis.set_major_locator(MaxNLocator(integer=True))
                
                ax_topic.spines['top'].set_visible(False)
                ax_topic.spines['right'].set_visible(False)
                for spine in ['left', 'bottom']:
                    ax_topic.spines[spine].set_color("#000000")
                    
                render_chart(fig_topic)

    time_series = df.dropna(subset=["published_hour"]).copy()
    if not time_series.empty:
        time_series["hour"] = time_series["published_hour"].astype(int)
        
        time_series["source"] = time_series["source"].astype(str).str.strip()

        hourly_by_source = (
            time_series.groupby(["hour", "source"]).size().unstack(fill_value=0)
        )
        
        hourly_counts = time_series.groupby("hour").size()

        with tab2:
            st.write("")
            col3, col4 = st.columns(2)

            with col3:
                render_chart_title("Articles Over Time by Source")
                fig_line, ax_line = plt.subplots(figsize=CHART_FIGSIZE, facecolor="none")
                ax_line.set_facecolor("none")
                
                # Uden orange toner: Kører nu i blå, grøn, lilla, pink, cyan og gul
                clean_line_colors = ["#29B6F6", "#66BB6A", "#AB47BC", "#EC407A", "#26A69A", "#FFEE58"]
                for i, column in enumerate(hourly_by_source.columns):
                    color_idx = i % len(clean_line_colors)
                    ax_line.plot(
                        hourly_by_source.index.astype(str), 
                        hourly_by_source[column], 
                        marker='o', 
                        markersize=5, 
                        linewidth=2.2, 
                        label=column,
                        color=clean_line_colors[color_idx]
                    )
                
                ax_line.set_ylabel("Articles", color="#000000")
                ax_line.set_xlabel("Hour", color="#000000")
                ax_line.tick_params(colors="#000000")
                ax_line.yaxis.set_major_locator(MaxNLocator(integer=True))
                
                ax_line.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2, frameon=False, labelcolor="#000000")
                
                ax_line.spines['top'].set_visible(False)
                ax_line.spines['right'].set_visible(False)
                for spine in ['left', 'bottom']:
                    ax_line.spines[spine].set_color("#000000")
                    
                render_chart(fig_line)

            with col4:
                render_chart_title("Articles Per Hour")
                fig_hour, ax_hour = plt.subplots(figsize=CHART_FIGSIZE, facecolor="none")
                ax_hour.set_facecolor("none")
                
                # FIX: Farven er nu ændret til en dyb, elegant blodrød (#991B1B)
                ax_hour.bar(hourly_counts.index.astype(str), hourly_counts.values, color="#991B1B", edgecolor="#7F1D1D", width=0.58)
                
                ax_hour.set_ylabel("Count", color="#000000")
                ax_hour.set_xlabel("Hour", color="#000000")
                ax_hour.tick_params(colors="#000000")
                ax_hour.yaxis.set_major_locator(MaxNLocator(integer=True))
                
                ax_hour.spines['top'].set_visible(False)
                ax_hour.spines['right'].set_visible(False)
                for spine in ['left', 'bottom']:
                    ax_hour.spines[spine].set_color("#000000")
                    
                plt.xticks(rotation=0) 
                render_chart(fig_hour)

    # Beregn læsetid baseret på vores multiplikator
    df["word_count"] = df["description"].fillna("").str.split().str.len() * 150
    df["read_time_min"] = (df["word_count"] / 200).round(2)
    
    # Klargør data til tab3
    read_time_by_source = (
        df.groupby("source")["read_time_min"].mean().round(2)
    ).sort_values(ascending=False)

    with tab3:
        st.write("")
        _, col_center, _ = st.columns([1, 2, 1])
        with col_center:
            render_chart_title("Estimated Reading Time per Source (min)")
            fig_read, ax_read = plt.subplots(figsize=CHART_FIGSIZE, facecolor="none")
            ax_read.set_facecolor("none")
            
            ax_read.bar(read_time_by_source.index, read_time_by_source.values, color="#7E57C2", width=0.55)
            
            ax_read.set_ylabel("Minutes", color="#000000")
            ax_read.tick_params(colors="#000000")
            ax_read.yaxis.set_major_locator(MaxNLocator(integer=True))
            
            ax_read.spines['top'].set_visible(False)
            ax_read.spines['right'].set_visible(False)
            for spine in ['left', 'bottom']:
                ax_read.spines[spine].set_color("#000000")
                
            plt.xticks(rotation=45, ha="right", color="#000000")
            render_chart(fig_read)

    topic_badge_styles = {
        "Business": {"bg": "#E8F5E9", "fg": "#2E7D32"}, 
        "Technology": {"bg": "#E3F2FD", "fg": "#1565C0"},
        "Politics": {"bg": "#FFEBEE", "fg": "#C62828"}, 
        "Health": {"bg": "#F3E5F5", "fg": "#6A1B9A"},
        "Sports": {"bg": "#E1F5FE", "fg": "#0277BD"},
        "Entertainment": {"bg": "#FFF3E0", "fg": "#E65100"},
        
        "Investments": {"bg": "#E8EAF6", "fg": "#283593"},       
        "Conflict & Crime": {"bg": "#FCE4EC", "fg": "#880E4F"}, 
        "Fashion": {"bg": "#F3E5F5", "fg": "#C2185B"},           
        "Travel": {"bg": "#E0F2F1", "fg": "#00695C"}             
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