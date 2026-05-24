import streamlit as st
import requests

# Set what is seen in the browser window tab and the main title on the page
st.set_page_config(page_title="NewsSync AI", page_icon="🚀")
st.title("Welcome to NewsSync AI")

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

try: 
    # Ping the backend to grab the news data
    params = {"country": selected_country}
    if selected_category:
        params["category"] = selected_category
    if selected_search_mode:
        params["search_mode"] = selected_search_mode

    response = requests.get(BACKEND_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        
        # check if we got a non empty list with articles / data inside, to avoid crash
        if isinstance(data, list) and data:
            st.success(f"Found: {len(data)} articles")

            for item in data:
                st.subheader(item.get("title", "Unknown title"))
                st.caption(f"Source: {item.get('source', 'Unknown source')}")
                if item.get("description"):
                    st.write(item.get("description"))
                if item.get("url"):
                    st.write(item.get("url"))
                st.divider()
        else:
            st.info("No news received from the backend.")
            if selected_country == "dk" and selected_search_mode == "strict":
                st.warning(
                    "Strict Danish Sources only shows articles that GNews has tagged "
                    "as Danish. If GNews has no Danish articles right now, the result "
                    "will be empty. Try selecting Broad Search in 'Search Mode' to include global articles that "
                    "mention Denmark."
                )

    else:
        error_detail = None
        try:
            body = response.json()
            if isinstance(body, dict) and body.get("detail"):
                error_detail = body["detail"]
        except ValueError:
            error_detail = None

        if error_detail:
            st.error(f"Backend error: {error_detail}")
        else:
            st.error(f"Backend returned an error: {response.status_code}")

except Exception as e:
    # catches connection failures if the backend container is completely offline
    st.warning("Could not connect to the backend. Is it running?")
    st.error(f"Technical error: {e}")